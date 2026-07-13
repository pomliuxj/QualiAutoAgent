<template>
  <div class="login-page">
    <!-- Background decorations -->
    <div class="bg-shape bg-shape--1"></div>
    <div class="bg-shape bg-shape--2"></div>
    <div class="bg-shape bg-shape--3"></div>
    <div class="bg-dots"></div>

    <!-- Main card -->
    <div class="login-card">
      <!-- Left: Brand panel -->
      <div class="brand-panel">
        <div class="brand-inner">
          <!-- Logo -->
          <div class="brand-logo">
            <svg width="44" height="44" viewBox="0 0 44 44" fill="none">
              <rect width="44" height="44" rx="12" fill="url(#logoGrad)"/>
              <path d="M13 22l6 6 12-12" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
              <defs><linearGradient id="logoGrad" x1="0" y1="0" x2="44" y2="44"><stop stop-color="#3b82f6"/><stop offset="1" stop-color="#1d4ed8"/></linearGradient></defs>
            </svg>
            <div class="logo-badge">v2.0</div>
          </div>

          <h1 class="brand-title">质量平台</h1>
          <p class="brand-desc">一站式自动化测试管理平台，助力团队高效交付高质量软件</p>

          <div class="brand-features">
            <div class="bf-item">
              <div class="bf-icon bf-icon--api">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12H3l3-9h4l3 9H5z"/><circle cx="16" cy="10" r="2"/><circle cx="18" cy="17" r="2"/><path d="M17.5 11.5L18.5 15"/></svg>
              </div>
              <div class="bf-text">
                <span class="bf-label">API 接口管理</span>
                <span class="bf-hint">统一管理与快速测试</span>
              </div>
            </div>
            <div class="bf-item">
              <div class="bf-icon bf-icon--auto">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
              </div>
              <div class="bf-text">
                <span class="bf-label">自动化编排</span>
                <span class="bf-hint">用例编排与定时执行</span>
              </div>
            </div>
            <div class="bf-item">
              <div class="bf-icon bf-icon--report">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
              </div>
              <div class="bf-text">
                <span class="bf-label">可视化报告</span>
                <span class="bf-hint">测试趋势与结果分析</span>
              </div>
            </div>
          </div>

          <div class="brand-footer">
            <div class="brand-stat" v-for="s in stats" :key="s.label">
              <span class="brand-stat-num">{{ s.num }}</span>
              <span class="brand-stat-label">{{ s.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Form panel -->
      <div class="form-panel">
        <div class="form-inner">
          <!-- Header -->
          <div class="form-header">
            <h2 class="form-title">{{ activeName === 'first' ? '创建账号' : '欢迎回来' }}</h2>
            <p class="form-sub">{{ activeName === 'first' ? '注册新账号以开始使用' : '登录您的账号以继续' }}</p>
          </div>

          <!-- Tabs -->
          <div class="form-tabs">
            <button
              class="form-tab"
              :class="{ 'form-tab--active': activeName === 'first' }"
              @click="activeName = 'first'"
            >注册</button>
            <button
              class="form-tab"
              :class="{ 'form-tab--active': activeName === 'second' }"
              @click="activeName = 'second'"
            >登录</button>
            <div class="form-tab-indicator" :class="{ 'form-tab-indicator--right': activeName === 'second' }"></div>
          </div>

          <!-- Register form -->
          <el-form v-if="activeName === 'first'" :model="registerForm" :rules="registerRules" ref="registerForm" class="login-form">
            <div class="field-row">
              <el-form-item prop="reg_username" class="field-group">
                <label class="field-label">账号</label>
                <el-input v-model.trim="registerForm.reg_username" placeholder="请输入账号" size="small">
                  <i slot="prefix" class="fa fa-user"></i>
                </el-input>
              </el-form-item>
              <el-form-item prop="reg_first_name" class="field-group">
                <label class="field-label">姓名</label>
                <el-input v-model.trim="registerForm.reg_first_name" placeholder="请输入姓名" size="small">
                  <i slot="prefix" class="fa fa-id-card-o"></i>
                </el-input>
              </el-form-item>
            </div>
            <el-form-item prop="reg_password" class="field-group">
              <label class="field-label">密码</label>
              <el-input v-model.trim="registerForm.reg_password" :type="showRegPwd ? 'text' : 'password'" placeholder="请输入密码" size="small">
                <i slot="prefix" class="fa fa-lock"></i>
                <i slot="suffix" :class="showRegPwd ? 'fa fa-eye' : 'fa fa-eye-slash'" class="pwd-toggle" @click="showRegPwd = !showRegPwd"></i>
              </el-input>
            </el-form-item>
            <div class="field-row">
              <el-form-item prop="reg_email" class="field-group">
                <label class="field-label">邮箱</label>
                <el-input v-model.trim="registerForm.reg_email" placeholder="请输入邮箱" size="small">
                  <i slot="prefix" class="fa fa-envelope-o"></i>
                </el-input>
              </el-form-item>
              <el-form-item prop="reg_phone" class="field-group">
                <label class="field-label">手机号</label>
                <el-input v-model.trim="registerForm.reg_phone" placeholder="请输入手机号" size="small">
                  <i slot="prefix" class="fa fa-mobile"></i>
                </el-input>
              </el-form-item>
            </div>
            <el-form-item>
              <el-button type="primary" class="submit-btn" @click="handleRegister" :loading="registering">
                <span v-if="!registering">创 建 账 号</span>
              </el-button>
            </el-form-item>
          </el-form>

          <!-- Login form -->
          <el-form v-if="activeName === 'second'" :model="loginForm" :rules="loginRules" ref="loginForm" class="login-form">
            <el-form-item prop="account" class="field-group">
              <label class="field-label">账号</label>
              <el-input v-model.trim="loginForm.account" placeholder="请输入账号" size="small">
                <i slot="prefix" class="fa fa-user"></i>
              </el-input>
            </el-form-item>
            <el-form-item prop="checkPass" class="field-group">
              <label class="field-label">密码</label>
              <el-input v-model.trim="loginForm.checkPass" :type="showLoginPwd ? 'text' : 'password'" placeholder="请输入密码" size="small" @keyup.enter.native="handleSubmit2">
                <i slot="prefix" class="fa fa-lock"></i>
                <i slot="suffix" :class="showLoginPwd ? 'fa fa-eye' : 'fa fa-eye-slash'" class="pwd-toggle" @click="showLoginPwd = !showLoginPwd"></i>
              </el-input>
            </el-form-item>
            <div class="form-extra">
              <el-checkbox v-model="checked">记住密码</el-checkbox>
              <a class="forgot-link" @click="handleForgot">忘记密码？</a>
            </div>
            <el-form-item>
              <el-button type="primary" class="submit-btn" @click="handleSubmit2" :loading="logining">
                <span v-if="!logining">登 录</span>
              </el-button>
            </el-form-item>
          </el-form>

          <!-- SSO hint -->
          <div class="form-footer">
            <span class="divider-text">其他登录方式</span>
            <div class="sso-icons">
              <button class="sso-btn" title="企业微信">
                <i class="fa fa-weixin"></i>
              </button>
              <button class="sso-btn" title="钉钉">
                <i class="fa fa-wechat"></i>
              </button>
              <button class="sso-btn" title="邮箱">
                <i class="fa fa-envelope"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>&copy; {{ year }} 质量平台 · 自动化测试管理系统</span>
    </div>
  </div>
</template>

<script>
import { requestLogin, recordVisitor, register } from '../../api/api'

export default {
  data() {
    return {
      activeName: 'second',
      logining: false,
      registering: false,
      showLoginPwd: false,
      showRegPwd: false,
      year: new Date().getFullYear(),
      stats: [
        { num: '99.9%', label: '服务可用性' },
        { num: '50ms', label: '平均响应' },
        { num: '10K+', label: 'API 调用' }
      ],
      registerForm: { reg_username: '', reg_password: '', reg_first_name: '', reg_email: '', reg_phone: '' },
      loginForm: { account: '', checkPass: '' },
      registerRules: {
        reg_username: [{ required: true, message: '请输入账号', trigger: 'blur' }, { min: 3, max: 50, message: '用户名长度应为3-50个字符', trigger: 'blur' }],
        reg_password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
        reg_first_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        reg_email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
        reg_phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
      },
      loginRules: {
        account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
        checkPass: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      },
      checked: true,
    }
  },
  methods: {
    handleSubmit2() {
      var _this = this
      this.$refs.loginForm.validate((valid) => {
        if (valid) {
          this.logining = true
          requestLogin({ username: this.loginForm.account, password: this.loginForm.checkPass }).then(_data => {
            _this.logining = false; let { msg, code, data } = _data
            if (code == '999999') {
              localStorage.setItem('username', JSON.stringify(data.first_name))
              localStorage.setItem('token', JSON.stringify(data.key))
              _this.$router.push(_this.$route.query.url || '/projectList')
            } else { _this.$message.error({ message: msg, center: true }) }
          })
        }
      })
    },
    getVisitor() {
      if (typeof AMap === 'undefined') return
      try {
        let self = this
        var map = new AMap.Map('container', { resizeEnable: true })
        map.plugin('AMap.Geolocation', function () {
          var geolocation = new AMap.Geolocation({ enableHighAccuracy: true, timeout: 10000, buttonOffset: new AMap.Pixel(10, 20), zoomToAccuracy: true, buttonPosition: 'RB' })
          map.addControl(geolocation); geolocation.getCurrentPosition()
          AMap.event.addListener(geolocation, 'complete', self.onComplete)
          AMap.event.addListener(geolocation, 'error', self.onError)
        })
      } catch (e) {}
    },
    onComplete(data) {
      try { recordVisitor({ success: 1, longitude: data.position.getLng(), latitude: data.position.getLat() }).then(_data => {}) } catch (e) {}
    },
    onError() {
      try { recordVisitor({ success: 0 }).then(_data => {}) } catch (e) {}
    },
    handleRegister() {
      var _this = this
      this.$refs.registerForm.validate((valid) => {
        if (valid) {
          this.registering = true
          register({ username: this.registerForm.reg_username, password: this.registerForm.reg_password, first_name: this.registerForm.reg_first_name, email: this.registerForm.reg_email, phone: this.registerForm.reg_phone }).then(_data => {
            _this.registering = false; let { msg, code, data } = _data
            if (code == '999999') {
              localStorage.setItem('username', JSON.stringify(data.first_name))
              localStorage.setItem('token', JSON.stringify(data.key))
              _this.$message.success({ message: msg, center: true })
              _this.$router.push(_this.$route.query.url || '/projectList')
            } else { _this.$message.error({ message: msg, center: true }) }
          })
        }
      })
    },
    handleForgot() {
      this.$message.info({ message: '请联系管理员重置密码', center: true })
    },
  },
  mounted() { this.getVisitor() },
}
</script>

<style lang="scss">
// ─── Design tokens ─────────────────────────────────
$color-primary: #3b82f6;
$color-primary-dark: #1d4ed8;
$color-primary-light: #eff6ff;
$color-text: #0f172a;
$color-text-secondary: #475569;
$color-text-muted: #94a3b8;
$color-border: #e2e8f0;
$color-bg: #f8fafc;
$radius-lg: 20px;
$radius-md: 12px;
$radius-sm: 8px;
$transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
$transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);

// ─── Page ──────────────────────────────────────────
.login-page {
  position: fixed; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 30%, #f8fafc 60%, #eff6ff 100%);
  font-family: 'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  overflow: hidden;

  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
  }
}

// ─── Background decorations ────────────────────────
.bg-shape {
  position: absolute; border-radius: 50%; opacity: 0.4; pointer-events: none;
  &--1 { width: 500px; height: 500px; top: -10%; left: -8%; background: radial-gradient(circle, rgba(59,130,246,.12) 0%, transparent 70%); }
  &--2 { width: 400px; height: 400px; bottom: -12%; right: -5%; background: radial-gradient(circle, rgba(29,78,216,.10) 0%, transparent 70%); }
  &--3 { width: 300px; height: 300px; top: 40%; right: 25%; background: radial-gradient(circle, rgba(96,165,250,.08) 0%, transparent 70%); }
}

.bg-dots {
  position: absolute; inset: 0; opacity: .3; pointer-events: none;
  background-image: radial-gradient(rgba(59,130,246,.12) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 60% 60% at 50% 50%, black 20%, transparent 70%);
}

// ─── Card ──────────────────────────────────────────
.login-card {
  position: relative; z-index: 1;
  display: flex; width: 960px; min-height: 600px;
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,.8);
  border-radius: $radius-lg;
  box-shadow:
    0 4px 6px -1px rgba(0,0,0,.02),
    0 10px 15px -3px rgba(0,0,0,.03),
    0 25px 50px -12px rgba(0,0,0,.08),
    0 0 0 1px rgba(0,0,0,.02) inset;
  overflow: hidden;
}

// ─── Brand panel ───────────────────────────────────
.brand-panel {
  flex: 1;
  background: linear-gradient(160deg, #0f172a 0%, #1e293b 40%, #1e3a5f 100%);
  display: flex; align-items: center; justify-content: center;
  padding: 48px 40px;
  position: relative;
  overflow: hidden;

  &::before {
    content: ''; position: absolute; inset: 0;
    background:
      radial-gradient(ellipse 80% 50% at 10% 90%, rgba(59,130,246,.25) 0%, transparent 60%),
      radial-gradient(ellipse 50% 70% at 90% 10%, rgba(96,165,250,.12) 0%, transparent 50%);
  }
}

.brand-inner { position: relative; z-index: 1; max-width: 380px; }

.brand-logo {
  display: inline-flex; align-items: center; gap: 10px; margin-bottom: 28px;
  .logo-badge {
    font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 100px;
    background: rgba(59,130,246,.2); color: #93c5fd; letter-spacing: .04em;
  }
}

.brand-title {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-size: 32px; font-weight: 800; color: #f8fafc;
  margin: 0 0 12px; letter-spacing: -0.03em;
}

.brand-desc {
  font-size: 14px; color: rgba(203,213,225,.75); margin: 0 0 36px; line-height: 1.7;
}

.brand-features { display: flex; flex-direction: column; gap: 16px; margin-bottom: 40px; }

.bf-item { display: flex; align-items: flex-start; gap: 12px; }

.bf-icon {
  width: 36px; height: 36px; border-radius: $radius-sm;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  &--api { background: rgba(59,130,246,.15); color: #60a5fa; }
  &--auto { background: rgba(34,197,94,.12); color: #4ade80; }
  &--report { background: rgba(168,85,247,.12); color: #c084fc; }
}

.bf-text { display: flex; flex-direction: column; gap: 2px; }
.bf-label { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.bf-hint { font-size: 11px; color: rgba(148,163,184,.6); }

.brand-footer { display: flex; gap: 32px; }
.brand-stat { display: flex; flex-direction: column; gap: 2px; }
.brand-stat-num { font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; font-size: 22px; font-weight: 700; color: #f1f5f9; }
.brand-stat-label { font-size: 11px; color: rgba(148,163,184,.55); }

// ─── Form panel ────────────────────────────────────
.form-panel {
  width: 460px; display: flex; align-items: center; justify-content: center; padding: 40px 36px;
}

.form-inner { width: 100%; max-width: 360px; }

.form-header { margin-bottom: 24px; }

.form-title {
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  font-size: 24px; font-weight: 700; color: $color-text; margin: 0 0 4px;
  letter-spacing: -0.02em;
}

.form-sub { font-size: 13px; color: $color-text-muted; margin: 0; }

// ─── Tabs ──────────────────────────────────────────
.form-tabs {
  position: relative;
  display: flex; background: #f1f5f9; border-radius: $radius-sm; padding: 4px;
  margin-bottom: 28px;
}

.form-tab {
  flex: 1; padding: 9px 0; font-size: 13px; font-weight: 600;
  border: none; background: transparent; color: $color-text-muted;
  cursor: pointer; border-radius: 6px; position: relative; z-index: 1;
  transition: color $transition-fast;

  &:hover { color: $color-text-secondary; }
  &--active { color: #fff; }
}

.form-tab-indicator {
  position: absolute; top: 4px; left: 4px;
  width: calc(50% - 4px); height: calc(100% - 8px);
  background: linear-gradient(135deg, $color-primary, $color-primary-dark);
  border-radius: 6px; z-index: 0;
  transition: transform $transition-normal;
  box-shadow: 0 2px 8px rgba(59,130,246,.25);

  &--right { transform: translateX(100%); }
}

.login-form .el-form-item { margin-bottom: 0; }
.login-form .el-form-item.is-error .el-input__inner { border-color: #ef4444; }

.field-group { margin-bottom: 18px; }

.field-label {
  display: block; font-size: 12px; font-weight: 600; color: #475569;
  margin-bottom: 6px; letter-spacing: .01em;
}

.field-row {
  display: flex; gap: 12px;
  .field-group { flex: 1; }
}

// Override Element UI input styles
.login-form .el-input__inner {
  height: 42px; font-size: 13px;
  background: #fff; border: 1.5px solid #e2e8f0; border-radius: 8px;
  color: #0f172a; transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}
.login-form .el-input__inner::placeholder { color: #94a3b8; font-size: 12px; }
.login-form .el-input__inner:focus,
.login-form .el-input__inner:hover:not(:disabled) { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,.08); }
.login-form .el-input.is-disabled .el-input__inner { background: #f8fafc; color: #94a3b8; }
.login-form .el-input__prefix { color: #94a3b8; left: 12px; font-size: 14px; }
.login-form .el-input__suffix { right: 8px; }
.login-form .el-input--prefix .el-input__inner { padding-left: 36px; }
.login-form .el-input--suffix .el-input__inner { padding-right: 36px; }

.pwd-toggle {
  cursor: pointer; color: #94a3b8; font-size: 14px; padding: 6px;
  transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}
.pwd-toggle:hover { color: #475569; }

// ─── Form extras ───────────────────────────────────
.form-extra {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; margin-top: 4px;
}
.form-extra .el-checkbox__label { color: #475569; font-size: 12px; }
.form-extra .el-checkbox__inner { border-color: #e2e8f0; border-radius: 4px; }
.form-extra .el-checkbox.is-checked .el-checkbox__inner { background: #3b82f6; border-color: #3b82f6; }

.forgot-link {
  font-size: 12px; font-weight: 500; color: #3b82f6; cursor: pointer;
  text-decoration: none; transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}
.forgot-link:hover { color: #1d4ed8; text-decoration: underline; }

// ─── Submit button ─────────────────────────────────
.submit-btn {
  width: 100%; height: 44px; font-size: 14px; font-weight: 700; letter-spacing: .15em;
  background: linear-gradient(135deg, $color-primary, $color-primary-dark);
  border: none; border-radius: $radius-sm;
  box-shadow: 0 4px 14px rgba(59,130,246,.3);
  transition: all $transition-normal;
  margin-top: 4px;

  &:hover:not(.is-loading) {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    box-shadow: 0 6px 20px rgba(59,130,246,.4);
    transform: translateY(-1px);
  }
  &:active:not(.is-loading) { transform: translateY(0); }
  &.is-loading { background: linear-gradient(135deg, $color-primary, $color-primary-dark); }
}

// ─── SSO footer ────────────────────────────────────
.form-footer { margin-top: 24px; text-align: center; }

.divider-text {
  display: flex; align-items: center; gap: 12px;
  font-size: 11px; color: $color-text-muted; margin-bottom: 16px;

  &::before, &::after {
    content: ''; flex: 1; height: 1px; background: $color-border;
  }
}

.sso-icons { display: flex; justify-content: center; gap: 12px; }

.sso-btn {
  width: 40px; height: 40px; border-radius: $radius-sm;
  border: 1.5px solid $color-border; background: #fff;
  color: $color-text-secondary; font-size: 16px;
  cursor: pointer; transition: all $transition-fast;
  display: flex; align-items: center; justify-content: center;

  &:hover { border-color: $color-primary; color: $color-primary; background: $color-primary-light; box-shadow: 0 2px 8px rgba(59,130,246,.1); }
}

// ─── Footer ────────────────────────────────────────
.page-footer {
  position: relative; z-index: 1; margin-top: 24px;
  font-size: 11px; color: $color-text-muted;
}

// ─── Responsive ────────────────────────────────────
@media (max-width: 800px) {
  .login-card { flex-direction: column; width: calc(100vw - 32px); min-height: auto; margin: 0 16px; }
  .brand-panel { padding: 32px 24px; }
  .brand-features { margin-bottom: 24px; }
  .brand-footer { display: none; }
  .brand-title { font-size: 24px; }
  .brand-desc { margin-bottom: 24px; font-size: 13px; }
  .form-panel { width: 100%; padding: 28px 24px; }
  .bg-shape { display: none; }
}

@media (max-width: 480px) {
  .field-row { flex-direction: column; gap: 0; }
  .form-panel { padding: 24px 18px; }
  .brand-panel { padding: 24px 18px; }
}
</style>
