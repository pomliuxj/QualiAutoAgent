<template>
  <div class="test-api">
    <!-- Environment selector -->
    <div class="env-bar">
      <div class="env-label">
        <i class="fa fa-globe"></i>
        <span>测试环境</span>
      </div>
      <el-form :model="form" ref="form" :rules="formRules" class="env-form">
        <el-form-item prop="url" class="form-item--clean">
          <el-select v-model="form.url" placeholder="选择测试环境" size="small" class="env-select">
            <el-option v-for="(item, index) in Host" :key="index" :label="item.name" :value="item.host" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- Request URL bar -->
    <div class="request-card">
      <div class="request-main">
        <el-select v-model="form.request4" placeholder="Method" size="small" class="method-select" @change="checkRequest">
          <el-option v-for="(item, index) in request" :key="index" :label="item.label" :value="item.value" />
        </el-select>
        <el-select v-model="form.Http4" placeholder="HTTP" size="small" class="http-select">
          <el-option v-for="(item, index) in Http" :key="index" :label="item.label" :value="item.value" />
        </el-select>
        <el-form-item prop="addr" class="form-item--clean url-input">
          <el-input v-model.trim="form.addr" placeholder="请求地址，例如 /api/user" size="small" class="addr-input" />
        </el-form-item>
      </div>
      <button class="send-btn" :class="{ 'send-btn--loading': loadingSend }" @click="Test" :disabled="loadingSend">
        <i class="fa fa-send" v-if="!loadingSend"></i>
        <i class="el-icon-loading" v-else></i>
        <span>{{ loadingSend ? '发送中' : '发送' }}</span>
      </button>
    </div>

    <!-- Collapse panels -->
    <el-collapse v-model="activeNames" class="test-collapse">
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

      <!-- Parameters -->
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
            <div class="panel-cell panel-cell--action">
              <button class="icon-btn icon-btn--del" @click="delParameter(index)" title="删除"><i class="fa fa-trash"></i></button>
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
          <el-input type="textarea" :rows="6" placeholder="输入 raw 数据，例如 JSON" v-model.trim="form.parameterRaw" class="raw-textarea" />
        </div>
      </el-collapse-item>

      <!-- Response -->
      <el-collapse-item name="4" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-arrow-down panel-title-icon"></i>
            <span>响应结果</span>
            <span class="panel-status" v-if="form.statusCode" :class="statusCodeClass">
              {{ form.statusCode }}
            </span>
          </div>
        </template>
        <div class="resp-toolbar">
          <div class="resp-tabs">
            <button class="resp-tab" :class="{ 'resp-tab--active': resultShow }" @click="showBody">Body</button>
            <button class="resp-tab" :class="{ 'resp-tab--active': !resultShow }" @click="showHeader">Header</button>
          </div>
          <button class="text-btn" @click="neatenFormat">格式转换</button>
        </div>
        <div v-if="!form.resultData && !form.resultHead" class="empty-block">发送请求后查看响应</div>
        <div v-show="form.resultData && resultShow && !format" class="resp-body">{{ form.resultData }}</div>
        <div v-show="form.resultHead && !resultShow" class="resp-body">{{ form.resultHead }}</div>
        <div v-show="form.resultData && resultShow && format" class="resp-body">
          <pre>{{ form.resultData }}</pre>
        </div>
      </el-collapse-item>

      <!-- History -->
      <el-collapse-item name="5" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-history panel-title-icon"></i>
            <span>请求历史</span>
          </div>
        </template>
        <el-table :data="requestHistory" v-loading="listLoading" class="info-table" empty-text="暂无请求历史">
          <el-table-column prop="requestTime" label="操作时间" min-width="160" />
          <el-table-column prop="requestType" label="请求方式" width="90">
            <template slot-scope="scope">
              <span class="method-label" :class="'method-label--' + (scope.row.requestType || '').toLowerCase()">
                {{ scope.row.requestType }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="requestAddress" label="请求地址" min-width="280" show-overflow-tooltip>
            <template slot-scope="scope">
              <code class="addr-code">{{ scope.row.requestAddress }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="httpCode" label="状态" width="80" align="center">
            <template slot-scope="scope">
              <span class="http-code" :class="codeClass(scope.row.httpCode)">{{ scope.row.httpCode }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template slot-scope="scope">
              <button class="icon-btn icon-btn--del" @click="delHistory(scope.row)" title="删除"><i class="fa fa-trash"></i></button>
            </template>
          </el-table-column>
        </el-table>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import { test, staticdata, testApi } from '../../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      request: staticdata.request,
      Http: staticdata.Http,
      ParameterTyep: true,
      radio: 'form-data',
      loadingSend: false,
      header: staticdata.header,
      header4: '',
      radioType: '',
      result: true,
      activeNames: ['1', '2', '3', '4', '5'],
      id: '',
      Host: [],
      request3: true,
      form: {
        url: '',
        request4: 'POST',
        Http4: 'http',
        addr: '',
        head: [],
        parameterRaw: '',
        parameter: [],
        parameterType: '',
        statusCode: '',
        resultData: '',
        resultHead: '',
      },
      formRules: {
        url: [{ required: true, message: '请选择测试环境', trigger: 'blur' }],
        addr: [{ required: true, message: '请输入地址', trigger: 'blur' }],
      },
      requestHistory: [],
      listLoading: false,
      headers: '',
      parameters: '',
      resultShow: true,
      format: false,
    }
  },
  computed: {
    statusCodeClass() {
      const c = String(this.form.statusCode)
      if (c.startsWith('2')) return 'status--2xx'
      if (c.startsWith('3')) return 'status--3xx'
      if (c.startsWith('4')) return 'status--4xx'
      if (c.startsWith('5')) return 'status--5xx'
      return ''
    },
  },
  methods: {
    checkRequest() {
      this.request3 = !(this.form.request4 === 'GET' || this.form.request4 === 'DELETE')
    },
    isJsonString(str) {
      try { if (typeof JSON.parse(str) === 'object') return true } catch (e) {}
      return false
    },
    getApiInfo() {
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/api/api_info', async: true,
        data: { project_id: self.$route.params.project_id, api_id: self.$route.params.api_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => {
          if (data.code === '999999') {
            self.form.request4 = data.data.requestType
            self.form.Http4 = data.data.httpType.toLowerCase()
            self.form.addr = data.data.apiAddress
            self.form.head = data.data.headers && data.data.headers.length ? [...data.data.headers] : [{ name: '', value: '' }, { name: '', value: '' }]
            self.form.parameter = data.data.requestParameter && data.data.requestParameter.length ? [...data.data.requestParameter] : [{ name: '', value: '', required: true, restrict: '', description: '' }, { name: '', value: '', required: true, restrict: '', description: '' }]
            try { self.form.parameterRaw = data.data.requestParameterRaw.data } catch (e) {}
            self.form.parameterType = data.data.requestParameterType
            self.radio = data.data.requestParameterType
            self.toggleHeadSelection(self.form.head)
            self.toggleParameterSelection(self.form.parameter)
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
      })
    },
    getHistory() {
      let self = this; this.listLoading = true
      $.ajax({
        type: 'get', url: test + '/api/api/history_list', async: true,
        data: { project_id: this.$route.params.project_id, api_id: self.$route.params.api_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => {
          self.listLoading = false
          if (data.code === '999999') { self.requestHistory = data.data } else { self.$message.error({ message: data.msg, center: true }) }
        },
      })
    },
    AddHistroy(code) {
      let self = this
      $.ajax({
        type: 'POST', url: test + '/api/api/add_history', async: true,
        data: JSON.stringify({
          project_id: Number(this.$route.params.project_id),
          api_id: Number(self.$route.params.api_id),
          requestType: self.form.request4,
          requestAddress: self.form.Http4 + '://' + self.form.url + self.form.addr,
          httpCode: code,
        }),
        headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => { if (data.code === '999999') { self.getHistory() } else { self.$message.error({ message: data.msg, center: true }) } },
      })
    },
    delHistory(row) {
      let self = this
      $.ajax({
        type: 'POST', url: test + '/api/api/del_history', async: true,
        data: JSON.stringify({ project_id: Number(self.$route.params.project_id), api_id: Number(self.$route.params.api_id), id: Number(row.id) }),
        headers: { 'Content-Type': 'application/json', Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => {
          if (data.code === '999999') { self.getHistory(); self.$message.success({ message: '删除成功！', center: true }) } else { self.$message.error({ message: data.msg, center: true }) }
        },
      })
    },
    getHost() {
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/global/host_total', async: true,
        data: { project_id: this.$route.params.project_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: (data) => {
          if (data.code === '999999') { data.data.data.forEach((item) => { if (item.status) self.Host.push(item) }) } else { self.$message.error({ message: data.msg, center: true }) }
        },
      })
    },
    toggleHeadSelection(rows) {
      if (this.$refs.multipleHeadTable) rows.forEach(row => this.$refs.multipleHeadTable.toggleRowSelection(row, true))
    },
    toggleParameterSelection(rows) {
      if (this.$refs.multipleParameterTable) rows.forEach(row => this.$refs.multipleParameterTable.toggleRowSelection(row, true))
    },
    selsChangeHead(sels) { this.headers = sels },
    selsChangeParameter(sels) { this.parameters = sels },
    Test() {
      let host = this.form.addr
      if (host.indexOf('http://') === 0) this.form.addr = host.slice(7)
      if (host.indexOf('https://') === 0) this.form.addr = host.slice(8)
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.loadingSend = true
          let self = this
          let _parameter = {}
          let headers = {}
          self.form.statusCode = ''; self.form.resultData = ''; self.form.resultHead = ''
          for (let i = 0; i < self.form.head.length; i++) {
            var a = self.form.head[i].name; if (a) headers[a] = self.form.head[i].value
          }
          let url = self.form.Http4 + '://' + self.form.url + host
          let _type = self.radio
          if (_type === 'form-data') {
            for (let i = 0; i < self.parameters.length; i++) {
              var b = self.parameters[i].name; if (b) _parameter[b] = self.parameters[i].value
            }
            _parameter = JSON.stringify(_parameter)
          } else { _parameter = self.form.parameterRaw }
          if (self.form.Http4 === 'dubbo') url = self.form.url + '|' + host
          if (self.form.parameterRaw && _type === 'raw' && !self.isJsonString(self.form.parameterRaw)) {
            self.$message({ message: '源数据格式错误', center: true, type: 'error' }); self.loadingSend = false
            return
          }
          let header = { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
          let params = { type: self.form.request4, url: url, data: _parameter, headers: headers, data_type: _type }
          testApi(header, params).then((_data) => {
            let { msg, code, data } = _data; self.loadingSend = false
            if (code === '999999') {
              self.form.resultData = data.data
              self.form.statusCode = data.httpCode
              self.form.resultHead = data.requstHeader
              // Auto-add to history
              self.AddHistroy(data.httpCode)
            } else {
              self.$message.error({ message: msg, center: true })
            }
          })
        }
      })
    },
    codeClass(code) {
      const c = String(code)
      if (c.startsWith('2')) return 'code--2xx'
      if (c.startsWith('3')) return 'code--3xx'
      if (c.startsWith('4')) return 'code--4xx'
      if (c.startsWith('5')) return 'code--5xx'
      return ''
    },
    neatenFormat() {
      let demo = document.getElementsByTagName('pre')[0]
      if (demo) hljs.highlightBlock(demo)
      this.format = !this.format
    },
    addHead() {
      this.form.head.push({ name: '', value: '' })
      this.toggleHeadSelection([this.form.head[this.form.head.length - 1]])
    },
    delHead(index) {
      if (this.form.head.length !== 1) this.form.head.splice(index, 1)
    },
    addParameter() {
      this.form.parameter.push({ name: '', value: '', required: 'True', restrict: '', description: '' })
      this.toggleParameterSelection([this.form.parameter[this.form.parameter.length - 1]])
    },
    delParameter(index) {
      if (this.form.parameter.length !== 1) this.form.parameter.splice(index, 1)
    },
    changeParameterType() { this.ParameterTyep = this.radio === 'form-data' },
    showBody() { this.resultShow = true },
    showHeader() { this.resultShow = false },
  },
  watch: { radio() { this.changeParameterType() } },
  mounted() { this.getApiInfo(); this.getHost(); this.getHistory() },
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
$radius: 8px;
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-mono: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', 'JetBrains Mono', monospace;

.test-api {
  padding: 4px 0 24px;
  background: transparent;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
}

// ─── Environment bar ─────────────────────────────────
.env-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.env-label {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
  flex-shrink: 0;

  i {
    font-size: 13px;
    color: $text-tertiary;
  }
}

.env-form {
  display: inline-flex;
}

.env-select {
  width: 220px;
}

.form-item--clean { margin-bottom: 0; }

// ─── Request card ────────────────────────────────────
.request-card {
  display: flex;
  align-items: center;
  gap: 10px;
  background: $surface;
  border: 1px solid $border;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 16px;
  box-shadow: $shadow-sm;
  transition: border-color 0.15s ease;

  &:focus-within {
    border-color: $accent;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 0 0 3px rgba(29, 78, 216, 0.08);
  }
}

.request-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.method-select { width: 110px; flex-shrink: 0; }
.http-select { width: 100px; flex-shrink: 0; }
.url-input { flex: 1; min-width: 140px; }

:deep(.addr-input) {
  input {
    font-family: $font-mono;
    font-size: 13px;
  }
}

.send-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  flex-shrink: 0;
  font-family: $font-body;
  font-size: 13px;
  font-weight: 600;
  padding: 9px 24px;
  border-radius: 7px;
  border: none;
  background: $accent;
  color: #fff;
  cursor: pointer;
  transition: all 0.15s ease;

  i {
    font-size: 12px;
  }

  &:hover {
    background: $accent-hover;
  }

  &:active {
    transform: scale(0.98);
  }

  &--loading {
    opacity: 0.75;
    pointer-events: none;
  }
}

// ─── Collapse ────────────────────────────────────────
.test-collapse {
  border: none;

  :deep(.collapse-panel) {
    background: $surface;
    border: 1px solid $border;
    border-radius: 10px;
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

.panel-status {
  font-family: $font-mono;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;

  &.status--2xx { color: #059669; background: #ecfdf5; }
  &.status--3xx { color: #1d4ed8; background: #eff3ff; }
  &.status--4xx { color: #d97706; background: #fffbeb; }
  &.status--5xx { color: #dc2626; background: #fef2f2; }
}

// ─── Panel tables ────────────────────────────────────
.panel-table { padding: 4px 0; }

.panel-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-bottom: 1px solid #f3f4f6;

  &:last-child { border-bottom: none; }

  &--head {
    .panel-cell--name { display: flex; gap: 0; flex: 2; min-width: 200px; }
    .panel-cell--value { flex: 3; min-width: 160px; }
  }

  &--param {
    .panel-cell--name { flex: 2; min-width: 120px; }
    .panel-cell--value { flex: 2; min-width: 120px; }
  }
}

.panel-cell {
  &--action { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
  &--add { flex-shrink: 0; }
}

// ─── Icon buttons ────────────────────────────────────
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
  background: none;
  border: none;
  font-size: 12px;
  color: $accent;
  cursor: pointer;
  padding: 3px 6px;
  border-radius: 4px;
  font-family: $font-body;
  transition: all 0.12s ease;

  &:hover {
    background: $accent-soft;
    color: $accent-hover;
  }
}

.head-select { width: 140px; flex-shrink: 0; }
.head-input { flex: 1; min-width: 100px; }

// ─── Parameter bar ───────────────────────────────────
.param-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.param-checkbox {
  margin-left: 4px;
}

// ─── Raw input ───────────────────────────────────────
.raw-section {
  padding: 0;
}

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

    &:focus {
      border: none;
      box-shadow: none;
    }
  }
}

// ─── Response ────────────────────────────────────────
.resp-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  border-bottom: 1px solid $border-light;
}

.resp-tabs {
  display: flex;
  gap: 4px;
}

.resp-tab {
  padding: 6px 14px;
  border: 1px solid $border;
  border-radius: 5px;
  background: $surface;
  font-size: 12px;
  font-weight: 500;
  color: $text-secondary;
  cursor: pointer;
  font-family: $font-body;
  transition: all 0.12s ease;

  &--active {
    background: $accent-soft;
    color: $accent;
    border-color: $accent;
  }

  &:hover:not(&--active) {
    border-color: #d1d5db;
  }
}

.resp-body {
  padding: 16px 20px;
  font-family: $font-mono;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
  color: $text;

  pre {
    margin: 0;
  }
}

.empty-block {
  padding: 48px 20px;
  text-align: center;
  color: $text-tertiary;
  font-size: 13px;
}

// ─── History table ───────────────────────────────────
.info-table {
  :deep(th) {
    background: #f9fafb;
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
  }
}

.method-label {
  font-family: $font-mono;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;

  &--get { color: #059669; background: #ecfdf5; }
  &--post { color: #1d4ed8; background: #eff3ff; }
  &--put { color: #d97706; background: #fffbeb; }
  &--delete { color: #dc2626; background: #fef2f2; }
}

.addr-code {
  font-family: $font-mono;
  font-size: 12px;
  color: $text-secondary;
}

.http-code {
  font-family: $font-mono;
  font-size: 12px;
  font-weight: 600;

  &.code--2xx { color: #059669; }
  &.code--3xx { color: #1d4ed8; }
  &.code--4xx { color: #d97706; }
  &.code--5xx { color: #dc2626; }
}
</style>
