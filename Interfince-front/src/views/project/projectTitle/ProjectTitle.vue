<template>
  <div class="overview">
    <!-- Hero card -->
    <div class="hero-card">
      <div class="hero-icon" :class="type === 'App' ? 'hero-icon--app' : 'hero-icon--web'">
        <i :class="type === 'App' ? 'fa fa-mobile' : 'fa fa-globe'"></i>
      </div>
      <div class="hero-body">
        <div class="hero-top">
          <h1 class="hero-name">{{ projectName || '加载中...' }}</h1>
          <span class="hero-badge">{{ type || '—' }}</span>
        </div>
        <div class="hero-meta">
          <span><span class="hero-meta-label">版本</span> {{ version || '—' }}</span>
          <span class="hero-meta-sep">·</span>
          <span><span class="hero-meta-label">更新于</span> {{ updateDate || '暂无' }}</span>
        </div>
      </div>
    </div>

    <!-- Metrics -->
    <div class="metrics-section">
      <h2 class="section-eyebrow">项目指标</h2>
      <div class="metrics-grid">
        <router-link :to="{ name: '接口列表' }" class="metric-card metric-card--link metric-card--blue">
          <span class="metric-icon"><i class="fa fa-plug"></i></span>
          <span class="metric-number">{{ apiCount }}</span>
          <span class="metric-label">接口数量</span>
          <span class="metric-sub">API Count</span>
        </router-link>
        <router-link :to="{ name: '用例列表' }" class="metric-card metric-card--link metric-card--green">
          <span class="metric-icon"><i class="fa fa-play-circle"></i></span>
          <span class="metric-number">{{ automationCaseCount }}</span>
          <span class="metric-label">自动化用例</span>
          <span class="metric-sub">Test Cases</span>
        </router-link>
        <router-link :to="{ name: '定时任务' }" class="metric-card metric-card--link metric-card--amber">
          <span class="metric-icon"><i class="fa fa-clock-o"></i></span>
          <span class="metric-number">{{ taskCount }}</span>
          <span class="metric-label">定时任务</span>
          <span class="metric-sub">Scheduled Tasks</span>
        </router-link>
        <div class="metric-card metric-card--teal">
          <span class="metric-icon"><i class="fa fa-users"></i></span>
          <span class="metric-number">{{ memberCount }}</span>
          <span class="metric-label">项目成员</span>
          <span class="metric-sub">Members</span>
        </div>
        <div class="metric-card metric-card--slate">
          <span class="metric-icon"><i class="fa fa-code"></i></span>
          <span class="metric-number">{{ statusCount }}</span>
          <span class="metric-label">通用状态码</span>
          <span class="metric-sub">Status Codes</span>
        </div>
        <router-link :to="{ name: '项目动态' }" class="metric-card metric-card--link metric-card--purple">
          <span class="metric-icon"><i class="fa fa-bolt"></i></span>
          <span class="metric-number">{{ dynamicCount }}</span>
          <span class="metric-label">近期动态</span>
          <span class="metric-sub">3-Day Activity</span>
        </router-link>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="actions-section">
      <h2 class="section-eyebrow">快捷操作</h2>
      <div class="actions-row">
        <router-link :to="{ name: '新增接口' }" class="action-chip">
          <i class="fa fa-plus"></i><span>新建接口</span>
        </router-link>
        <router-link :to="{ name: '快速测试' }" class="action-chip action-chip--accent">
          <i class="fa fa-bolt"></i><span>快速测试</span>
        </router-link>
        <router-link :to="{ name: '用例列表' }" class="action-chip">
          <i class="fa fa-list-alt"></i><span>添加用例</span>
        </router-link>
        <router-link :to="{ name: '自动化测试报告' }" class="action-chip">
          <i class="fa fa-bar-chart"></i><span>测试报告</span>
        </router-link>
        <router-link :to="{ name: '定时任务' }" class="action-chip">
          <i class="fa fa-clock-o"></i><span>定时任务</span>
        </router-link>
      </div>
    </div>

    <div v-if="!apiCount && !automationCaseCount && !taskCount" class="empty-hint">
      <p>项目刚刚创建，还没有数据。</p>
      <router-link :to="{ name: '新增接口' }" class="empty-cta">创建第一个接口 →</router-link>
    </div>
  </div>
</template>

<script>
import { getProjectDetail } from '../../../api/api'

export default {
  data() {
    return {
      type: '', projectName: '', version: '', updateDate: '',
      apiCount: 0, statusCount: 0, dynamicCount: 0,
      memberCount: 0, automationCaseCount: 0, taskCount: 0,
    }
  },
  methods: {
    getProjectInfo() {
      var self = this
      let params = { project_id: this.$route.params.project_id }
      let headers = {
        'Content-Type': 'application/json',
        Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')),
      }
      getProjectDetail(headers, params).then((_data) => {
        let { msg, code, data } = _data
        if (code == '999999') {
          self.projectName = data.name
          self.type = data.type
          self.version = data.version
          self.updateDate = data.LastUpdateTime
          self.apiCount = data.apiCount
          self.statusCount = data.statusCount
          self.dynamicCount = data.dynamicCount
          self.memberCount = data.memberCount
          self.automationCaseCount = data.automationCaseCount
          self.taskCount = data.automationTask
        } else {
          self.$message.error({ message: msg, center: true })
        }
      }).catch(() => {
        self.$message.error({ message: '获取项目信息失败', center: true })
      })
    },
  },
  mounted() { this.getProjectInfo() },
}
</script>

<style lang="scss" scoped>
// ─── Design tokens ──────────────────────────────────
$bg:            #f7f8fa;
$surface:       #ffffff;
$accent:        #1d4ed8;
$accent-hover:  #1a43c0;
$accent-soft:   #eff3ff;
$text:          #111827;
$text-secondary:#6b7280;
$text-tertiary: #9ca3af;
$border:        #e5e7eb;
$shadow-sm:     0 1px 2px rgba(0,0,0,.04);
$shadow-md:     0 4px 12px rgba(0,0,0,.06);
$shadow-lg:     0 8px 24px rgba(0,0,0,.08);
$font-display:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-body:     -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;

$clr-blue:   #1d4ed8;
$clr-green:  #0d9488;
$clr-amber:  #d97706;
$clr-teal:   #0891b2;
$clr-slate:  #64748b;
$clr-purple: #7c3aed;

.overview {
  padding: 24px 32px 32px;
  background: $bg;
  min-height: 100%;
  font-family: $font-body;
  color: $text;
  background-image:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(29,78,216,.025) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 60%, rgba(124,58,237,.015) 0%, transparent 60%);
}

// ─── Hero card ──────────────────────────────────────
.hero-card {
  display: flex;
  align-items: center;
  gap: 18px;
  background: $surface;
  border: 1px solid $border;
  border-radius: 10px;
  padding: 18px 22px;
  margin-bottom: 22px;
  box-shadow: $shadow-sm;
}

.hero-icon {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;

  &--web {
    background: linear-gradient(135deg, #eff3ff, #dbe4ff);
    color: $clr-blue;
  }
  &--app {
    background: linear-gradient(135deg, #f5f3ff, #ede4ff);
    color: $clr-purple;
  }
}

.hero-body {
  flex: 1;
  min-width: 0;
}

.hero-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.hero-name {
  font-family: $font-display;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: $text;
  margin: 0;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hero-badge {
  display: inline-block;
  font-family: $font-display;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: $accent;
  background: $accent-soft;
  padding: 3px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.hero-meta {
  font-size: 12px;
  color: $text-tertiary;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;

  .hero-meta-label {
    font-weight: 500;
    color: $text-secondary;
  }
  .hero-meta-sep { color: $border; }
}

// ─── Section eyebrow ────────────────────────────────
.section-eyebrow {
  font-family: $font-display;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: $text-tertiary;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;

  &::before {
    content: '';
    display: inline-block;
    width: 3px; height: 11px;
    border-radius: 2px;
    background: $accent;
  }
}

// ─── Metrics grid ───────────────────────────────────
.metrics-section { margin-bottom: 22px; }

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.metric-card {
  background: $surface;
  border: 1px solid $border;
  border-radius: 9px;
  padding: 18px 20px 15px;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  box-shadow: $shadow-sm;
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
  cursor: default;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 9px 9px 0 0;
    opacity: 0;
    transition: opacity .18s ease;
  }

  &--link {
    cursor: pointer;
    &:hover {
      border-color: transparent;
      box-shadow: $shadow-lg;
      transform: translateY(-2px);
      &::before { opacity: 1; }
    }
  }

  &--blue   { &::before { background: $clr-blue;   } .metric-icon { background: #eff3ff; color: $clr-blue;   } }
  &--green  { &::before { background: $clr-green;  } .metric-icon { background: #ecfdf5; color: $clr-green;  } }
  &--amber  { &::before { background: $clr-amber;  } .metric-icon { background: #fff7ed; color: $clr-amber;  } }
  &--teal   { &::before { background: $clr-teal;   } .metric-icon { background: #ecfeff; color: $clr-teal;   } }
  &--slate  { &::before { background: $clr-slate;  } .metric-icon { background: #f8fafc; color: $clr-slate;  } }
  &--purple { &::before { background: $clr-purple; } .metric-icon { background: #f5f3ff; color: $clr-purple; } }

  .metric-icon {
    width: 30px; height: 30px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    margin-bottom: 10px;
    flex-shrink: 0;
  }

  .metric-number {
    font-family: $font-display;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.03em;
    font-feature-settings: 'tnum';
    font-variant-numeric: tabular-nums;
    color: $text;
    line-height: 1.1;
    margin-bottom: 1px;
    transition: color .18s ease;
  }

  .metric-label {
    font-size: 13px;
    font-weight: 500;
    color: $text;
    margin-bottom: 1px;
  }

  .metric-sub {
    font-size: 10px;
    color: $text-tertiary;
    font-family: $font-display;
    letter-spacing: 0.03em;
  }
}

// ─── Quick actions ──────────────────────────────────
.actions-section { margin-bottom: 0; }

.actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-family: $font-body;
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
  background: $surface;
  border: 1px solid $border;
  border-radius: 7px;
  padding: 8px 16px;
  text-decoration: none;
  box-shadow: $shadow-sm;
  transition: color .15s ease, border-color .15s ease, background .15s ease, box-shadow .15s ease, transform .15s ease;

  i { font-size: 12px; color: $text-tertiary; transition: color .15s ease; }

  &:hover {
    color: $accent;
    border-color: $accent;
    background: $accent-soft;
    box-shadow: $shadow-md;
    transform: translateY(-1px);
    i { color: $accent; }
  }

  &--accent {
    background: $accent;
    color: #fff;
    border-color: $accent;
    i { color: rgba(255,255,255,.8); }
    &:hover {
      background: $accent-hover;
      border-color: $accent-hover;
      color: #fff;
      i { color: #fff; }
    }
  }
}

// ─── Empty state ────────────────────────────────────
.empty-hint {
  text-align: center;
  padding: 48px 24px;
  color: $text-tertiary;
  font-size: 14px;
  p { margin: 0 0 14px; }
}
.empty-cta {
  font-family: $font-display;
  font-weight: 600;
  font-size: 14px;
  color: $accent;
  text-decoration: none;
  &:hover { text-decoration: underline; }
}

// ─── Responsive ─────────────────────────────────────
@media (max-width: 900px) {
  .overview { padding: 20px 18px 28px; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .actions-row { flex-direction: column; }
  .action-chip { justify-content: center; }
  .hero-card { flex-direction: column; align-items: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  .metric-card, .action-chip { transition: none; }
}
</style>
