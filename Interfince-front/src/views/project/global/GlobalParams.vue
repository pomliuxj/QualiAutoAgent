<template>
  <div class="global-params">
    <!-- Left sidebar: variable list -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-title-row">
          <i class="fa fa-code sidebar-title-icon"></i>
          <h3 class="sidebar-title">全局变量</h3>
        </div>
        <span v-if="variablesData.length" class="sidebar-count">{{ variablesData.length }}</span>
      </div>

      <!-- Create new variable -->
      <div class="create-bar">
        <input
          v-model="variablesname"
          class="create-input"
          placeholder="新建变量名称"
          @keyup.enter="handleCreate"
        />
        <button
          class="create-btn"
          :disabled="!variablesname.trim()"
          @click="handleCreate"
          title="创建变量"
        >
          <i class="fa fa-plus"></i>
        </button>
      </div>

      <!-- Variable list -->
      <div class="var-list" v-if="variablesData && variablesData.length">
        <button
          v-for="(item, index) in variablesData"
          :key="item.id"
          class="var-item"
          :class="{ 'var-item--active': variablesname === item.variablesName }"
          @click="setSelectValue(item.variablesName)"
        >
          <span class="var-name">{{ item.variablesName }}</span>
          <span
            class="var-copy"
            @click.stop="copytext(item.variablesName)"
            title="复制引用"
          >
            <i class="fa fa-clipboard"></i>
          </span>
        </button>
      </div>
      <div v-else class="var-empty">
        <i class="fa fa-cube var-empty-icon"></i>
        <p class="var-empty-title">暂无变量</p>
        <p class="var-empty-hint">在上方输入名称，按回车创建第一个全局变量</p>
      </div>

      <!-- Pagination -->
      <div class="sidebar-footer" v-if="total > 10">
        <el-pagination
          small
          layout="prev, pager, next"
          @current-change="handleCurrentChange"
          :page-size="10"
          :page-count="Math.ceil(total / 10)"
        />
      </div>
    </aside>

    <!-- Right: editor + console -->
    <div class="workspace">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="toolbar-label">变量名</span>
          <span class="toolbar-var-name">{{ variablesname || '未选择' }}</span>
        </div>
        <div class="toolbar-actions">
          <button class="tb-btn tb-btn--secondary" @click="handleRunCode">
            <i class="fa fa-play"></i>
            <span>运行</span>
          </button>
          <button class="tb-btn tb-btn--primary" @click="handleConfirm">
            <i class="fa fa-check"></i>
            <span>保存</span>
          </button>
        </div>
      </div>

      <!-- Code editor -->
      <div class="editor-pane">
        <editor
          v-model="code"
          @init="editorInit"
          lang="python"
          theme="monokai"
          width="100%"
          :height="editorHeight"
          :options="{
            enableSnippets: true,
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
            fontSize: 14,
            showPrintMargin: false,
          }"
        />
      </div>

      <!-- Output console -->
      <div class="console-pane" :class="{ 'console-pane--open': consoleOpen }">
        <div class="console-header" @click="consoleOpen = !consoleOpen">
          <span class="console-title">
            <span class="console-dot" :class="{ 'has-output': resp.data }"></span>
            <i class="fa fa-terminal"></i>
            调试控制台
            <span v-if="resp.data" class="console-badge">输出</span>
          </span>
          <i
            class="fa console-toggle"
            :class="consoleOpen ? 'fa-chevron-down' : 'fa-chevron-up'"
          ></i>
        </div>
        <div class="console-body" v-show="consoleOpen">
          <editor
            v-model="resp.data"
            lang="text"
            theme="monokai"
            width="100%"
            :height="consoleEditorHeight"
            :options="{
              readOnly: true,
              fontSize: 13,
              showPrintMargin: false,
              highlightActiveLine: false,
              showGutter: false,
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  CreateVariables,
  GetVariables,
  RunVariables,
  UpdateVariables,
} from '../../../api/api'

export default {
  data() {
    return {
      editorHeight: 420,
      consoleEditorHeight: 180,
      total: 0,
      page: 1,
      variablesData: [],
      code: '# 在此编写 Python 代码',
      variablesname: '',
      resp: {
        data: '',
      },
      consoleOpen: true,
    }
  },
  methods: {
    handleRunCode() {
      if (!this.variablesname) {
        this.$message({
          message: '请先选择一个变量',
          center: true,
          type: 'warning',
        })
        return
      }
      this.consoleOpen = true
      this.resp.data = ''
      let headers = {
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      let params = {
        Code: this.code,
        variablesName: this.variablesname,
      }
      RunVariables(headers, params).then((resp) => {
        this.resp = resp.data
      }).catch(() => {
        this.$message({
          message: '运行失败，请检查网络',
          center: true,
          type: 'error',
        })
      })
    },

    handleConfirm() {
      if (!this.variablesname) {
        this.$message({
          message: '请先选择或创建一个变量',
          center: true,
          type: 'warning',
        })
        return
      }
      let headers = {
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      let params = {
        project_id: Number(this.$route.params.project_id),
        variablesName: this.variablesname,
        Code: this.code,
      }
      UpdateVariables(headers, params).then((resp) => {
        if (resp.code == '999999') {
          this.$message({
            message: resp.msg || '保存成功',
            center: true,
            type: 'success',
          })
          this.getVariablesList()
        } else {
          this.$message.error({
            message: resp.msg || '保存失败',
            center: true,
          })
        }
      }).catch(() => {
        this.$message({
          message: '保存失败，请检查网络',
          center: true,
          type: 'error',
        })
      })
    },

    copytext(text) {
      var input = document.createElement('input')
      input.value = '$' + text
      document.body.appendChild(input)
      input.select()
      document.execCommand('Copy')
      document.body.removeChild(input)
      this.$message({
        message: '$' + text + ' 已复制',
        type: 'success',
      })
    },

    editorInit() {
      require('brace/ext/language_tools')
      require('brace/mode/python')
      require('brace/theme/monokai')
      require('brace/snippets/python')
    },

    getVariablesList() {
      let headers = {
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      let params = {
        page_size: 10,
        page: this.page,
      }
      GetVariables(headers, params).then((res) => {
        if (res.data) {
          this.variablesData = res.data.data || res.data
          this.total = res.data.total || 0
          if (res.data.page) {
            this.page = res.data.page
          }
        }
      }).catch(() => {
        this.$message({
          message: '获取变量列表失败',
          center: true,
          type: 'error',
        })
      })
    },

    setSelectValue(name) {
      this.variablesname = name
      let headers = {
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      let params = {
        variablesName: this.variablesname,
      }
      GetVariables(headers, params).then((res) => {
        if (res.data && res.data.length) {
          this.code = res.data[0].Code
        } else if (res.data && res.data.data && res.data.data.length) {
          this.code = res.data.data[0].Code
        }
      }).catch(() => {
        this.$message({
          message: '获取变量内容失败',
          center: true,
          type: 'error',
        })
      })
    },

    handleCreate() {
      const name = this.variablesname.trim()
      if (!name) {
        this.$message({
          message: '请输入变量名称',
          center: true,
          type: 'warning',
        })
        return
      }
      let headers = {
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      let params = {
        project_id: Number(this.$route.params.project_id),
        variablesName: name,
        Code: this.code,
      }
      CreateVariables(headers, params).then((res) => {
        if (res.code == '999999') {
          this.$message({
            message: '变量创建成功',
            center: true,
            type: 'success',
          })
          this.page = 1
          this.variablesname = name
          this.getVariablesList()
        } else {
          this.$message({
            message: res.msg || '创建失败',
            center: true,
          })
        }
      }).catch(() => {
        this.$message({
          message: '请求失败，请检查网络',
          center: true,
          type: 'error',
        })
      })
    },

    handleCurrentChange(val) {
      this.page = val
      this.getVariablesList()
    },
  },

  components: {
    editor: require('vue2-ace-editor'),
  },

  mounted() {
    this.getVariablesList()
  },
}
</script>

<style lang="scss" scoped>
// ─── Design tokens ───────────────────────────────────
$bg: #f0f2f6;
$surface: #ffffff;
$accent: #4F6EF7;
$accent-hover: #3D5CE5;
$accent-soft: rgba(79, 110, 247, 0.06);
$accent-wash: rgba(79, 110, 247, 0.1);
$text: #1f2f3d;
$text-secondary: #606266;
$text-tertiary: #a8abb2;
$border: #e4e7ed;
$border-light: #f0f2f5;
$green: #0EAD69;
$green-soft: #ecfdf5;
$shadow-xs: 0 1px 2px rgba(0,0,0,.03);
$shadow-sm: 0 1px 3px rgba(0,0,0,.04);
$shadow-md: 0 4px 12px rgba(0,0,0,.05);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
$font-mono: 'SF Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;
$radius-sm: 6px;
$radius-md: 8px;
$radius-lg: 10px;
$ease: cubic-bezier(0.4, 0, 0.2, 1);

// ─── Layout ─────────────────────────────────────────
.global-params {
  display: flex;
  height: calc(100vh - 120px);
  background: $bg;
  font-family: $font-body;
  color: $text;
  min-height: 520px;
}

// ─── Sidebar ────────────────────────────────────────
.sidebar {
  width: 268px;
  min-width: 268px;
  background: $surface;
  border-right: 1px solid $border;
  box-shadow: 1px 0 6px rgba(0,0,0,.02);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid $border-light;
}

.sidebar-title-row {
  display: flex;
  align-items: center;
  gap: 9px;
}

.sidebar-title-icon {
  font-size: 16px;
  color: $accent;
}

.sidebar-title {
  font-family: $font-display;
  font-size: 15px;
  font-weight: 600;
  color: $text;
  margin: 0;
}

.sidebar-count {
  font-size: 11px;
  font-weight: 600;
  color: $accent;
  background: $accent-soft;
  padding: 2px 9px;
  border-radius: 12px;
  min-width: 24px;
  text-align: center;
}

// ─── Create bar ─────────────────────────────────────
.create-bar {
  display: flex;
  gap: 0;
  padding: 14px 18px;
}

.create-input {
  flex: 1;
  border: 1px solid $border;
  border-right: none;
  border-radius: $radius-sm 0 0 $radius-sm;
  padding: 8px 12px;
  font-family: $font-body;
  font-size: 13px;
  color: $text;
  outline: none;
  min-width: 0;
  transition: border-color 0.2s $ease, box-shadow 0.2s $ease;

  &::placeholder {
    color: $text-tertiary;
  }

  &:focus {
    border-color: $accent;
    box-shadow: -1px 0 0 $accent, 0 -1px 0 $accent, 0 1px 0 $accent;
  }
}

.create-btn {
  flex-shrink: 0;
  width: 38px;
  border: 1px solid $accent;
  border-radius: 0 $radius-sm $radius-sm 0;
  background: $accent;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s $ease, box-shadow 0.15s $ease;

  &:hover:not(:disabled) {
    background: $accent-hover;
    box-shadow: 0 2px 6px rgba(79, 110, 247, 0.25);
  }

  &:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }
}

// ─── Variable list ──────────────────────────────────
.var-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0;
}

.var-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: $text-secondary;
  font-family: $font-body;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: background 0.12s $ease, color 0.12s $ease;

  &:hover {
    background: $accent-soft;
    color: $accent;

    .var-copy {
      opacity: 1;
    }
  }

  &--active {
    background: $accent-soft;
    color: $accent;
    font-weight: 600;
    box-shadow: inset 3px 0 0 $accent;

    .var-copy {
      opacity: 1;
    }
  }
}

.var-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 8px;
  font-family: $font-mono;
  font-size: 12px;
}

.var-copy {
  opacity: 0;
  flex-shrink: 0;
  padding: 5px 7px;
  border-radius: 4px;
  font-size: 11px;
  color: $text-tertiary;
  transition: opacity 0.12s $ease, color 0.12s $ease, background 0.12s $ease;

  &:hover {
    color: $accent;
    background: $accent-wash;
  }
}

// ─── Empty state ────────────────────────────────────
.var-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.var-empty-icon {
  font-size: 32px;
  color: #dcdfe6;
  margin-bottom: 12px;
}

.var-empty-title {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: $text-secondary;
}

.var-empty-hint {
  margin: 0;
  font-size: 12px;
  color: $text-tertiary;
  max-width: 180px;
  line-height: 1.5;
}

// ─── Sidebar footer ─────────────────────────────────
.sidebar-footer {
  padding: 10px 18px;
  border-top: 1px solid $border-light;
  display: flex;
  justify-content: center;
}

// ─── Workspace ──────────────────────────────────────
.workspace {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: $surface;
}

// ─── Toolbar ────────────────────────────────────────
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: $surface;
  border-bottom: 1px solid $border-light;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.toolbar-label {
  font-size: 11px;
  font-weight: 600;
  color: $text-tertiary;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-family: $font-display;
  flex-shrink: 0;
}

.toolbar-var-name {
  font-family: $font-mono;
  font-size: 13px;
  font-weight: 500;
  color: $accent;
  background: $accent-soft;
  padding: 3px 10px;
  border-radius: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.tb-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: $font-body;
  font-size: 12px;
  font-weight: 500;
  padding: 7px 15px;
  border-radius: $radius-sm;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.15s $ease;

  i {
    font-size: 11px;
  }

  &--primary {
    background: $accent;
    color: #fff;
    border-color: $accent;

    &:hover {
      background: $accent-hover;
      box-shadow: 0 2px 8px rgba(79, 110, 247, 0.2);
    }
  }

  &--secondary {
    background: $surface;
    color: $text-secondary;
    border-color: $border;

    &:hover {
      color: $green;
      border-color: $green;
      background: $green-soft;
    }
  }
}

// ─── Editor pane ────────────────────────────────────
.editor-pane {
  flex: 1;
  overflow: hidden;
}

// ─── Console pane ───────────────────────────────────
.console-pane {
  flex-shrink: 0;
  border-top: 1px solid $border;
  transition: all 0.25s $ease;
}

.console-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 24px;
  background: #fafbfc;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s $ease;

  &:hover {
    background: #f5f6f8;
  }
}

.console-title {
  font-family: $font-display;
  font-size: 12px;
  font-weight: 600;
  color: $text-secondary;
  display: flex;
  align-items: center;
  gap: 8px;

  i {
    font-size: 12px;
    color: $text-tertiary;
  }
}

.console-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #dcdfe6;
  transition: background 0.3s;

  &.has-output {
    background: $green;
    box-shadow: 0 0 0 3px rgba(14, 173, 105, 0.15);
  }
}

.console-badge {
  font-size: 10px;
  font-weight: 600;
  color: $green;
  background: $green-soft;
  padding: 1px 7px;
  border-radius: 8px;
}

.console-toggle {
  font-size: 11px;
  color: $text-tertiary;
  transition: transform 0.2s $ease;
}

.console-body {
  background: #272822;
}

.console-body ::v-deep .ace_gutter {
  display: none;
}

// ─── Responsive ─────────────────────────────────────
@media (max-width: 860px) {
  .global-params {
    flex-direction: column;
    height: auto;
  }

  .sidebar {
    width: 100%;
    min-width: 0;
    max-height: 280px;
    border-right: none;
    border-bottom: 1px solid $border;
  }

  .workspace {
    min-height: 500px;
  }
}

// ─── Reduced motion ─────────────────────────────────
@media (prefers-reduced-motion: reduce) {
  .var-item,
  .tb-btn,
  .create-btn,
  .var-copy,
  .console-header {
    transition: none;
  }
}
</style>
