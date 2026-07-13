<template>
  <div class="api-dynamic">
    <div class="dynamic-card">
      <div class="card-header">
        <div class="card-title">
          <i class="fa fa-history"></i>
          <span>操作历史</span>
        </div>
        <span class="card-count" v-if="total">共 {{ total }} 条记录</span>
      </div>
      <el-table :data="tableData" v-loading="listLoading" class="dynamic-table" empty-text="暂无操作记录">
        <el-table-column type="index" label="#" width="56" />
        <el-table-column prop="time" label="操作时间" min-width="170" sortable>
          <template slot-scope="scope">
            <span class="time-cell">{{ scope.row.time }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="操作人" min-width="130" sortable>
          <template slot-scope="scope">
            <div class="user-cell">
              <span class="user-avatar">{{ (scope.row.user || '?')[0] }}</span>
              <span>{{ scope.row.user }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="320" show-overflow-tooltip>
          <template slot-scope="scope">
            <span class="desc-cell">{{ scope.row.description || '—' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer" v-if="total > 20">
        <el-pagination
          small
          layout="prev, pager, next"
          @current-change="handleCurrentChange"
          :page-size="20"
          :page-count="Math.ceil(total / 20)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { test } from '../../../../api/api'
import $ from 'jquery'

export default {
  data() {
    return {
      tableData: [],
      total: 0,
      page: 1,
      listLoading: false,
    }
  },
  methods: {
    handleCurrentChange(val) {
      this.page = val
      this.getApiDynamic()
    },
    getApiDynamic() {
      this.listLoading = true
      let self = this
      $.ajax({
        type: 'get',
        url: test + '/api/api/operation_history',
        async: true,
        data: {
          project_id: this.$route.params.project_id,
          page: self.page,
          api_id: this.$route.params.api_id,
        },
        headers: {
          Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
        },
        timeout: 5000,
        success: function (data) {
          self.listLoading = false
          if (data.code === '999999') {
            self.total = data.data.total
            self.tableData = data.data.data
          } else {
            self.$message.error({ message: data.msg, center: true })
          }
        },
        error: function () {
          self.listLoading = false
          self.$message.error({ message: '获取历史记录失败', center: true })
        },
      })
    },
  },
  mounted() {
    this.getApiDynamic()
  },
}
</script>

<style lang="scss" scoped>
// ─── Tokens ──────────────────────────────────────────
$bg: #f7f8fa;
$surface: #fff;
$accent: #1d4ed8;
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

.api-dynamic {
  padding: 4px 0 24px;
  background: transparent;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
}

// ─── Card ────────────────────────────────────────────
.dynamic-card {
  background: $surface;
  border: 1px solid $border;
  border-radius: $radius;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fafbfc;
  border-bottom: 1px solid $border;
}

.card-title {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: $font-display;
  font-size: 14px;
  font-weight: 600;
  color: $text;

  i {
    font-size: 14px;
    color: $accent;
  }
}

.card-count {
  font-size: 12px;
  color: $text-tertiary;
}

// ─── Table ───────────────────────────────────────────
.dynamic-table {
  :deep(th) {
    background: #f9fafb;
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
    padding: 10px 0;
  }

  :deep(td) {
    font-size: 13px;
    padding: 10px 0;
  }

  :deep(.el-table__empty-text) {
    padding: 48px 0;
    color: $text-tertiary;
    font-size: 13px;
  }
}

.time-cell {
  font-family: $font-mono;
  font-size: 12px;
  color: $text-secondary;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: $accent;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  font-family: $font-display;
  flex-shrink: 0;
}

.desc-cell {
  color: $text;
}

// ─── Footer ──────────────────────────────────────────
.card-footer {
  display: flex;
  justify-content: flex-end;
  padding: 14px 20px;
  border-top: 1px solid $border-light;
  background: #fafbfc;
}

// ─── Responsive ──────────────────────────────────────
@media (max-width: 640px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
