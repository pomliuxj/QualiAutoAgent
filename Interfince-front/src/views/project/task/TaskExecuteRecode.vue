<template>
  <div class="task-record">
    <button class="back-btn" @click="$router.push({ name: '定时任务', params: { project_id: $route.params.project_id } })">
      <i class="fa fa-arrow-left"></i> 返回定时任务
    </button>

    <!-- Filter toolbar -->
    <div class="toolbar-card">
      <div class="tb-row">
        <div class="tb-left">
          <el-input v-model.trim="filters.taskName" placeholder="搜索任务名称" size="small" class="tb-search" @keyup.enter.native="handleSearch" clearable />
          <el-select v-model="filters.result" placeholder="执行结果" size="small" class="tb-select" clearable @change="handleSearch">
            <el-option v-for="item in resultOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" class="tb-date" value-format="yyyy-MM-dd" @change="handleSearch" />
          <el-button type="primary" size="small" @click="handleSearch">查询</el-button>
          <el-button size="small" @click="handleReset">重置</el-button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <h3 class="table-title">执行记录</h3>
      <el-table :data="tableData" v-loading="listLoading" class="data-table">
        <el-table-column type="index" width="55" label="#" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" sortable show-overflow-tooltip>
          <template slot-scope="scope"><span class="task-name">{{ scope.row.taskName }}</span></template>
        </el-table-column>
        <el-table-column label="执行结果" width="100">
          <template slot-scope="scope">
            <span class="result-badge" :class="scope.row.taskResult ? 'result--pass' : 'result--fail'">
              {{ scope.row.taskResult ? '成功' : '失败' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="执行 ID" width="100" />
        <el-table-column prop="elapsedTime" label="耗时" width="100">
          <template slot-scope="scope"><span class="time-text">{{ scope.row.elapsedTime }}</span></template>
        </el-table-column>
        <el-table-column prop="startTime" label="执行时间" width="170" sortable show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" min-width="140" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="goReport(scope.row)">查看报告</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="tb-footer">
        <span class="tb-total">共 {{ total }} 条记录</span>
        <el-pagination v-if="total > 10" small layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="10" :page-count="Math.ceil(total / 10)" />
      </div>
    </div>
  </div>
</template>

<script>
import { TaskRecode } from '../../../api/api'

export default {
  data() {
    return {
      tableData: [], total: 0, page: 1, listLoading: false,
      filters: { taskName: '', result: '', dateRange: [] },
      resultOptions: [
        { value: '', label: '全部结果' },
        { value: '1', label: '成功' },
        { value: '0', label: '失败' },
      ],
    }
  },
  methods: {
    handleCurrentChange(val) { this.page = val; this.getTaskExecuteRecord() },
    handleSearch() { this.page = 1; this.getTaskExecuteRecord() },
    handleReset() {
      this.filters = { taskName: '', result: '', dateRange: [] }
      this.page = 1
      this.getTaskExecuteRecord()
    },
    goReport(row) {
      this.$router.push({
        name: '任务报告',
        params: { project_id: this.$route.params.project_id },
        query: { taskName: row.taskName, time: row.startTime },
      })
    },
    getTaskExecuteRecord() {
      let self = this
      self.listLoading = true
      let params = { taskName: this.$route.query.taskName, page: self.page }
      if (self.filters.taskName) params.searchName = self.filters.taskName
      if (self.filters.result !== '') params.taskResult = self.filters.result
      if (self.filters.dateRange && self.filters.dateRange.length === 2) {
        params.startTime = self.filters.dateRange[0]
        params.endTime = self.filters.dateRange[1]
      }
      TaskRecode({ Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }, params).then(_data => {
        self.listLoading = false
        if (_data.code == '999999') { self.tableData = _data.data.data; self.total = _data.data.total } else { self.$message.error({ message: _data.msg, center: true }) }
      })
    },
  },
  mounted() {
    if (this.$route.query.taskName) this.filters.taskName = this.$route.query.taskName
    this.getTaskExecuteRecord()
  },
}
</script>

<style lang="scss" scoped>
$bg: #f7f8fa; $surface: #fff; $text: #111827; $text-secondary: #6b7280; $border: #e5e7eb;
$shadow-sm: 0 1px 2px rgba(0,0,0,.04);
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.task-record { padding: 20px 28px 40px; background: $bg; min-height: 100%; font-family: $font-body; color: $text; }

.back-btn {
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 14px;
  font-family: $font-display; font-size: 13px; font-weight: 600; color: $text-secondary;
  background: none; border: none; cursor: pointer; padding: 0;
  &:hover { color: #1d4ed8; } i { font-size: 12px; }
}

// ─── Toolbar ────────────────────────────────────────
.toolbar-card { background: $surface; border: 1px solid $border; border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; box-shadow: $shadow-sm; .tb-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; } .tb-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; } .tb-search { width: 200px; } .tb-select { width: 120px; } .tb-date { width: 260px; } }

.table-card { background: $surface; border: 1px solid $border; border-radius: 10px; box-shadow: $shadow-sm; overflow: hidden; }

.table-title { font-family: $font-display; font-size: 13px; font-weight: 600; color: $text; padding: 16px 20px 0; margin: 0; }

.data-table { :deep(th) { background: #f9fafb; color: $text-secondary; font-size: 12px; font-weight: 600; } }
.task-name { font-weight: 500; color: $text; }

.result-badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 4px;
  &.result--pass { background: #ecfdf5; color: #059669; }
  &.result--fail { background: #fef2f2; color: #dc2626; }
}
.time-text { color: $text-secondary; }

.tb-footer { display: flex; align-items: center; justify-content: space-between; padding: 10px 18px; border-top: 1px solid #f3f4f6; }
.tb-total { font-size: 12px; color: $text-secondary; }
</style>
