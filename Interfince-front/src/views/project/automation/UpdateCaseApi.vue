<template>
  <div class="case-form">
    <div class="toolbar">
      <router-link :to="{ name: '用例接口列表', params: { project_id: $route.params.project_id, case_id: $route.params.case_id } }" class="tb-back"><i class="fa fa-arrow-left"></i> 返回列表</router-link>
      <div class="tb-right">
        <router-link :to="{ name: '用例接口列表', params: { project_id: $route.params.project_id, case_id: $route.params.case_id } }" class="tb-btn tb-btn--ghost">取消</router-link>
        <button class="tb-btn tb-btn--primary" @click="updateApi">保存</button>
      </div>
    </div>

    <div class="section-card">
      <h3 class="section-title">基本信息</h3>
      <el-form :model="form" ref="form" :rules="FormRules" class="api-form">
        <div class="form-row">
          <div class="form-col form-col--name">
            <label class="form-label">接口名称</label>
            <el-form-item prop="name" class="form-item--clean"><el-input v-model.trim="form.name" placeholder="名称" size="small" /></el-form-item>
          </div>
        </div>
        <div class="form-row form-row--url">
          <div class="form-col form-col--method">
            <label class="form-label">请求方式</label>
            <el-select v-model="form.request4" placeholder="Method" size="small" @change="checkRequest"><el-option v-for="(item, i) in request" :key="i" :label="item.label" :value="item.value" /></el-select>
          </div>
          <div class="form-col form-col--http">
            <label class="form-label">协议</label>
            <el-select v-model="form.Http4" placeholder="HTTP" size="small"><el-option v-for="(item, i) in Http" :key="i" :label="item.label" :value="item.value" /></el-select>
          </div>
          <div class="form-col form-col--addr">
            <label class="form-label">URL</label>
            <el-form-item prop="addr" class="form-item--clean"><el-input v-model.trim="form.addr" placeholder="请求地址" size="small" /></el-form-item>
          </div>
        </div>
      </el-form>
    </div>

    <el-collapse v-model="activeNames" class="case-collapse">
      <!-- Step mapping hint -->
      <div class="step-map-bar" v-if="Object.keys(stepIndexMap).length">
        <span class="step-map-label">步骤引用映射：</span>
        <span v-for="(step, apiId) in stepIndexMap" :key="apiId" class="step-map-chip">${{ step }} → {{ stepApiNames[apiId] || '接口#' + apiId }}</span>
        <span class="step-map-hint">在参数中使用 <code>$N.字段路径</code> 引用前置步骤的响应</span>
      </div>

      <!-- Headers -->
      <el-collapse-item title="请求头部" name="1" class="collapse-panel">
        <div class="panel-table">
          <div class="panel-row panel-row--head" v-for="(item, index) in form.head" :key="'h' + index">
            <div class="panel-cell panel-cell--name">
              <el-select placeholder="标签" filterable v-model="item.name" size="small" class="head-select"><el-option v-for="(h, i) in header" :key="i" :label="h.label" :value="h.value" /></el-select>
              <el-input v-model.trim="item.name" placeholder="自定义" size="small" class="head-input" />
            </div>
            <div class="panel-cell panel-cell--value">
              <div class="value-input-wrap">
                <el-input v-model.trim="item.value" placeholder="$1.data.token / $var.xxx" size="small" class="value-input" :class="{ 'is-ref': item.value && (item.value.startsWith('$') || item.interrelate) }" />
                <button class="dollar-btn" @click="openVarPicker(index, item, 'head')" title="插入变量引用"><span>$</span></button>
              </div>
            </div>
            <div class="panel-cell panel-cell--action"><button class="icon-btn icon-btn--del" @click="delHead(index)"><i class="fa fa-trash"></i></button></div>
            <div class="panel-cell panel-cell--add" v-if="index === form.head.length - 1"><button class="icon-btn icon-btn--add" @click="addHead"><i class="fa fa-plus"></i></button></div>
          </div>
        </div>
      </el-collapse-item>

      <!-- Params -->
      <el-collapse-item title="请求参数" name="2" class="collapse-panel">
        <div class="param-type-bar">
          <el-radio v-model="radio" label="form-data">表单(form-data)</el-radio>
          <el-radio v-if="request3" v-model="radio" label="raw">源数据(raw)</el-radio>
          <el-checkbox v-if="request3" v-model="radioType" v-show="ParameterTyep">表单转源数据</el-checkbox>
        </div>
        <div class="panel-table" v-show="ParameterTyep">
          <div class="panel-row panel-row--param" v-for="(item, index) in form.parameter" :key="'p' + index">
            <div class="panel-cell panel-cell--name"><el-input v-model.trim="item.name" placeholder="参数名" size="small" /></div>
            <div class="panel-cell panel-cell--value">
              <div class="value-input-wrap">
                <el-input v-model.trim="item.value" placeholder="$1.code / $var.xxx / 旧格式" size="small" class="value-input" :class="{ 'is-ref': item.value && (item.value.startsWith('$') || item.interrelate) }" />
                <button class="dollar-btn" @click="openVarPicker(index, item, 'param')" title="插入变量引用"><span>$</span></button>
              </div>
            </div>
            <div class="panel-cell panel-cell--action"><button class="icon-btn icon-btn--del" @click="delParameter(index)"><i class="fa fa-trash"></i></button></div>
            <div class="panel-cell panel-cell--add" v-if="index === form.parameter.length - 1"><button class="icon-btn icon-btn--add" @click="addParameter"><i class="fa fa-plus"></i></button></div>
          </div>
        </div>
        <div v-show="!ParameterTyep" class="raw-input"><el-input type="textarea" :rows="5" placeholder="输入 raw 数据" v-model.trim="form.parameterRaw" /></div>
      </el-collapse-item>

      <!-- Check -->
      <el-collapse-item title="测试结果校验" name="3" class="collapse-panel">
        <div class="check-section">
          <div class="check-mode-bar">
            <el-radio-group v-model="form.check" size="small">
              <el-radio-button label="no_check">不校验</el-radio-button>
              <el-radio-button label="json">JSON校验</el-radio-button>
              <el-radio-button label="entirely_check">完全校验</el-radio-button>
              <el-radio-button label="Regular_check">正则校验</el-radio-button>
            </el-radio-group>
            <el-input v-if="form.check === 'Regular_check'" v-model="form.RegularParam" placeholder="绑定参数名" size="small" style="width:180px" />
          </div>

          <div v-show="showCheck" class="check-body">
            <div class="check-http-row">
              <span class="check-http-label">期望 HTTP 状态</span>
              <el-select v-model="form.checkHttp" placeholder="状态码" size="small" style="width:120px"><el-option v-for="(item, i) in httpCode" :key="i" :label="item.label" :value="item.value" /></el-select>
            </div>
            <el-input v-model.trim="form.checkData" type="textarea" :rows="6" placeholder="输入期望的响应内容，将与实际返回做完全匹配" />
          </div>

          <div v-show="jsonCheck" class="check-body">
            <div class="check-http-row">
              <span class="check-http-label">期望 HTTP 状态</span>
              <el-select v-model="form.checkHttp" placeholder="状态码" size="small" style="width:120px"><el-option v-for="(item, i) in httpCode" :key="i" :label="item.label" :value="item.value" /></el-select>
              <button class="icon-btn icon-btn--add" @click="addJsonCheck" style="margin-left:auto"><i class="fa fa-plus"></i></button>
            </div>
            <el-table :data="form.jsonCheckData" class="check-table" size="small">
              <el-table-column prop="name" label="参数名" min-width="120">
                <template slot-scope="scope"><el-input v-model.trim="scope.row.name" placeholder="参数名" size="small" /></template>
              </el-table-column>
              <el-table-column prop="checkRule" label="JSON 取值" min-width="140">
                <template slot-scope="scope"><el-input v-model.trim="scope.row.checkRule" placeholder="如 data[0].id" size="small" /></template>
              </el-table-column>
              <el-table-column prop="checkType" label="检验方式" width="130">
                <template slot-scope="scope"><el-select v-model="scope.row.checkType" placeholder="方式" size="small"><el-option v-for="(t, i) in jsonType" :key="i" :label="t.label" :value="t.value" /></el-select></template>
              </el-table-column>
              <el-table-column prop="value" label="校验值" min-width="120">
                <template slot-scope="scope"><el-input v-model.trim="scope.row.value" placeholder="期望值" size="small" /></template>
              </el-table-column>
              <el-table-column label="" width="50">
                <template slot-scope="scope"><button class="icon-btn icon-btn--del" @click="delJsonCheck(scope.$index)"><i class="fa fa-trash"></i></button></template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-collapse-item>

      <!-- Post operations -->
      <el-collapse-item title="后置操作" name="4" class="collapse-panel">
        <div class="post-section">
          <div class="post-actions">
            <el-button size="small" @click="addMysql">新增 MySQL</el-button>
            <el-button size="small" @click="handleAdd">新增 Redis</el-button>
            <el-button size="small" @click="handleAdd">新增 MQ</el-button>
          </div>
          <el-table :data="caseDataList" v-loading="listLoading" style="width:100%" class="post-table">
            <el-table-column prop="name" label="名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="dataInfo" label="数据源" width="120" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="80" />
            <el-table-column prop="excutesql" label="执行操作" min-width="200" show-overflow-tooltip />
            <el-table-column label="操作" width="180">
              <template slot-scope="scope">
                <el-button type="text" size="small" @click="TestMysqlCase(scope.row)">执行</el-button>
                <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button type="text" size="small" class="btn--danger" @click="delMysqlCase(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- Variable source dialog (unified: API / Global / DB) -->
    <el-dialog :visible.sync="searchApiVisible" :close-on-click-modal="false" width="700px" class="corr-dialog">
      <template slot="title"><span class="dialog-title-text">选择变量来源</span></template>
      <div class="corr-tabs">
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'api' }" @click="switchVarSource('api')">前置接口</button>
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'global' }" @click="switchVarSource('global')">全局变量</button>
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'db' }" @click="switchVarSource('db')">数据库查询</button>
      </div>

      <!-- API source -->
      <div v-show="varSource === 'api'">
        <el-row :gutter="14">
          <el-col :span="8">
            <div class="corr-api-list">
              <div class="corr-api-title">前置接口</div>
              <button v-for="(item, i) in ApiList" :key="item.id" class="corr-api-item" :class="{ 'corr-api-item--active': activeApiIndex === i }" @click="handleResponse(i)">{{ item.name }}</button>
              <div v-if="!ApiList.length" class="corr-api-empty">暂无可关联的前置接口</div>
            </div>
          </el-col>
          <el-col :span="16">
            <div class="corr-field-list">
              <div class="corr-field-title">可选字段</div>
              <el-table :data="ApiResponse" v-loading="apiResponseLoading" @current-change="handleCurrentChange" highlight-current-row max-height="300" class="corr-table" empty-text="请先在左侧选择一个接口">
                <el-table-column prop="name" label="字段名" min-width="140" show-overflow-tooltip />
                <el-table-column label="引用值" min-width="180" show-overflow-tooltip>
                  <template slot-scope="scope">
                    <code class="corr-code">\${{ stepIndexMap[scope.row.automationCaseApi] || '?' }}.{{ scope.row.checkRule }}</code>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="currentRow && varSource === 'api'" class="corr-selected"><i class="fa fa-check-circle"></i> 已选：<strong>{{ currentRow.name }}</strong><span class="corr-selected-val">→ ${{ stepIndexMap[currentRow.automationCaseApi] || '?' }}.{{ currentRow.checkRule }}</span></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Global variable source -->
      <div v-show="varSource === 'global'" class="corr-simple-list">
        <el-table :data="globalVars" v-loading="globalVarLoading" @current-change="onGlobalSelect" highlight-current-row max-height="340" class="corr-table" empty-text="暂无全局变量">
          <el-table-column prop="variablesName" label="变量名" min-width="160" show-overflow-tooltip />
          <el-table-column label="引用方式" min-width="200" show-overflow-tooltip>
            <template slot-scope="scope"><code class="corr-code">$var.{{ scope.row.variablesName }}</code></template>
          </el-table-column>
        </el-table>
        <div v-if="currentRow && varSource === 'global'" class="corr-selected"><i class="fa fa-check-circle"></i> 已选：<strong>{{ currentRow.variablesName || currentRow.name }}</strong><span class="corr-selected-val">→ $var.{{ currentRow.variablesName || currentRow.name }}</span></div>
      </div>

      <!-- DB source -->
      <div v-show="varSource === 'db'" class="corr-simple-list">
        <el-table :data="dataBaseList" v-loading="dbVarLoading" @current-change="onDbSelect" highlight-current-row max-height="340" class="corr-table" empty-text="暂无数据源">
          <el-table-column prop="name" label="数据源名称" min-width="160" show-overflow-tooltip />
          <el-table-column prop="dataInfo" label="连接信息" min-width="200" show-overflow-tooltip />
        </el-table>
        <div v-if="currentRow && varSource === 'db'" class="corr-selected"><i class="fa fa-check-circle"></i> 已选：<strong>{{ currentRow.name }}</strong><span class="corr-selected-val">→ db|{{ currentRow.id }}</span></div>
      </div>

      <div slot="footer" class="dialog-footer-bar">
        <el-button @click="searchApiVisible = false" size="small">取消</el-button>
        <el-button type="primary" :disabled="!currentRow" @click="addInterrelateSubmit" :loading="saveCorrelation" size="small">确认关联</el-button>
      </div>
    </el-dialog>

    <!-- MySQL add dialog -->
    <el-dialog title="新增 MySQL" :visible.sync="MysqlShow" :close-on-click-modal="false" width="520px">
      <el-form :model="addMysqlForm" label-width="100px">
        <el-form-item label="名称"><el-input v-model.trim="addMysqlForm.name" placeholder="SQL 名称" /></el-form-item>
        <el-form-item label="数据源"><el-select v-model="addMysqlForm.dataInfo_id" placeholder="选择数据源"><el-option v-for="item in dataBaseList" :key="item.name" :label="item.name" :value="item.id" /></el-select></el-form-item>
        <el-form-item label="执行 SQL"><el-input type="textarea" v-model.trim="addMysqlForm.excutesql" :rows="4" placeholder="输入 SQL" /></el-form-item>
        <el-form-item><el-button type="primary" :loading="editLoading" @click="addMysqlCase">新增</el-button></el-form-item>
      </el-form>
    </el-dialog>

    <!-- MySQL edit dialog -->
    <el-dialog title="修改 MySQL" :visible.sync="editMysqlShow" :close-on-click-modal="false" width="520px">
      <el-form :model="editMysqlForm" label-width="100px">
        <el-form-item label="名称"><el-input v-model.trim="editMysqlForm.name" placeholder="SQL 名称" /></el-form-item>
        <el-form-item label="数据源"><el-select v-model="editMysqlForm.dataInfo_id" placeholder="选择数据源"><el-option v-for="item in dataBaseList" :key="item.name" :label="item.name" :value="item.id" /></el-select></el-form-item>
        <el-form-item label="执行 SQL"><el-input type="textarea" v-model.trim="editMysqlForm.excutesql" :rows="4" placeholder="输入 SQL" /></el-form-item>
        <el-form-item><el-button type="primary" :loading="editLoading" @click="editMysqlCase">修改</el-button></el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { test, staticdata, GetDataBase, Createcasedatabase, Testruncasedata, Deletecasedatabase, Updatecasedatabase } from '../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      request: staticdata.request, Http: staticdata.Http, ParameterTyep: true, radio: 'form-data',
      header: staticdata.header, httpCode: staticdata.httpCode, jsonType: staticdata.jsonType,
      radioType: '', activeNames: ['1', '2', '3'],
      searchApiVisible: false, ApiList: [], ApiResponse: [], apiResponseLoading: false, saveCorrelation: false,
      activeApiIndex: -1, currentRow: null, varSource: 'api',
      globalVars: [], globalVarLoading: false, dbVarLoading: false,
      showCheck: false, jsonCheck: false, MysqlShow: false, editMysqlShow: false,
      sels: [], interrelateObjects: '', interrelateSection: 'param', stepIndexMap: {}, stepApiNames: {}, request3: true,
      dataBaseList: [], caseDataList: [],
      addMysqlForm: { name: '', dataInfo_id: '', excutesql: '' },
      editMysqlForm: { name: '', dataInfo_id: '', excutesql: '', id: '' },
      form: { name: '', request4: 'GET', Http4: 'HTTP', addr: '', head: [{ name: '', value: '', interrelate: 0 }, { name: '', value: '', interrelate: 0 }], parameterRaw: '', parameter: [{ name: '', value: '', interrelate: 0 }, { name: '', value: '', interrelate: 0 }], parameterType: '', check: 'no_check', RegularParam: '', checkHttp: '', checkData: '', jsonCheckData: [{ name: '', value: '', checkType: '', checkRule: '' }] },
      FormRules: { name: [{ required: true, message: '请输入名称', trigger: 'blur' }], addr: [{ required: true, message: '请输入地址', trigger: 'blur' }] },
    }
  },
  methods: {
    checkRequest() { this.request3 = !(this.form.request4 === 'GET' || this.form.request4 === 'DELETE') },
    handleCurrentChange(val) { this.currentRow = val },
    selsChange(sels) { this.sels = sels },
    openVarPicker(index, row, section) {
      this.interrelateObjects = row
      this.interrelateSection = section  // 'head' | 'param'
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/automation/get_correlation_response', async: true,
        data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id, api_id: this.$route.params.api_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) {
          if (data.code === '999999') {
            if (data.data.length) {
              self.ApiList = []; self.stepIndexMap = {}; self.stepApiNames = {}
              data.data.forEach((item, i) => {
                self.ApiList.push(item)
                self.stepIndexMap[item.id] = i + 1  // 1-based step index
                self.stepApiNames[item.id] = item.name  // api name for display
              })
              self.searchApiVisible = true
            } else {
              self.$message.warning({ message: '无前置接口', center: true })
            }
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
      })
    },
    handleCorrelation(index, row) { this.openVarPicker(index, row, 'param') },
    handleResponse(index) {
      this.activeApiIndex = index
      this.currentRow = null
      this.ApiResponse = []
      if (this.ApiList[index] && this.ApiList[index].jsonCheckDetail) {
        this.ApiList[index].jsonCheckDetail.forEach((item) => { this.ApiResponse.push(item) })
      }
    },
    switchVarSource(src) {
      this.varSource = src; this.currentRow = null
      if (src === 'global' && !this.globalVars.length) this.fetchGlobalVars()
      if (src === 'db' && !this.dataBaseList.length) this.getDatabase()
    },
    fetchGlobalVars() {
      this.globalVarLoading = true; let self = this
      $.ajax({ type: 'get', url: test + '/api/global/global_variables', async: true, data: { page_size: 100 }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { self.globalVarLoading = false; if (data.code === '999999') { self.globalVars = data.data && data.data.data ? data.data.data : [] } else { self.$message.error({ message: data.msg, center: true }) } },
        error: function () { self.globalVarLoading = false },
      })
    },
    onGlobalSelect(row) { this.currentRow = { name: row.variablesName, value: '$var.' + row.variablesName } },
    onDbSelect(row) { this.currentRow = { name: row.name, value: 'db|' + row.id, id: row.id } },
    addInterrelateSubmit() {
      if (!this.currentRow) { this.$message.warning({ message: '请先选择一个变量', center: true }); return }
      this.saveCorrelation = true
      let refValue = ''
      if (this.varSource === 'api') {
        // 格式: $N.field_path — 从 automationCaseApi 提取 step index 并拼接 path
        const apiId = this.currentRow.automationCaseApi
        const stepIdx = this.stepIndexMap[apiId] || '?'
        refValue = '$' + stepIdx + '.' + (this.currentRow.checkRule || '')
      } else if (this.varSource === 'global') {
        refValue = this.currentRow.value  // $var.xxx
      } else if (this.varSource === 'db') {
        refValue = this.currentRow.value  // db|xxx (legacy compat)
      }
      this.interrelateObjects.value = refValue
      // 新统一 $ 语法不需要 interrelate 标志（旧 {api_id}|field 格式才需要）
      this.interrelateObjects.interrelate = 0
      // 同时清除 _corrLabel，让 _resolveCorrLabels 重新计算
      this.$set(this.interrelateObjects, '_corrLabel', refValue)
      this.saveCorrelation = false
      this.searchApiVisible = false
    },

    updateApi() {
      this.$refs.form.validate((valid) => { if (valid) { let self = this; let formatRaw = false; this.$confirm('确认提交吗？', '提示', {}).then(() => { self.form.parameterType = self.radio; let _type = self.form.parameterType; let _parameter = {}; if (_type === 'form-data') { if (self.radioType === true) formatRaw = true; _parameter = self.form.parameter } else { _parameter = self.form.parameterRaw }; $.ajax({ type: 'post', url: test + '/api/automation/update_api', async: true, data: JSON.stringify({ project_id: Number(self.$route.params.project_id), automationTestCase_id: Number(self.$route.params.case_id), id: Number(self.$route.params.api_id), name: self.form.name, httpType: self.form.Http4, requestType: self.form.request4, apiAddress: self.form.addr, headDict: self.form.head, requestParameterType: _type, formatRaw, requestList: _parameter, examineType: self.form.check, RegularParam: self.form.RegularParam, httpCode: self.form.checkHttp, responseData: self.form.checkData, jsonCheckData: self.form.jsonCheckData }), headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') { self.$router.push({ name: '用例接口列表', params: { project_id: self.$route.params.project_id, case_id: self.$route.params.case_id } }); self.$message({ message: '修改成功', center: true, type: 'success' }) } else { self.$message.error({ message: data.msg, center: true }) } } }) }) } })
    },

    addHead() { this.form.head.push({ name: '', value: '', interrelate: 0 }) },
    delHead(index) { this.form.head.splice(index, 1); if (!this.form.head.length) this.form.head.push({ name: '', value: '', interrelate: 0 }) },
    addJsonCheck() { this.form.jsonCheckData.push({ name: '', value: '', checkType: '', checkRule: '' }) },
    delJsonCheck(index) { this.form.jsonCheckData.splice(index, 1); if (!this.form.jsonCheckData.length) this.form.jsonCheckData.push({ name: '', value: '', checkType: '', checkRule: '' }) },
    addParameter() { this.form.parameter.push({ name: '', value: '', interrelate: 0 }) },
    delParameter(index) { this.form.parameter.splice(index, 1); if (!this.form.parameter.length) this.form.parameter.push({ name: '', value: '', interrelate: 0 }) },
    changeParameterType() { this.ParameterTyep = this.radio === 'form-data' },

    addMysql() { this.MysqlShow = true },
    handleEdit(row) { this.editMysqlShow = true; this.editMysqlForm = Object.assign({}, row) },
    handleAdd() { this.$message({ message: '功能开发中', center: true, type: 'info' }) },
    addMysqlCase() { let self = this; Createcasedatabase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { name: self.addMysqlForm.name, dataInfo_id: self.addMysqlForm.dataInfo_id, excutesql: self.addMysqlForm.excutesql, project_id: this.$route.params.project_id, AutomationCaseApi_id: this.$route.params.api_id, pre_excute: true, type: 'mysql' }).then(_data => { let { msg, code } = _data; if (code === '999999') { self.MysqlShow = false; self.$message({ message: msg, center: true, type: 'success' }); self.getCaseApiInfo() } else { self.$message.error({ message: msg, center: true }) } }) },
    editMysqlCase() { let self = this; Updatecasedatabase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { name: self.editMysqlForm.name, dataInfo_id: self.editMysqlForm.dataInfo_id, excutesql: self.editMysqlForm.excutesql, type: 'mysql', id: self.editMysqlForm.id }).then(_data => { let { msg, code } = _data; if (code == 999999) { self.editMysqlShow = false; self.$message({ message: msg, center: true, type: 'success' }); self.getCaseApiInfo() } else { self.$message.error({ message: msg, center: true }) } }) },
    delMysqlCase(id) { let self = this; Deletecasedatabase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { ids: [id] }).then(_data => { let { msg, code } = _data; if (code === '999999') { self.$message({ message: msg, center: true, type: 'success' }); self.getCaseApiInfo() } else { self.$message.error({ message: msg, center: true }) } }) },
    TestMysqlCase(row) { Testruncasedata({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { dataInfo_id: row.dataInfo, excutesql: row.excutesql, pre_excute: true, type: 'mysql' }).then(_data => { let { msg, code, data } = _data; if (code === '999999') this.$alert(data, '执行返回'); else self.$message.error({ message: msg, center: true }) }) },
    getDatabase() { let self = this; GetDataBase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { page: self.page }).then(_data => { let { msg, code, data } = _data; if (code === '999999') self.dataBaseList = data.data; else self.$message.error({ message: msg, center: true }) }) },
    getCaseApiInfo() {
      let self = this
      $.ajax({ type: 'get', url: test + '/api/automation/api_info', async: true, data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id, api_id: this.$route.params.api_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { if (data.code === '999999') { data = data.data; self.caseDataList = data.CaseDataExcutedatail; self.form.name = data.name; self.form.request4 = data.requestType; self.form.Http4 = data.httpType; self.form.addr = data.apiAddress; if (data.formatRaw) self.radioType = true; if (data.header.length) { self.form.head = []; data.header.forEach((item) => { self.form.head.push(item) }) } if (data.parameterList.length) { self.form.parameter = []; data.parameterList.forEach((item) => { self.form.parameter.push(item) }) } if (data.jsonCheckDetail.length) { self.form.jsonCheckData = []; data.jsonCheckDetail.forEach((item) => { self.form.jsonCheckData.push(item) }) } try { self.form.parameterRaw = data.parameterRaw.data.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false') } catch (e) {} self.form.parameterType = data.requestParameterType; self.form.check = data.examineType; self.form.checkHttp = data.httpCode; try { self.form.RegularParam = data.RegularParam } catch (e) {} self.form.checkData = data.responseData; self.radio = data.requestParameterType; self.checkRequest(); self._resolveCorrLabels() } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    _resolveCorrLabels() {
      let self = this
      $.ajax({ type: 'get', url: test + '/api/automation/get_correlation_response', async: true,
        data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id, api_id: this.$route.params.api_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) {
          var map = {}
          if (data.code === '999999' && data.data && data.data.length) {
            data.data.forEach(function (api, i) {
              self.$set(self.stepIndexMap, api.id, i + 1)
              self.$set(self.stepApiNames, api.id, api.name)
              if (api.jsonCheckDetail) {
                api.jsonCheckDetail.forEach(function (f) {
                  map[api.id + '|' + f.checkRule] = f.name
                })
              }
            })
          }
          ;[self.form.head, self.form.parameter, self.form.jsonCheckData].forEach(function (list) {
            if (list && list.length) {
              list.forEach(function (item) {
                if (item.interrelate && item.value && !item._corrLabel) {
                  if (item.value.startsWith('$')) {
                    self.$set(item, '_corrLabel', item.value)
                  } else if (item.value.startsWith('db|')) {
                    self.$set(item, '_corrLabel', item.value.replace('db|', 'DB#'))
                  } else if (item.value.includes('|')) {
                    self.$set(item, '_corrLabel', map[item.value] || item.value.split('|')[1] || item.value)
                  }
                }
              })
            }
          })
        },
      })
    },
    handleChange() {},
  },
  watch: { radio() { this.changeParameterType() }, 'form.check': { handler(v) { this.showCheck = !['no_check', 'json'].includes(v); this.jsonCheck = v === 'json' }, deep: true } },
  mounted() { this.getCaseApiInfo(); this.getDatabase() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $accent-hover: #1a43c0; $accent-soft: #eff3ff;
$text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.case-form { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }
.toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; }
.tb-back { display: inline-flex; align-items: center; gap: 6px; font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; text-decoration: none; &:hover { color: $accent; } i { font-size: 12px; } }
.tb-right { display: flex; gap: 10px; }
.tb-btn { display: inline-flex; align-items: center; font-size: 13px; font-weight: 500; padding: 8px 20px; border-radius: 6px; border: 1px solid transparent; cursor: pointer; text-decoration: none; transition: all .15s ease; font-family: $font-body;
  &--primary { background: $accent; color: #fff; border-color: $accent; &:hover { background: $accent-hover; } }
  &--ghost { background: $surface; color: $text-secondary; border-color: $border; &:hover { color: $accent; border-color: $accent; } }
}
.section-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 20px 24px; margin-bottom: 14px; box-shadow: $shadow-sm; }
.section-title { font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; margin: 0 0 16px; }
.api-form { .form-row { display: flex; gap: 16px; align-items: flex-end; margin-bottom: 14px; flex-wrap: wrap; &:last-child { margin-bottom: 0; } &--url { border-top: 1px solid $border; padding-top: 14px; } } .form-col--name { flex: 1; min-width: 160px; } .form-col--method { width: 130px; } .form-col--http { width: 100px; } .form-col--addr { flex: 1; min-width: 200px; } }
.form-label { display: block; font-size: 12px; font-weight: 500; color: $text-tertiary; margin-bottom: 5px; }
.form-item--clean { margin-bottom: 0; }

.step-map-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 4px 10px; padding: 8px 20px; background: #f0f9ff; border-bottom: 1px solid #bae6fd; font-size: 11px; }
.step-map-label { font-weight: 600; color: #0c4a6e; white-space: nowrap; }
.step-map-chip { display: inline-block; background: #dbeafe; color: #1e40af; padding: 1px 7px; border-radius: 3px; font-weight: 500; font-family: monospace; white-space: nowrap; }
.step-map-hint { color: #6b7280; margin-left: 4px; code { background: #e5e7eb; padding: 0 3px; border-radius: 2px; font-size: 10px; } }

.case-collapse { border: none;
  :deep(.collapse-panel) { background: $surface; border: 1px solid $border; border-radius: 10px; margin-bottom: 10px; box-shadow: $shadow-sm; overflow: hidden;
    .el-collapse-item__header { height: 46px; line-height: 46px; padding: 0 20px; font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; background: #fafbfc; border-bottom: 1px solid transparent; &.is-active { border-bottom-color: $border; } }
    .el-collapse-item__wrap { border: none; background: $surface; }
    .el-collapse-item__content { padding: 0; }
  }
}
.panel-table { padding: 4px 0; }
.panel-row { display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-bottom: 1px solid #f3f4f6; &:last-child { border-bottom: none; }
  &--head { .panel-cell--name { display: flex; gap: 0; flex: 2; min-width: 200px; } .panel-cell--value { flex: 3; min-width: 160px; } }
  &--param { flex-wrap: wrap; .panel-cell--name { flex: 2; min-width: 100px; } .panel-cell--value { flex: 2; min-width: 100px; } .panel-cell--type { width: 110px; } }
}
.panel-cell { &--action { display: flex; align-items: center; gap: 4px; flex-shrink: 0; } &--add { flex-shrink: 0; } }
.icon-btn { width: 30px; height: 30px; border-radius: 5px; border: 1px solid transparent; background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 13px; transition: all .12s ease;
  &--del { color: #9ca3af; &:hover { color: #dc2626; background: #fef2f2; } }
  &--add { color: $accent; border-color: $accent-soft; &:hover { background: $accent-soft; } }
}
.head-select { width: 140px; flex-shrink: 0; }
.head-input { flex: 1; min-width: 100px; }
.link-btn { background: none; border: none; font-size: 12px; color: $accent; cursor: pointer; &:hover { text-decoration: underline; } }
// ─── Variable reference ─────────────────────────────
.value-input-wrap {
  display: flex; align-items: center; gap: 0; width: 100%;
  .value-input { flex: 1; min-width: 0;
    :deep(.el-input__inner) {
      border-radius: 4px 0 0 4px;
    }
    &.is-ref :deep(.el-input__inner) {
      color: #7c3aed;
      background: #f5f3ff;
      border-color: #c4b5fd;
      font-family: 'Fira Code', 'Consolas', monospace;
      font-size: 12px;
    }
  }
}
.dollar-btn {
  width: 32px; height: 32px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: $accent-soft; border: 1px solid $accent-soft;
  border-left: none; border-radius: 0 4px 4px 0;
  cursor: pointer; transition: all .12s ease;
  span { font-size: 14px; font-weight: 800; color: $accent; }
  &:hover { background: #dbe4ff; border-color: $accent; }
}
.param-type-bar { display: flex; align-items: center; gap: 20px; padding: 12px 20px; border-bottom: 1px solid #f3f4f6; }
.raw-input { padding: 16px 20px; }

.check-section { padding: 16px 24px 20px; }
.check-mode-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.check-http-row { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.check-http-label { font-size: 12px; color: $text-secondary; font-weight: 500; }
.check-body { margin-top: 16px; padding: 16px; background: #f9fafb; border: 1px solid $border; border-radius: 8px;
  :deep(.el-textarea) { margin-top: 12px; }
}
.check-table { margin-top: 0;
  :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; padding: 10px 8px; }
  :deep(td) { padding: 6px 8px; }
  :deep(.el-input--small .el-input__inner) { font-size: 12px; }
}

.post-section { padding: 16px 24px; }
.post-actions { display: flex; gap: 8px; margin-bottom: 14px; }
.post-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }

.corr-list { height: 360px; overflow: auto; border: 1px solid $border; border-radius: 6px; }

// ─── Correlation dialog ────────────────────────────
.corr-dialog {
  .corr-hint { font-size: 12px; color: $text-tertiary; margin-bottom: 14px; }
}
.corr-tabs { display: flex; gap: 0; border-bottom: 2px solid $border; margin-bottom: 14px; }
.corr-tab {
  padding: 8px 18px; font-size: 13px; font-weight: 500; color: $text-tertiary;
  background: none; border: none; border-bottom: 2px solid transparent; margin-bottom: -2px;
  cursor: pointer; transition: all .12s ease;
  &:hover { color: $text-secondary; }
  &--active { color: $accent; border-bottom-color: $accent; font-weight: 600; }
}
.corr-simple-list {
  :deep(.corr-table) { margin-top: 0; }
}
.corr-api-list { border: 1px solid $border; border-radius: 8px; overflow: hidden; }
.corr-api-title { font-size: 11px; font-weight: 600; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 12px 6px; }
.corr-api-item {
  display: block; width: 100%; text-align: left; padding: 8px 12px;
  border: none; background: transparent; cursor: pointer;
  font-size: 12px; color: $text-secondary; border-left: 3px solid transparent;
  transition: all .12s ease;
  &:hover { background: #f9fafb; }
  &--active { background: $accent-soft; color: $accent; font-weight: 600; border-left-color: $accent; }
}
.corr-api-empty { padding: 24px 12px; text-align: center; font-size: 12px; color: $text-tertiary; }

.corr-field-list { border: 1px solid $border; border-radius: 8px; overflow: hidden; }
.corr-field-title { font-size: 11px; font-weight: 600; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 14px 6px; }
.corr-table {
  :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; padding: 8px 10px; }
  :deep(td) { padding: 6px 10px; }
}
.corr-code { font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 11px; color: $text-tertiary; background: #f3f4f6; padding: 2px 6px; border-radius: 3px; }
.corr-selected { margin-top: 10px; padding: 8px 12px; background: #ecfdf5; border-radius: 6px; font-size: 12px; color: #059669;
  i { margin-right: 4px; }
  .corr-selected-val { color: $text-tertiary; margin-left: 8px; font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 11px; }
}

// ─── Correlation tag in form ────────────────────────
.corr-tag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 500; color: $accent;
  background: $accent-soft; padding: 5px 10px; border-radius: 4px;
  border: 1px solid #c7d2fe;
  i { font-size: 10px; opacity: .7; }
}

.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
</style>
