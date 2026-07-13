<template>
  <div class="list-page">
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <el-input v-model.trim="filters.name" placeholder="搜索用例名称" size="small" class="tb-search" @keyup.enter.native="getCaseList" clearable />
          <el-button type="primary" size="small" @click="getCaseList">查询</el-button>
          <el-button type="primary" size="small" @click="handleAdd"><i class="fa fa-plus"></i> 新增用例集</el-button>
          <el-button size="small" :disabled="update" @click="changeGroup">修改分组</el-button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="Case" v-loading="listLoading" @selection-change="selsChange" class="data-table">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="caseName" label="用例集名称" min-width="200" sortable show-overflow-tooltip>
          <template slot-scope="scope">
            <router-link :to="{ name: '用例接口列表', params: { case_id: scope.row.id } }" class="table-link">{{ scope.row.caseName }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="240" sortable show-overflow-tooltip>
          <template slot-scope="scope"><span class="desc-text">{{ scope.row.description || '—' }}</span></template>
        </el-table-column>
        <el-table-column prop="createUser" label="创建人" width="100" sortable />
        <el-table-column prop="updateTime" label="更新日期" width="150" sortable show-overflow-tooltip />
        <el-table-column label="操作" width="140" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="handleEdit(scope.$index, scope.row)">修改</el-button>
            <el-button type="text" size="small" class="btn--danger" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <el-button type="danger" size="small" plain :disabled="!sels.length" @click="batchRemove">批量删除</el-button>
        <el-pagination small layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="10" :page-count="Math.ceil(total / 10)" />
      </div>
    </div>

    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false" width="480px">
      <el-form :model="editForm" :rules="editFormRules" ref="editForm" label-width="80px">
        <el-form-item label="名称" prop="caseName"><el-input v-model.trim="editForm.caseName" /></el-form-item>
        <el-form-item label="分组" prop="automationGroupLevelFirst"><el-select v-model="editForm.automationGroupLevelFirst" placeholder="选择分组"><el-option v-for="(item, i) in group" :key="i" :label="item.name" :value="item.id" /></el-select></el-form-item>
        <el-form-item label="描述" prop="description"><el-input type="textarea" :rows="4" v-model.trim="editForm.description" /></el-form-item>
      </el-form>
      <div slot="footer"><el-button @click="editFormVisible = false">取消</el-button><el-button type="primary" @click="editSubmit" :loading="editLoading">提交</el-button></div>
    </el-dialog>

    <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" width="480px">
      <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-form-item label="名称" prop="caseName"><el-input v-model.trim="addForm.caseName" /></el-form-item>
        <el-form-item label="分组" prop="firstGroup"><el-select v-model="addForm.firstGroup" placeholder="选择分组"><el-option v-for="(item, i) in group" :key="i" :label="item.name" :value="item.id" /></el-select></el-form-item>
        <el-form-item label="描述" prop="description"><el-input type="textarea" :rows="4" v-model.trim="addForm.description" /></el-form-item>
      </el-form>
      <div slot="footer"><el-button @click="addFormVisible = false">取消</el-button><el-button type="primary" @click="addSubmit" :loading="addLoading">提交</el-button></div>
    </el-dialog>

    <el-dialog title="修改所属分组" :visible.sync="updateGroupFormVisible" :close-on-click-modal="false" width="420px">
      <el-form :model="updateGroupForm" label-width="80px" :rules="updateGroupFormRules" ref="updateGroupForm">
        <el-form-item label="分组" prop="firstGroup"><el-select v-model="updateGroupForm.firstGroup" placeholder="选择分组"><el-option v-for="(item, i) in group" :key="i" :label="item.name" :value="item.id" /></el-select></el-form-item>
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
      filters: { name: '' }, Case: [], total: 0, page: 1, listLoading: false, sels: [],
      updateGroupFormVisible: false, updateGroupForm: { firstGroup: '' }, updateGroupFormRules: { firstGroup: [{ type: 'number', required: true, message: '请选择父分组', trigger: 'blur' }] },
      group: [], updateGroupLoading: false, update: true,
      editFormVisible: false, editLoading: false,
      editFormRules: { caseName: [{ required: true, message: '请输入名称', trigger: 'blur' }, { min: 1, max: 50, message: '长度在 1 到 50 个字符' }], automationGroupLevelFirst: [{ type: 'number', required: true, message: '请选择分组', trigger: 'blur' }], description: [{ max: 1024, message: '不能超过1024个字符' }] },
      editForm: { caseName: '', automationGroupLevelFirst: '', description: '' },
      addFormVisible: false, addLoading: false,
      addFormRules: { caseName: [{ required: true, message: '请输入名称', trigger: 'blur' }], firstGroup: [{ type: 'number', required: true, message: '请选择父分组', trigger: 'blur' }], description: [{ max: 1024, message: '不能超过1024个字符' }] },
      addForm: { caseName: '', firstGroup: '', description: '' },
    }
  },
  methods: {
    getCaseList() {
      this.listLoading = true; let self = this; let param = { project_id: this.$route.params.project_id, page: self.page, name: self.filters.name }
      if (this.$route.params.firstGroup) { param.first_group_id = this.$route.params.firstGroup; if (this.$route.params.secondGroup) param.second_group_id = this.$route.params.secondGroup }
      $.ajax({ type: 'get', url: test + '/api/automation/case_list', async: true, data: param, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.listLoading = false; if (data.code === '999999') { self.total = data.data.total; self.Case = data.data.data } else { self.$message.error({ message: data.msg, center: true }) } } })
    },
    updateGroupSubmit() { let ids = this.sels.map(item => item.id); let self = this; this.$confirm('确认修改所属分组吗？', '提示', { type: 'warning' }).then(() => { self.updateGroupLoading = true; $.ajax({ type: 'post', url: test + '/api/automation/update_case_group', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), automationGroupLevelFirst_id: self.updateGroupForm.firstGroup, ids }), headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.updateGroupLoading = false; if (data.code === '999999') { self.$message({ message: '修改成功', center: true, type: 'success' }); self.$router.push({ name: '分组用例列表', params: { project_id: self.$route.params.project_id, firstGroup: self.updateGroupForm.firstGroup } }) } else { self.$message.error({ message: data.msg, center: true }) }; self.updateGroupFormVisible = false; self.getCaseList() } }) }).catch(() => {}) },
    getCaseGroup() { let self = this; $.ajax({ type: 'get', url: test + '/api/automation/group', async: true, data: { project_id: this.$route.params.project_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') { self.group = data.data; self.updateGroupForm.firstGroup = self.group[0] ? self.group[0].id : ''; self.addForm.firstGroup = self.group[0] ? self.group[0].id : '' } else { self.$message.error({ message: data.msg, center: true }) } } }) },
    changeGroup() { this.getCaseGroup(); this.updateGroupFormVisible = true },
    handleDel(index, row) { this.$confirm('确认删除该记录吗?', '提示', { type: 'warning' }).then(() => { this.listLoading = true; let self = this; $.ajax({ type: 'post', url: test + '/api/automation/del_case', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), ids: [row.id] }), headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') self.$message({ message: '删除成功', center: true, type: 'success' }); else self.$message.error({ message: data.msg, center: true }); self.getCaseList() } }) }).catch(() => {}) },
    handleCurrentChange(val) { this.page = val; this.getCaseList() },
    selsChange(sels) { this.sels = sels; this.update = !sels.length },
    batchRemove() { let ids = this.sels.map(item => item.id); let self = this; this.$confirm('确认删除选中记录吗？', '提示', { type: 'warning' }).then(() => { self.listLoading = true; $.ajax({ type: 'post', url: test + '/api/automation/del_case', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), ids }), headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.listLoading = false; if (data.code === '999999') self.$message({ message: '删除成功', center: true, type: 'success' }); else self.$message.error({ message: data.msg, center: true }); self.getCaseList() } }) }).catch(() => {}) },
    handleEdit(index, row) { this.getCaseGroup(); this.editFormVisible = true; this.editForm = Object.assign({}, row) },
    handleAdd() { this.getCaseGroup(); this.addFormVisible = true },
    editSubmit() { let self = this; this.$refs.editForm.validate((valid) => { if (valid) { this.$confirm('确认提交吗？', '提示', {}).then(() => { self.editLoading = true; $.ajax({ type: 'post', url: test + '/api/automation/update_case', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), id: Number(self.editForm.id), caseName: self.editForm.caseName, automationGroupLevelFirst_id: Number(this.editForm.automationGroupLevelFirst), description: self.editForm.description }), headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.editLoading = false; if (data.code === '999999') { self.$message({ message: '修改成功', center: true, type: 'success' }); self.editFormVisible = false; self.getCaseList() } else { self.$message.error({ message: data.msg, center: true }) } } }) }) } }) },
    addSubmit() { this.$refs.addForm.validate((valid) => { if (valid) { let self = this; this.$confirm('确认提交吗？', '提示', {}).then(() => { self.addLoading = true; $.ajax({ type: 'post', url: test + '/api/automation/add_case', async: true, data: JSON.stringify({ project_id: Number(this.$route.params.project_id), automationGroupLevelFirst_id: this.addForm.firstGroup, caseName: self.addForm.caseName, description: self.addForm.description }), headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { self.addLoading = false; if (data.code === '999999') { self.$message({ message: '添加成功', center: true, type: 'success' }); self.addFormVisible = false; self.getCaseList() } else { self.$message.error({ message: data.msg, center: true }) } } }) }) } }) },
  },
  watch: { '$route': function (to, from) { if (to !== from) this.getCaseList() } },
  mounted() { this.getCaseList() },
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
.desc-text { color: $text-secondary; }
.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
.tb-footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 18px; border-top: 1px solid #f3f4f6; }
</style>
