<template>
  <div class="task-report">
    <!-- Back -->
    <button class="back-btn" @click="$router.go(-1)"><i class="fa fa-arrow-left"></i>返回执行记录</button>

    <!-- Hero verdict card -->
    <div class="verdict-card">
      <div class="verdict-ring" :class="verdictClass">
        <svg viewBox="0 0 100 100" class="ring-svg">
          <circle cx="50" cy="50" r="42" fill="none" stroke="#f3f4f6" stroke-width="8" />
          <circle cx="50" cy="50" r="42" fill="none" :stroke="verdictColor" stroke-width="8"
            stroke-linecap="round" :stroke-dasharray="264" :stroke-dashoffset="264 - (264 * passRate / 100)"
            transform="rotate(-90 50 50)" class="ring-arc" />
        </svg>
        <span class="ring-pct">{{ Math.round(passRate) }}%</span>
      </div>
      <div class="verdict-body">
        <div class="verdict-header">
          <h1 class="verdict-task">{{ taskName }}</h1>
          <span class="verdict-badge" :class="verdictClass">{{ verdictLabel }}</span>
        </div>
        <div class="verdict-meta">
          <span><i class="fa fa-clock-o"></i>{{ reportTime }}</span>
          <span v-if="elapsedTime"><i class="fa fa-hourglass-half"></i>{{ elapsedTime }}s</span>
          <span v-if="host" :title="host"><i class="fa fa-link"></i>{{ host }}</span>
        </div>
        <div class="verdict-distro">
          <div class="distro-bar">
            <span class="distro-label">通过</span>
            <span class="distro-track"><span class="distro-fill fill--pass" :style="{ width: passPct + '%' }"></span></span>
            <span class="distro-num">{{ pass }}</span>
          </div>
          <div class="distro-bar">
            <span class="distro-label">失败</span>
            <span class="distro-track"><span class="distro-fill fill--fail" :style="{ width: failPct + '%' }"></span></span>
            <span class="distro-num">{{ fail }}</span>
          </div>
          <div class="distro-bar">
            <span class="distro-label">错误</span>
            <span class="distro-track"><span class="distro-fill fill--error" :style="{ width: errorPct + '%' }"></span></span>
            <span class="distro-num">{{ error }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Results table -->
    <div class="table-card">
      <h3 class="table-title">测试明细</h3>
      <el-table :data="tableData" v-loading="listLoading" :row-class-name="tableRowClass" class="data-table" empty-text="暂无测试结果">
        <el-table-column type="expand">
          <template slot-scope="props">
            <div class="expand-body">
              <div class="expand-grid">
                <div class="expand-item"><span class="expand-label">名称</span><span>{{ props.row.name }}</span></div>
                <div class="expand-item"><span class="expand-label">接口地址</span><span class="mono">{{ props.row.apiAddress }}</span></div>
                <div class="expand-item"><span class="expand-label">请求方式</span><span>{{ props.row.requestType }}</span></div>
                <div class="expand-item"><span class="expand-label">测试结果</span><span :class="resultClass(props.row.result)">{{ props.row.result }}</span></div>
              </div>
              <div class="expand-section" v-if="props.row.header"><span class="expand-label">请求头</span><pre class="expand-pre">{{ props.row.header }}</pre></div>
              <div class="expand-section" v-if="props.row.responseHeader"><span class="expand-label">返回头</span><pre class="expand-pre">{{ props.row.responseHeader }}</pre></div>
              <div class="expand-section" v-if="props.row.parameter"><span class="expand-label">请求参数</span><pre class="expand-pre">{{ props.row.parameter }}</pre></div>
              <div class="expand-section" v-if="props.row.responseData"><span class="expand-label">返回结果</span><pre class="expand-pre">{{ props.row.responseData }}</pre></div>
            </div>
          </template>
        </el-table-column>
        <el-table-column type="index" label="#" width="55" />
        <el-table-column prop="name" label="接口名称" min-width="160" sortable show-overflow-tooltip />
        <el-table-column prop="automationTestCase" label="用例名称" min-width="160" sortable show-overflow-tooltip />
        <el-table-column prop="apiAddress" label="请求地址" min-width="200" sortable show-overflow-tooltip />
        <el-table-column prop="examineType" label="校验方式" width="120" />
        <el-table-column label="结果" width="90">
          <template slot-scope="scope">
            <span class="result-badge" :class="resultBadgeClass(scope.row.result)">{{ scope.row.result || 'NotRun' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { getTestResultList } from '../../../api/api'

export default {
  data() {
    return {
      taskName: '', reportTime: '',
      tableData: [], listLoading: false,
      pass: 0, fail: 0, error: 0,
      elapsedTime: '', host: '',
    }
  },
  computed: {
    total() { return this.pass + this.fail + this.error },
    passRate() { return this.total ? (this.pass / this.total * 100) : 0 },
    passPct() { return this.total ? (this.pass / this.total * 100) : 0 },
    failPct() { return this.total ? (this.fail / this.total * 100) : 0 },
    errorPct() { return this.total ? (this.error / this.total * 100) : 0 },
    verdictClass() {
      if (!this.total) return 'verdict--none'
      if (this.passRate >= 90) return 'verdict--pass'
      if (this.passRate >= 50) return 'verdict--warn'
      return 'verdict--fail'
    },
    verdictColor() {
      if (!this.total) return '#d1d5db'
      if (this.passRate >= 90) return '#059669'
      if (this.passRate >= 50) return '#d97706'
      return '#dc2626'
    },
    verdictLabel() {
      if (!this.total) return '无数据'
      if (this.passRate >= 90) return '通过'
      if (this.passRate >= 50) return '部分通过'
      return '未通过'
    },
  },
  methods: {
    fetchReport() {
      this.taskName = this.$route.query.taskName || ''
      this.reportTime = this.$route.query.time || ''
      this.listLoading = true; let self = this
      getTestResultList({
        'Content-Type': 'application/json',
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }, {
        project_id: this.$route.params.project_id,
        time: this.reportTime,
        taskName: this.taskName,
      }).then((_data) => {
        let { msg, code, data } = _data; self.listLoading = false
        if (code == '999999') {
          self.pass = data.pass || 0; self.fail = data.fail || 0; self.error = data.error || 0
          self.elapsedTime = data.elapsedTime || ''; self.host = data.host || ''
          self.tableData = data.data || []
        } else { self.$message.error({ message: msg, center: true }) }
      }).catch(() => { self.listLoading = false; self.$message.error({ message: '获取报告失败', center: true }) })
    },
    tableRowClass({ row }) {
      if (row.result === 'ERROR' || row.result === 'FAIL') return 'row--fail'
      if (row.result === 'TimeOut') return 'row--timeout'
      return ''
    },
    resultClass(r) { return { PASS: 'clr--pass', FAIL: 'clr--fail', ERROR: 'clr--error', TimeOut: 'clr--timeout' }[r] || 'clr--none' },
    resultBadgeClass(r) { return { PASS: 'badge--pass', FAIL: 'badge--fail', ERROR: 'badge--error', TimeOut: 'badge--timeout' }[r] || 'badge--none' },
  },
  mounted() { this.fetchReport() },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $accent: #1d4ed8; $text: #111827; $text-secondary: #6b7280; $text-tertiary: #9ca3af; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04); $shadow-md: 0 4px 12px rgba(0,0,0,.06);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.task-report {
  padding: 24px 32px 44px; background: $bg; min-height: 100%;
  font-family: $font-body; color: $text;
  background-image:
    radial-gradient(ellipse 70% 50% at 30% 15%, rgba(29,78,216,.02) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 75% 55%, rgba(5,150,105,.015) 0%, transparent 60%);
}

.back-btn {
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 20px;
  font-family: $font-display; font-size: 13px; font-weight: 600; color: $text-secondary;
  background: none; border: none; cursor: pointer; padding: 0;
  &:hover { color: $accent; } i { font-size: 12px; }
}

// ─── Verdict card ──────────────────────────────────
.verdict-card {
  display: flex; align-items: center; gap: 28px;
  background: $surface; border: 1px solid $border; border-radius: 12px;
  padding: 24px 28px; margin-bottom: 18px; box-shadow: $shadow-sm;
}

.verdict-ring {
  width: 110px; height: 110px; flex-shrink: 0; position: relative;
  display: flex; align-items: center; justify-content: center;

  .ring-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
  .ring-arc { transition: stroke-dashoffset .8s ease; }
  .ring-pct { font-family: $font-display; font-size: 22px; font-weight: 700; color: $text; z-index: 1; }

  &.verdict--pass .ring-pct { color: #059669; }
  &.verdict--warn .ring-pct { color: #d97706; }
  &.verdict--fail .ring-pct { color: #dc2626; }
  &.verdict--none .ring-pct { color: $text-tertiary; }
}

.verdict-body { flex: 1; min-width: 0; }

.verdict-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.verdict-task { font-family: $font-display; font-size: 18px; font-weight: 700; color: $text; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.verdict-badge {
  display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 0.04em;
  padding: 3px 10px; border-radius: 4px; flex-shrink: 0;
  &.verdict--pass { background: #ecfdf5; color: #059669; }
  &.verdict--warn { background: #fffbeb; color: #b45309; }
  &.verdict--fail { background: #fef2f2; color: #dc2626; }
  &.verdict--none { background: #f9fafb; color: #9ca3af; }
}

.verdict-meta {
  display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 14px;
  font-size: 12px; color: $text-tertiary;
  i { margin-right: 4px; }
}

// ─── Distribution bars ─────────────────────────────
.verdict-distro { display: flex; flex-direction: column; gap: 6px; }

.distro-bar {
  display: flex; align-items: center; gap: 10px; font-size: 12px;
  .distro-label { width: 32px; flex-shrink: 0; color: $text-secondary; font-weight: 500; text-align: right; }
  .distro-track { flex: 1; height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
  .distro-fill { height: 100%; border-radius: 4px; transition: width .6s ease; }
  .fill--pass { background: linear-gradient(90deg, #34d399, #059669); }
  .fill--fail { background: linear-gradient(90deg, #f87171, #dc2626); }
  .fill--error { background: linear-gradient(90deg, #fbbf24, #d97706); }
  .distro-num { width: 32px; flex-shrink: 0; font-family: $font-display; font-weight: 600; color: $text; }
}

// ─── Table ─────────────────────────────────────────
.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }
.table-title { font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; padding: 16px 20px 0; margin: 0; }
.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }

.result-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 4px;
  &.badge--pass { background: #ecfdf5; color: #059669; } &.badge--fail { background: #fef2f2; color: #dc2626; }
  &.badge--error { background: #fff7ed; color: #d97706; } &.badge--timeout { background: #fffbeb; color: #b45309; }
  &.badge--none { background: #f9fafb; color: #9ca3af; }
}

.expand-body { padding: 14px 20px; }
.expand-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 24px; margin-bottom: 10px; }
.expand-item { display: flex; gap: 8px; font-size: 13px; }
.expand-label { color: $text-tertiary; flex-shrink: 0; }
.mono { font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; font-size: 12px; }
.expand-section { margin-top: 8px; .expand-label { display: block; font-size: 12px; margin-bottom: 3px; } }
.expand-pre { background: #f9fafb; border: 1px solid $border; border-radius: 5px; padding: 8px 12px; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-break: break-all; margin: 0; max-height: 180px; overflow-y: auto; font-family: 'SF Mono','Monaco','Menlo','Consolas',monospace; }

.clr--pass { color: #059669; font-weight: 600; } .clr--fail { color: #dc2626; font-weight: 600; }
.clr--error { color: #d97706; font-weight: 600; } .clr--timeout { color: #b45309; font-weight: 600; }
:deep(.row--fail) { background-color: #fef2f2 !important; }
:deep(.row--timeout) { background-color: #fffbeb !important; }
</style>
