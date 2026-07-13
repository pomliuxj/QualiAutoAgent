<template>
  <div class="report">
    <!-- Charts row -->
    <div class="charts-row">
      <div class="chart-card chart-card--main">
        <h3 class="chart-title">近十次测试结果</h3>
        <div id="reportBarChart" class="chart-box"></div>
      </div>
      <div class="chart-card chart-card--side">
        <h3 class="chart-title">本次测试分布</h3>
        <div id="reportPieChart" class="chart-box"></div>
      </div>
    </div>

    <p class="chart-note">只保留最近十次测试记录</p>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <span class="filter-label">测试记录</span>
        <el-select
          v-model="time"
          placeholder="选择测试时间"
          size="small"
          @change="changeHost()"
        >
          <el-option
            v-for="item in options"
            :key="item.id"
            :label="item.startTime"
            :value="[item.startTime, item.taskName]"
          />
        </el-select>
      </div>
      <div class="filter-info">
        <span class="info-chip">
          <i class="fa fa-clock-o"></i>
          {{ elapsedTime }}s
        </span>
        <span class="info-chip" :title="host">
          <i class="fa fa-link"></i>
          {{ host }}
        </span>
        <span class="info-chip" v-if="time[1]">
          <i class="fa fa-tasks"></i>
          {{ time[1] }}
        </span>
      </div>
    </div>

    <!-- Results table -->
    <div class="table-section">
      <el-table
        :data="tableData"
        v-loading="listLoading"
        :row-class-name="tableRowClass"
        class="result-table"
      >
        <el-table-column type="expand">
          <template slot-scope="props">
            <div class="expand-body">
              <div class="expand-grid">
                <div class="expand-item">
                  <span class="expand-label">名称</span>
                  <span class="expand-value">{{ props.row.name }}</span>
                </div>
                <div class="expand-item">
                  <span class="expand-label">接口地址</span>
                  <span class="expand-value mono">{{ props.row.apiAddress }}</span>
                </div>
                <div class="expand-item">
                  <span class="expand-label">请求方式</span>
                  <span class="expand-value">{{ props.row.requestType }}</span>
                </div>
                <div class="expand-item">
                  <span class="expand-label">测试结果</span>
                  <span class="expand-value" :class="resultClass(props.row.result)">{{ props.row.result }}</span>
                </div>
              </div>
              <div class="expand-section" v-if="props.row.header">
                <span class="expand-label">请求头</span>
                <pre class="expand-pre">{{ props.row.header }}</pre>
              </div>
              <div class="expand-section" v-if="props.row.responseHeader">
                <span class="expand-label">返回头</span>
                <pre class="expand-pre">{{ props.row.responseHeader }}</pre>
              </div>
              <div class="expand-section" v-if="props.row.parameter">
                <span class="expand-label">请求参数</span>
                <pre class="expand-pre">{{ props.row.parameter }}</pre>
              </div>
              <div class="expand-section" v-if="props.row.responseData">
                <span class="expand-label">返回结果</span>
                <pre class="expand-pre">{{ props.row.responseData }}</pre>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="接口名称" min-width="140" sortable show-overflow-tooltip />
        <el-table-column prop="automationTestCase" label="用例名称" min-width="140" sortable show-overflow-tooltip />
        <el-table-column prop="apiAddress" label="请求地址" min-width="180" sortable show-overflow-tooltip />
        <el-table-column prop="examineType" label="校验方式" width="130" sortable>
          <template slot-scope="scope">
            <span class="examine-tag">{{ examineLabel(scope.row.examineType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="100" :filters="resultFilter" :filter-method="filterHandler">
          <template slot-scope="scope">
            <span class="result-badge" :class="resultClass(scope.row.result)">
              {{ scope.row.result || 'NotRun' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import echarts from 'echarts'
import { getTestResultList, getTestTenTime, getTestTenResult } from '../../api/api'

export default {
  data() {
    return {
      tableData: [],
      listLoading: false,
      resultFilter: [
        { text: 'ERROR', value: 'ERROR' },
        { text: 'FAIL', value: 'FAIL' },
        { text: 'NotRun', value: 'NotRun' },
        { text: 'PASS', value: 'PASS' },
      ],
      time: '',
      elapsedTime: '',
      host: '',
      options: [],
      pass: 0,
      fail: 0,
      error: 0,
      latelyTenPass: [],
      latelyTenFail: [],
      latelyTenError: [],
    }
  },
  mounted() {
    this.getTenTestTime()
    this.getLatelyTenTestResult()
  },
  methods: {
    getTestResult() {
      this.listLoading = true
      let self = this
      let params = {
        project_id: this.$route.params.project_id,
        time: this.time[0].toString(),
        taskName: this.time[1],
      }
      let headers = {
        'Content-Type': 'application/json',
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      getTestResultList(headers, params).then((_data) => {
        let { msg, code, data } = _data
        self.listLoading = false
        if (code == '999999') {
          self.pass = data.pass || 0
          self.fail = data.fail || 0
          self.error = data.error || 0
          self.tableData = data.data || []
          self.singleTestDraw()
        } else {
          self.$message.error({ message: msg, center: true })
        }
      }).catch(() => {
        self.listLoading = false
        self.$message.error({ message: '获取测试结果失败', center: true })
      })
    },

    drawLine() {
      let myChart = echarts.init(document.getElementById('reportBarChart'))
      let option = {
        title: { show: false },
        color: ['#059669', '#d97706', '#dc2626'],
        tooltip: {
          trigger: 'axis',
          backgroundColor: '#fff',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827', fontSize: 13 },
          axisPointer: { type: 'cross', crossStyle: { color: '#d1d5db' } },
        },
        legend: {
          bottom: 0,
          textStyle: { color: '#6b7280', fontSize: 12 },
          data: ['通过率', '失败率', '错误率'],
        },
        grid: { top: 16, right: 24, bottom: 40, left: 48 },
        xAxis: {
          type: 'category',
          data: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false },
          axisLabel: { color: '#9ca3af', fontSize: 11 },
        },
        yAxis: {
          type: 'value',
          name: '%',
          min: 0,
          max: 100,
          interval: 20,
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLabel: { color: '#9ca3af', fontSize: 11, formatter: '{value}' },
          nameTextStyle: { color: '#9ca3af', fontSize: 11 },
        },
        series: [
          { name: '通过率', type: 'bar', data: this.latelyTenPass, barWidth: 16, itemStyle: { borderRadius: [3, 3, 0, 0] } },
          { name: '失败率', type: 'bar', data: this.latelyTenFail, barWidth: 16, itemStyle: { borderRadius: [3, 3, 0, 0] } },
          { name: '错误率', type: 'line', data: this.latelyTenError, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 6, smooth: true },
        ],
      }
      myChart.setOption(option)
    },

    singleTestDraw() {
      let myChart = echarts.init(document.getElementById('reportPieChart'))
      let option = {
        title: { show: false },
        color: ['#dc2626', '#d97706', '#059669'],
        tooltip: {
          trigger: 'item',
          backgroundColor: '#fff',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827', fontSize: 13 },
          formatter: '{b}: {c} ({d}%)',
        },
        legend: { show: false },
        series: [
          {
            type: 'pie',
            radius: ['52%', '80%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 2,
            },
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}\n{d}%',
              color: '#6b7280',
              fontSize: 12,
            },
            emphasis: {
              label: { fontSize: 16, fontWeight: 'bold' },
              scaleSize: 6,
            },
            data: [
              { value: this.error || 0, name: 'ERROR' },
              { value: this.fail || 0, name: 'FAIL' },
              { value: this.pass || 0, name: 'PASS' },
            ],
          },
        ],
      }
      myChart.setOption(option)
    },

    tableRowClass({ row }) {
      if (row.result === 'ERROR' || row.result === 'FAIL') return 'row--fail'
      if (row.result === 'TimeOut') return 'row--timeout'
      return ''
    },

    resultClass(result) {
      if (result === 'PASS') return 'result--pass'
      if (result === 'FAIL') return 'result--fail'
      if (result === 'ERROR') return 'result--error'
      if (result === 'TimeOut') return 'result--timeout'
      return 'result--notrun'
    },

    examineLabel(type) {
      const map = {
        no_check: '不校验',
        only_check_status: '校验HTTP状态',
        json: 'JSON校验',
        entirely_check: '完全校验',
        Regular_check: '正则校验',
      }
      return map[type] || type
    },

    filterHandler(value, row) {
      return row.result === value
    },

    getTenTestTime() {
      let self = this
      let params = { project_id: this.$route.params.project_id }
      let headers = {
        'Content-Type': 'application/json',
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      getTestTenTime(headers, params).then((_data) => {
        let { msg, code, data } = _data
        if (code == '999999') {
          self.options = data
          if (data && data.length) {
            self.time = [data[0].startTime, data[0].taskName]
            self.elapsedTime = data[0].elapsedTime
            self.host = data[0].host
          }
        } else {
          self.$message.error({ message: msg, center: true })
        }
      }).catch(() => {
        self.$message.error({ message: '获取测试记录失败', center: true })
      })
    },

    changeHost() {
      for (let i = 0; i < this.options.length; i++) {
        if (this.options[i].startTime === this.time[0]) {
          this.host = this.options[i].host
          this.elapsedTime = this.options[i].elapsedTime
          break
        }
      }
    },

    getLatelyTenTestResult() {
      let self = this
      let params = { project_id: this.$route.params.project_id }
      let headers = {
        'Content-Type': 'application/json',
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      getTestTenResult(headers, params).then((_data) => {
        let { msg, code, data } = _data
        if (code == '999999') {
          self.latelyTenPass = []
          self.latelyTenFail = []
          self.latelyTenError = []
          data.forEach((item) => {
            self.latelyTenPass.push((item.pass * 100).toFixed(1))
            self.latelyTenFail.push((item.fail * 100).toFixed(1))
            self.latelyTenError.push((item.error * 100).toFixed(1))
          })
          self.drawLine()
        } else {
          self.$message.error({ message: msg, center: true })
        }
      }).catch(() => {
        self.$message.error({ message: '获取历史趋势失败', center: true })
      })
    },
  },
  watch: {
    time() {
      this.getTestResult()
      this.changeHost()
    },
  },
}
</script>

<style lang="scss" scoped>
// ─── Design tokens ──────────────────────────────────
$bg: #f7f8fa;
$surface: #ffffff;
$accent: #1d4ed8;
$text: #111827;
$text-secondary: #6b7280;
$text-tertiary: #9ca3af;
$border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
$shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.report {
  padding: 24px 32px 40px;
  background: $bg;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
}

// ─── Charts row ─────────────────────────────────────
.charts-row {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.chart-card {
  background: $surface;
  border: 1px solid $border;
  border-radius: 10px;
  box-shadow: $shadow-sm;
  padding: 18px 20px 14px;

  &--main { flex: 3; min-width: 0; }
  &--side { flex: 2; min-width: 0; }
}

.chart-title {
  font-family: $font-display;
  font-size: 13px;
  font-weight: 600;
  color: $text;
  margin: 0 0 8px;
}

.chart-box {
  width: 100%;
  height: 340px;
}

.chart-note {
  font-size: 11px;
  color: $text-tertiary;
  margin: 0 0 20px;
  padding-left: 4px;
}

// ─── Filter bar ─────────────────────────────────────
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: $surface;
  border: 1px solid $border;
  border-radius: 9px;
  padding: 14px 20px;
  margin-bottom: 16px;
  box-shadow: $shadow-sm;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-family: $font-display;
  font-size: 12px;
  font-weight: 600;
  color: $text-secondary;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.info-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: $text-secondary;

  i { font-size: 11px; color: $text-tertiary; }
}

// ─── Table section ──────────────────────────────────
.table-section {
  background: $surface;
  border: 1px solid $border;
  border-radius: 9px;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

// ─── Result badges ──────────────────────────────────
.result-badge {
  display: inline-block;
  font-family: $font-display;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 4px;
  letter-spacing: 0.03em;

  &.result--pass    { background: #ecfdf5; color: #059669; }
  &.result--fail    { background: #fff7ed; color: #d97706; }
  &.result--error   { background: #fef2f2; color: #dc2626; }
  &.result--timeout { background: #fffbeb; color: #b45309; }
  &.result--notrun  { background: #f9fafb; color: #9ca3af; }
}

// ─── Examine tag ────────────────────────────────────
.examine-tag {
  font-size: 12px;
  color: $text-secondary;
}

// ─── Expand body ────────────────────────────────────
.expand-body {
  padding: 16px 24px;
}

.expand-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 32px;
  margin-bottom: 12px;
}

.expand-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.expand-label {
  color: $text-tertiary;
  flex-shrink: 0;
  min-width: 60px;
}

.expand-value {
  color: $text;
  word-break: break-all;

  &.mono {
    font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
    font-size: 12px;
  }
}

.expand-section {
  margin-top: 10px;

  .expand-label {
    display: block;
    font-size: 12px;
    color: $text-tertiary;
    margin-bottom: 4px;
  }
}

.expand-pre {
  background: #f9fafb;
  border: 1px solid $border;
  border-radius: 5px;
  padding: 10px 14px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: $text;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

// ─── Table row accents ──────────────────────────────
:deep(.row--fail) {
  background-color: #fef2f2 !important;
}
:deep(.row--timeout) {
  background-color: #fffbeb !important;
}

// ─── Responsive ─────────────────────────────────────
@media (max-width: 960px) {
  .report { padding: 20px 16px 32px; }
  .charts-row { flex-direction: column; }
  .chart-box { height: 280px; }
  .expand-grid { grid-template-columns: 1fr; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
</style>
