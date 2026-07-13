<template>
  <div class="case-api-list">
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <router-link :to="{ name: '用例列表', params: { project_id: $route.params.project_id } }" class="tb-back">
            <i class="fa fa-arrow-left"></i> 用例列表
          </router-link>
          <el-button size="small" @click="addOldApi"><i class="fa fa-plus"></i> 已有接口</el-button>
          <router-link :to="{ name: '添加新接口' }"><el-button size="small"><i class="fa fa-plus"></i> 新建接口</el-button></router-link>
          <el-button type="primary" size="small" @click="TestAllApi"><i class="fa fa-play"></i> 顺序测试全部</el-button>
        </div>
        <div class="tb-right">
          <span class="host-label">测试环境</span>
          <el-select v-model="url" placeholder="选择环境" size="small" style="width:180px">
            <el-option v-for="(item, i) in Host" :key="i" :label="item.name" :value="item.id" />
          </el-select>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="ApiList" v-loading="listLoading" class="data-table">
        <el-table-column type="index" width="55" label="#" />
        <el-table-column prop="name" label="接口名称" min-width="160" sortable show-overflow-tooltip>
          <template slot-scope="scope">
            <router-link :to="{ name: '修改接口', params: { api_id: scope.row.id } }" class="table-link">{{ scope.row.name }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="apiAddress" label="接口地址" min-width="280" sortable show-overflow-tooltip>
          <template slot-scope="scope">
            <span class="method-tag" :class="'method--' + (scope.row.requestType || '').toLowerCase()">{{ scope.row.requestType }}</span>
            <span class="addr-text">{{ scope.row.apiAddress }}</span>
          </template>
        </el-table-column>
        <el-table-column label="测试结果" width="150">
          <template slot-scope="scope">
            <span v-if="scope.row.testStatus" class="result-text result--testing"><i class="fa fa-spinner fa-spin"></i> 测试中</span>
            <span v-else-if="!scope.row.result && !scope.row.testStatus" class="result-text result--none">尚无结果</span>
            <span v-else-if="scope.row.result == 'true' || scope.row.result === true" class="result-text result--pass" @click="resultShow(scope.row)">PASS 详情</span>
            <span v-else-if="scope.row.result == 'false' || scope.row.result === false" class="result-text result--fail" @click="resultShow(scope.row)">FAIL 详情</span>
            <span v-else-if="scope.row.result === 'timeout'" class="result-text result--timeout" @click="resultShow(scope.row)">超时</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="Test(scope.$index, scope.row)">顺序测试</el-button>
            <router-link :to="{ name: '修改接口', params: { api_id: scope.row.id } }"><el-button type="text" size="small">修改</el-button></router-link>
            <el-button type="text" size="small" class="btn--danger" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <el-pagination small layout="total, prev, pager, next, jumper" @current-change="handleCurrentChange" :page-size="10" :current-page.sync="pageApi" :page-count="Math.ceil(totalNum / 10)" :total="totalNum" v-if="totalNum != 0" />
      </div>
    </div>

    <!-- Add existing API dialog -->
    <el-dialog title="选择已有接口" :visible.sync="searchApiListVisible" :close-on-click-modal="false" width="720px">
      <el-row :gutter="12">
        <el-col :span="7">
          <div class="api-group-list">
            <el-menu active-text-color="#1d4ed8" :unique-opened="true" @select="handleSelect">
              <el-menu-item index="-1" @click.native="getApiList()"><i class="fa fa-list"></i> 所有接口</el-menu-item>
              <el-menu-item v-for="(item, i) in groupData" :index="i + ''" :key="item.id" @click.native="getApiList(item.id)">{{ item.name }}</el-menu-item>
            </el-menu>
          </div>
        </el-col>
        <el-col :span="17">
          <el-table :data="searchApiList" v-loading="apiListLoading" @selection-change="selsChange" max-height="360" style="width:100%">
            <el-table-column type="selection" width="50" />
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="requestType" label="方式" width="70" />
            <el-table-column prop="apiAddress" label="地址" min-width="160" show-overflow-tooltip />
          </el-table>
          <el-pagination small layout="prev, pager, next" @current-change="handleCurrentChangeApi" :page-size="20" :page-count="Math.ceil(total / 20)" style="text-align:right;margin-top:10px" />
        </el-col>
      </el-row>
      <div slot="footer"><el-button @click="searchApiListVisible = false">取消</el-button><el-button type="primary" @click="addOldApiSubmit" :loading="searchApi">提交</el-button></div>
    </el-dialog>

    <!-- Test result dialog -->
    <el-dialog title="测试结果" :visible.sync="TestResult" :close-on-click-modal="false" width="680px">
      <div class="result-detail" v-if="result.name">
        <h3 class="result-name">{{ result.name }}</h3>
        <div class="result-row"><span class="dl">请求地址</span><span>{{ result.url }}</span></div>
        <div class="result-row"><span class="dl">请求方式</span><span>{{ result.requestType }}</span></div>
        <div class="result-row"><span class="dl">状态码</span><span>{{ result.statusCode }}</span></div>
        <div class="result-row"><span class="dl">请求时间</span><span>{{ result.testTime }}</span></div>
        <div class="result-divider"></div>
        <h4 class="result-section">请求头部</h4>
        <div class="result-row" v-for="(val, key) in result.header" :key="key"><span class="dl">{{ key }}</span><span class="mono">{{ val }}</span></div>
        <div class="result-divider"></div>
        <h4 class="result-section">请求参数</h4>
        <pre class="result-pre">{{ result.parameter }}</pre>
        <div class="result-divider"></div>
        <h4 class="result-section">返回结果</h4>
        <div class="result-row"><span class="dl">HTTP状态</span><span>{{ result.statusCode }}</span></div>
        <div class="result-row"><span class="dl">校验方式</span><span>{{ result.examineType }}</span></div>
        <div class="result-pre-wrap"><pre class="result-pre">{{ result.data || '无校验规则' }}</pre></div>
        <h4 class="result-section">实际结果</h4>
        <div class="result-row"><span class="dl">HTTP状态</span><span>{{ result.httpStatus }}</span></div>
        <div class="result-pre-wrap"><pre class="result-pre">{{ result.responseData || '无返回内容' }}</pre></div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { test } from '../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      project: '', case: '', ApiList: [], listLoading: false, searchName: '', total: 0, totalNum: 0,
      url: '', Host: [], pageApi: '',
      searchApiListVisible: false, searchApi: false, searchApiList: [], groupData: [], apiListIds: [],
      apiListLoading: false, sels: [], TestResult: false, result: {}, activeIndex: '',
    }
  },
  methods: {
    handleSelect(key) { this.activeIndex = key },
    getCaseApiList() {
      this.listLoading = true; let self = this
      $.ajax({ type: 'get', url: test + '/api/automation/api_list', async: true, data: { project_id: this.$route.params.project_id, page: self.pageApi, name: self.searchName, case_id: this.$route.params.case_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { self.listLoading = false; if (data.code == '999999') { self.ApiList = []; self.total = data.data.total; self.totalNum = data.data.totalNum; data.data.data.forEach((item) => { self.$set(item, 'result', false); self.$set(item, 'testStatus', false); self.ApiList.push(item) }) } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    // 批量顺序执行全部接口（单次请求，支持 $N.field 步骤引用）
    Test(index, row) { this.runBatchTest() },
    TestAllApi() { this.runBatchTest() },
    runBatchTest() {
      if (!this.url) { this.$message({ message: '请选择测试环境', center: true, type: 'warning' }); return }
      var allIds = this.ApiList.map(function (item) { return item.id })
      if (!allIds.length) { this.$message({ message: '无可测试的接口', center: true, type: 'warning' }); return }

      // 全部置为测试中
      var self = this
      this.ApiList.forEach(function (item) {
        self.$set(item, 'result', '')
        self.$set(item, 'testStatus', true)
      })

      $.ajax({
        type: 'post', url: test + '/api/automation/start_test_sequential', async: true,
        data: JSON.stringify({
          project_id: Number(this.$route.params.project_id),
          case_id: Number(this.$route.params.case_id),
          host_id: Number(this.url),
          id: allIds,
        }),
        headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) },
        timeout: 120000,
        success: function (data) {
          if (data.code == '999999' && data.data && data.data.result) {
            data.data.result.forEach(function (r) {
              var row = self.ApiList.find(function (item) { return item.id == r.case_id })
              if (row) {
                self.$set(row, 'testStatus', false)
                var ok = r.success === true || r.success === 'true'
                var fail = r.success === false || r.success === 'false'
                self.$set(row, 'result', ok ? 'true' : fail ? 'false' : String(r.success))
              }
            })
          } else {
            self.ApiList.forEach(function (item) { self.$set(item, 'testStatus', false) })
            self.$message.error({ message: data.msg || '测试失败', center: true })
          }
        },
        error: function () {
          self.ApiList.forEach(function (item) {
            self.$set(item, 'testStatus', false)
            self.$set(item, 'result', 'false')
          })
          self.$message.error({ message: '请求失败，请检查网络', center: true })
        },
      })
    },
    handleDel(index, row) { this.$confirm('确认删除该记录吗?', '提示', { type: 'warning' }).then(() => { this.listLoading = true; let self = this; $.ajax({ type: 'post', url: test + '/api/automation/del_api', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), case_id: Number(this.$route.params.case_id), ids: [row.id] }), headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') self.$message({ message: '删除成功', center: true, type: 'success' }); else self.$message.error({ message: data.msg, center: true }); self.getCaseApiList() } }) }).catch(() => {}) },
    getApiGroup() { let self = this; $.ajax({ type: 'get', url: test + '/api/api/group', async: true, data: { project_id: this.$route.params.project_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') self.groupData = data.data; else self.$message.error({ message: data.msg, center: true }) } }) },
    getApiList(_list) { this.apiListLoading = true; let self = this; let param = { project_id: Number(this.$route.params.project_id), page: self.page }; if (_list) param.apiGroupLevelFirst_id = Number(_list); $.ajax({ type: 'get', url: test + '/api/api/api_list', async: true, data: param, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.apiListLoading = false; if (data.code === '999999') { self.searchApiList = data.data.data; self.total = data.data.total } else { self.$message.error({ message: data.msg, center: true }) } } }) },
    resultShow(row) { this.result.name = row.name; this.getResult(row.id) },
    getResult(_id) { let self = this; $.ajax({ type: 'get', url: test + '/api/automation/look_result', async: true, data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id, api_id: _id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: (data) => { if (data.code === '999999') { self.result.url = data.data.url; self.result.requestType = data.data.requestType; self.result.header = eval('(' + data.data.header + ')'); self.result.parameter = data.data.parameter; self.result.statusCode = data.data.statusCode; self.result.examineType = data.data.examineType; self.result.data = data.data.data; self.result.result = data.data.result; self.result.httpStatus = data.data.httpStatus; self.result.responseData = data.data.responseData.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false'); self.result.testTime = data.data.testTime; self.TestResult = true } else { self.$message.error({ message: data.msg, center: true }) } }, error: function () { self.$message.error({ message: '获取失败', center: true }) } }) },
    addOldApi() { this.searchApiListVisible = true; this.getApiGroup(); this.getApiList() },
    addOldApiSubmit() { let ids = this.sels.map(item => item.id); let self = this; this.$confirm('确认添加选中记录吗？', '提示', { type: 'warning' }).then(() => { $.ajax({ type: 'post', url: test + '/api/automation/add_old_api', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), case_id: Number(this.$route.params.case_id), api_ids: ids }), headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.searchApiListVisible = false; if (data.code === '999999') { self.$message({ message: '添加成功', center: true, type: 'success' }) } else { self.$message.error({ message: data.msg, center: true }) }; self.getCaseApiList() } }) }).catch(() => {}) },
    handleCurrentChange(val) { this.pageApi = val; sessionStorage.setItem('currentPage', val); this.getCaseApiList() },
    handleCurrentChangeApi(val) { this.page = val; if (this.groupData[this.activeIndex]) { this.getApiList(this.groupData[this.activeIndex].id) } else { this.getApiList() } },
    selsChange(sels) { this.sels = sels },
    getHost() { let self = this; $.ajax({ type: 'get', url: test + '/api/global/host_total', async: true, data: { project_id: this.$route.params.project_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: (data) => { if (data.code === '999999') { data.data.data.forEach((item) => { if (item.status) self.Host.push(item) }) } else { self.$message.error({ message: data.msg, center: true }) } } }) },
  },
  created() { this.getHost(); this.pageApi = sessionStorage.getItem('currentPage') || 1; this.getCaseApiList() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

.case-api-list { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }

.toolbar-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: $shadow-sm;
  .tb-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
  .tb-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .tb-right { display: flex; align-items: center; gap: 8px; }
}
.tb-back { display: inline-flex; align-items: center; gap: 6px; font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; text-decoration: none; &:hover { color: $accent; } i { font-size: 12px; } }
.host-label { font-size: 12px; color: $text-tertiary; font-weight: 500; }

.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }
.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }
.table-link { color: $accent; text-decoration: none; font-weight: 500; &:hover { text-decoration: underline; } }

.method-tag { display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 0.03em; padding: 2px 7px; border-radius: 3px; color: #fff; margin-right: 8px;
  &.method--get { background: #059669; } &.method--post { background: #1d4ed8; } &.method--put { background: #d97706; } &.method--delete { background: #dc2626; }
}
.addr-text { font-size: 13px; color: $text-secondary; }

.result-text { font-size: 12px; cursor: default;
  &.result--testing { color: $text-tertiary; }
  &.result--none { color: $text-tertiary; }
  &.result--pass { color: #059669; cursor: pointer; font-weight: 600; &:hover { text-decoration: underline; } }
  &.result--fail { color: #dc2626; cursor: pointer; font-weight: 600; &:hover { text-decoration: underline; } }
  &.result--timeout { color: #d97706; cursor: pointer; font-weight: 600; &:hover { text-decoration: underline; } }
}

.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
.tb-footer { display: flex; justify-content: flex-end; padding: 10px 18px; border-top: 1px solid #f3f4f6; }

.api-group-list { height: 360px; overflow: auto; border: 1px solid $border; border-radius: 6px; }

// Result dialog
.result-detail { max-height: 520px; overflow-y: auto; }
.result-name { font-family: $font-display; font-size: 16px; font-weight: 600; margin: 0 0 14px; color: $text; }
.result-section { font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; margin: 12px 0 8px; }
.result-row { display: flex; gap: 12px; padding: 4px 0; font-size: 13px; .dl { width: 80px; flex-shrink: 0; color: $text-tertiary; } .mono { font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 12px; } }
.result-divider { height: 1px; background: $border; margin: 10px 0; }
.result-pre-wrap { border: 1px solid $border; border-radius: 6px; overflow: hidden; margin-top: 4px; }
.result-pre { margin: 0; padding: 10px 14px; font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; background: #f9fafb; }
</style>
