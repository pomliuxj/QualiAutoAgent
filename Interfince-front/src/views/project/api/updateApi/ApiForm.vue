<template>
  <div class="api-detail">
    <!-- Top bar: back + actions -->
    <div class="top-bar">
      <router-link
        :to="{ name: '接口列表', params: { project_id: $route.params.project_id } }"
        class="back-link"
      >
        <i class="el-icon-d-arrow-left"></i>
        <span>接口列表</span>
      </router-link>
      <button class="del-btn" @click="handleDel" title="删除接口">
        <i class="fa fa-trash-o"></i>
        <span>删除</span>
      </button>
    </div>

    <!-- Tab navigation -->
    <nav class="tab-nav">
      <router-link
        v-for="tab in tabs"
        :key="tab.name"
        :to="{ name: tab.name, params: { project_id: $route.params.project_id, api_id: $route.params.api_id } }"
        class="tab-link"
        :class="{ 'tab-link--active': radio === tab.name }"
        @click.native="radio = tab.name"
      >
        <i :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </router-link>
    </nav>

    <!-- Content area -->
    <div class="content-area">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import { test } from '../../../../api/api'
import $ from 'jquery'

export default {
  name: 'api-form',
  data() {
    return {
      radio: '',
      tabs: [
        { name: '基础信息', label: '基础信息', icon: 'fa fa-info-circle' },
        { name: '测试', label: '测试', icon: 'fa fa-flask' },
        { name: '历史', label: '历史', icon: 'fa fa-history' },
        { name: '修改', label: '修改', icon: 'fa fa-edit' },
      ],
    }
  },
  methods: {
    handleDel() {
      this.$confirm('确认删除该接口吗？删除后不可恢复。', '删除确认', {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      })
        .then(() => {
          const self = this
          $.ajax({
            type: 'post',
            url: test + '/api/api/del_api',
            async: true,
            data: JSON.stringify({
              project_id: Number(this.$route.params.project_id),
              ids: [this.$route.params.api_id],
            }),
            headers: {
              'Content-Type': 'application/json',
              Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
            },
            timeout: 5000,
            success: function (data) {
              if (data.code === '999999') {
                self.$message({ message: '删除成功', center: true, type: 'success' })
                self.$router.push({ name: '接口列表', params: { project_id: self.$route.params.project_id } })
              } else {
                self.$message.error({ message: data.msg, center: true })
              }
            },
          })
        })
        .catch(() => {})
    },
  },
  mounted() {
    this.radio = this.$route.name
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
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
$shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
$radius: 8px;
$font-display: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

.api-detail {
  font-family: $font-body;
  color: $text;
}

// ─── Top bar ─────────────────────────────────────────
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
  text-decoration: none;
  padding: 8px 14px;
  border-radius: $radius;
  background: $surface;
  border: 1px solid $border;
  box-shadow: $shadow-sm;
  transition: all 0.15s ease;

  i {
    font-size: 13px;
  }

  &:hover {
    color: $accent;
    border-color: $accent;
    box-shadow: $shadow-md;
  }
}

.del-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: $radius;
  border: 1px solid $border;
  background: $surface;
  color: $text-tertiary;
  cursor: pointer;
  box-shadow: $shadow-sm;
  transition: all 0.15s ease;
  font-family: $font-body;

  i {
    font-size: 12px;
  }

  &:hover {
    color: #dc2626;
    border-color: #fecaca;
    background: #fef2f2;
  }
}

// ─── Tab navigation ──────────────────────────────────
.tab-nav {
  display: flex;
  gap: 4px;
  padding: 5px;
  background: $surface;
  border: 1px solid $border;
  border-radius: 10px;
  box-shadow: $shadow-sm;
  margin-bottom: 20px;
}

.tab-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 22px;
  font-size: 13px;
  font-weight: 500;
  font-family: $font-body;
  color: $text-secondary;
  text-decoration: none;
  border-radius: 7px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;

  i {
    font-size: 13px;
    color: $text-tertiary;
    transition: color 0.2s ease;
  }

  &:hover {
    color: $text;
    background: #f9fafb;

    i {
      color: $text-secondary;
    }
  }

  &--active {
    color: $accent;
    background: $accent-soft;
    font-weight: 600;

    i {
      color: $accent;
    }

    &:hover {
      color: $accent;
      background: $accent-soft;

      i {
        color: $accent;
      }
    }
  }
}

// ─── Content ─────────────────────────────────────────
.content-area {
  // Child pages handle their own background/padding
}

@media (max-width: 640px) {
  .tab-link {
    padding: 8px 14px;
    font-size: 12px;

    span {
      display: none;
    }

    i {
      font-size: 15px;
    }
  }
}
</style>
