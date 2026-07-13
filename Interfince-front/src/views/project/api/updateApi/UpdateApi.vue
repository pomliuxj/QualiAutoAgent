<template>
  <div class="api-update">
    <!-- Form card: Basic info -->
    <div class="form-card">
      <div class="form-card-header">
        <i class="fa fa-info-circle"></i>
        <span>基本信息</span>
      </div>
      <div class="form-card-body">
        <el-form :model="form" ref="form" :rules="FormRules" class="api-form">
          <div class="form-row">
            <div class="form-col form-col--group">
              <label class="form-label">接口分组</label>
              <el-form-item prop="firstGroup" class="form-item--clean">
                <el-select v-model="form.firstGroup" placeholder="选择分组" size="small">
                  <el-option v-for="(item, index) in group" :key="index" :label="item.name" :value="item.id" />
                </el-select>
              </el-form-item>
            </div>
            <div class="form-col form-col--name">
              <label class="form-label">接口名称</label>
              <el-form-item prop="name" class="form-item--clean">
                <el-input v-model.trim="form.name" placeholder="接口名称" size="small" />
              </el-form-item>
            </div>
            <div class="form-col form-col--status">
              <label class="form-label">状态</label>
              <el-form-item class="form-item--clean">
                <el-select v-model="form.status" placeholder="状态" size="small">
                  <el-option v-for="(item, index) in status" :key="index" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </div>
          </div>
          <div class="form-row form-divider">
            <div class="form-col form-col--method">
              <label class="form-label">请求方式</label>
              <el-select v-model="form.request4" placeholder="Method" size="small" @change="checkRequest">
                <el-option v-for="(item, index) in request" :key="index" :label="item.label" :value="item.value" />
              </el-select>
            </div>
            <div class="form-col form-col--http">
              <label class="form-label">协议</label>
              <el-select v-model="form.Http4" placeholder="HTTP" size="small">
                <el-option v-for="(item, index) in Http" :key="index" :label="item.label" :value="item.value" />
              </el-select>
            </div>
            <div class="form-col form-col--addr">
              <label class="form-label">URL</label>
              <el-form-item prop="addr" class="form-item--clean">
                <el-input v-model.trim="form.addr" placeholder="请求地址" size="small" />
              </el-form-item>
            </div>
          </div>
        </el-form>
      </div>
    </div>

    <!-- Collapse sections -->
    <el-collapse v-model="activeNames" class="api-collapse">
      <!-- Headers -->
      <el-collapse-item name="1" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-arrow-up panel-title-icon"></i>
            <span>请求头部</span>
          </div>
        </template>
        <div class="panel-table">
          <div class="panel-row panel-row--head" v-for="(item, index) in form.head" :key="'h' + index">
            <div class="panel-cell panel-cell--name">
              <el-select placeholder="标签" filterable v-model="item.name" size="small" class="head-select">
                <el-option v-for="(h, i) in header" :key="i" :label="h.label" :value="h.value" />
              </el-select>
              <el-input v-model.trim="item.name" placeholder="自定义" size="small" class="head-input" />
            </div>
            <div class="panel-cell panel-cell--value">
              <el-input v-model.trim="item.value" placeholder="内容" size="small" />
            </div>
            <div class="panel-cell panel-cell--action">
              <button class="icon-btn icon-btn--del" @click="delHead(index)" title="删除"><i class="fa fa-trash"></i></button>
            </div>
            <div class="panel-cell panel-cell--add" v-if="index === form.head.length - 1">
              <button class="icon-btn icon-btn--add" @click="addHead" title="添加"><i class="fa fa-plus"></i></button>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <!-- Request parameters -->
      <el-collapse-item name="2" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-cube panel-title-icon"></i>
            <span>请求参数</span>
          </div>
        </template>
        <div class="param-bar">
          <el-radio v-model="radio" label="form-data">表单(form-data)</el-radio>
          <el-radio v-if="request3" v-model="radio" label="raw">源数据(raw)</el-radio>
          <el-checkbox v-if="request3" v-model="radioType" v-show="ParameterTyep" class="param-checkbox">表单转源数据</el-checkbox>
        </div>
        <div class="panel-table" v-show="ParameterTyep">
          <div class="panel-row panel-row--param" v-for="(item, index) in form.parameter" :key="'p' + index">
            <div class="panel-cell panel-cell--name">
              <el-input v-model.trim="item.name" placeholder="参数名" size="small" />
            </div>
            <div class="panel-cell panel-cell--value">
              <el-input v-model.trim="item.value" placeholder="参数值" size="small" />
            </div>
            <div class="panel-cell panel-cell--type">
              <el-select v-model="item._type" placeholder="类型" size="small">
                <el-option v-for="(t, i) in paramTyep" :key="i" :label="t.label" :value="t.value" />
              </el-select>
            </div>
            <div class="panel-cell panel-cell--desc">
              <el-input v-model.trim="item.description" placeholder="说明" size="small" />
            </div>
            <div class="panel-cell panel-cell--action">
              <button class="icon-btn icon-btn--del" @click="delParameter(index)" title="删除"><i class="fa fa-trash"></i></button>
              <button class="text-btn" @click="handleParameterEdit(index, item)">更多设置</button>
            </div>
            <div class="panel-cell panel-cell--add" v-if="index === form.parameter.length - 1">
              <button class="icon-btn icon-btn--add" @click="addParameter" title="添加"><i class="fa fa-plus"></i></button>
            </div>
          </div>
        </div>
        <div v-show="!ParameterTyep" class="raw-section">
          <div class="raw-header">
            <span class="raw-label">raw</span>
          </div>
          <el-input type="textarea" :rows="5" placeholder="输入 raw 数据" v-model.trim="parameterRaw" class="raw-textarea" />
        </div>
      </el-collapse-item>

      <!-- Response parameters -->
      <el-collapse-item name="3" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-arrow-down panel-title-icon"></i>
            <span>返回参数</span>
          </div>
        </template>
        <div class="panel-table">
          <div class="panel-row panel-row--param" v-for="(item, index) in form.response" :key="'r' + index">
            <div class="panel-cell panel-cell--name">
              <el-input v-model.trim="item.name" placeholder="参数名" size="small" />
            </div>
            <div class="panel-cell panel-cell--tier">
              <el-input v-model.trim="item.tier" placeholder="层级" size="small" />
            </div>
            <div class="panel-cell panel-cell--value">
              <el-input v-model.trim="item.value" placeholder="参数值" size="small" />
            </div>
            <div class="panel-cell panel-cell--type">
              <el-select v-model.trim="item._type" placeholder="类型" size="small">
                <el-option v-for="(t, i) in paramTyep" :key="i" :label="t.label" :value="t.value" />
              </el-select>
            </div>
            <div class="panel-cell panel-cell--desc">
              <el-input v-model.trim="item.description" placeholder="说明" size="small" />
            </div>
            <div class="panel-cell panel-cell--action">
              <button class="icon-btn icon-btn--del" @click="delResponse(index)" title="删除"><i class="fa fa-trash"></i></button>
              <button class="text-btn" @click="handleResponseEdit(index, item)">更多设置</button>
            </div>
            <div class="panel-cell panel-cell--add" v-if="index === form.response.length - 1">
              <button class="icon-btn icon-btn--add" @click="addResponse" title="添加"><i class="fa fa-plus"></i></button>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <!-- Mock -->
      <el-collapse-item name="4" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-code panel-title-icon"></i>
            <span>普通 Mock</span>
          </div>
        </template>
        <div class="mock-section">
          <div class="form-row">
            <div class="form-col form-col--method">
              <label class="form-label">HTTP 状态</label>
              <el-select v-model="form.mockCode" placeholder="状态码" size="small">
                <el-option v-for="(item, index) in httpCode" :key="index" :label="item.label" :value="item.value" />
              </el-select>
            </div>
          </div>
          <label class="form-label mock-label">Mock 数据</label>
          <el-input v-model.trim="form.mockData" type="textarea" :rows="8" placeholder="输入 mock 内容（JSON 格式）" class="mock-textarea" />
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- Save bar -->
    <div class="save-bar">
      <router-link
        :to="{ name: '基础信息', params: { project_id: $route.params.project_id, api_id: $route.params.api_id } }"
        class="cancel-btn"
      >取消</router-link>
      <button class="save-btn" @click="updateApiInfo">保存修改</button>
    </div>

    <!-- Dialogs -->
    <el-dialog title="更多设置 - 请求参数" :visible.sync="addParameterFormVisible" :close-on-click-modal="false" width="480px" class="edit-dialog">
      <el-form :model="editForm" label-width="80px" :rules="FormRules" ref="editForm">
        <el-form-item label="参数名" prop="name"><el-input v-model.trim="editForm.name" placeholder="参数名称" /></el-form-item>
        <el-form-item label="参数值"><el-input v-model.trim="editForm.value" placeholder="参数值" /></el-form-item>
        <el-form-item label="必填" prop="required">
          <el-select v-model.trim="editForm.required" placeholder="必填？">
            <el-option v-for="(item, i) in required4" :key="i" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="输入限制"><el-input v-model.trim="editForm.restrict" placeholder="输入限制" /></el-form-item>
        <el-form-item label="描述"><el-input type="textarea" :rows="4" v-model.trim="editForm.description" placeholder="描述" /></el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addParameterFormVisible = false">取消</el-button>
        <el-button type="primary" @click="editParameterSubmit">提交</el-button>
      </div>
    </el-dialog>

    <el-dialog title="更多设置 - 返回参数" :visible.sync="addResponseFormVisible" :close-on-click-modal="false" width="480px" class="edit-dialog">
      <el-form :model="editForm" label-width="80px" :rules="FormRules" ref="editForm">
        <el-form-item label="参数名" prop="name"><el-input v-model.trim="editForm.name" placeholder="参数名称" /></el-form-item>
        <el-form-item label="层级"><el-input v-model.trim="editForm.tier" placeholder="如 data / data.roles" /></el-form-item>
        <el-form-item label="参数值"><el-input v-model.trim="editForm.value" placeholder="参数值" /></el-form-item>
        <el-form-item label="必填" prop="required">
          <el-select v-model.trim="editForm.required" placeholder="必填？">
            <el-option v-for="(item, i) in required4" :key="i" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="输入限制"><el-input v-model.trim="editForm.restrict" placeholder="输入限制" /></el-form-item>
        <el-form-item label="描述"><el-input type="textarea" :rows="4" v-model.trim="editForm.description" placeholder="描述" /></el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addResponseFormVisible = false">取消</el-button>
        <el-button type="primary" @click="editResponseSubmit">提交</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { test, staticdata } from '../../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      request: staticdata.request,
      Http: staticdata.Http,
      paramTyep: staticdata.paramTyep,
      checkHeadList: [],
      checkParameterList: [],
      ParameterTyep: true,
      group: [],
      radio: 'form-data',
      status: [
        { value: true, label: '启用' },
        { value: false, label: '禁用' },
      ],
      header: staticdata.header,
      header4: '',
      addParameterFormVisible: false,
      addResponseFormVisible: false,
      required4: [
        { value: true, label: '是' },
        { value: false, label: '否' },
      ],
      httpCode: staticdata.httpCode,
      radioType: '',
      result: true,
      activeNames: ['1', '2', '3', '4'],
      id: '',
      parameterRaw: '',
      request3: true,
      form: {
        firstGroup: '',
        name: '',
        status: 'True',
        request4: 'GET',
        Http4: 'HTTP',
        addr: '',
        head: [
          { name: '', value: '' },
          { name: '', value: '' },
        ],
        parameter: [
          { name: '', value: '', _type: 'String', required: true, restrict: '', description: '' },
          { name: '', value: '', _type: 'String', required: true, restrict: '', description: '' },
        ],
        parameterType: '',
        response: [
          { name: '', tier: '', value: '', _type: 'String', required: true, description: '' },
          { name: '', tier: '', value: '', _type: 'String', required: true, description: '' },
        ],
        mockCode: '',
        mockData: '',
      },
      FormRules: {
        name: [
          { required: true, message: '请输入名称', trigger: 'blur' },
          { max: 50, message: '不能超过50个字', trigger: 'blur' },
        ],
        addr: [{ required: true, message: '请输入地址', trigger: 'blur' }],
        required: [{ required: true, message: '请选择是否必填', trigger: 'blur' }],
        firstGroup: [{ type: 'number', required: true, message: '请选择分组', trigger: 'blur' }],
      },
      editForm: { name: '', tier: '', value: '', required: '', restrict: '', description: '' },
    }
  },
  methods: {
    checkRequest() {
      let request = this.form.request4
      if (request === 'GET' || request === 'DELETE') {
        this.request3 = false
      } else {
        this.request3 = true
      }
    },
    isJsonString(str) {
      try { if (typeof JSON.parse(str) === 'object') { return true } } catch (e) {}
      return false
    },
    getApiInfo() {
      let self = this
      let param = { project_id: self.$route.params.project_id, api_id: self.$route.params.api_id }
      $.ajax({
        type: 'get', url: test + '/api/api/api_info', async: true, data: param,
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) {
          if (data.code === '999999') {
            data = data.data
            self.id = data.id
            self.form.firstGroup = data.apiGroupLevelFirst
            self.form.name = data.name
            self.form.status = !!data.status
            self.form.request4 = data.requestType
            self.form.Http4 = data.httpType
            self.form.addr = data.apiAddress
            if (data.headers && data.headers.length) { self.form.head = data.headers }
            try {
              self.parameterRaw = data.requestParameterRaw.data
                .replace(/'/g, '"')
                .replace(/None/g, 'null')
                .replace(/True/g, 'true')
                .replace(/False/g, 'false')
            } catch (e) {}
            if (data.requestParameter && data.requestParameter.length) { self.form.parameter = data.requestParameter }
            self.form.parameterType = data.requestParameterType
            self.radio = self.form.parameterType
            if (data.response && data.response.length) { self.form.response = data.response }
            self.form.mockCode = data.mockCode
            self.form.mockData = data.data
            if (data.data) { self.form.mockJsonData = JSON.parse(data.data) }
            self.checkRequest()
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
      })
    },
    updateApiInfo() {
      if (this.form.mockData && this.form.mockCode) {
        if (!this.isJsonString(this.form.mockData)) {
          this.$message({ message: 'Mock 格式错误', center: true, type: 'error' })
        } else {
          this.updateApi()
        }
      } else if (this.form.mockData || this.form.mockCode) {
        this.$message({ message: 'HTTP 状态或 Mock 数据为空', center: true, type: 'warning' })
      } else {
        this.updateApi()
      }
    },
    updateApi() {
      this.$refs.form.validate((valid) => {
        if (valid) {
          let self = this
          this.$confirm('确认提交修改吗？', '提示', {
            confirmButtonText: '确认',
            cancelButtonText: '取消',
          }).then(() => {
            self.form.parameterType = self.radio
            let _type = self.form.parameterType
            let _parameter = {}
            if (_type === 'form-data') {
              if (self.radioType === true) {
                _type = 'raw'
                self.form.parameter.forEach((item) => { _parameter[item.name] = item.value })
              } else {
                _parameter = self.form.parameter
              }
            } else {
              _parameter = self.parameterRaw
            }
            let param = JSON.stringify({
              project_id: Number(self.$route.params.project_id),
              id: Number(self.$route.params.api_id),
              apiGroupLevelFirst_id: Number(self.form.firstGroup),
              name: self.form.name,
              httpType: self.form.Http4,
              requestType: self.form.request4,
              apiAddress: self.form.addr,
              status: self.form.status,
              headDict: self.form.head,
              requestParameterType: _type,
              requestList: _parameter,
              responseList: self.form.response,
              mockCode: self.form.mockCode,
              data: self.form.mockData,
              description: '',
            })
            const doUpdate = () => {
              $.ajax({
                type: 'post', url: test + '/api/api/update_api', async: true, data: param,
                headers: {
                  'Content-Type': 'application/json',
                  Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
                }, timeout: 5000,
                success: function (data) {
                  if (data.code === '999999') {
                    self.$router.push({
                      name: '基础信息',
                      params: { project_id: self.$route.params.project_id, api_id: self.$route.params.api_id },
                    })
                    self.$message({ message: '修改成功', center: true, type: 'success' })
                  } else {
                    self.$message.error({ message: data.msg, center: true })
                  }
                },
              })
            }
            if (self.parameterRaw && _type === 'raw' && !self.isJsonString(self.parameterRaw)) {
              self.$message({ message: '源数据格式错误', center: true, type: 'error' })
            } else {
              doUpdate()
            }
          })
        }
      })
    },
    editParameterSubmit() {
      this.$refs.editForm.validate((valid) => {
        if (valid) {
          this.form.parameter[this.id] = this.editForm
          this.addParameterFormVisible = false
        }
      })
    },
    handleParameterEdit(index, row) {
      this.addParameterFormVisible = true
      this.id = index
      this.editForm = Object.assign({}, row)
    },
    editResponseSubmit() {
      this.$refs.editForm.validate((valid) => {
        if (valid) {
          this.form.response[this.id] = this.editForm
          this.addResponseFormVisible = false
        }
      })
    },
    handleResponseEdit(index, row) {
      this.addResponseFormVisible = true
      this.id = index
      this.editForm = Object.assign({}, row)
    },
    getApiGroup() {
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/api/group', async: true,
        data: { project_id: this.$route.params.project_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) {
          if (data.code === '999999') {
            self.group = data.data
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
      })
    },
    addHead() { this.form.head.push({ name: '', value: '' }) },
    delHead(index) {
      this.form.head.splice(index, 1)
      if (!this.form.head.length) { this.form.head.push({ name: '', value: '' }) }
    },
    addParameter() {
      this.form.parameter.push({ name: '', value: '', _type: 'String', required: true, restrict: '', description: '' })
    },
    delParameter(index) {
      this.form.parameter.splice(index, 1)
      if (!this.form.parameter.length) {
        this.form.parameter.push({ name: '', value: '', _type: 'String', required: true, restrict: '', description: '' })
      }
    },
    addResponse() {
      this.form.response.push({ name: '', tier: '', value: '', _type: 'String', required: true, description: '' })
    },
    delResponse(index) {
      this.form.response.splice(index, 1)
      if (!this.form.response.length) {
        this.form.response.push({ name: '', tier: '', value: '', _type: 'String', required: true, description: '' })
      }
    },
    changeParameterType() { this.ParameterTyep = this.radio === 'form-data' },
  },
  watch: {
    radio() { this.changeParameterType() },
  },
  mounted() {
    this.getApiGroup()
    this.getApiInfo()
  },
}
</script>

<style lang="scss" scoped>
// ─── Tokens ──────────────────────────────────────────
$bg: #f7f8fa;
$surface: #fff;
$accent: #1d4ed8;
$accent-hover: #1a43c0;
$accent-soft: #eff3ff;
$text: #111827;
$text-secondary: #6b7280;
$text-tertiary: #9ca3af;
$border: #e5e7eb;
$border-light: #f3f4f6;
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
$radius: 10px;
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-mono: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;

.api-update {
  padding: 4px 0 24px;
  background: transparent;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
}

// ─── Form card ──────────────────────────────────────
.form-card {
  background: $surface;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow-sm;
  margin-bottom: 16px;
  overflow: hidden;
}

.form-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: #fafbfc;
  border-bottom: 1px solid $border;
  font-family: $font-display;
  font-size: 14px;
  font-weight: 600;
  color: $text;

  i {
    font-size: 14px;
    color: $accent;
  }
}

.form-card-body {
  padding: 20px 24px;
}

// ─── Form layout ────────────────────────────────────
.api-form {
  .form-row {
    display: flex;
    gap: 16px;
    align-items: flex-end;
    margin-bottom: 14px;
    flex-wrap: wrap;

    &:last-child { margin-bottom: 0; }
  }

  .form-divider {
    padding-top: 16px;
    border-top: 1px solid $border-light;
  }

  .form-col {
    &--group { width: 180px; }
    &--name { flex: 1; min-width: 160px; }
    &--status { width: 120px; }
    &--method { width: 130px; }
    &--http { width: 110px; }
    &--addr { flex: 1; min-width: 200px; }
  }
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: $text-tertiary;
  margin-bottom: 5px;
}

.form-item--clean {
  margin-bottom: 0;
}

// ─── Collapse panels ────────────────────────────────
.api-collapse {
  border: none;
  margin-bottom: 16px;

  :deep(.collapse-panel) {
    background: $surface;
    border: 1px solid $border;
    border-radius: $radius;
    margin-bottom: 10px;
    box-shadow: $shadow-sm;
    overflow: hidden;

    .el-collapse-item__header {
      height: 48px;
      line-height: 48px;
      padding: 0 20px;
      background: #fafbfc;
      border-bottom: 1px solid transparent;
      transition: border-color 0.2s ease;

      &.is-active {
        border-bottom-color: $border;
      }
    }

    .el-collapse-item__wrap {
      border: none;
      background: $surface;
    }

    .el-collapse-item__content {
      padding: 0;
    }
  }
}

.panel-title {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: $font-display;
  font-size: 13px;
  font-weight: 600;
  color: $text;

  &-icon {
    font-size: 13px;
    color: $accent;
    width: 18px;
    text-align: center;
  }
}

// ─── Panel tables ───────────────────────────────────
.panel-table { padding: 4px 0; }

.panel-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid $border-light;

  &:last-child { border-bottom: none; }

  &--head {
    .panel-cell--name { display: flex; gap: 0; flex: 2; min-width: 200px; }
    .panel-cell--value { flex: 3; min-width: 160px; }
  }

  &--param {
    flex-wrap: wrap;
    .panel-cell--name { flex: 1.5; min-width: 100px; }
    .panel-cell--tier { flex: 1.2; min-width: 90px; }
    .panel-cell--value { flex: 1.5; min-width: 100px; }
    .panel-cell--type { width: 100px; }
    .panel-cell--desc { flex: 1.5; min-width: 100px; }
  }
}

.panel-cell {
  &--action { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
  &--add { flex-shrink: 0; }
}

// ─── Icon buttons ───────────────────────────────────
.icon-btn {
  width: 30px; height: 30px;
  border-radius: 5px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  transition: all 0.12s ease;

  &--del { color: #9ca3af; &:hover { color: #dc2626; background: #fef2f2; } }
  &--add { color: $accent; border-color: $accent-soft; &:hover { background: $accent-soft; } }
}

.text-btn {
  background: none; border: none;
  font-size: 11px; color: $accent;
  cursor: pointer; padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  font-family: $font-body;
  transition: all 0.12s ease;
  &:hover { background: $accent-soft; color: $accent-hover; }
}

// ─── Param bar ──────────────────────────────────────
.param-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 20px;
  border-bottom: 1px solid $border-light;
}

.param-checkbox { margin-left: 4px; }

// ─── Raw input ──────────────────────────────────────
.raw-section { padding: 0; }

.raw-header {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: #f9fafb;
  border-bottom: 1px solid $border-light;
}

.raw-label {
  font-family: $font-mono;
  font-size: 11px;
  font-weight: 600;
  color: $text-tertiary;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.raw-textarea {
  :deep(textarea) {
    font-family: $font-mono;
    font-size: 13px;
    line-height: 1.6;
    border: none;
    border-radius: 0;
    resize: vertical;
    &:focus { border: none; box-shadow: none; }
  }
}

// ─── Head select ────────────────────────────────────
.head-select { width: 140px; flex-shrink: 0; }
.head-input { flex: 1; min-width: 100px; }

// ─── Mock section ────────────────────────────────────
.mock-section {
  padding: 16px 24px 20px;
}

.mock-label {
  margin-top: 14px;
}

.mock-textarea {
  margin-top: 5px;
}

// ─── Save bar ────────────────────────────────────────
.save-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
}

.cancel-btn {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  padding: 9px 22px;
  border-radius: 7px;
  border: 1px solid $border;
  background: $surface;
  color: $text-secondary;
  text-decoration: none;
  font-family: $font-body;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    color: $accent;
    border-color: $accent;
  }
}

.save-btn {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  padding: 9px 26px;
  border-radius: 7px;
  border: none;
  background: $accent;
  color: #fff;
  cursor: pointer;
  font-family: $font-body;
  transition: all 0.15s ease;

  &:hover {
    background: $accent-hover;
  }

  &:active {
    transform: scale(0.98);
  }
}

// ─── Dialogs ─────────────────────────────────────────
:deep(.edit-dialog) {
  .el-dialog {
    border-radius: 12px;
    overflow: hidden;
  }

  .el-dialog__header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid $border-light;
  }

  .el-dialog__title {
    font-family: $font-display;
    font-size: 15px;
    font-weight: 600;
    color: $text;
  }

  .el-dialog__body {
    padding: 20px 24px 8px;
  }

  .el-dialog__footer {
    padding: 12px 24px 20px;
    border-top: 1px solid $border-light;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// ─── Responsive ─────────────────────────────────────
@media (max-width: 800px) {
  .api-update { }

  .form-row { flex-direction: column; }

  .form-col--group, .form-col--name, .form-col--status,
  .form-col--method, .form-col--http, .form-col--addr { width: 100%; }

  .panel-row { flex-direction: column; align-items: flex-start; }
}
</style>
