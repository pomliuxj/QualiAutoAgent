<template>
    <section class="project-list-page">
        <!-- ═══════════ 欢迎条 ═══════════ -->
        <div class="welcome-bar">
            <div class="welcome-greet">
                <span class="welcome-emoji">👋</span>
                <span class="welcome-text">{{ greeting }}，<strong>{{ sysUserName }}</strong></span>
            </div>
            <div class="welcome-stats">
                <div class="welcome-stat">
                    <span class="welcome-stat-num">{{ total }}</span>
                    <span class="welcome-stat-label">个项目</span>
                </div>
                <span class="welcome-stat-sep">·</span>
                <div class="welcome-stat is-active">
                    <span class="welcome-stat-num">{{ activeCount }}</span>
                    <span class="welcome-stat-label">启用中</span>
                </div>
            </div>
        </div>

        <!-- ═══════════ 操作栏 ═══════════ -->
        <div class="action-bar">
            <div class="action-left">
                <el-input
                    v-model="filters.name"
                    placeholder="搜索项目..."
                    prefix-icon="el-icon-search"
                    clearable
                    size="small"
                    @keyup.enter.native="getProjectList"
                    @clear="getProjectList"
                    class="search-input">
                </el-input>
                <el-button size="small" type="primary" @click="handleAdd" icon="el-icon-plus">
                    新建项目
                </el-button>
            </div>
            <div class="action-right">
                <el-button
                    size="small"
                    type="danger"
                    plain
                    icon="el-icon-delete"
                    @click="batchRemove"
                    :disabled="sels.length === 0">
                    批量删除
                </el-button>
            </div>
        </div>

        <!-- ═══════════ 项目表格 ═══════════ -->
        <div class="table-card">
            <el-table
                :data="project"
                v-loading="listLoading"
                @selection-change="selsChange"
                :row-class-name="tableRowClass"
                class="project-table">
                <el-table-column type="selection" width="44" align="center" />

                <el-table-column prop="name" label="项目名称" min-width="24%" sortable show-overflow-tooltip>
                    <template slot-scope="scope">
                        <router-link
                            v-if="scope.row.status"
                            :to="{ name: '项目概况', params: {project_id: scope.row.id}}"
                            class="project-link">
                            <span class="project-initial" :style="{ background: initialColor(scope.row.name) }">
                                {{ (scope.row.name || '?')[0] }}
                            </span>
                            <span class="project-name-text">{{ scope.row.name }}</span>
                        </router-link>
                        <div v-else class="project-link is-disabled">
                            <span class="project-initial is-disabled">{{ (scope.row.name || '?')[0] }}</span>
                            <span class="project-name-text is-disabled">{{ scope.row.name }}</span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column prop="version" label="版本" width="100" sortable>
                    <template slot-scope="scope">
                        <span class="version-text">v{{ scope.row.version || '--' }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="type" label="类型" width="90" sortable align="center">
                    <template slot-scope="scope">
                        <span class="type-badge" :class="scope.row.type === 'App' ? 'is-app' : 'is-web'">
                            {{ scope.row.type }}
                        </span>
                    </template>
                </el-table-column>

                <el-table-column prop="LastUpdateTime" label="最近更新" min-width="16%" sortable>
                    <template slot-scope="scope">
                        <span class="time-text">{{ scope.row.LastUpdateTime || '--' }}</span>
                    </template>
                </el-table-column>

                <el-table-column prop="status" label="状态" width="90" sortable align="center">
                    <template slot-scope="scope">
                        <span class="status-dot" :class="scope.row.status ? 'is-on' : 'is-off'"></span>
                        <span class="status-label">{{ scope.row.status ? '启用' : '禁用' }}</span>
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="220" fixed="right">
                    <template slot-scope="scope">
                        <div class="row-actions">
                            <el-button size="mini" type="primary" plain @click="handleEdit(scope.$index, scope.row)">
                                编辑
                            </el-button>
                            <el-button
                                size="mini"
                                :type="scope.row.status ? 'warning' : 'success'"
                                plain
                                @click="handleChangeStatus(scope.$index, scope.row)">
                                {{ scope.row.status ? '禁用' : '启用' }}
                            </el-button>
                            <el-popconfirm
                                title="确定删除该项目？"
                                confirm-button-text="删除"
                                cancel-button-text="取消"
                                confirm-button-type="danger"
                                @confirm="handleDel(scope.$index, scope.row)">
                                <el-button slot="reference" size="mini" type="danger" plain icon="el-icon-delete" />
                            </el-popconfirm>
                        </div>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- ═══════════ 分页 ═══════════ -->
        <div class="pagination-bar" v-if="total > 20">
            <el-pagination
                background
                layout="prev, pager, next"
                @current-change="handleCurrentChange"
                :page-size="20"
                :page-count="Math.ceil(total / 20)"
                :current-page="page" />
            <span class="pagination-total">共 {{ total }} 条</span>
        </div>

        <!-- ═══════════ 编辑弹窗 ═══════════ -->
        <el-dialog
            title="编辑项目"
            :visible.sync="editFormVisible"
            :close-on-click-modal="false"
            width="520px"
            class="pj-dialog">
            <el-form :model="editForm" label-width="70px" :rules="editFormRules" ref="editForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="editForm.name" placeholder="项目名称" />
                </el-form-item>
                <el-row :gutter="16">
                    <el-col :span="12">
                        <el-form-item label="类型" prop="type">
                            <el-select v-model="editForm.type" placeholder="选择类型" style="width:100%">
                                <el-option label="Web" value="Web" />
                                <el-option label="App" value="App" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="版本" prop="version">
                            <el-input v-model="editForm.version" placeholder="版本号" />
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-form-item label="描述" prop="description">
                    <el-input type="textarea" :rows="3" v-model="editForm.description" placeholder="项目描述（选填）" />
                </el-form-item>
            </el-form>
            <span slot="footer">
                <el-button @click="editFormVisible = false" round>取消</el-button>
                <el-button type="primary" :loading="editLoading" @click="editSubmit" round>保存</el-button>
            </span>
        </el-dialog>

        <!-- ═══════════ 新增弹窗 ═══════════ -->
        <el-dialog
            title="新建项目"
            :visible.sync="addFormVisible"
            :close-on-click-modal="false"
            width="520px"
            class="pj-dialog">
            <el-form :model="addForm" label-width="70px" :rules="addFormRules" ref="addForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model.trim="addForm.name" placeholder="项目名称" />
                </el-form-item>
                <el-row :gutter="16">
                    <el-col :span="12">
                        <el-form-item label="类型" prop="type">
                            <el-select v-model="addForm.type" placeholder="选择类型" style="width:100%">
                                <el-option label="Web" value="Web" />
                                <el-option label="App" value="App" />
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                        <el-form-item label="版本" prop="version">
                            <el-input v-model.trim="addForm.version" placeholder="版本号" />
                        </el-form-item>
                    </el-col>
                </el-row>
                <el-form-item label="描述" prop="description">
                    <el-input type="textarea" :rows="3" v-model="addForm.description" placeholder="项目描述（选填）" />
                </el-form-item>
            </el-form>
            <span slot="footer">
                <el-button @click="addFormVisible = false" round>取消</el-button>
                <el-button type="primary" :loading="addLoading" @click="addSubmit" round>创建项目</el-button>
            </span>
        </el-dialog>
    </section>
</template>

<script>
import { getProject, delProject, disableProject, enableProject, updateProject, addProject } from '../api/api'

function hueFromName(name) {
    if (!name) return 228
    let h = 0
    for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360
    return h
}

export default {
    data() {
        const nameRule = [
            { required: true, message: '请输入项目名称', trigger: 'blur' },
            { min: 1, max: 50, message: '1~50 个字符', trigger: 'blur' },
        ]
        const typeRule = [{ required: true, message: '请选择类型', trigger: 'change' }]
        const versionRule = [
            { required: true, message: '请输入版本号', trigger: 'blur' },
            { min: 1, max: 20, message: '1~20 个字符', trigger: 'blur' },
        ]
        const descRule = [{ max: 1024, message: '不能超过 1024 字符', trigger: 'blur' }]

        return {
            filters: { name: '' },
            project: [],
            total: 0,
            page: 1,
            listLoading: false,
            sels: [],

            editFormVisible: false,
            editLoading: false,
            editFormRules: { name: nameRule, type: typeRule, version: versionRule, description: descRule },
            editForm: { name: '', version: '', type: '', description: '' },

            addFormVisible: false,
            addLoading: false,
            addFormRules: { name: nameRule, type: typeRule, version: versionRule, description: descRule },
            addForm: { name: '', version: '', type: '', description: '' },
        }
    },
    computed: {
        sysUserName() {
            const user = localStorage.getItem('username')
            return user ? JSON.parse(user) : ''
        },
        greeting() {
            const h = new Date().getHours()
            if (h < 6) return '夜深了'
            if (h < 9) return '早上好'
            if (h < 12) return '上午好'
            if (h < 14) return '中午好'
            if (h < 18) return '下午好'
            return '晚上好'
        },
        activeCount() {
            return this.project.filter(p => p.status).length
        },
    },
    methods: {
        initialColor(name) {
            return `hsl(${hueFromName(name)}, 50%, 88%)`
        },
        tableRowClass({ row }) {
            if (!row.status) return 'row--disabled'
            const idx = this.project.indexOf(row)
            if (idx >= 0 && this.sels.includes(row)) return 'row--selected'
            return ''
        },

        // ── 列表 ────────────────────────────────────
        getProjectList() {
            this.listLoading = true
            const headers = { Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
            getProject(headers, { page: this.page, name: this.filters.name }).then(res => {
                this.listLoading = false
                if (res.code === '999999') {
                    this.total = res.data.total
                    this.project = res.data.data
                } else {
                    this.$message.error({ message: res.msg, center: true })
                }
            }).catch(() => {
                this.listLoading = false
            })
        },
        handleCurrentChange(val) {
            this.page = val
            this.getProjectList()
        },
        selsChange(sels) { this.sels = sels },

        // ── 删除 ────────────────────────────────────
        handleDel(index, row) {
            this.$confirm('确定删除「' + row.name + '」？删除后不可恢复。', '提示', { type: 'warning' }).then(() => {
                this.listLoading = true
                const headers = { "Content-Type": "application/json", Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
                delProject(headers, { ids: [row.id] }).then(res => {
                    if (res.code === '999999') {
                        this.$message.success({ message: '已删除', center: true })
                    } else {
                        this.$message.error({ message: res.msg, center: true })
                    }
                    this.getProjectList()
                })
            }).catch(() => {})
        },
        batchRemove() {
            const ids = this.sels.map(item => item.id)
            this.$confirm('确定删除选中的 ' + ids.length + ' 个项目？', '提示', { type: 'warning' }).then(() => {
                this.listLoading = true
                const headers = { "Content-Type": "application/json", Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
                delProject(headers, { ids }).then(res => {
                    if (res.code === '999999') {
                        this.$message.success({ message: '已删除', center: true })
                    } else {
                        this.$message.error({ message: res.msg, center: true })
                    }
                    this.getProjectList()
                })
            }).catch(() => {})
        },

        // ── 启用/禁用 ──────────────────────────────
        handleChangeStatus(index, row) {
            this.listLoading = true
            const headers = { "Content-Type": "application/json", Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
            const params = { project_id: row.id }
            const fn = row.status ? disableProject : enableProject
            const label = row.status ? '禁用' : '启用'
            fn(headers, params).then(res => {
                this.listLoading = false
                if (res.code === '999999') {
                    this.$message.success({ message: '已' + label, center: true })
                    row.status = !row.status
                } else {
                    this.$message.error({ message: res.msg, center: true })
                }
            })
        },

        // ── 编辑 ────────────────────────────────────
        handleEdit(index, row) {
            this.editForm = { ...row }
            this.editFormVisible = true
        },
        editSubmit() {
            this.$refs.editForm.validate(valid => {
                if (!valid) return
                this.$confirm('确认保存修改？', '提示').then(() => {
                    this.editLoading = true
                    const headers = { "Content-Type": "application/json", Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
                    const params = { project_id: this.editForm.id, name: this.editForm.name, type: this.editForm.type, version: this.editForm.version, description: this.editForm.description }
                    updateProject(headers, params).then(res => {
                        this.editLoading = false
                        if (res.code === '999999') {
                            this.$message.success({ message: '修改成功', center: true })
                            this.editFormVisible = false
                            this.getProjectList()
                        } else {
                            this.$message.error({ message: res.msg, center: true })
                        }
                    })
                }).catch(() => {})
            })
        },

        // ── 新增 ────────────────────────────────────
        handleAdd() {
            this.addForm = { name: '', version: '', type: '', description: '' }
            this.addFormVisible = true
            this.$nextTick(() => { if (this.$refs.addForm) this.$refs.addForm.clearValidate() })
        },
        addSubmit() {
            this.$refs.addForm.validate(valid => {
                if (!valid) return
                this.$confirm('确认创建项目？', '提示').then(() => {
                    this.addLoading = true
                    const headers = { "Content-Type": "application/json", Authorization: 'Token ' + JSON.parse(localStorage.getItem('token')) }
                    const params = JSON.stringify({ name: this.addForm.name, type: this.addForm.type, version: this.addForm.version, description: this.addForm.description })
                    addProject(headers, params).then(res => {
                        this.addLoading = false
                        if (res.code === '999999') {
                            this.$message.success({ message: '创建成功', center: true })
                            this.addFormVisible = false
                            this.getProjectList()
                        } else {
                            this.$message.error({ message: res.msg, center: true })
                        }
                    })
                }).catch(() => {})
            })
        },
    },
    mounted() {
        this.getProjectList()
    },
}
</script>

<style scoped lang="scss">
$accent: #4F6EF7;
$accent-soft: #EEF2FF;
$text-primary: #111827;
$text-secondary: #4B5563;
$text-muted: #9CA3AF;
$border: #E5E7EB;
$page-bg: #F3F4F6;

.project-list-page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 24px 20px 40px;
}

// ═══════════════════════════════════════════
//  欢迎条 — quiet, not a banner
// ═══════════════════════════════════════════
.welcome-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 10px;
}

.welcome-greet {
    display: flex;
    align-items: center;
    gap: 8px;
}

.welcome-emoji {
    font-size: 22px;
    line-height: 1;
}

.welcome-text {
    font-size: 16px;
    color: $text-secondary;
    font-weight: 450;
    letter-spacing: -0.01em;

    strong {
        color: $text-primary;
        font-weight: 650;
    }
}

.welcome-stats {
    display: flex;
    align-items: center;
    gap: 10px;
}

.welcome-stat {
    display: flex;
    align-items: baseline;
    gap: 4px;
    font-size: 13px;
    color: $text-muted;

    .welcome-stat-num {
        font-size: 18px;
        font-weight: 700;
        color: $text-primary;
        font-variant-numeric: tabular-nums;
    }

    &.is-active .welcome-stat-num {
        color: $accent;
    }
}

.welcome-stat-sep {
    color: #d4d8e0;
    font-size: 16px;
    user-select: none;
}

// ═══════════════════════════════════════════
//  操作栏
// ═══════════════════════════════════════════
.action-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    gap: 10px;
    flex-wrap: wrap;
}

.action-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.search-input {
    width: 240px;

    ::v-deep .el-input__inner {
        border-radius: 8px;
        border-color: $border;
        transition: all 0.2s;

        &:focus {
            border-color: $accent;
            box-shadow: 0 0 0 3px rgba(79,110,247,.08);
        }
    }
}

.action-right {
    flex-shrink: 0;
}

// ═══════════════════════════════════════════
//  表格卡片
// ═══════════════════════════════════════════
.table-card {
    background: #fff;
    border-radius: 14px;
    border: 1px solid $border;
    box-shadow: 0 1px 2px rgba(0,0,0,.03), 0 4px 12px rgba(0,0,0,.02);
    overflow: hidden;
}

// ── 项目名称 ──
.project-link {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: $text-primary;
    transition: color 0.15s;
    max-width: 100%;

    &:hover {
        color: $accent;

        .project-initial {
            transform: scale(1.06);
        }
    }

    &.is-disabled {
        cursor: default;
        &:hover { color: $text-primary; }
    }
}

.project-initial {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    color: $text-secondary;
    flex-shrink: 0;
    transition: transform 0.2s ease;

    &.is-disabled {
        opacity: 0.4;
    }
}

.project-name-text {
    font-size: 13.5px;
    font-weight: 550;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    &.is-disabled {
        color: $text-muted;
    }
}

// ── 版本 ──
.version-text {
    font-size: 12px;
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    color: $text-muted;
    background: #f5f7fa;
    padding: 2px 8px;
    border-radius: 4px;
}

// ── 类型 ──
.type-badge {
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 5px;
    letter-spacing: 0.02em;

    &.is-web {
        color: $accent;
        background: $accent-soft;
    }
    &.is-app {
        color: #D18A1F;
        background: #FFF8EC;
    }
}

// ── 时间 ──
.time-text {
    font-size: 12px;
    color: $text-muted;
}

// ── 状态 ──
.status-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;

    &.is-on {
        background: #0EAD69;
        box-shadow: 0 0 0 3px rgba(14,173,105,.15);
    }
    &.is-off {
        background: #d0d4da;
    }
}

.status-label {
    font-size: 12px;
    color: $text-secondary;
    vertical-align: middle;
}

// ── 操作列 ──
.row-actions {
    display: flex;
    gap: 6px;
    flex-wrap: nowrap;
}

// ── 分页 ──
.pagination-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 18px;
}

.pagination-total {
    font-size: 12px;
    color: $text-muted;
}
</style>

<!-- 全局覆盖（非 scoped） -->
<style lang="scss">
$accent: #4F6EF7;
$text-muted: #9CA3AF;
$border: #E5E7EB;

// ── 表格 ──
.project-table {
    &.el-table {
        border: none;
    }

    .el-table__header th {
        background: #fafbfc;
        font-size: 11px;
        font-weight: 600;
        color: $text-muted;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid #f0f2f5;
        padding: 11px 0;
    }

    .el-table__body td {
        padding: 14px 0;
        border-bottom: 1px solid #f7f8fa;
    }

    .el-table__body tr:hover > td {
        background: #fafbff !important;
    }

    // Disabled rows
    .row--disabled td {
        background: #fafafa;
    }

    // Selection highlight — subtle
    .el-table-column--selection .el-checkbox {
        opacity: 0.5;
        transition: opacity 0.15s;
    }
    .el-table__body tr:hover .el-table-column--selection .el-checkbox {
        opacity: 1;
    }

    // Empty
    .el-table__empty-block {
        padding: 48px 0;
    }
}

// ── 弹窗 ──
.pj-dialog {
    .el-dialog {
        border-radius: 14px;
        overflow: hidden;
    }
    .el-dialog__header {
        padding: 20px 24px 0;
    }
    .el-dialog__title {
        font-size: 16px;
        font-weight: 650;
        color: #111827;
    }
    .el-dialog__body {
        padding: 20px 24px 8px;
    }
    .el-dialog__footer {
        padding: 12px 24px 20px;
        text-align: right;
    }
    .el-dialog__headerbtn {
        top: 20px;
        right: 20px;
    }
}
</style>
