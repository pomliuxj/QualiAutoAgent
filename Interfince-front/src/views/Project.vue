<template>
	  <div class="project-layout">
	    <!-- Header -->
	    <header class="project-header">
	      <!-- Brand -->
	      <div class="header-brand">
	        <router-link to="/projectList" class="brand-link">
	          <span class="brand-mark">
	            <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
	              <rect x="2" y="2" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9"/>
	              <rect x="13" y="2" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.65"/>
	              <rect x="2" y="13" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.5"/>
	              <rect x="13" y="13" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.35"/>
	            </svg>
	          </span>
	          <span class="brand-text">质量平台</span>
	        </router-link>
	      </div>

	      <!-- Navigation -->
	      <nav class="header-nav">
	        <el-menu
	          :default-active="$route.path"
	          class="project-nav-menu"
	          mode="horizontal"
	          @select="handleselect"
	          background-color="transparent"
	          text-color="rgba(255,255,255,0.65)"
	          active-text-color="#ffffff"
	          unique-opened
	        >
	          <template v-for="item in menus">
	            <el-submenu :index="item.indexname" :key="item.indexname" class="nav-submenu">
	              <template slot="title">
	                <i :class="item.icon || 'el-icon-menu'"></i>
	                <span>{{ item.indexname }}</span>
	              </template>
	              <el-menu-item
	                v-for="child in item.children"
	                :key="child.path"
	                :index="child.path"
	                class="nav-dropdown-item"
	              >
	                <router-link
	                  :to="{ name: child.name, params: { project_id: project_id } }"
	                  class="nav-dropdown-link"
	                >
	                  <i :class="child.icon || 'el-icon-caret-right'"></i>
	                  <span class="nav-dropdown-text">{{ child.name }}</span>
	                </router-link>
	              </el-menu-item>
	            </el-submenu>
	          </template>
	        </el-menu>
	      </nav>

	      <!-- User -->
	      <div class="header-user">
	        <!-- System status -->
	        <el-tooltip content="系统运行正常" placement="bottom" effect="dark">
	          <span class="status-dot">
	            <span class="status-dot__pulse"></span>
	          </span>
	        </el-tooltip>

	        <el-dropdown trigger="hover" class="user-dropdown">
	          <span class="user-trigger">
	            <span class="user-name">{{ sysUserName }}</span>
	            <span class="user-avatar">
	              <img src="../assets/userphoto.jpg" alt="avatar" />
	            </span>
	          </span>
	          <el-dropdown-menu slot="dropdown">
	            <el-dropdown-item disabled>
	              <div class="dropdown-card">
	                <span class="dropdown-card-avatar">
	                  <img src="../assets/userphoto.jpg" alt="avatar" />
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

	    <!-- Content -->
	    <main class="project-content">
	      <transition name="fade" mode="out-in">
	        <router-view></router-view>
	      </transition>
	    </main>
	  </div>
	</template>

	<script>
	export default {
	  data() {
	    return {
	      project_id: '',
	      sysName: '质量平台',
	      collapsed: false,
	      sysUserName: '',
	      sysUserAvatar: '',
	      menus: [
	        {
	          indexname: '项目概览',
	          icon: 'el-icon-data-line',
	          children: [
	            { name: '项目概况', path: '/ProjectTitle/project=:project_id', icon: 'el-icon-s-home' },
	            { name: '项目动态', path: '/projectDynamic/project=:project_id', icon: 'el-icon-time' },
	          ],
	        },
	        {
	          indexname: '项目配置',
	          icon: 'el-icon-setting',
	          children: [
	            { name: 'Host配置', path: '/GlobalHost/project=:project_id', icon: 'el-icon-link' },
	            { name: '成员管理', path: '/projectMember/project=:project_id', icon: 'el-icon-user' },
	            { name: '数据源配置', path: '/GlobalDataBase/project=:project_id', icon: 'el-icon-coin' },
	            { name: '全局变量', path: '/GlobalParams/project=:project_id', icon: 'el-icon-s-operation' },
	          ],
	        },
	        {
	          indexname: '接口自动化',
	          icon: 'el-icon-connection',
	          children: [
	            { name: '接口列表', path: '/api/project=:project_id', icon: 'el-icon-document' },
	            { name: '用例列表', path: '/automationTest/project=:project_id', icon: 'el-icon-s-grid' },
	            { name: '自动化测试报告', path: '/projectReport/project=:project_id', icon: 'el-icon-data-analysis' },
	            { name: '定时任务', path: '/TaskInfo/project=:project_id', icon: 'el-icon-alarm-clock' },
	          ],
	        },
        {
          indexname: 'AI测试',
          icon: 'el-icon-cpu',
          children: [
            { name: 'AI生成用例', path: '/aiTestCase/project=:project_id', icon: 'el-icon-magic-stick' },
          ],
        },
	      ],
	    }
	  },
	  methods: {
	    handleselect(a, b) {},
	    logout() {
	      const _this = this
	      this.$confirm('确认退出吗?', '提示', {}).then(() => {
	        localStorage.removeItem('token')
	        _this.$router.push('/login')
	      }).catch(() => {})
	    },
	  },
	  mounted() {
	    const user = localStorage.getItem('username')
	    if (user) {
	      const name = JSON.parse(user)
	      this.sysUserName = name || ''
	    }
	    this.project_id = this.$route.params.project_id
	  },
	}
	</script>

	<style scoped lang="scss">
	// ═══════════════════════════════════════════════════════
	// Design: "Precision Console" — Project shell
	// Deep navy header with horizontal nav, matching Home.
	// ═══════════════════════════════════════════════════════

	$header-bg-start: #0B1121;
	$header-bg-end: #111D35;
	$accent: #4F6EF7;
	$page-bg: #F3F4F6;

	// ─── Layout ─────────────────────────────────────────
	.project-layout {
	  position: absolute;
	  top: 0;
	  bottom: 0;
	  width: 100%;
	  display: flex;
	  flex-direction: column;
	  background: $page-bg;
	}

	// ─── Header ─────────────────────────────────────────
	.project-header {
	  height: 56px;
	  display: flex;
	  align-items: center;
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

	  // Subtle bottom glow
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
	}

	// Brand
	.header-brand {
	  flex-shrink: 0;
	  margin-right: 12px;

	  .brand-link {
	    display: flex;
	    align-items: center;
	    text-decoration: none; white-space: nowrap;
	    color: #fff;
	    padding: 4px 0;
	    gap: 6px;
	  }

	  .brand-mark {
	    display: flex;
	    align-items: center;
	    color: rgba(255, 255, 255, 0.9);
	    flex-shrink: 0;
	  }

	  .brand-text {
	    font-size: 16px;
	    font-weight: 700;
	    letter-spacing: 0.02em;
	    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
	  }
	}

	// Navigation
	.header-nav {
	  flex: 1;
	  display: flex;
	  justify-content: center;
	  overflow: visible;
	}

	// User area
	.header-user {
	  flex-shrink: 0;
	  margin-left: 16px;
	  display: flex;
	  align-items: center;

	  // System status dot
	  .status-dot {
	    display: inline-flex;
	    align-items: center;
	    justify-content: center;
	    width: 28px;
	    height: 28px;
	    border-radius: 8px;
	    cursor: pointer;
	    margin-right: 8px;
	    transition: background 0.2s;

	    &:hover {
	      background: rgba(255, 255, 255, 0.06);
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
	        border: 1.5px solid rgba(14, 173, 105, 0.35);
	        animation: status-ripple 2.4s ease-out infinite;
	      }
	    }
	  }

	  .user-trigger {
	    display: flex;
	    align-items: center;
	    gap: 10px;
	    cursor: pointer;
	    padding: 5px 12px;
	    border-radius: 10px;
	    transition: background 0.2s;

	    &:hover {
	      background: rgba(255, 255, 255, 0.08);
	    }
	  }

	  .user-name {
	    font-size: 13px;
	    font-weight: 500;
	    color: rgba(255, 255, 255, 0.8);
	    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
	    letter-spacing: 0.01em;
	  }

	  .user-avatar {
	    width: 32px;
	    height: 32px;
	    border-radius: 50%;
	    overflow: visible;
	    flex-shrink: 0;
	    background: rgba(255, 255, 255, 0.12);
	    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.15);
	    transition: box-shadow 0.2s;

	    .user-trigger:hover & {
	      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
	    }

	    img {
	      width: 100%;
	      height: 100%;
	      object-fit: cover;
	    }
	  }
	}

	// Dropdown card
	.dropdown-card {
	  display: flex;
	  align-items: center;
	  padding: 4px 0;

	  .dropdown-card-avatar {
	    width: 44px;
	    height: 44px;
	    border-radius: 50%;
	    overflow: visible;
	    margin-right: 12px;
	    flex-shrink: 0;

	    img {
	      width: 100%;
	      height: 100%;
	      object-fit: cover;
	    }
	  }

	  .dropdown-card-info {
	    display: flex;
	    flex-direction: column;

	    strong {
	      font-size: 14px;
	      color: #111827;
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

	// ─── Content ────────────────────────────────────────
	.project-content {
	  flex: 1;
	  overflow-y: auto;
	  overflow-x: hidden;
	}

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

	<!-- Global (non-scoped) overrides for Element menu -->
	<style lang="scss">
	$accent: #4F6EF7;
	$accent-soft: rgba(79, 110, 247, 0.07);
	$accent-wash: rgba(79, 110, 247, 0.11);
	$text-primary: #111827;
	$text-secondary: #4B5563;
	$text-muted: #9CA3AF;

	// ─── Top nav menu ───────────────────────────────────
	.project-nav-menu {
	  border-bottom: none !important;
	  background: transparent !important;

	  // Top-level submenu trigger
	  .nav-submenu {
	    .el-submenu__title {
	      height: 56px !important;
	      line-height: 56px !important;
	      padding: 0 16px !important;
	      font-size: 13.5px;
	      font-weight: 500;
	      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
	      color: rgba(255, 255, 255, 0.65) !important;
	      border-bottom: none !important;
	      letter-spacing: 0.015em;
	      transition: all 0.22s ease;
	      position: relative;

	      i {
	        font-size: 15px;
	        color: rgba(255, 255, 255, 0.5);
	        margin-right: 7px;
	        transition: all 0.22s ease;
	      }

	      // Active indicator bar at bottom
	      &::after {
	        content: '';
	        position: absolute;
	        bottom: 0;
	        left: 50%;
	        transform: translateX(-50%) scaleX(0);
	        width: 55%;
	        height: 2.5px;
	        background: rgba(255, 255, 255, 0.9);
	        border-radius: 2px 2px 0 0;
	        transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
	      }

	      &:hover {
	        background: rgba(255, 255, 255, 0.06) !important;
	        color: rgba(255, 255, 255, 0.9) !important;

	        i {
	          color: rgba(255, 255, 255, 0.85) !important;
	        }
	      }
	    }

	    // Active state
	    &.is-active .el-submenu__title {
	      color: #fff !important;
	      background: rgba(255, 255, 255, 0.08) !important;

	      i {
	        color: rgba(255, 255, 255, 0.9) !important;
	      }

	      &::after {
	        transform: translateX(-50%) scaleX(1);
	      }
	    }

	    // Submenu arrow icon
	    .el-submenu__icon-arrow {
	      color: rgba(255, 255, 255, 0.4) !important;
	      font-size: 12px;
	      margin-top: -2px;
	    }
	  }

	  // ─── Dropdown popover ───────────────────────────
		.el-menu--vertical {
		  background: #ffffff !important;
		    border-radius: 12px;
	    box-shadow:
	      0 4px 6px -1px rgba(0, 0, 0, 0.09),
	      0 10px 15px -3px rgba(0, 0, 0, 0.09),
	      0 20px 40px -8px rgba(0, 0, 0, 0.08);
	    padding: 6px;
	    border: 1px solid #E5E7EB;
	    margin-top: 4px !important;
	    min-width: 200px; z-index: 2000 !important; position: relative;
		    // Caret arrow pointing up to parent menu
		    &::before {
		      content: '';
		      position: absolute;
		      top: -5px;
		      left: 24px;
		      width: 10px;
		      height: 10px;
		      background: #fff;
		      border-left: 1px solid #E5E7EB;
		      border-top: 1px solid #E5E7EB;
		      transform: rotate(45deg);
		      border-radius: 1px;
		    }
	  }

	  // ─── Dropdown item ──────────────────────────────
	  .nav-dropdown-item {
	    height: auto !important;
	    line-height: normal !important;
	    margin: 2px;
	    border-radius: 8px;
	    font-size: 14px;
	    padding: 0 !important;
	    transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
	    position: relative;
	    overflow: visible;

	    &:hover {
	      background: $accent-soft !important;
	    }

	    &.is-active {
	      background: $accent-wash !important;

	      .nav-dropdown-link {
	        color: $accent;
	        font-weight: 600;
	      }
	    }
	  }

	  // ─── Dropdown link ──────────────────────────────
	  .nav-dropdown-link {
	    display: flex !important;
	    align-items: center;
	    gap: 10px;
	    text-decoration: none; white-space: nowrap;
	    color: #374151 !important;
	    padding: 10px 14px;
	    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
	    font-size: 13.5px;
	    font-weight: 450;
	    letter-spacing: 0.005em;
	    transition: all 0.18s ease;
	    position: relative;

	    i {
	      font-size: 16px;
	      color: #6B7280;
	      width: 20px;
	      text-align: center;
	      flex-shrink: 0;
	      transition: all 0.18s ease;
	    }

	    .nav-dropdown-text {
	      flex: 1;
	      line-height: 1.4;
	    }

	    &:hover {
	      color: $accent;

	      i {
	        color: $accent;
	        transform: translateX(2px);
	      }
	    }
	  }
	}

	// ─── Reduced motion ─────────────────────────────────
	@media (prefers-reduced-motion: reduce) {
	  .status-dot__pulse::after {
	    animation: none !important;
	  }

	  .nav-submenu .el-submenu__title::after {
	    transition: none !important;
	  }
	}
	</style>
