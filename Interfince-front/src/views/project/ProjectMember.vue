<template>
    <section class="member-manage">
        <!-- ═══════════ 角色概览条 ═══════════ -->
        <div class="summary-strip" v-if="memberData.length">
            <div class="summary-item">
                <span class="summary-dot dot-super"></span>
                <span class="summary-label">超管</span>
                <strong class="summary-num">{{ roleCounts.super }}</strong>
            </div>
            <span class="summary-sep"></span>
            <div class="summary-item">
                <span class="summary-dot dot-dev"></span>
                <span class="summary-label">开发</span>
                <strong class="summary-num">{{ roleCounts.dev }}</strong>
            </div>
            <span class="summary-sep"></span>
            <div class="summary-item">
                <span class="summary-dot dot-tester"></span>
                <span class="summary-label">测试</span>
                <strong class="summary-num">{{ roleCounts.tester }}</strong>
            </div>
            <span class="summary-sep"></span>
            <div class="summary-item">
                <span class="summary-label">共</span>
                <strong class="summary-num summary-total">{{ total }}</strong>
                <span class="summary-label">人</span>
            </div>
        </div>

        <!-- ═══════════ 成员卡片区 ═══════════ -->
        <div class="member-section">
            <div class="member-header">
                <div class="member-header-left">
                    <span class="member-icon-box">
                        <i class="el-icon-user-solid"></i>
                    </span>
                    <span class="member-title">项目成员</span>
                </div>
                <div class="member-header-right">
                    <el-button type="primary" size="small" @click="openAddMember" icon="el-icon-plus" round>
                        添加成员
                    </el-button>
                </div>
            </div>

            <!-- 成员表格 -->
            <el-table
                :data="memberData"
                v-loading="listLoading"
                class="member-table"
                :default-sort="{prop: 'permissionType', order: 'ascending'}"
                row-class-name="member-row">
                <el-table-column prop="username" label="成员" min-width="22%" sortable>
                    <template slot-scope="scope">
                        <div class="user-cell">
                            <span
                                class="user-avatar"
                                :style="{ background: avatarColor(scope.row.username) }">
                                {{ (scope.row.username || '?')[0] }}
                            </span>
                            <div class="user-meta">
                                <span class="user-name">{{ scope.row.username }}</span>
                                <span class="user-email">{{ scope.row.userEmail || '' }}</span>
                            </div>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column prop="userPhone" label="手机号" min-width="16%" sortable>
                    <template slot-scope="scope">
                        <span class="cell-text">{{ scope.row.userPhone || '--' }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="permissionType" label="角色" min-width="18%" sortable>
                    <template slot-scope="scope">
                        <el-select
                            v-model="scope.row.permissionType"
                            size="mini"
                            :disabled="scope.row._roleUpdating"
                            @change="(val) => onChangeRole(scope.row, val)"
                            class="role-select"
                            :class="'role-' + getRoleClass(scope.row.permissionType)">
                            <el-option
                                v-for="role in roleOptions"
                                :key="role"
                                :label="role"
                                :value="role">
                                <span class="role-option">
                                    <i class="role-option-dot" :class="'dot-' + getRoleClass(role)"></i>
                                    {{ role }}
                                </span>
                            </el-option>
                        </el-select>
                        <i v-if="scope.row._roleUpdating" class="el-icon-loading role-spin"></i>
                    </template>
                </el-table-column>
                <el-table-column label="" width="56" fixed="right">
                    <template slot-scope="scope">
                        <el-popconfirm
                            :title="'将 ' + scope.row.username + ' 移出项目？'"
                            confirm-button-text="移除"
                            cancel-button-text="取消"
                            confirm-button-type="danger"
                            @confirm="removeMember(scope.row)"
                            popper-class="member-popconfirm">
                            <el-button
                                slot="reference"
                                type="text"
                                size="mini"
                                class="remove-btn"
                                icon="el-icon-close">
                            </el-button>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div v-if="total > 20" class="member-pagination">
                <el-pagination
                    background
                    layout="prev, pager, next"
                    @current-change="handleCurrentChange"
                    :page-size="20"
                    :page-count="Math.ceil(total / 20) || 1"
                    :current-page="page">
                </el-pagination>
            </div>
        </div>

        <!-- ═══════════ 添加成员弹窗 ═══════════ -->
        <el-dialog
            title="添加项目成员"
            :visible.sync="addMemberVisible"
            :close-on-click-modal="false"
            width="440px"
            class="add-member-dialog">
            <el-form
                :model="addForm"
                label-width="70px"
                :rules="addFormRules"
                ref="addForm"
                @submit.native.prevent
                class="add-form">
                <el-form-item label="用户" prop="user_id">
                    <el-select
                        v-model="addForm.user_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="输入用户名或邮箱搜索"
                        :remote-method="searchUsers"
                        :loading="userSearching"
                        value-key="id"
                        class="user-search-select"
                        popper-class="user-search-popper">
                        <el-option
                            v-for="u in userSearchResults"
                            :key="u.id"
                            :label="u.username"
                            :value="u.id">
                            <div class="user-option">
                                <span
                                    class="user-option-avatar"
                                    :style="{ background: avatarColor(u.username) }">
                                    {{ (u.username || '?')[0] }}
                                </span>
                                <div class="user-option-info">
                                    <strong>{{ u.username }}</strong>
                                    <span>{{ u.email || '无邮箱' }}</span>
                                </div>
                            </div>
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="角色" prop="permissionType">
                    <div class="role-pick-group">
                        <el-radio-group v-model="addForm.permissionType" size="small">
                            <el-radio-button
                                v-for="role in roleOptions"
                                :key="role"
                                :label="role">
                                {{ role }}
                            </el-radio-button>
                        </el-radio-group>
                    </div>
                </el-form-item>
            </el-form>
            <span slot="footer" class="dialog-footer">
                <el-button @click="addMemberVisible = false" round>取消</el-button>
                <el-button type="primary" :loading="addMemberLoading" @click="submitAddMember" round>
                    确定添加
                </el-button>
            </span>
        </el-dialog>
    </section>
</template>

<script>
import {
    getProjectMemberList,
    addProjectMember,
    removeProjectMember,
    updateMemberRole,
    getUserList,
} from "../../api/api"

const ROLE_OPTIONS = ['超级管理员', '开发人员', '测试人员']

/** Generate a stable pastel gradient hue from a string */
function hueFromName(name) {
    if (!name) return 228
    let h = 0
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360
    return h
}

export default {
    name: "project-member",
    data() {
        return {
            memberData: [],
            total: 0,
            page: 1,
            listLoading: false,
            roleOptions: ROLE_OPTIONS,

            addMemberVisible: false,
            addMemberLoading: false,
            addForm: { user_id: null, permissionType: '开发人员' },
            addFormRules: {
                user_id: [{ required: true, message: '请选择用户', trigger: 'change' }],
                permissionType: [{ required: true, message: '请选择角色', trigger: 'change' }],
            },
            userSearchResults: [],
            userSearching: false,
        }
    },
    computed: {
        projectId() {
            return this.$route.params.project_id
        },
        authHeaders() {
            return {
                "Content-Type": "application/json",
                Authorization: 'Token ' + JSON.parse(localStorage.getItem('token') || '""'),
            }
        },
        roleCounts() {
            const counts = { super: 0, dev: 0, tester: 0 }
            for (const m of this.memberData) {
                if (m.permissionType === '超级管理员') counts.super++
                else if (m.permissionType === '开发人员') counts.dev++
                else if (m.permissionType === '测试人员') counts.tester++
            }
            return counts
        },
    },
    methods: {
        // ── Helpers ──────────────────────────────────
        avatarColor(name) {
            const h = hueFromName(name)
            return `hsl(${h}, 55%, 90%)`
        },
        getRoleClass(role) {
            return role === '超级管理员' ? 'super' : role === '开发人员' ? 'dev' : 'tester'
        },

        // ── 成员列表 ─────────────────────────────────
        handleCurrentChange(val) { this.page = val; this.getProjectMember() },
        getProjectMember() {
            this.listLoading = true
            const params = { project_id: this.projectId, page: this.page }
            getProjectMemberList(this.authHeaders, params).then(res => {
                this.listLoading = false
                if (res.code === '999999') {
                    this.total = res.data.total
                    this.memberData = (res.data.data || []).map(m => ({
                        ...m, _roleUpdating: false,
                    }))
                } else {
                    this.$message.error({ message: res.msg, center: true })
                }
            }).catch(() => {
                this.listLoading = false
                this.$message.error({ message: '网络异常，请重试', center: true })
            })
        },

        // ── 角色变更 ─────────────────────────────────
        onChangeRole(row, newRole) {
            if (row._roleUpdating) return
            const oldRole = row._prevRole || row.permissionType
            this.$set(row, '_prevRole', oldRole)
            this.$set(row, '_roleUpdating', true)
            const params = { project_id: Number(this.projectId), user_id: row.id, permissionType: newRole }
            updateMemberRole(this.authHeaders, params).then(res => {
                this.$set(row, '_roleUpdating', false)
                if (res.code === '999999') {
                    this.$message.success({ message: '角色已更新', center: true })
                    this.$set(row, '_prevRole', newRole)
                } else {
                    this.$message.error({ message: res.msg, center: true })
                    this.$set(row, 'permissionType', oldRole)
                }
            }).catch(() => {
                this.$set(row, '_roleUpdating', false)
                this.$set(row, 'permissionType', oldRole)
                this.$message.error({ message: '网络异常', center: true })
            })
        },

        // ── 移除成员 ─────────────────────────────────
        removeMember(row) {
            const params = { project_id: Number(this.projectId), user_id: row.id }
            removeProjectMember(this.authHeaders, params).then(res => {
                if (res.code === '999999') {
                    this.$message.success({ message: '已移除 ' + row.username, center: true })
                    this.getProjectMember()
                } else {
                    this.$message.error({ message: res.msg, center: true })
                }
            }).catch(() => {
                this.$message.error({ message: '网络异常', center: true })
            })
        },

        // ── 添加成员 ─────────────────────────────────
        openAddMember() {
            this.addForm = { user_id: null, permissionType: '开发人员' }
            this.userSearchResults = []
            this.addMemberVisible = true
            this.$nextTick(() => { if (this.$refs.addForm) this.$refs.addForm.clearValidate() })
        },
        searchUsers(query) {
            if (!query || query.length < 1) { this.userSearchResults = []; return }
            this.userSearching = true
            getUserList(this.authHeaders, { search: query, page_size: 20 }).then(res => {
                this.userSearching = false
                if (res.code === '999999') this.userSearchResults = res.data.data || []
                else this.userSearchResults = []
            }).catch(() => { this.userSearching = false; this.userSearchResults = [] })
        },
        submitAddMember() {
            this.$refs.addForm.validate(valid => {
                if (!valid) return
                this.addMemberLoading = true
                const params = { project_id: Number(this.projectId), user_id: this.addForm.user_id, permissionType: this.addForm.permissionType }
                addProjectMember(this.authHeaders, params).then(res => {
                    this.addMemberLoading = false
                    if (res.code === '999999') {
                        this.$message.success({ message: '添加成功', center: true })
                        this.addMemberVisible = false
                        this.getProjectMember()
                    } else {
                        this.$message.error({ message: res.msg, center: true })
                    }
                }).catch(() => { this.addMemberLoading = false; this.$message.error({ message: '网络异常', center: true }) })
            })
        },
    },
    mounted() {
        this.getProjectMember()
    },
}
</script>

<style scoped lang="scss">
$accent: #4F6EF7;
$accent-soft: #EEF2FF;
$green: #0EAD69;
$green-soft: #E6F9F1;
$amber: #D18A1F;
$amber-soft: #FFF8EC;
$text-primary: #111827;
$text-secondary: #4B5563;
$text-muted: #9CA3AF;
$border: #E5E7EB;
$shadow-card: 0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.03);

.member-manage {
    max-width: 860px;
    margin: 28px auto;
    padding: 0 20px;
}

// ═══════════════════════════════════════════
//  角色概览条 — the signature element
// ═══════════════════════════════════════════
.summary-strip {
    display: flex;
    align-items: center;
    gap: 0;
    background: #fff;
    border-radius: 14px;
    padding: 14px 24px;
    margin-bottom: 16px;
    box-shadow: $shadow-card;
    border: 1px solid $border;
}

.summary-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.summary-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-super { background: $green; }
.dot-dev { background: $accent; }
.dot-tester { background: $amber; }

.summary-label {
    font-size: 13px;
    color: $text-muted;
    font-weight: 450;
}

.summary-num {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
}

.summary-total {
    color: $accent;
}

.summary-sep {
    width: 1px;
    height: 22px;
    background: #f0f2f5;
    margin: 0 18px;
    flex-shrink: 0;
}

// ═══════════════════════════════════════════
//  成员区域
// ═══════════════════════════════════════════
.member-section {
    background: #fff;
    border-radius: 14px;
    border: 1px solid $border;
    box-shadow: $shadow-card;
    overflow: hidden;
}

.member-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 22px;
    border-bottom: 1px solid #f3f4f6;
}

.member-header-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.member-icon-box {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: $accent-soft;
    color: $accent;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

.member-title {
    font-size: 15px;
    font-weight: 650;
    color: $text-primary;
    letter-spacing: -0.01em;
}

.member-header-right {
    flex-shrink: 0;
}

// ── 表格 ──
.member-table {
    ::v-deep .el-table__header th {
        background: #fafbfc;
        font-weight: 600;
        color: $text-muted;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid #f0f2f5;
        padding: 10px 0;
    }

    ::v-deep .member-row td {
        padding: 12px 0;
        border-bottom: 1px solid #f7f8fa;
        transition: background 0.15s;
    }

    ::v-deep .member-row:hover td {
        background: #fafbff !important;
    }

    ::v-deep .el-table__empty-block {
        padding: 40px 0;
    }
}

// ── 用户列 ──
.user-cell {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-left: 4px;
}

.user-avatar {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 700;
    color: $text-secondary;
    flex-shrink: 0;
    letter-spacing: -0.01em;
}

.user-meta {
    display: flex;
    flex-direction: column;
    gap: 1px;
    min-width: 0;
}

.user-name {
    font-weight: 600;
    color: $text-primary;
    font-size: 13.5px;
    line-height: 1.3;
}

.user-email {
    font-size: 11px;
    color: $text-muted;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cell-text {
    color: $text-secondary;
    font-size: 13px;
}

// ── 角色下拉 ──
.role-select {
    width: 114px;

    ::v-deep .el-input__inner {
        border-radius: 7px;
        font-size: 12px;
        font-weight: 550;
        text-align: center;
        transition: all 0.2s;
        height: 30px;
        line-height: 30px;
        padding: 0 24px 0 10px;
        border-width: 1.5px;
    }

    ::v-deep .el-input__suffix {
        right: 2px;
    }
}

.role-super ::v-deep .el-input__inner {
    color: $green;
    border-color: #a3e4c5;
    background: $green-soft;
}
.role-dev ::v-deep .el-input__inner {
    color: $accent;
    border-color: #c8d2fb;
    background: $accent-soft;
}
.role-tester ::v-deep .el-input__inner {
    color: $amber;
    border-color: #ecd79a;
    background: $amber-soft;
}

.role-option {
    display: flex;
    align-items: center;
    gap: 7px;
}

.role-option-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-super { background: $green; }
.dot-dev { background: $accent; }
.dot-tester { background: $amber; }

.role-spin {
    margin-left: 5px;
    font-size: 12px;
    color: $accent;
}

// ── 移除按钮 ──
.remove-btn {
    color: #d0d4da !important;
    font-size: 15px;
    padding: 4px 6px;
    transition: all 0.15s;

    &:hover {
        color: #EF4444 !important;
        background: #fef5f5;
        border-radius: 6px;
    }
}

// ── 分页 ──
.member-pagination {
    display: flex;
    justify-content: center;
    padding: 14px 20px;
    border-top: 1px solid #f3f4f6;
}

// ═══════════════════════════════════════════
//  添加成员弹窗
// ═══════════════════════════════════════════
.add-form {
    padding-top: 4px;
}

.user-search-select {
    width: 100%;
}

.user-option {
    display: flex;
    align-items: center;
    gap: 10px;
}

.user-option-avatar {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    color: $text-secondary;
    flex-shrink: 0;
}

.user-option-info {
    display: flex;
    flex-direction: column;
    line-height: 1.4;

    strong { font-size: 13px; color: $text-primary; }
    span { font-size: 11px; color: $text-muted; }
}

.role-pick-group {
    ::v-deep .el-radio-button__inner {
        padding: 8px 18px;
        border-radius: 6px;
        font-size: 13px;
    }
}
</style>
