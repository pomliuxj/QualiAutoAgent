<template>
  <div class="list-page">
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <el-input v-model.trim="filters.name" placeholder="搜索接口名称" size="small" class="tb-search" @keyup.enter.native="getApiList" clearable />
          <el-button type="primary" size="small" @click="getApiList">查询</el-button>
          <router-link :to="{ name: '新增接口', params: { project_id: $route.params.project_id } }">
            <el-button type="primary" size="small"><i class="fa fa-plus"></i> 新增</el-button>
          </router-link>
          <el-button size="small" :disabled="update" @click="changeGroup">修改分组</el-button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="api" v-loading="listLoading" @selection-change="selsChange" class="data-table">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="接口名称" min-width="160" sortable show-overflow-tooltip>
          <template slot-scope="scope">
            <router-link :to="{ name: '基础信息', params: { api_id: scope.row.id } }" class="table-link">{{ scope.row.name }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="requestType" label="请求方式" width="100" sortable>
          <template slot-scope="scope">
            <span class="method-tag" :class="'method--' + (scope.row.requestType || '').toLowerCase()">{{ scope.row.requestType }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="apiAddress" label="接口地址" min-width="200" sortable show-overflow-tooltip />
        <el-table-column prop="userUpdate" label="最近更新者" width="110" sortable show-overflow-tooltip />
        <el-table-column prop="lastUpdateTime" label="更新日期" width="150" sortable show-overflow-tooltip />
        <el-table-column label="Mock" width="80">
          <template slot-scope="scope">
            <span class="mock-badge" :class="scope.row.mockStatus ? 'mock--on' : 'mock--off'" @click="checkMockStatus(scope.row)">{{ scope.row.mockStatus ? 'ON' : 'OFF' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template slot-scope="scope">
            <router-link :to="{ name: '修改', params: { api_id: scope.row.id } }"><el-button type="text" size="small">修改</el-button></router-link>
            <el-button type="text" size="small" class="btn--danger" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <el-button type="danger" size="small" plain :disabled="!sels.length" @click="batchRemove">批量删除</el-button>
        <el-pagination small layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="Math.ceil(total / 20)" />
      </div>
    </div>

    <el-dialog title="修改所属分组" :visible.sync="updateGroupFormVisible" :close-on-click-modal="false" width="420px">
      <el-form :model="updateGroupForm" label-width="80px" :rules="updateGroupFormRules" ref="updateGroupForm">
        <el-form-item label="分组名称" prop="firstGroup">
          <el-select v-model="updateGroupForm.firstGroup" placeholder="选择分组">
            <el-option v-for="(item, i) in group" :key="i" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer"><el-button @click="updateGroupFormVisible = false">取消</el-button><el-button type="primary" @click="updateGroupSubmit" :loading="updateGroupLoading">提交</el-button></div>
    </el-dialog>
  </div>
</template>

<script>
import { test } from '../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      filters: { name: '' }, api: [], total: 0, page: 1, listLoading: false, sels: [],
      updateGroupFormVisible: false, updateGroupForm: { firstGroup: '' },
      updateGroupFormRules: { firstGroup: [{ type: 'number', required: true, message: '请选择分组', trigger: 'blur' }] },
      group: [], updateGroupLoading: false, update: true,
    }
  },
  methods: {
    checkMockStatus(row) {
      let self = this
      $.ajax({
        type: 'post', url: test + '/api/api/updateMock', async: true,
        data: JSON.stringify({ project_id: Number(this.$route.params.project_id), id: Number(row.id) }),
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { if (data.code === '999999') { self.$message.success({ message: data.msg, center: true }); self.getApiList() } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    getApiList() {
      this.listLoading = true; let self = this
      let param = { project_id: this.$route.params.project_id, page: self.page }
      if (this.$route.params.firstGroup) { param['apiGroupLevelFirst_id'] = this.$route.params.firstGroup }
      $.ajax({
        type: 'get', url: test + '/api/api/api_list', async: true, data: param,
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { self.listLoading = false; if (data.code === '999999') { self.total = data.data.total; self.api = data.data.data } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    updateGroupSubmit() {
      let ids = this.sels.map(item => item.id); let self = this
      this.$confirm('确认修改所属分组吗？', '提示', { type: 'warning' }).then(() => {
        self.updateGroupLoading = true
        $.ajax({
          type: 'post', url: test + '/api/api/update_group', async: true,
          data: JSON.stringify({ project_id: Number(this.$route.params.project_id), apiGroupLevelFirst_id: Number(self.updateGroupForm.firstGroup), ids }),
          headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
          success: function (data) { self.updateGroupLoading = false; if (data.code === '999999') { self.$message({ message: '修改成功', center: true, type: 'success' }); self.$router.push({ name: '分组接口列表', params: { project_id: self.$route.params.project_id, firstGroup: self.updateGroupForm.firstGroup } }) } else { self.$message.error({ message: data.msg, center: true }) }; self.updateGroupFormVisible = false; self.getApiList() },
        })
      }).catch(() => {})
    },
    getApiGroup() {
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/api/group', async: true, data: { project_id: this.$route.params.project_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) { if (data.code === '999999') { self.group = data.data; self.updateGroupForm.firstGroup = self.group[0] ? self.group[0].id : '' } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    changeGroup() { this.getApiGroup(); this.updateGroupFormVisible = true },
    handleDel(index, row) {
      this.$confirm('确认删除该记录吗?', '提示', { type: 'warning' }).then(() => {
        this.listLoading = true; let self = this
        $.ajax({
          type: 'post', url: test + '/api/api/del_api', async: true,
          data: JSON.stringify({ project_id: Number(this.$route.params.project_id), ids: [row.id] }),
          headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
          success: function (data) { if (data.code === '999999') { self.$message({ message: '删除成功', center: true, type: 'success' }) } else { self.$message.error({ message: data.msg, center: true }) }; self.getApiList() },
        })
      }).catch(() => {})
    },
    handleCurrentChange(val) { this.page = val; this.getApiList() },
    selsChange(sels) { this.sels = sels; this.update = !sels.length },
    batchRemove() {
      let ids = this.sels.map(item => item.id); let self = this
      this.$confirm('确认删除选中记录吗？', '提示', { type: 'warning' }).then(() => {
        self.listLoading = true
        $.ajax({
          type: 'post', url: test + '/api/api/del_api', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), ids }),
          headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
          success: function (data) { self.listLoading = false; if (data.code === '999999') { self.$message({ message: '删除成功', center: true, type: 'success' }) } else { self.$message.error({ message: data.msg, center: true }) }; self.getApiList() },
        })
      }).catch(() => {})
    },
  },
  watch: { '$route': function (to, from) { if (to !== from) this.getApiList() } },
  mounted() { this.getApiList() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.list-page { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }
.toolbar-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: $shadow-sm; .tb-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; } .tb-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; } .tb-search { width: 200px; } }
.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }
.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }
.table-link { color: $accent; text-decoration: none; font-weight: 500; &:hover { text-decoration: underline; } }
.method-tag { display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.03em; padding: 2px 8px; border-radius: 3px; color: #fff; &.method--get { background: #059669; } &.method--post { background: #1d4ed8; } &.method--put { background: #d97706; } &.method--delete { background: #dc2626; } }
.mock-badge { display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 0.05em; padding: 3px 9px; border-radius: 3px; cursor: pointer; user-select: none; &.mock--on { background: #ecfdf5; color: #059669; } &.mock--off { background: #f3f4f6; color: #9ca3af; } }
.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
.tb-footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 18px; border-top: 1px solid #f3f4f6; }
</style>
