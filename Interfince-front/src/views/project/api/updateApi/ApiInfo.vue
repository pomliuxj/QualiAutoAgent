<template>
  <div class="api-info">
    <!-- Hero card -->
    <div class="hero-card">
      <div class="hero-top">
        <div class="hero-main">
          <span class="method-badge" :class="methodClass">{{ requestType }}</span>
          <h2 class="api-name">{{ apiName }}</h2>
        </div>
        <div class="hero-meta">
          <span class="status-chip" :class="status ? 'status--on' : 'status--off'">
            <span class="status-chip-dot"></span>
            {{ status ? '已启用' : '已禁用' }}
          </span>
          <span class="update-time">{{ updateTime }}</span>
        </div>
      </div>
      <div class="hero-url">
        <i class="fa fa-link"></i>
        <code>{{ httpType }}://{{ addr }}</code>
      </div>
    </div>

    <!-- Collapse panels -->
    <el-collapse v-model="activeNames" class="info-collapse">
      <!-- Request headers -->
      <el-collapse-item name="1" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-arrow-up panel-title-icon"></i>
            <span>请求头部</span>
            <span class="panel-badge" v-if="head.length">{{ head.length }}</span>
          </div>
        </template>
        <el-table :data="head" v-loading="listLoadingHead" class="info-table" empty-text="暂无请求头部">
          <el-table-column type="index" label="#" width="56" />
          <el-table-column prop="name" label="标签" min-width="200">
            <template slot-scope="scope">
              <code class="field-code">{{ scope.row.name || '—' }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="内容" min-width="320" show-overflow-tooltip>
            <template slot-scope="scope">
              <span class="field-value">{{ scope.row.value || '—' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-collapse-item>

      <!-- Request parameters -->
      <el-collapse-item name="2" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-cube panel-title-icon"></i>
            <span>请求参数</span>
            <span class="panel-type-tag">{{ parameterType || 'form-data' }}</span>
          </div>
        </template>
        <!-- Raw mode -->
        <div v-if="parameterRaw && !ParameterTyep" class="code-block">
          <div class="code-block-header">
            <span class="code-block-lang">raw</span>
          </div>
          <pre class="code-block-content">{{ parameterRaw }}</pre>
        </div>
        <!-- Form mode -->
        <el-table v-show="ParameterTyep" :data="parameter" v-loading="listLoadingParameter" class="info-table" empty-text="暂无请求参数">
          <el-table-column type="index" label="#" width="56" />
          <el-table-column prop="name" label="参数名" min-width="150">
            <template slot-scope="scope">
              <code class="field-code">{{ scope.row.name || '—' }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="参数值" min-width="200" show-overflow-tooltip>
            <template slot-scope="scope">
              <span class="field-value">{{ scope.row.value || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="_type" label="类型" width="80">
            <template slot-scope="scope">
              <span class="type-tag">{{ scope.row._type || 'String' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="必填" width="70">
            <template slot-scope="scope">
              <span class="bool-tag" :class="scope.row.required ? 'bool--yes' : 'bool--no'">
                {{ scope.row.required ? '是' : '否' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="详情" width="70" align="center">
            <template slot-scope="scope">
              <button class="text-btn" @click="lookParameterInfo(scope.$index)">查看</button>
            </template>
          </el-table-column>
        </el-table>
        <!-- Empty when no raw and no form -->
        <div v-if="!parameterRaw && !parameter.length" class="empty-block">暂无请求参数</div>
      </el-collapse-item>

      <!-- Response parameters -->
      <el-collapse-item name="3" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-arrow-down panel-title-icon"></i>
            <span>返回参数</span>
            <span class="panel-badge" v-if="response.length">{{ response.length }}</span>
          </div>
        </template>
        <el-table :data="response" v-loading="listLoadingResponse" class="info-table" empty-text="暂无返回参数">
          <el-table-column type="index" label="#" width="56" />
          <el-table-column prop="tier" label="层级" width="130">
            <template slot-scope="scope">
              <span class="tier-path" v-if="scope.row.tier">{{ scope.row.tier }}</span>
              <span class="tier-path tier-path--root" v-else>根层级</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="参数名" min-width="130">
            <template slot-scope="scope">
              <code class="field-code">{{ scope.row.name || '—' }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="参数值" min-width="170" show-overflow-tooltip>
            <template slot-scope="scope">
              <span class="field-value">{{ scope.row.value || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="_type" label="类型" width="80">
            <template slot-scope="scope">
              <span class="type-tag">{{ scope.row._type || 'String' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="必含" width="70">
            <template slot-scope="scope">
              <span class="bool-tag" :class="scope.row.required ? 'bool--yes' : 'bool--no'">
                {{ scope.row.required ? '是' : '否' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="详情" width="70" align="center">
            <template slot-scope="scope">
              <button class="text-btn" @click="lookResponseInfo(scope.$index)">查看</button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="!response.length" class="empty-block">暂无返回参数</div>
      </el-collapse-item>

      <!-- Mock -->
      <el-collapse-item name="4" class="collapse-panel">
        <template slot="title">
          <div class="panel-title">
            <i class="fa fa-code panel-title-icon"></i>
            <span>普通 Mock</span>
            <span class="panel-type-tag" v-if="mockCode">{{ mockCode }}</span>
          </div>
        </template>
        <div class="mock-section">
          <div class="mock-toolbar">
            <el-select v-model="mockCode" placeholder="HTTP 状态" size="small" class="mock-select">
              <el-option v-for="(item, index) in httpCode" :key="index" :label="item.label" :value="item.value" />
            </el-select>
            <button class="text-btn" @click="changFormat">格式转换</button>
          </div>
          <div v-if="mockData && resultShow" class="code-block">
            <pre class="code-block-content">{{ mockData }}</pre>
          </div>
          <div v-if="mockJsonData && !resultShow" class="code-block">
            <pre class="code-block-content">{{ mockJsonData }}</pre>
          </div>
          <div v-if="!mockData && !mockJsonData" class="empty-block">暂无 Mock 数据</div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <!-- Parameter detail dialog -->
    <el-dialog title="请求参数详情" :visible.sync="parameterInfoVisible" :close-on-click-modal="false" width="460px" class="info-dialog">
      <div class="detail-grid" v-if="parameterInfo">
        <div class="detail-item">
          <span class="detail-label">参数名</span>
          <code class="detail-value">{{ parameterInfo.name || '—' }}</code>
        </div>
        <div class="detail-item">
          <span class="detail-label">参数值</span>
          <span class="detail-value">{{ parameterInfo.value || '—' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">类型</span>
          <span class="type-tag">{{ parameterInfo._type || 'String' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">必填</span>
          <span class="bool-tag" :class="parameterInfo.required ? 'bool--yes' : 'bool--no'">
            {{ parameterInfo.required ? '是' : '否' }}
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">输入限制</span>
          <span class="detail-value">{{ parameterInfo.restrict || '无限制' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">说明</span>
          <span class="detail-value detail-value--desc">{{ parameterInfo.description || '无说明' }}</span>
        </div>
      </div>
    </el-dialog>

    <!-- Response detail dialog -->
    <el-dialog title="返回参数详情" :visible.sync="responseInfoVisible" :close-on-click-modal="false" width="460px" class="info-dialog">
      <div class="detail-grid" v-if="responseInfo">
        <div class="detail-item">
          <span class="detail-label">参数名</span>
          <code class="detail-value">{{ responseInfo.name || '—' }}</code>
        </div>
        <div class="detail-item">
          <span class="detail-label">层级</span>
          <span class="tier-path" :class="{ 'tier-path--root': !responseInfo.tier }">{{ responseInfo.tier || '根层级' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">参数值</span>
          <span class="detail-value">{{ responseInfo.value || '—' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">类型</span>
          <span class="type-tag">{{ responseInfo._type || 'String' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">必含</span>
          <span class="bool-tag" :class="responseInfo.required ? 'bool--yes' : 'bool--no'">
            {{ responseInfo.required ? '是' : '否' }}
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">说明</span>
          <span class="detail-value detail-value--desc">{{ responseInfo.description || '无说明' }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { test } from '../../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      activeNames: ['1', '2', '3', '4'],
      id: '',
      httpType: '',
      requestType: '',
      addr: '',
      apiName: '',
      updateTime: '',
      head: [],
      ParameterTyep: true,
      parameterType: '',
      parameter: [],
      parameterRaw: '',
      response: [],
      mockCode: '',
      mockData: '',
      mockJsonData: '',
      httpCode: [
        { value: '200', label: '200' },
        { value: '404', label: '404' },
        { value: '400', label: '400' },
        { value: '500', label: '500' },
        { value: '502', label: '502' },
        { value: '302', label: '302' },
      ],
      resultShow: true,
      status: true,
      listLoadingHead: false,
      listLoadingParameter: false,
      listLoadingResponse: false,
      parameterInfoVisible: false,
      parameterInfo: null,
      responseInfoVisible: false,
      responseInfo: null,
    }
  },
  computed: {
    methodClass() {
      const m = this.requestType
      if (m === 'GET') return 'method--get'
      if (m === 'POST') return 'method--post'
      if (m === 'PUT') return 'method--put'
      if (m === 'DELETE') return 'method--del'
      if (m === 'PATCH') return 'method--patch'
      return ''
    },
  },
  methods: {
    getApiInfo() {
      let self = this
      self.listLoadingHead = self.listLoadingParameter = self.listLoadingResponse = true
      $.ajax({
        type: 'get',
        url: test + '/api/api/api_info',
        async: true,
        data: { project_id: self.$route.params.project_id, api_id: self.$route.params.api_id },
        headers: { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) },
        timeout: 5000,
        success: function (data) {
          self.listLoadingHead = self.listLoadingParameter = self.listLoadingResponse = false
          if (data.code === '999999') {
            data = data.data
            self.id = data.id
            self.httpType = data.httpType
            self.requestType = data.requestType
            self.addr = data.apiAddress
            self.apiName = data.name
            self.updateTime = data.lastUpdateTime
            self.status = data.status
            self.head = data.headers || []
            self.parameterType = data.requestParameterType
            self.parameter = data.requestParameter || []
            try { self.parameterRaw = data.requestParameterRaw.data } catch (e) {}
            self.response = data.response || []
            self.mockCode = data.mockCode
            self.mockData = data.data
            if (data.data) {
              try { self.mockJsonData = JSON.parse(data.data) } catch (e) {}
            }
            self.parameterTypeChange()
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
      })
    },
    changFormat() {
      let demo = document.getElementsByTagName('pre')[0]
      if (demo) hljs.highlightBlock(demo)
      this.resultShow = !this.resultShow
    },
    lookParameterInfo(index) {
      this.parameterInfoVisible = true
      this.parameterInfo = this.parameter[index]
    },
    lookResponseInfo(index) {
      this.responseInfoVisible = true
      this.responseInfo = this.response[index]
    },
    parameterTypeChange() {
      this.ParameterTyep = this.parameterType === 'form-data'
    },
  },
  watch: {
    parameterType() {
      this.parameterTypeChange()
    },
  },
  mounted() {
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
$accent-soft-hover: #dbe4ff;
$text: #111827;
$text-secondary: #6b7280;
$text-tertiary: #9ca3af;
$border: #e5e7eb;
$border-light: #f3f4f6;
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
$shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
$radius: 8px;
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-mono: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', 'JetBrains Mono', monospace;

.api-info {
  padding: 4px 0 24px;
  background: transparent;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
}

// ─── Hero card ───────────────────────────────────────
.hero-card {
  background: $surface;
  border: 1px solid $border;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 16px;
  box-shadow: $shadow-sm;
}

.hero-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.hero-main {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.method-badge {
  display: inline-block;
  font-family: $font-display;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 6px 16px;
  border-radius: 6px;
  color: #fff;
  flex-shrink: 0;

  &.method--get { background: #059669; }
  &.method--post { background: #1d4ed8; }
  &.method--put { background: #d97706; }
  &.method--del { background: #dc2626; }
  &.method--patch { background: #7c3aed; }
}

.api-name {
  font-family: $font-display;
  font-size: 20px;
  font-weight: 700;
  color: $text;
  margin: 0;
  line-height: 1.3;
  word-break: break-word;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  white-space: nowrap;

  &.status--on {
    background: #ecfdf5;
    color: #059669;
  }

  &.status--off {
    background: #f9fafb;
    color: #9ca3af;
  }
}

.status-chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;

  .status--on & {
    background: #059669;
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
  }

  .status--off & {
    background: #d1d5db;
  }
}

.update-time {
  font-size: 12px;
  color: $text-tertiary;
}

.hero-url {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #f9fafb;
  border-radius: $radius;
  border: 1px solid $border-light;

  i {
    font-size: 12px;
    color: $text-tertiary;
    flex-shrink: 0;
  }

  code {
    font-family: $font-mono;
    font-size: 14px;
    color: $text;
    word-break: break-all;
  }
}

// ─── Collapse ────────────────────────────────────────
.info-collapse {
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

.panel-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 600;
  color: $accent;
  background: $accent-soft;
  border-radius: 10px;
}

.panel-type-tag {
  font-size: 11px;
  font-weight: 500;
  color: $text-tertiary;
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 4px;
  font-family: $font-mono;
}

// ─── Table ───────────────────────────────────────────
.info-table {
  :deep(th) {
    background: #f9fafb;
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
    padding: 10px 0;
  }

  :deep(td) {
    padding: 10px 0;
  }
}

.field-code {
  font-family: $font-mono;
  font-size: 12px;
  color: $accent;
  background: $accent-soft;
  padding: 2px 7px;
  border-radius: 4px;
}

.field-value {
  font-size: 13px;
  color: $text;
}

.type-tag {
  display: inline-block;
  font-family: $font-mono;
  font-size: 11px;
  font-weight: 500;
  color: $text-secondary;
  background: #f3f4f6;
  padding: 2px 7px;
  border-radius: 4px;
}

.bool-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;

  &.bool--yes {
    background: #ecfdf5;
    color: #059669;
  }

  &.bool--no {
    background: #f9fafb;
    color: $text-tertiary;
  }
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

// ─── Code block ──────────────────────────────────────
.code-block {
  margin: 0;

  &-header {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    background: #f9fafb;
    border-bottom: 1px solid $border-light;
  }

  &-lang {
    font-family: $font-mono;
    font-size: 11px;
    font-weight: 600;
    color: $text-tertiary;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  &-content {
    margin: 0;
    padding: 16px 20px;
    font-family: $font-mono;
    font-size: 12px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 360px;
    overflow-y: auto;
    color: $text;
    background: $surface;
    border: none;
  }
}

// ─── Empty ───────────────────────────────────────────
.empty-block {
  padding: 48px 20px;
  text-align: center;
  color: $text-tertiary;
  font-size: 13px;
  background: #fafbfc;
}

// ─── Mock section ────────────────────────────────────
.mock-section {
  padding: 0;
}

.mock-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  border-bottom: 1px solid $border-light;
}

.mock-select {
  width: 140px;
}

// ─── Detail dialog ───────────────────────────────────
.detail-grid {
  font-size: 13px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid $border-light;

  &:last-child {
    border-bottom: none;
  }
}

.detail-label {
  width: 80px;
  flex-shrink: 0;
  color: $text-tertiary;
  font-weight: 500;
  font-size: 12px;
  padding-top: 1px;
}

.detail-value {
  flex: 1;
  color: $text;
  line-height: 1.5;

  &--desc {
    color: $text-secondary;
  }
}

:deep(.info-dialog) {
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
    padding: 8px 24px 20px;
  }
}

// ─── Tier / 层级 ────────────────────────────────────
.tier-path {
  display: inline-block;
  font-family: $font-mono;
  font-size: 11px;
  font-weight: 500;
  color: #7c3aed;
  background: #f5f3ff;
  padding: 2px 8px;
  border-radius: 4px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &--root {
    color: $text-tertiary;
    background: #f3f4f6;
  }
}

// ─── Responsive ──────────────────────────────────────
@media (max-width: 640px) {
  .hero-top {
    flex-direction: column;
  }

  .hero-meta {
    align-self: flex-start;
  }

  .hero-url code {
    font-size: 13px;
  }
}
</style>
