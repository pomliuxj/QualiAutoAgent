<template>
  <div class="case-form">
    <div class="toolbar">
      <router-link :to="{ name: '用例接口列表', params: { project_id: $route.params.project_id, case_id: $route.params.case_id } }" class="tb-back"><i class="fa fa-arrow-left"></i> 返回列表</router-link>
      <div class="tb-right">
        <router-link :to="{ name: '用例接口列表', params: { project_id: $route.params.project_id, case_id: $route.params.case_id } }" class="tb-btn tb-btn--ghost">取消</router-link>
        <button class="tb-btn tb-btn--primary" @click="addApi">保存</button>
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

      <el-collapse-item title="测试结果校验" name="3" class="collapse-panel">
        <div class="check-section">
          <el-radio-group v-model="form.check" class="check-radios">
            <el-radio-button label="no_check">不校验</el-radio-button>
            <el-radio-button label="json">JSON校验</el-radio-button>
            <el-radio-button label="entirely_check">完全校验</el-radio-button>
            <el-radio-button label="Regular_check">正则校验</el-radio-button>
          </el-radio-group>
          <el-input v-if="form.check === 'Regular_check'" v-model="form.RegularParam" placeholder="绑定参数名" size="small" style="width:180px;margin-left:10px" />
        </div>
        <div v-show="showCheck" class="check-body">
          <el-select v-model="form.checkHttp" placeholder="HTTP状态" size="small"><el-option v-for="(item, i) in httpCode" :key="i" :label="item.label" :value="item.value" /></el-select>
          <el-input v-model.trim="form.checkData" type="textarea" :rows="6" placeholder="校验值" style="margin-top:10px" />
        </div>
        <div v-show="jsonCheck" class="check-body">
          <el-select v-model="form.checkHttp" placeholder="HTTP状态" size="small"><el-option v-for="(item, i) in httpCode" :key="i" :label="item.label" :value="item.value" /></el-select>
          <div class="panel-table" style="margin-top:10px">
            <div class="panel-row panel-row--param" v-for="(item, index) in form.jsonCheckData" :key="'j' + index">
              <div class="panel-cell panel-cell--name"><el-input v-model.trim="item.name" placeholder="参数名" size="small" /></div>
              <div class="panel-cell panel-cell--value"><el-input v-model.trim="item.checkRule" placeholder="取值" size="small" /></div>
              <div class="panel-cell panel-cell--type">
                <el-select v-model="item.checkType" placeholder="检验方式" size="small"><el-option v-for="(t, i) in jsonType" :key="i" :label="t.label" :value="t.value" /></el-select>
              </div>
              <div class="panel-cell panel-cell--value"><el-input v-model.trim="item.value" placeholder="校验值" size="small" /></div>
              <div class="panel-cell panel-cell--action"><button class="icon-btn icon-btn--del" @click="delJsonCheck(index)"><i class="fa fa-trash"></i></button></div>
              <div class="panel-cell panel-cell--add" v-if="index === form.jsonCheckData.length - 1"><button class="icon-btn icon-btn--add" @click="addJsonCheck"><i class="fa fa-plus"></i></button></div>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <el-dialog :visible.sync="searchApiVisible" :close-on-click-modal="false" width="700px" class="corr-dialog">
      <template slot="title"><span class="dialog-title-text">选择变量来源</span></template>
      <div class="corr-tabs">
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'api' }" @click="switchVarSource('api')">前置接口</button>
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'global' }" @click="switchVarSource('global')">全局变量</button>
        <button class="corr-tab" :class="{ 'corr-tab--active': varSource === 'db' }" @click="switchVarSource('db')">数据库查询</button>
      </div>

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
                  <template slot-scope="scope"><code class="corr-code">\${{ stepIndexMap[scope.row.automationCaseApi] || '?' }}.{{ scope.row.checkRule }}</code></template>
                </el-table-column>
              </el-table>
              <div v-if="currentRow && varSource === 'api'" class="corr-selected"><i class="fa fa-check-circle"></i> 已选：<strong>{{ currentRow.name }}</strong><span class="corr-selected-val">→ ${{ stepIndexMap[currentRow.automationCaseApi] || '?' }}.{{ currentRow.checkRule }}</span></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <div v-show="varSource === 'global'" class="corr-simple-list">
        <el-table :data="globalVars" v-loading="globalVarLoading" @current-change="onGlobalSelect" highlight-current-row max-height="340" class="corr-table" empty-text="暂无全局变量">
          <el-table-column prop="variablesName" label="变量名" min-width="160" show-overflow-tooltip />
          <el-table-column label="引用方式" min-width="200" show-overflow-tooltip>
            <template slot-scope="scope"><code class="corr-code">$var.{{ scope.row.variablesName }}</code></template>
          </el-table-column>
        </el-table>
        <div v-if="currentRow && varSource === 'global'" class="corr-selected"><i class="fa fa-check-circle"></i> 已选：<strong>{{ currentRow.variablesName || currentRow.name }}</strong><span class="corr-selected-val">→ $var.{{ currentRow.variablesName || currentRow.name }}</span></div>
      </div>

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
  </div>
</template>

<script>
import { test, staticdata, GetDataBase } from '../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      request: staticdata.request, Http: staticdata.Http, ParameterTyep: true, radio: 'form-data',
      header: staticdata.header, httpCode: staticdata.httpCode, jsonType: staticdata.jsonType,
      radioType: '', result: true, activeNames: ['1', '2', '3'], id: '',
      searchApiVisible: false, ApiList: [], ApiResponse: [], apiResponseLoading: false, saveCorrelation: false,
      activeApiIndex: -1, currentRow: null, varSource: 'api',
      globalVars: [], globalVarLoading: false, dbVarLoading: false, dataBaseList: [],
      showCheck: false, jsonCheck: false, sels: [], interrelateObjects: '', interrelateSection: 'param', stepIndexMap: {}, stepApiNames: {}, request3: true,
      form: { name: '', request4: 'POST', Http4: 'HTTP', addr: '', head: [{ name: '', value: '', interrelate: 0 }, { name: '', value: '', interrelate: 0 }], parameterRaw: '', parameter: [{ name: '', value: '', interrelate: 0 }, { name: '', value: '', interrelate: 0 }], parameterType: '', check: 'no_check', RegularParam: '', checkHttp: '', checkData: '', jsonCheckData: [{ name: '', value: '', checkType: '', checkRule: '' }] },
      FormRules: { name: [{ required: true, message: '请输入名称', trigger: 'blur' }], addr: [{ required: true, message: '请输入地址', trigger: 'blur' }] },
    }
  },
  methods: {
    checkRequest() { this.request3 = !(this.form.request4 === 'GET' || this.form.request4 === 'DELETE') },
    handleCurrentChange(val) { this.currentRow = val },
    selsChange(sels) { this.sels = sels },
    openVarPicker(index, row, section) {
      this.interrelateObjects = row
      this.interrelateSection = section
      this.varSource = 'api'; this.currentRow = null; this.activeApiIndex = -1
      let self = this
      $.ajax({
        type: 'get', url: test + '/api/automation/get_correlation_response', async: true,
        data: { project_id: this.$route.params.project_id, case_id: this.$route.params.case_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000,
        success: function (data) {
          if (data.code === '999999') {
            if (data.data.length) {
              self.ApiList = []; self.stepIndexMap = {}; self.stepApiNames = {}
              data.data.forEach((item, i) => {
                self.ApiList.push(item)
                self.stepIndexMap[item.id] = i + 1
                self.stepApiNames[item.id] = item.name
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
        const apiId = this.currentRow.automationCaseApi
        const stepIdx = this.stepIndexMap[apiId] || '?'
        refValue = '$' + stepIdx + '.' + (this.currentRow.checkRule || '')
      } else if (this.varSource === 'global') {
        refValue = this.currentRow.value
      } else if (this.varSource === 'db') {
        refValue = this.currentRow.value
      }
      this.interrelateObjects.value = refValue
      // 新统一 $ 语法不需要 interrelate 标志
      this.interrelateObjects.interrelate = 0
      this.$set(this.interrelateObjects, '_corrLabel', refValue)
      this.saveCorrelation = false; this.searchApiVisible = false
    },
    addApi() { this.$refs.form.validate((valid) => { if (valid) { let self = this; let formatRaw = false; this.$confirm('确认提交吗？', '提示', {}).then(() => { self.form.parameterType = self.radio; let _type = self.form.parameterType; let _parameter = {}; if (_type === 'form-data') { if (self.radioType === true) formatRaw = true; _parameter = self.form.parameter } else { _parameter = self.form.parameterRaw }; $.ajax({ type: 'post', url: test + '/api/automation/add_new_api', async: true, data: JSON.stringify({ project_id: Number(self.$route.params.project_id), automationTestCase_id: Number(self.$route.params.case_id), name: self.form.name, httpType: self.form.Http4, requestType: self.form.request4, apiAddress: self.form.addr, headDict: self.form.head, requestParameterType: _type, formatRaw, requestList: _parameter, examineType: self.form.check, RegularParam: self.form.RegularParam, httpCode: self.form.checkHttp, responseData: self.form.checkData.toString(), jsonCheckData: self.form.jsonCheckData }), headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, timeout: 5000, success: function (data) { if (data.code === '999999') { self.$router.push({ name: '用例接口列表', params: { project_id: self.$route.params.project_id, case_id: self.$route.params.case_id } }); self.$message({ message: '保存成功', center: true, type: 'success' }) } else { self.$message.error({ message: data.msg, center: true }) } } }) }) } }) },
    addHead() { this.form.head.push({ name: '', value: '', interrelate: 0 }) },
    delHead(index) { this.form.head.splice(index, 1); if (!this.form.head.length) this.form.head.push({ name: '', value: '', interrelate: 0 }) },
    addJsonCheck() { this.form.jsonCheckData.push({ name: '', value: '', checkType: '', checkRule: '' }) },
    delJsonCheck(index) { this.form.jsonCheckData.splice(index, 1); if (!this.form.jsonCheckData.length) this.form.jsonCheckData.push({ name: '', value: '', checkType: '', checkRule: '' }) },
    addParameter() { this.form.parameter.push({ name: '', value: '', interrelate: 0 }) },
    delParameter(index) { this.form.parameter.splice(index, 1); if (!this.form.parameter.length) this.form.parameter.push({ name: '', value: '', interrelate: 0 }) },
    changeParameterType() { this.ParameterTyep = this.radio === 'form-data' },
    getDatabase() { let self = this; GetDataBase({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, { page: 1 }).then(_data => { let { msg, code, data } = _data; if (code === '999999') self.dataBaseList = data.data; else self.$message.error({ message: msg, center: true }) }) },
    handleChange() {},
  },
  watch: { radio() { this.changeParameterType() }, 'form.check': { handler(v) { this.showCheck = !['no_check', 'json'].includes(v); this.jsonCheck = v === 'json' }, deep: true } },
  mounted() {},
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
.corr-code { font-family: 'Fira Code', 'Consolas', monospace; font-size: 11px; color: #7c3aed; background: #f5f3ff; padding: 1px 5px; border-radius: 3px; }
.param-type-bar { display: flex; align-items: center; gap: 20px; padding: 12px 20px; border-bottom: 1px solid #f3f4f6; }
.raw-input { padding: 16px 20px; }

.check-section { padding: 16px 24px; }
.check-radios { :deep(.el-radio-button__inner) { font-size: 12px; } }
.check-body { padding: 0 24px 20px; }

.corr-list { height: 360px; overflow: auto; border: 1px solid $border; border-radius: 6px; }

// ─── Step mapping bar ────────────────────────────
.step-map-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 4px 10px; padding: 8px 20px; background: #f0f9ff; border-bottom: 1px solid #bae6fd; font-size: 11px; }
.step-map-label { font-weight: 600; color: #0c4a6e; white-space: nowrap; }
.step-map-chip { display: inline-block; background: #dbeafe; color: #1e40af; padding: 1px 7px; border-radius: 3px; font-weight: 500; font-family: monospace; white-space: nowrap; }
.step-map-hint { color: #6b7280; margin-left: 4px; code { background: #e5e7eb; padding: 0 3px; border-radius: 2px; font-size: 10px; } }

// ─── Variable picker dialog ──────────────────────
.corr-dialog { :deep(.el-dialog__header) { padding: 16px 20px 0; } :deep(.el-dialog__body) { padding: 12px 20px; } }
.dialog-title-text { font-family: $font-display; font-size: 15px; font-weight: 700; color: $text; }
.dialog-footer-bar { display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; }
.corr-tabs { display: flex; gap: 0; border-bottom: 2px solid $border; margin-bottom: 14px; }
.corr-tab {
  padding: 8px 18px; font-size: 12px; font-weight: 500; color: $text-secondary; background: none; border: none; border-bottom: 2px solid transparent; margin-bottom: -2px; cursor: pointer; transition: all .15s;
  &:hover { color: $accent; }
  &--active { color: $accent; border-bottom-color: $accent; font-weight: 600; }
}
.corr-simple-list {
  :deep(.corr-table) { margin-top: 0; }
}
.corr-api-list { border: 1px solid $border; border-radius: 8px; overflow: hidden; }
.corr-api-title { font-size: 11px; font-weight: 600; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 14px 6px; }
.corr-api-item {
  display: block; width: 100%; padding: 8px 14px; font-size: 12px; color: $text-secondary; background: none; border: none; border-bottom: 1px solid #f3f4f6; cursor: pointer; text-align: left; transition: all .12s;
  &:last-child { border-bottom: none; }
  &:hover { background: #f9fafb; color: $accent; }
  &--active { background: $accent-soft; color: $accent; font-weight: 600; }
}
.corr-api-empty { padding: 24px 12px; text-align: center; font-size: 12px; color: $text-tertiary; }
.corr-field-list { border: 1px solid $border; border-radius: 8px; overflow: hidden; }
.corr-field-title { font-size: 11px; font-weight: 600; color: $text-tertiary; text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 14px 6px; }
.corr-table {
  :deep(.el-table__body tr.current-row > td) { background: $accent-soft !important; }
  :deep(.el-table__body tr) { cursor: pointer; }
}
.corr-selected { margin-top: 10px; padding: 8px 12px; background: #ecfdf5; border-radius: 6px; font-size: 12px; color: #059669;
  strong { color: $text; }
  .corr-selected-val { color: $text-tertiary; margin-left: 8px; font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 11px; }
}
</style>
