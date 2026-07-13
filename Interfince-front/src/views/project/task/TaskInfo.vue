<template>
  <div class="task-page">
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <el-input v-model.trim="filters.name" placeholder="搜索任务名称" size="small" class="tb-search" @keyup.enter.native="getTaskRecord" clearable />
          <el-button type="primary" size="small" @click="getTaskRecord">查询</el-button>
          <el-button type="primary" size="small" @click="getTask"><i class="fa fa-plus"></i> 新增任务</el-button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table :data="project" v-loading="listLoading" class="data-table">
        <el-table-column type="index" width="55" />
        <el-table-column prop="name" label="任务名称" min-width="140" sortable show-overflow-tooltip>
          <template slot-scope="scope"><span class="task-name">{{ scope.row.name }}</span></template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="80">
          <template slot-scope="scope">
            <span class="type-badge" :class="scope.row.type === 'circulation' ? 'type--cycle' : 'type--timing'">
              {{ scope.row.type === 'circulation' ? '循环' : '定时' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="frequency" label="频率" width="80" />
        <el-table-column prop="unit" label="单位" width="70">
          <template slot-scope="scope">
            <span class="unit-text">{{ unitMap[scope.row.unit] || scope.row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="160" show-overflow-tooltip />
        <el-table-column prop="endTime" label="结束时间" width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="260" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="GetTaskExecuteRecode(scope.row)">执行记录</el-button>
            <el-button type="text" size="small" @click="getUpdateTask(scope.row)">修改</el-button>
            <el-button type="text" size="small" class="btn--danger" @click="DelTask(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <el-pagination small layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="10" :page-count="Math.ceil(total / 10)" />
      </div>
    </div>

    <!-- Add dialog -->
    <el-dialog :visible.sync="taskVShow" :close-on-click-modal="false" width="480px" class="task-dialog">
      <template slot="title"><span class="dialog-title-text">新增定时任务</span></template>

      <el-form ref="form" :model="form" label-width="0" :rules="formRules" class="task-form">
        <div class="form-field">
          <label class="field-label">任务名称</label>
          <el-form-item prop="name"><el-input v-model.trim="form.name" placeholder="输入任务名称" size="small" /></el-form-item>
        </div>

        <div class="form-field">
          <label class="field-label">执行模式</label>
          <div class="mode-switch">
            <label class="mode-option" :class="{ 'mode-option--active': form.type === 'circulation' }" @click="form.type = 'circulation'">
              <i class="fa fa-refresh"></i> 循环执行
            </label>
            <label class="mode-option" :class="{ 'mode-option--active': form.type === 'timing' }" @click="form.type = 'timing'">
              <i class="fa fa-calendar-check-o"></i> 单次定时
            </label>
          </div>
        </div>

        <template v-if="form.type === 'circulation'">
          <div class="form-field">
            <label class="field-label">执行间隔</label>
            <div class="interval-row">
              <el-form-item prop="frequency" class="interval-num"><el-input v-model.number="form.frequency" placeholder="间隔" size="small" /></el-form-item>
              <el-form-item prop="unit" class="interval-unit"><el-select v-model="form.unit" size="small"><el-option v-for="item in unit" :key="item.value" :label="item.label" :value="item.value" /></el-select></el-form-item>
            </div>
          </div>
          <div class="form-field">
            <label class="field-label">有效时间范围</label>
            <el-form-item prop="timeArray">
              <el-date-picker v-model="form.timeArray" type="datetimerange" :picker-options="pickerOptions2" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width:100%" size="small" />
            </el-form-item>
          </div>
        </template>

        <template v-if="form.type === 'timing'">
          <div class="form-field">
            <label class="field-label">执行时间</label>
            <el-form-item prop="time">
              <el-date-picker v-model="form.time" type="datetime" placeholder="选择日期和时间" :picker-options="pickerOptions1" style="width:100%" size="small" />
            </el-form-item>
          </div>
        </template>

        <div class="form-field">
          <label class="field-label">测试环境</label>
          <el-form-item prop="Host">
            <el-select v-model="form.Host" placeholder="选择 Host" style="width:100%" size="small">
              <el-option v-for="(item, i) in Host" :key="i" :label="item.name + ' — ' + item.host" :value="item.id" />
            </el-select>
          </el-form-item>
        </div>

        <div class="form-field">
          <label class="field-label">用例集</label>
          <el-form-item prop="Case">
            <el-select v-model="sels" multiple placeholder="选择用例集" style="width:100%" size="small">
              <el-option v-for="(item, i) in Case" :key="i" :label="item.caseName" :value="item.id" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer-bar">
        <el-button @click="taskVShow = false" size="small">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="addTask" size="small">创建任务</el-button>
      </div>
    </el-dialog>

    <!-- Edit dialog -->
    <el-dialog :visible.sync="updateTaskVShow" :close-on-click-modal="false" width="480px" class="task-dialog">
      <template slot="title"><span class="dialog-title-text">修改定时任务</span></template>

      <el-form ref="updateForm" :model="form" label-width="0" :rules="formRules" class="task-form">
        <div class="form-field">
          <label class="field-label">任务名称</label>
          <el-form-item prop="name"><el-input v-model.trim="form.name" placeholder="输入任务名称" size="small" /></el-form-item>
        </div>

        <div class="form-field">
          <label class="field-label">执行模式</label>
          <div class="mode-switch">
            <label class="mode-option" :class="{ 'mode-option--active': form.type === 'circulation' }" @click="form.type = 'circulation'">
              <i class="fa fa-refresh"></i> 循环执行
            </label>
            <label class="mode-option" :class="{ 'mode-option--active': form.type === 'timing' }" @click="form.type = 'timing'">
              <i class="fa fa-calendar-check-o"></i> 单次定时
            </label>
          </div>
        </div>

        <template v-if="form.type === 'circulation'">
          <div class="form-field">
            <label class="field-label">执行间隔</label>
            <div class="interval-row">
              <el-form-item prop="frequency" class="interval-num"><el-input v-model.number="form.frequency" placeholder="间隔" size="small" /></el-form-item>
              <el-form-item prop="unit" class="interval-unit"><el-select v-model="form.unit" size="small"><el-option v-for="item in unit" :key="item.value" :label="item.label" :value="item.value" /></el-select></el-form-item>
            </div>
          </div>
          <div class="form-field">
            <label class="field-label">有效时间范围</label>
            <el-form-item prop="timeArray">
              <el-date-picker v-model="form.timeArray" type="datetimerange" :picker-options="pickerOptions2" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width:100%" size="small" />
            </el-form-item>
          </div>
        </template>

        <template v-if="form.type === 'timing'">
          <div class="form-field">
            <label class="field-label">执行时间</label>
            <el-form-item prop="time">
              <el-date-picker v-model="form.time" type="datetime" placeholder="选择日期和时间" :picker-options="pickerOptions1" style="width:100%" size="small" :key="'edit-time-' + updateTaskVShow" />
            </el-form-item>
          </div>
        </template>

        <div class="form-field">
          <label class="field-label">测试环境</label>
          <el-form-item prop="Host">
            <el-select v-model="form.Host" placeholder="选择 Host" style="width:100%" size="small">
              <el-option v-for="(item, i) in Host" :key="i" :label="item.name + ' — ' + item.host" :value="item.id" />
            </el-select>
          </el-form-item>
        </div>

        <div class="form-field">
          <label class="field-label">用例集</label>
          <el-form-item prop="Case">
            <el-select v-model="sels" multiple placeholder="选择用例集" style="width:100%" size="small">
              <el-option v-for="(item, i) in Case" :key="i" :label="item.caseName" :value="item.id" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer-bar">
        <el-button @click="updateTaskVShow = false" size="small">取消</el-button>
        <el-button type="primary" :loading="updateLoading" @click="UpdateTask" size="small">保存修改</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import $ from 'jquery'
import moment from 'moment'
import { test, getHost, getCase, updateTask, addTask, seachTask, delTask } from '../../../api/api'

export default {
  data() {
    return {
      filters: { name: '' }, Case: [], total: 0, page: 1, listLoading: false, sels: [],
      taskVShow: false, updateTaskVShow: false, delLoading: false, disDel: true, TestStatus: false,
      form: { name: '', type: 'circulation', frequency: '', unit: 'm', time: '', timeArray: [], Host: '', id: '' },
      formRules: {
        name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }, { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }],
        frequency: [{ type: 'number', required: true, message: '请输入时间间隔' }],
        timeArray: [{ type: 'array', required: true, message: '请选择执行时间' }],
        time: [{ required: true, message: '请选择执行时间' }],
        Host: [{ required: true, message: '请选择测试域名' }],
        type: [{ required: true, message: '请选择任务类型', trigger: 'blur' }],
      },
      Host: [],
      unit: [{ value: 'm', label: '分' }, { value: 'h', label: '时' }, { value: 'd', label: '天' }, { value: 'w', label: '周' }],
      type: [{ value: 'circulation', label: '循环' }, { value: 'timing', label: '定时' }],
      unitMap: { m: '分', h: '时', d: '天', w: '周' },
      pickerOptions1: { disabledDate(time) { return time.getTime() < Date.now() - 8.64e7 } },
      pickerOptions2: { disabledDate(time) { return time.getTime() < Date.now() - 8.64e7 }, shortcuts: [{ text: '最近一周', onClick(picker) { const e = new Date(), s = new Date(); e.setTime(e.getTime() + 3600 * 1000 * 24 * 7); picker.$emit('pick', [s, e]) } }, { text: '最近一个月', onClick(picker) { const e = new Date(), s = new Date(); e.setTime(e.getTime() + 3600 * 1000 * 24 * 30); picker.$emit('pick', [s, e]) } }, { text: '最近三个月', onClick(picker) { const e = new Date(), s = new Date(); e.setTime(e.getTime() + 3600 * 1000 * 24 * 90); picker.$emit('pick', [s, e]) } }] },
    }
  },
  methods: {
    getTaskRecord() {
      this.listLoading = true; let self = this
      seachTask({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { projectId: this.$route.params.project_id, page: self.page, name: self.filters.name }).then(_data => {
        let { msg, code, data } = _data; self.listLoading = false
        if (code == '999999') { self.total = data.total; self.project = data.data } else { self.$message.error({ message: msg, center: true }) }
      })
    },
    GetTaskExecuteRecode(rows) { this.$router.push({ name: '定时任务记录', query: { taskName: rows.name } }) },
    handleCurrentChange(val) { this.page = val; this.getTaskRecord() },
    getUpdateTask(row) {
      let self = this
      try { this.form = Object.assign({}, row); self.form.timeArray = [new Date(row.startTime), new Date(row.endTime)]; self.form.time = new Date(row.startTime); self.disDel = true; self.updateTaskVShow = true } catch (e) { self.$message.error({ message: '返回参数异常', center: true }) }
    },
    UpdateTask() {
      let self = this
      this.$refs.updateForm.validate((valid) => {
        if (valid) { this.$confirm('确认提交吗？', '提示', {}).then(() => { self.updateLoading = true; let params = { project_id: Number(self.$route.params.project_id), Host_id: Number(self.form.Host), name: self.form.name, type: self.form.type, frequency: Number(self.form.frequency), unit: self.form.unit, caseId: self.sels, id: self.form.id }; if (self.form.type === 'circulation') { params.startTime = moment(self.form.timeArray[0]).format('YYYY-MM-DD HH:mm:ss'); params.endTime = moment(self.form.timeArray[1]).format('YYYY-MM-DD HH:mm:ss') } else { params.startTime = moment(self.form.time).format('YYYY-MM-DD HH:mm:ss'); params.endTime = moment(self.form.time).format('YYYY-MM-DD HH:mm:ss') }; updateTask({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, params).then(_data => { let { code, msg } = _data; self.updateLoading = false; if (code == '999999') { self.$message({ message: '修改成功', center: true, type: 'success' }); self.updateTaskVShow = false; self.getTaskRecord() } else { self.$message.error({ message: msg, center: true }) } }) }) }
      })
    },
    getTask() {
      let self = this
      $.ajax({ type: 'get', url: test + '/api/automation/get_time_task', async: true, data: { project_id: self.$route.params.project_id }, headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => {
          if (data.code === '999999') {
            try { self.form.name = data.data.name; self.form.type = data.data.type; self.form.frequency = data.data.frequency; self.form.unit = self.form.type === 'timing' ? 'm' : data.data.unit; self.form.time = data.data.startTime; self.form.timeArray = [data.data.startTime, data.data.endTime]; self.form.Host = data.data.Host; self.disDel = false } catch (e) { self.form = { name: '', type: 'circulation', frequency: '', unit: 'm', time: '', timeArray: [], Host: '', id: '' }; self.disDel = true }
            self.taskVShow = true
          } else { self.$message.error({ message: data.msg, center: true }) }
        },
        error: function () { self.$message.error({ message: '获取失败', center: true }) },
      })
    },
    addTask() {
      let self = this
      this.$refs.form.validate((valid) => {
        if (valid) { this.$confirm('确认提交吗？', '提示', {}).then(() => { self.editLoading = true; let params = { project_id: Number(self.$route.params.project_id), Host_id: Number(self.form.Host), name: self.form.name, type: self.form.type, frequency: Number(self.form.frequency), unit: self.form.unit, case_id: self.sels }; if (self.form.type === 'circulation') { params.startTime = moment(self.form.timeArray[0]).format('YYYY-MM-DD HH:mm:ss'); params.endTime = moment(self.form.timeArray[1]).format('YYYY-MM-DD HH:mm:ss') } else { params.startTime = moment(self.form.time).format('YYYY-MM-DD HH:mm:ss'); params.endTime = moment(self.form.time).format('YYYY-MM-DD HH:mm:ss') }; addTask({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, params).then(_data => { let { code, msg } = _data; self.editLoading = false; if (code == '999999') { self.taskVShow = false; self.$message({ message: '创建成功', center: true, type: 'success' }); self.getTaskRecord() } else { self.$message.error({ message: msg, center: true }) } }) }) }
      })
    },
    GetHost() { let self = this; getHost({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { project_id: this.$route.params.project_id, page: this.page }).then(_data => { if (_data.code == '999999') { _data.data.data.forEach((item) => { if (item.status) self.Host.push(item) }) } else { self.$message.error({ message: _data.msg, center: true }) } }) },
    GetCase() { let self = this; getCase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { project_id: this.$route.params.project_id }).then(_data => { if (_data.code == '999999') { _data.data.data.forEach((item) => { if (item.caseName) self.Case.push(item) }) } else { self.$message.error({ message: _data.msg, center: true }) } }) },
    DelTask(row) { let self = this; self.delLoading = true; delTask({ 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { project_id: Number(self.$route.params.project_id), taskName: row.name }).then(_data => { self.delLoading = false; if (_data.code == '999999') { self.$message({ message: '删除成功', center: true, type: 'success' }); self.getTaskRecord() } else { self.$message.error({ message: _data.msg, center: true }) } }) },
  },
  mounted() { this.getTaskRecord(); this.GetHost(); this.GetCase() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.task-page { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }

.toolbar-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: $shadow-sm; .tb-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; } .tb-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; } .tb-search { width: 200px; } }
.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }
.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }
.task-name { font-weight: 500; color: $text; }

.type-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 4px; letter-spacing: 0.03em;
  &.type--cycle { background: #eff3ff; color: #1d4ed8; }
  &.type--timing { background: #fef3c7; color: #92400e; }
}
.unit-text { color: $text-secondary; font-size: 12px; }
.btn--danger { color: #dc2626 !important; &:hover { color: #b91c1c !important; } }
.tb-footer { display: flex; justify-content: flex-end; padding: 10px 18px; border-top: 1px solid #f3f4f6; }

// ─── Dialog ─────────────────────────────────────────
.task-dialog {
  :deep(.el-dialog__header) { padding: 18px 20px 0; }
  :deep(.el-dialog__body) { padding: 12px 20px 4px; }
  :deep(.el-dialog__footer) { padding: 0; }
}

.dialog-title-text {
  font-family: $font-display; font-size: 15px; font-weight: 700; color: $text;
}

// ─── Form fields ────────────────────────────────────
.form-field {
  margin-bottom: 12px;
  &:last-child { margin-bottom: 0; }
  :deep(.el-form-item) { margin-bottom: 0; }
  :deep(.el-form-item__error) { padding-top: 1px; font-size: 11px; }
}

.field-label {
  display: block; font-size: 12px; font-weight: 500; color: $text-secondary; margin-bottom: 4px;
}

// ─── Mode switch (compact inline) ───────────────────
.mode-switch {
  display: flex; gap: 0;
  border: 1px solid $border; border-radius: 6px; overflow: hidden;
}

.mode-option {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 5px;
  padding: 7px 12px; font-size: 12px; font-weight: 500;
  background: $surface; color: $text-secondary; cursor: pointer;
  transition: all .15s ease; user-select: none;
  border-right: 1px solid $border;
  &:last-child { border-right: none; }
  i { font-size: 12px; color: $text-tertiary; transition: color .15s ease; }
  &:hover { background: #f9fafb; }

  &--active {
    background: #eff3ff; color: $accent; font-weight: 600;
    i { color: $accent; }
    & + .mode-option { border-left-color: transparent; }
  }
}

// ─── Interval row ───────────────────────────────────
.interval-row {
  display: flex; align-items: center; gap: 8px;
  .interval-num { width: 120px; }
  .interval-unit { width: 100px; }
}

// ─── Dialog footer ──────────────────────────────────
.dialog-footer-bar {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid $border;
}
</style>
