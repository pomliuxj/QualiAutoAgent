<template>
  <div class="home-layout">
    <!-- Header ────────────────────────────────────── -->
    <header class="home-header">
      <div class="header-left">
        <button
          class="collapse-btn"
          @click.prevent="collapse"
          :title="collapsed ? '展开侧栏' : '收起侧栏'"
          :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
        >
          <span class="collapse-icon" :class="{ 'is-collapsed': collapsed }">
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>

        <router-link to="/projectList" class="brand-link">
          <span class="brand-mark">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <rect x="2" y="2" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9"/>
              <rect x="13" y="2" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.65"/>
              <rect x="2" y="13" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.5"/>
              <rect x="13" y="13" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.35"/>
            </svg>
          </span>
          <span v-show="!collapsed" class="brand-text">质量平台</span>
        </router-link>
      </div>

      <div class="header-right">
        <!-- Status dot — subtle system health indicator -->
        <el-tooltip content="系统运行正常" placement="bottom" effect="dark">
          <span class="status-dot" title="系统状态">
            <span class="status-dot__pulse"></span>
          </span>
        </el-tooltip>

        <el-badge is-dot class="notice-bell" title="通知">
          <i class="fa fa-bell"></i>
        </el-badge>

        <el-dropdown trigger="hover" class="user-dropdown">
          <span class="user-trigger">
            <span class="user-name">{{ sysUserName }}</span>
            <span class="user-avatar-circle">
              <span>{{ (sysUserName || '?')[0] }}</span>
            </span>
          </span>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item disabled>
              <div class="dropdown-card">
                <span class="dropdown-card-avatar">
                  <span>{{ (sysUserName || '?')[0] }}</span>
                </span>
                <div class="dropdown-card-info">
                  <strong>{{ sysUserName }}</strong>
                  <span>管理员</span>
                </div>
              </div>
            </el-dropdown-item>
            <el-dropdown-item divided @click.native="logout">
              <i class="fa fa-sign-out"></i> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </header>

    <!-- Body ──────────────────────────────────────── -->
    <div class="home-body">
      <!-- Sidebar -->
      <aside :class="collapsed ? 'sidebar sidebar--collapsed' : 'sidebar sidebar--expanded'">
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          @select="handleselect"
          unique-opened
          router
          :collapse="collapsed"
          background-color="#ffffff"
          text-color="#4B5563"
          active-text-color="#4F6EF7"
        >
          <template v-for="(item, index) in $router.options.routes" v-if="!item.hidden">
            <el-menu-item
              v-for="child in item.children"
              :index="child.path"
              :key="child.path"
              v-if="!child.hidden"
              class="sidebar-item"
            >
              <i :class="child.iconCls || 'el-icon-menu'"></i>
              <span slot="title">{{ child.name }}</span>
            </el-menu-item>
          </template>
        </el-menu>

        <!-- Collapsed-mode bottom hint -->
        <div v-show="collapsed" class="sidebar-collapsed-hint">
          <span class="hint-bar"></span>
        </div>
      </aside>

      <!-- Content -->
      <main class="content-area">
        <!-- Breadcrumb -->
        <div class="breadcrumb-bar">
          <div class="breadcrumb-left">
            <h1 class="page-title">{{ $route.name }}</h1>
          </div>
          <el-breadcrumb separator="" class="breadcrumb-path">
            <el-breadcrumb-item v-for="(item, i) in $route.matched" :key="item.path">
              <span v-if="i > 0" class="breadcrumb-sep">/</span>
              {{ item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <!-- Page -->
        <div class="page-content">
          <transition name="fade" mode="out-in">
            <router-view></router-view>
          </transition>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      sysName: '质量平台',
      collapsed: false,
      sysUserName: '',
      form: {
        name: '', region: '', date1: '', date2: '',
        delivery: false, type: [], resource: '', desc: '',
      },
    }
  },
  methods: {
    onSubmit() {},
    handleselect(a, b) {},
    logout() {
      const _this = this
      this.$confirm('确认退出吗?', '提示', {}).then(() => {
        localStorage.removeItem('token')
        _this.$router.push('/login')
      }).catch(() => {})
    },
    collapse() {
      this.collapsed = !this.collapsed
    },
  },
  mounted() {
    const user = localStorage.getItem('username')
    if (user) {
      const name = JSON.parse(user)
      this.sysUserName = name || ''
    }
  },
}
</script>

<style scoped lang="scss">
// ═══════════════════════════════════════════════════════
// Design: "Precision Console"
// A navigation shell for an automated testing platform.
// Deep navy header, crisp white sidebar, indigo accents.
// ═══════════════════════════════════════════════════════

$header-bg-start: #0B1121;
$header-bg-end: #111D35;
$accent: #4F6EF7;
$accent-glow: rgba(79, 110, 247, 0.35);
$accent-soft: rgba(79, 110, 247, 0.12);
$accent-wash: rgba(79, 110, 247, 0.12);
$text-primary: #111827;
$text-secondary: #4B5563;
$text-muted: #9CA3AF;
$border-subtle: #E5E7EB;
$page-bg: #F3F4F6;
$white: #FFFFFF;

// ─── Layout ─────────────────────────────────────────
.home-layout {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: $page-bg;
}

// ═══════════════════════════════════════════════════════
// HEADER
// ═══════════════════════════════════════════════════════
.home-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(
    135deg,
    $header-bg-start 0%,
    #0F1829 40%,
    $header-bg-end 100%
  );
  color: #fff;
  padding: 0 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 100;

  // Subtle bottom glow — feels like a precision instrument
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(79, 110, 247, 0.3) 20%,
      rgba(79, 110, 247, 0.15) 50%,
      rgba(79, 110, 247, 0.3) 80%,
      transparent 100%
    );
  }

  // Subtle ambient texture — barely visible noise
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
    pointer-events: none;
  }
}

// ─── Header left ────────────────────────────────────
.header-left {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;

  .collapse-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: rgba(255, 255, 255, 0.55);
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;

    &:hover {
      background: rgba(255, 255, 255, 0.12);
      color: rgba(255, 255, 255, 0.9);
    }

    &:active {
      background: rgba(255, 255, 255, 0.09);
      transform: scale(0.94);
    }
  }

  // Hamburger icon — three precise bars
  .collapse-icon {
    display: flex;
    flex-direction: column;
    gap: 4px;
    width: 16px;

    span {
      display: block;
      height: 1.5px;
      background: currentColor;
      border-radius: 1px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      transform-origin: center;

      &:nth-child(1) { width: 16px; }
      &:nth-child(2) { width: 11px; }
      &:nth-child(3) { width: 14px; }
    }

    &.is-collapsed span {
      &:nth-child(1) { width: 16px; }
      &:nth-child(2) { width: 14px; }
      &:nth-child(3) { width: 10px; }
    }
  }

  .brand-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: #fff;
    margin-left: 6px;
    gap: 0;
    position: relative;
  }

  .brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.9);
    transition: all 0.25s ease;
    flex-shrink: 0;

    svg {
      transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .brand-link:hover & svg {
      transform: scale(1.08);
    }
  }

  .brand-text {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.02em;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin-left: 2px;
    white-space: nowrap;
  }
}

// ─── Header right ───────────────────────────────────
.header-right {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;

  // Live status indicator — shows system is operational
  .status-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    cursor: pointer;
    margin-right: 10px;
    transition: background 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.09);
    }

    &__pulse {
      display: block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #0EAD69;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        inset: -3px;
        border-radius: 50%;
        background: transparent;
        border: 1.5px solid rgba(14, 173, 105, 0.35);
        animation: status-ripple 2.4s ease-out infinite;
      }
    }
  }

  .notice-bell {
    font-size: 17px;
    color: rgba(255, 255, 255, 0.55);
    cursor: pointer;
    margin-right: 18px;
    transition: all 0.2s ease;
    padding: 6px;
    border-radius: 8px;

    &:hover {
      color: rgba(255, 255, 255, 0.9);
      background: rgba(255, 255, 255, 0.09);
    }

    ::v-deep .el-badge__content.is-fixed.is-dot {
      border: 2px solid $header-bg-start;
      top: 8px;
      right: 6px;
    }
  }

  .user-trigger {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 5px 12px;
    border-radius: 10px;
    transition: background 0.2s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.12);
    }
  }

  .user-name {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.8);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    letter-spacing: 0.01em;
  }

  .user-avatar-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    flex-shrink: 0;
    transition: all 0.2s ease;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);

    .user-trigger:hover & {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
    }
  }
}

// ─── Dropdown card ──────────────────────────────────
.dropdown-card {
  display: flex;
  align-items: center;
  padding: 4px 0;

  .dropdown-card-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #EEF2FF;
    color: $accent;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 700;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin-right: 12px;
    flex-shrink: 0;
  }

  .dropdown-card-info {
    display: flex;
    flex-direction: column;

    strong {
      font-size: 14px;
      color: $text-primary;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-weight: 600;
    }

    span {
      font-size: 12px;
      color: #6B7280;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
  }
}

// ═══════════════════════════════════════════════════════
// BODY
// ═══════════════════════════════════════════════════════
.home-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

// ═══════════════════════════════════════════════════════
// SIDEBAR
// ═══════════════════════════════════════════════════════
.sidebar {
  background: $white;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  position: relative;

  // Subtle right edge
  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: 1px;
    background: $border-subtle;
    pointer-events: none;
  }

  &--expanded {
    width: 232px;
  }

  &--collapsed {
    width: 64px;
  }

  .sidebar-menu {
    border-right: none;
    padding: 10px 0;
    flex: 1;
  }
}

// Collapsed hint — subtle indicator at bottom
.sidebar-collapsed-hint {
  padding: 12px 0 16px;
  display: flex;
  justify-content: center;

  .hint-bar {
    width: 20px;
    height: 3px;
    border-radius: 2px;
    background: $border-subtle;
    transition: background 0.2s;

    &:hover {
      background: #D1D5DB;
    }
  }
}

// ═══════════════════════════════════════════════════════
// CONTENT AREA
// ═══════════════════════════════════════════════════════
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

// ─── Breadcrumb ─────────────────────────────────────
.breadcrumb-bar {
  background: $white;
  padding: 15px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid $border-subtle;
}

.breadcrumb-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: -0.01em;
}

.breadcrumb-path {
  font-size: 13px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 450;
  color: #6B7280;

  ::v-deep .el-breadcrumb__item:last-child .el-breadcrumb__inner {
    color: $text-secondary;
    font-weight: 500;
  }

  ::v-deep .el-breadcrumb__inner {
    color: #6B7280;
    font-weight: 450;
    transition: color 0.18s;

    &:hover {
      color: $accent;
    }
  }

  .breadcrumb-sep {
    margin: 0 6px;
    color: #D1D5DB;
    font-weight: 300;
  }
}

// ─── Page content ───────────────────────────────────
.page-content {
  padding: 20px 24px 24px;
}

// ─── Animations ─────────────────────────────────────
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter,
.fade-leave-active {
  opacity: 0;
}

@keyframes status-ripple {
  0% {
    transform: scale(1);
    opacity: 0.7;
  }
  60% {
    transform: scale(1.8);
    opacity: 0;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}
</style>

<!-- ═══════════════════════════════════════════════════════
Global (non-scoped) overrides for Element UI menu internals
═══════════════════════════════════════════════════════ -->
<style lang="scss">
$accent: #4F6EF7;
$accent-soft: rgba(79, 110, 247, 0.07);
$accent-wash: rgba(79, 110, 247, 0.11);
$accent-glow: rgba(79, 110, 247, 0.2);
$text-primary: #111827;
$text-secondary: #4B5563;
$text-muted: #9CA3AF;
$border-subtle: #E5E7EB;

// ─── Sidebar menu items ─────────────────────────────
.sidebar-menu {
  .sidebar-item {
    margin: 2px 8px !important;
    border-radius: 9px !important;
    height: 42px !important;
    line-height: 42px !important;
    font-size: 13.5px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    font-weight: 450;
    letter-spacing: -0.005em;
    transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: visible;
    color: $text-secondary !important;

    i {
      margin-right: 10px;
      font-size: 16px;
      color: #6B7280;
      transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    }

    &:hover {
      background: $accent-soft !important;
      color: $text-primary !important;

      i {
        color: $accent;
        transform: translateX(1px);
      }
    }

    // Active state — the signature "live cursor" indicator
    &.is-active {
      background: $accent-wash !important;
      color: $accent !important;
      font-weight: 600;

      i {
        color: $accent !important;
      }

      // Left accent bar with subtle glow
      &::before {
        content: '';
        position: absolute;
        left: -4px;
        top: 9px;
        bottom: 9px;
        width: 3px;
        background: $accent;
        border-radius: 0 2px 2px 0;
        box-shadow:
          0 0 6px $accent-glow,
          0 0 12px $accent-glow;
        animation: cursor-glow 2.8s ease-in-out infinite;
      }
    }
  }
}

// Collapsed mode — center icons perfectly
.el-menu--collapse .sidebar-item {
  i {
    margin-right: 0 !important;
  }

  &.is-active::before {
    left: 0;
    top: 10px;
    bottom: 10px;
  }
}

// ─── Breadcrumb separator override ──────────────────
.breadcrumb-path .el-breadcrumb__separator {
  display: none; // we use custom separators
}

// ─── Sidebar submenu ────────────────────────────────
.sidebar-menu .el-submenu__title {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
  font-weight: 500;
  font-size: 13px;
  letter-spacing: 0.02em;
  color: #6B7280;
  text-transform: uppercase;
  height: 36px !important;
  line-height: 36px !important;
  margin: 4px 12px 2px;

  i {
    color: #6B7280;
    font-size: 12px;
  }

  &:hover {
    color: $text-secondary;
  }
}

// ─── User dropdown menu ─────────────────────────────
.home-layout .user-dropdown .el-dropdown-menu {
  background: #ffffff;
  border-radius: 12px;
  padding: 6px;
  border: 1px solid #E5E7EB;
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.09),
    0 10px 15px -3px rgba(0, 0, 0, 0.09),
    0 20px 40px -8px rgba(0, 0, 0, 0.12);

  .el-dropdown-menu__item {
    border-radius: 8px;
    margin: 2px;
    padding: 9px 14px;
    font-size: 13.5px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-weight: 450;
    letter-spacing: 0.005em;
    transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    color: #374151;

    i {
      font-size: 15px;
      margin-right: 10px;
      color: #6B7280;
      transition: color 0.18s;
    }

    &:hover {
      background: $accent-soft;
      color: $accent;

      i { color: $accent; }
    }

    &.is-disabled {
      opacity: 1;
      cursor: default;
      &:hover {
        background: transparent;
        color: inherit;
      }
    }
  }
}

// ─── Active indicator glow animation ────────────────
@keyframes cursor-glow {
  0%, 100% {
    box-shadow:
      0 0 4px rgba(79, 110, 247, 0.15),
      0 0 8px rgba(79, 110, 247, 0.1);
  }
  50% {
    box-shadow:
      0 0 6px rgba(79, 110, 247, 0.3),
      0 0 14px rgba(79, 110, 247, 0.18);
  }
}

// ─── Reduced motion ─────────────────────────────────
@media (prefers-reduced-motion: reduce) {
  .sidebar-item.is-active::before {
    animation: none !important;
  }

  .status-dot__pulse::after {
    animation: none !important;
  }
}
</style>
