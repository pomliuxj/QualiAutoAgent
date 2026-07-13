<template>
  <div class="db-page">
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <el-input v-model.trim="filters.name" placeholder="搜索名称" size="small" class="tb-search" @keyup.enter.native="getGlobalBase" clearable />
          <el-button type="primary" size="small" @click="getGlobalBase">查询</el-button>
          <el-button type="primary" size="small" @click="handleAdd"><i class="fa fa-plus"></i> 新增</el-button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="project" v-loading="listLoading" @selection-change="selsChange" class="data-table">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="name" label="名称" min-width="140" sortable show-overflow-tooltip>
          <template slot-scope="scope"><span class="db-name">{{ scope.row.name }}</span></template>
        </el-table-column>
        <el-table-column prop="host" label="Host" width="160" show-overflow-tooltip />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="user" label="用户" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row._maskUser" class="mask-text">{{ scope.row._maskUser }}</span>
            <span v-else class="mask-text">***</span>
            <i class="fa fa-eye toggle-eye" @click="toggleMask(scope.row, 'user')" title="显示/隐藏"></i>
          </template>
        </el-table-column>
        <el-table-column prop="password" label="密码" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row._showPass"> {{ scope.row.password }}</span>
            <span v-else class="mask-text">••••••••</span>
            <i class="fa fa-eye toggle-eye" @click="toggleMask(scope.row, 'pass')" title="显示/隐藏"></i>
          </template>
        </el-table-column>
        <el-table-column prop="db" label="数据库" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button type="text" size="small" class="btn--danger" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <el-button type="danger" size="small" plain :disabled="!sels.length" @click="batchRemove">批量删除</el-button>
        <el-pagination small layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :page-count="Math.ceil(total / 20)" />
      </div>
    </div>

    <!-- Add dialog -->
    <el-dialog :visible.sync="addFormVisible" :close-on-click-modal="false" width="480px" class="db-dialog">
      <template slot="title"><span class="dialog-title-text">新增数据源</span></template>
      <el-form :model="addForm" label-width="0" :rules="addFormRules" ref="addForm" class="db-form">
        <div class="form-field">
          <label class="field-label">名称</label>
          <el-form-item prop="name"><el-input v-model.trim="addForm.name" placeholder="数据源名称" size="small" /></el-form-item>
        </div>
        <div class="form-row-inline">
          <div class="form-field form-field--half">
            <label class="field-label">Host</label>
            <el-form-item prop="host"><el-input v-model.trim="addForm.host" placeholder="IP 或域名" size="small" /></el-form-item>
          </div>
          <div class="form-field form-field--half">
            <label class="field-label">端口</label>
            <el-form-item prop="port"><el-input v-model.trim="addForm.port" placeholder="3306" size="small" /></el-form-item>
          </div>
        </div>
        <div class="form-row-inline">
          <div class="form-field form-field--half">
            <label class="field-label">用户</label>
            <el-form-item prop="user"><el-input v-model.trim="addForm.user" placeholder="数据库用户" size="small" /></el-form-item>
          </div>
          <div class="form-field form-field--half">
            <label class="field-label">密码</label>
            <el-form-item prop="password">
              <el-input v-model.trim="addForm.password" placeholder="数据库密码" size="small" :type="addPassVisible ? 'text' : 'password'">
                <i slot="suffix" class="fa field-eye" :class="addPassVisible ? 'fa-eye' : 'fa-eye-slash'" @click="addPassVisible = !addPassVisible" style="cursor:pointer;line-height:32px;padding-right:8px"></i>
              </el-input>
            </el-form-item>
          </div>
        </div>
        <div class="form-field">
          <label class="field-label">连接库</label>
          <el-form-item prop="db"><el-input v-model.trim="addForm.db" placeholder="数据库名" size="small" /></el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer-bar">
        <el-button size="small" @click="checkAvailable(addForm)">校验可用</el-button>
        <div>
          <el-button @click="addFormVisible = false" size="small">取消</el-button>
          <el-button type="primary" :loading="addLoading" @click="addSubmit" size="small">创建</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Edit dialog -->
    <el-dialog :visible.sync="editFormVisible" :close-on-click-modal="false" width="480px" class="db-dialog">
      <template slot="title"><span class="dialog-title-text">编辑数据源</span></template>
      <el-form :model="editForm" :rules="addFormRules" ref="editForm" label-width="0" class="db-form">
        <div class="form-field">
          <label class="field-label">名称</label>
          <el-form-item prop="name"><el-input v-model.trim="editForm.name" placeholder="数据源名称" size="small" /></el-form-item>
        </div>
        <div class="form-row-inline">
          <div class="form-field form-field--half">
            <label class="field-label">Host</label>
            <el-form-item prop="host"><el-input v-model.trim="editForm.host" placeholder="IP 或域名" size="small" /></el-form-item>
          </div>
          <div class="form-field form-field--half">
            <label class="field-label">端口</label>
            <el-form-item prop="port"><el-input v-model.trim="editForm.port" placeholder="3306" size="small" /></el-form-item>
          </div>
        </div>
        <div class="form-row-inline">
          <div class="form-field form-field--half">
            <label class="field-label">用户</label>
            <el-form-item prop="user"><el-input v-model.trim="editForm.user" placeholder="数据库用户" size="small" /></el-form-item>
          </div>
          <div class="form-field form-field--half">
            <label class="field-label">密码</label>
            <el-form-item prop="password">
              <el-input v-model.trim="editForm.password" placeholder="数据库密码" size="small" :type="editPassVisible ? 'text' : 'password'">
                <i slot="suffix" class="fa field-eye" :class="editPassVisible ? 'fa-eye' : 'fa-eye-slash'" @click="editPassVisible = !editPassVisible" style="cursor:pointer;line-height:32px;padding-right:8px"></i>
              </el-input>
            </el-form-item>
          </div>
        </div>
        <div class="form-field">
          <label class="field-label">连接库</label>
          <el-form-item prop="db"><el-input v-model.trim="editForm.db" placeholder="数据库名" size="small" /></el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer-bar">
        <el-button size="small" @click="checkAvailable(editForm)">校验可用</el-button>
        <div>
          <el-button @click="editFormVisible = false" size="small">取消</el-button>
          <el-button type="primary" :loading="editLoading" @click="editSubmit" size="small">保存</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { CreateDataBase, GetDataBase, UpdateDataBase, DeleteDataBase, CheckDataBase } from '../../../api/api'

export default {
  data() {
    return {
      filters: { name: '' }, project: [], total: 0, page: 1, listLoading: false, sels: [],
      editFormVisible: false, editLoading: false,
      editForm: { name: '', host: '', user: '', db: '', password: '', port: '' },
      addFormVisible: false, addLoading: false, addPassVisible: false, editPassVisible: false,
      addFormRules: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }, { max: 50, message: '不超过50个字符', trigger: 'blur' }],
        host: [{ required: true, message: '请输入Host', trigger: 'blur' }],
        port: [{ required: true, message: '请输入端口', trigger: 'blur' }, { max: 10, message: '不超过10个字符', trigger: 'blur' }],
        user: [{ required: true, message: '请输入用户', trigger: 'blur' }, { max: 50, message: '不超过50个字符', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { max: 50, message: '不超过50个字符', trigger: 'blur' }],
        db: [{ max: 50, message: '不超过50个字符', trigger: 'blur' }],
      },
      addForm: { name: '', host: '', user: '', db: '', password: '', port: '' },
    }
  },
  methods: {
    getGlobalBase() {
      this.listLoading = true; let self = this
      GetDataBase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { page: self.page, name: self.filters.name }).then(_data => {
        let { msg, code, data } = _data; self.listLoading = false
        if (code == '999999') { self.total = data.total; self.project = (data.data || []).map(item => { item._showPass = false; item._maskUser = self.maskUser(item.user); return item }) } else { self.$message.error({ message: msg, center: true }) }
      })
    },
    maskUser(u) { if (!u) return '***'; if (u.length <= 2) return u[0] + '***'; return u[0] + '***' + u[u.length - 1] },
    toggleMask(row, field) {
      if (field === 'pass') { this.$set(row, '_showPass', !row._showPass) }
      else { this.$set(row, '_maskUser', row._showUser ? this.maskUser(row.user) : row.user); this.$set(row, '_showUser', !row._showUser) }
    },
    handleDel(index, row) {
      this.$confirm('确认删除该记录吗?', '提示', { type: 'warning' }).then(() => {
        this.listLoading = true; let self = this
        DeleteDataBase({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { ids: [row.id] }).then(_data => {
          let { msg, code } = _data
          if (code == '999999') { self.$message({ message: '删除成功', center: true, type: 'success' }) } else { self.$message.error({ message: msg, center: true }) }
          self.getGlobalBase()
        })
      }).catch(() => {})
    },
    handleCurrentChange(val) { this.page = val; this.getGlobalBase() },
    handleEdit(index, row) { this.editFormVisible = true; this.editForm = Object.assign({}, row); this.editPassVisible = false },
    handleAdd() { this.addFormVisible = true; this.addPassVisible = false },
    editSubmit() {
      let self = this; let host = this.editForm.host.toLowerCase()
      if (host.startsWith('http://')) host = host.slice(7)
      if (host.startsWith('https://')) host = host.slice(8)
      this.$refs.editForm.validate((valid) => {
        if (valid) { this.$confirm('确认提交吗？', '提示', {}).then(() => { self.editLoading = true
          UpdateDataBase({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { id: Number(self.editForm.id), name: self.editForm.name, host, user: self.editForm.user, password: self.editForm.password, port: self.editForm.port, db: self.editForm.db }).then(_data => {
            let { msg, code } = _data; self.editLoading = false
            if (code == 999999) { self.$message({ message: '修改成功', center: true, type: 'success' }); self.editFormVisible = false; self.getGlobalBase() } else { self.$message.error({ message: msg, center: true }) }
          })
        })}
      })
    },
    addSubmit() {
      let host = this.addForm.host.toLowerCase()
      if (host.startsWith('http://')) host = host.slice(7)
      if (host.startsWith('https://')) host = host.slice(8)
      this.$refs.addForm.validate((valid) => {
        if (valid) { let self = this; this.$confirm('确认提交吗？', '提示', {}).then(() => { self.addLoading = true
          CreateDataBase({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { name: self.addForm.name, host, user: self.addForm.user, password: self.addForm.password, port: self.addForm.port, db: self.addForm.db }).then(_data => {
            let { msg, code } = _data; self.addLoading = false
            if (code == '999999') { self.$message({ message: '添加成功', center: true, type: 'success' }); self.addFormVisible = false; self.getGlobalBase() } else { self.$message.error({ message: msg, center: true }) }
          })
        })}
      })
    },
    checkAvailable(val) {
      let self = this
      CheckDataBase({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, val).then(_data => {
        let { msg, code } = _data
        if (code == '999999') { self.$message({ message: msg, center: true, type: 'success' }) } else { self.$message.error({ message: msg, center: true }) }
      })
    },
    selsChange(sels) { this.sels = sels },
    batchRemove() {
      let ids = this.sels.map(item => item.id); let self = this
      this.$confirm('确认删除选中记录吗？', '提示', { type: 'warning' }).then(() => { self.listLoading = true
        DeleteDataBase({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { ids }).then(_data => {
          let { msg, code } = _data; self.listLoading = false
          if (code == '999999') { self.$message({ message: '删除成功', center: true, type: 'success' }) } else { self.$message.error({ message: msg, center: true }) }
          self.getGlobalBase()
        })
      }).catch(() => {})
    },
  },
  mounted() { this.getGlobalBase() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.db-page { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }

.toolbar-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: $shadow-sm; .tb-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; } .tb-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; } .tb-search { width: 200px; } }
.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }
.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }
.db-name { font-weight: 500; color: $text; }
.mask-text { font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 12px; color: $text-tertiary; letter-spacing: 1px; user-select: none; }
.toggle-eye { cursor: pointer; color: $text-tertiary; font-size: 12px; margin-left: 6px; transition: color .12s ease; &:hover { color: $accent; } }
.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
.tb-footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 18px; border-top: 1px solid #f3f4f6; }

// Dialog
.db-dialog {
  :deep(.el-dialog__header) { padding: 18px 20px 0; }
  :deep(.el-dialog__body) { padding: 12px 20px 4px; }
  :deep(.el-dialog__footer) { padding: 0; }
}
.dialog-title-text { font-family: $font-display; font-size: 15px; font-weight: 700; color: $text; }
.db-form {
  .form-row-inline { display: flex; gap: 14px; }
  .form-field { margin-bottom: 12px; &:last-child { margin-bottom: 0; } :deep(.el-form-item) { margin-bottom: 0; } :deep(.el-form-item__error) { font-size: 11px; } }
  .form-field--half { flex: 1; min-width: 0; }
}
.field-label { display: block; font-size: 12px; font-weight: 500; color: $text-secondary; margin-bottom: 4px; }
.dialog-footer-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-top: 1px solid $border; }
.field-eye { color: $text-tertiary; &:hover { color: $text-secondary; } }
</style>
