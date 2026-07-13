<template>
    <section class="ai-testcase-container">
        <el-row :gutter="20" class="main-row">
            <!-- 中间：对话区域 -->
            <el-col :xs="24" :sm="24" :md="15" :lg="15" class="center-col">
                <div class="chat-container">
                    <!-- 对话头部 -->
                    <div class="chat-header">
                        <div class="chat-header-left">
                            <span class="chat-header-title">
                                <i class="el-icon-cpu"></i> AI 生成用例
                            </span>
                            <el-switch
                                v-model="enableDeepThinking"
                                active-text="深度思考"
                                inactive-text="快速"
                                active-color="#4F6EF7"
                                inactive-color="#909399"
                                class="header-think-switch">
                            </el-switch>
                        </div>
                        <div class="chat-header-right">
                            <span class="thread-label">会话</span>
                            <el-tag size="mini" type="info" class="thread-tag">{{ shortThreadId }}</el-tag>
                            <el-button
                                type="text"
                                size="mini"
                                @click="refreshThread"
                                :disabled="isRunning"
                                icon="el-icon-refresh"
                                class="thread-refresh">
                            </el-button>
                        </div>
                    </div>

                    <!-- 消息列表 -->
                    <div class="chat-messages" ref="chatMessages">
                        <!-- 欢迎界面（无消息时） -->
                        <div v-if="messages.length === 0" class="welcome-area">
                            <div class="welcome-header">
                                <span class="welcome-title">AI 智能体</span>
                                <span class="welcome-sub">选择一个智能体开始，或直接输入需求</span>
                            </div>

                            <!-- 智能体快速入口 -->
                            <div class="quick-entries">
                                <div class="quick-card" @click="quickEntry('接口用例', '为以下接口生成测试用例，覆盖功能、参数校验、边界值、异常等维度：')">
                                    <div class="quick-card-icon qc-case">
                                        <i class="el-icon-document"></i>
                                    </div>
                                    <div class="quick-card-body">
                                        <span class="quick-card-title">接口用例生成</span>
                                        <span class="quick-card-desc">单接口多维测试覆盖</span>
                                    </div>
                                </div>
                                <div class="quick-card" @click="quickEntry('场景用例', '为以下接口设计业务场景测试流程，包含多步骤的数据传递与依赖：')">
                                    <div class="quick-card-icon qc-scenario">
                                        <i class="el-icon-share"></i>
                                    </div>
                                    <div class="quick-card-body">
                                        <span class="quick-card-title">场景用例生成</span>
                                        <span class="quick-card-desc">多接口业务流端到端测试</span>
                                    </div>
                                </div>
                                <div class="quick-card" @click="quickEntry('知识库问答', '请帮我查询：')">
                                    <div class="quick-card-icon qc-knowledge">
                                        <i class="el-icon-reading"></i>
                                    </div>
                                    <div class="quick-card-body">
                                        <span class="quick-card-title">知识库问答</span>
                                        <span class="quick-card-desc">检索文档精准回答</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 对话消息 -->
                        <div
                            v-for="msg in messages"
                            :key="msg.id"
                            class="chat-msg-wrapper"
                            :class="'msg-role-' + msg.role">

                            <!-- 用户消息：右对齐气泡 -->
                            <div v-if="msg.role === 'user'" class="msg-user">
                                <div class="msg-user-bubble">
                                    <div class="msg-user-text">{{ msg.content }}</div>
                                </div>
                                <div class="msg-user-meta">
                                    <span class="msg-time">{{ formatTime(msg.timestamp) }}</span>
                                </div>
                            </div>

                            <!-- AI 消息 -->
                            <div v-else-if="msg.role === 'ai'" class="msg-ai">
                                <div class="msg-ai-card" :class="{
                                    'is-streaming': msg.status === 'streaming',
                                    'is-done': msg.status === 'completed',
                                    'is-error': msg.status === 'error'
                                }">
                                    <!-- Header -->
                                    <div class="msg-ai-header">
                                        <span class="msg-ai-dot" :class="{
                                            'dot-running': msg.status === 'streaming',
                                            'dot-done': msg.status === 'completed',
                                            'dot-error': msg.status === 'error'
                                        }"></span>
                                        <span class="msg-ai-node-label">{{ msg.nodeLabel }}</span>
                                        <span class="msg-ai-status">{{ msg.status === 'streaming' ? '运行中' : msg.status === 'completed' ? '完成' : msg.status === 'error' ? '出错' : '' }}</span>
                                    </div>

                                    <!-- Text / Report -->
                                    <div v-if="msg.content" class="msg-ai-body">
                                        <div v-if="msg.isReport" class="msg-report" v-html="renderMarkdown(msg.content)"></div>
                                        <div v-else class="msg-text">
                                            <span>{{ msg.content }}</span>
                                            <span v-if="msg.status === 'streaming'" class="cursor-blink"></span>
                                        </div>
                                    </div>
                                    <div v-else-if="msg.summary && !msg.interruptData" class="msg-ai-body">
                                        <div class="msg-summary">{{ msg.summary }}</div>
                                    </div>

                                    <!-- Inline tool calls -->
                                    <div v-if="msg.toolCalls && msg.toolCalls.length > 0" class="msg-ai-tools">
                                        <div
                                            v-for="tc in msg.toolCalls"
                                            :key="tc.tool + '_' + tc.timestamp"
                                            class="inline-tool"
                                            :class="{ 'is-expanded': tc._expanded, 'is-end': tc.status === 'end' }"
                                            @click.stop="toggleToolExpand(tc)">
                                            <div class="inline-tool-header">
                                                <span class="inline-tool-dot" :class="{ 'dot-end': tc.status === 'end' }"></span>
                                                <span class="inline-tool-name">{{ getToolLabel(tc.tool) || tc.tool }}</span>
                                                <span class="inline-tool-status">{{ tc.status === 'start' ? '执行中...' : '完成' }}</span>
                                                <i class="el-icon-arrow-down inline-tool-arrow" :class="{ 'is-open': tc._expanded }"></i>
                                            </div>
                                            <div v-if="tc._expanded" class="inline-tool-body">
                                                <div v-if="tc.input" class="inline-tool-section">
                                                    <span class="inline-tool-section-label">输入</span>
                                                    <pre class="inline-tool-pre">{{ formatToolData(tc.input) }}</pre>
                                                </div>
                                                <div v-if="tc.output" class="inline-tool-section">
                                                    <span class="inline-tool-section-label">输出</span>
                                                    <pre class="inline-tool-pre">{{ formatToolData(tc.output) }}</pre>
                                                </div>
                                                <div v-if="!tc.input && !tc.output" class="inline-tool-empty">无详情</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 内联 API 选择（中断交互 - select_apis） -->
                                    <div v-if="msg.interruptData && (!msg.interruptData.type || msg.interruptData.type === 'select_apis')" class="msg-ai-select">
                                        <div class="select-notice">
                                            <i class="el-icon-info"></i>
                                            <span>{{ msg.interruptData.message || '请选择需要生成测试用例的接口：' }}</span>
                                        </div>
                                        <div class="select-list">
                                            <el-checkbox-group v-model="selectedApiIndices">
                                                <div
                                                    v-for="(api, index) in (msg.interruptData.available_apis || [])"
                                                    :key="api.api_id || index"
                                                    class="select-api-item"
                                                    :class="{ 'is-selected': selectedApiIndices.includes(index) }"
                                                    @click.native="toggleApiSelection(index)">
                                                    <el-checkbox :label="index" class="select-checkbox" @click.native.stop>
                                                        <div class="select-api-content">
                                                            <div class="select-api-top">
                                                                <el-tag
                                                                    :type="api.request_type === 'POST' ? 'success' : api.request_type === 'GET' ? 'primary' : 'info'"
                                                                    size="mini"
                                                                    effect="dark"
                                                                    class="select-api-method">
                                                                    {{ api.request_type || 'GET' }}
                                                                </el-tag>
                                                                <span class="select-api-path">{{ api.api_address || '/' }}</span>
                                                            </div>
                                                            <div class="select-api-bottom">
                                                                <span class="select-api-name">{{ api.name }}</span>
                                                                <span v-if="api.http_type" class="select-api-type">{{ api.http_type }}</span>
                                                            </div>
                                                        </div>
                                                    </el-checkbox>
                                                </div>
                                            </el-checkbox-group>
                                        </div>
                                        <div class="select-bar">
                                            <span class="select-count">
                                                已选 <strong>{{ selectedApiIndices.length }}</strong> / {{ (msg.interruptData.available_apis || []).length }} 个接口
                                            </span>
                                            <div class="select-actions">
                                                <el-button @click="cancelSelection" size="small">取消</el-button>
                                                <el-button
                                                    type="primary"
                                                    @click="confirmSelection"
                                                    size="small"
                                                    :loading="isResuming"
                                                    :disabled="selectedApiIndices.length === 0"
                                                    icon="el-icon-check">
                                                    确认生成
                                                </el-button>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 场景确认面板（中断交互 - scenario_confirm） -->
                                    <div v-if="msg.interruptData && msg.interruptData.type === 'scenario_confirm'" class="msg-ai-scenario">
                                        <div class="scenario-confirm-panel">
                                            <div class="scenario-header">
                                                <div class="scenario-name">
                                                    <i class="el-icon-s-operation"></i>
                                                    <span>{{ msg.interruptData.scenario_name }}</span>
                                                </div>
                                                <div class="scenario-description">{{ msg.interruptData.scenario_description }}</div>
                                            </div>

                                            <div class="scenario-steps-flow">
                                                <div
                                                    v-for="(step, idx) in msg.interruptData.steps"
                                                    :key="step.step"
                                                    class="scenario-step-wrapper">
                                                    <div class="scenario-step-connector">
                                                        <div class="scenario-step-dot">{{ step.step }}</div>
                                                        <div v-if="idx < msg.interruptData.steps.length - 1" class="scenario-step-line"></div>
                                                    </div>
                                                    <div class="scenario-step-card">
                                                        <div class="step-card-header">
                                                            <span class="step-number-label">Step {{ step.step }}</span>
                                                            <span class="step-api-name">{{ step.api_name }}</span>
                                                        </div>
                                                        <div class="step-card-desc">{{ step.description }}</div>
                                                        <div v-if="step.dependencies && step.dependencies.length" class="step-card-deps">
                                                            <div class="deps-label">数据依赖：</div>
                                                            <div
                                                                v-for="dep in step.dependencies"
                                                                :key="dep.target_field"
                                                                class="dep-item">
                                                                <i class="el-icon-top dep-arrow-icon"></i>
                                                                <span class="dep-desc">{{ dep.description }}</span>
                                                                <code class="dep-path">{{ dep.source_json_path }}</code>
                                                                <span class="dep-arrow">→</span>
                                                                <code class="dep-path">{{ dep.target_field }}</code>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <div class="scenario-actions">
                                                <template v-if="!showModifyInput">
                                                    <el-button @click="cancelScenario" size="small">取消</el-button>
                                                    <el-button @click="showModifyInput = true" size="small" icon="el-icon-edit">修改方案</el-button>
                                                    <el-button type="primary" @click="confirmScenario" size="small" :loading="isResuming">确认方案</el-button>
                                                </template>
                                                <template v-else>
                                                    <div class="modify-input-area">
                                                        <el-input
                                                            v-model="modifyFeedback"
                                                            type="textarea"
                                                            :rows="3"
                                                            placeholder="请描述您希望如何修改场景设计...">
                                                        </el-input>
                                                        <div class="modify-input-actions">
                                                            <el-button @click="showModifyInput = false" size="small">取消</el-button>
                                                            <el-button type="primary" @click="submitModifyScenario" size="small" :loading="isResuming">提交修改意见</el-button>
                                                        </div>
                                                    </div>
                                                </template>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 场景执行进度面板 -->
                                    <div v-if="msg.nodeKey === 'scenario_run' && scenarioExecSteps.length > 0" class="msg-ai-exec">
                                        <div class="scenario-exec-panel">
                                            <div class="exec-header">
                                                <span class="exec-col-step">步骤</span>
                                                <span class="exec-col-api">接口</span>
                                                <span class="exec-col-status">状态</span>
                                            </div>
                                            <div
                                                v-for="s in scenarioExecSteps"
                                                :key="s.step"
                                                class="exec-row"
                                                :class="'exec-status-' + s.status">
                                                <span class="exec-col-step">{{ s.step }}</span>
                                                <span class="exec-col-api">{{ s.api_name }}</span>
                                                <span class="exec-col-status">
                                                    <i v-if="s.status === 'success'" class="el-icon-circle-check exec-ok"></i>
                                                    <i v-else-if="s.status === 'running'" class="el-icon-loading exec-running-icon"></i>
                                                    <i v-else-if="s.status === 'error'" class="el-icon-circle-close exec-fail"></i>
                                                    <span v-else class="exec-pending-text">等待</span>
                                                    <span class="exec-status-text">{{ s.status === 'success' ? '通过' : s.status === 'error' ? '失败' : s.status === 'running' ? '执行中' : '等待' }}</span>
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="msg-ai-meta">
                                    <span class="msg-time">{{ formatTime(msg.timestamp) }}</span>
                                </div>
                            </div>

                            <!-- 系统消息：居中提示 -->
                            <div v-else-if="msg.role === 'system'" class="msg-system">
                                <div class="msg-system-bubble" :class="{
                                    'sys-done': msg.nodeKey === 'done',
                                    'sys-error': msg.nodeKey === 'error',
                                    'sys-info': msg.nodeKey === 'cancelled'
                                }">
                                    <i v-if="msg.nodeKey === 'done'" class="el-icon-success"></i>
                                    <i v-else-if="msg.nodeKey === 'error'" class="el-icon-warning"></i>
                                    <i v-else-if="msg.nodeKey === 'cancelled'" class="el-icon-info"></i>
                                    <span class="sys-msg-text">{{ msg.content }}</span>
                                    <template v-if="msg.nodeKey === 'done'">
                                        <el-button type="primary" size="small" @click="resetAndNew" icon="el-icon-refresh">重新生成</el-button>
                                    </template>
                                    <template v-else-if="msg.nodeKey === 'error'">
                                        <el-button size="small" @click="retryLast" icon="el-icon-refresh">重试</el-button>
                                        <el-button type="primary" size="small" @click="resetAndNew" icon="el-icon-edit">重新开始</el-button>
                                    </template>
                                    <template v-else-if="msg.nodeKey === 'cancelled'">
                                        <el-button size="small" @click="retryLast" icon="el-icon-refresh">重试</el-button>
                                    </template>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 底部输入区域 -->
                    <div class="chat-composer">
                        <div class="composer-input-row">
                            <el-input
                                type="textarea"
                                v-model="userInput"
                                :rows="2"
                                :disabled="isRunning"
                                placeholder="描述接口用例或业务场景，自动生成接口用例与自动化场景用例，Enter 发送，Shift+Enter 换行"
                                class="composer-textarea"
                                @keydown.enter.native="onComposerKeydown">
                            </el-input>
                        </div>
                        <div class="composer-bar">
                            <div class="composer-left">
                                <el-button
                                    @click="clearAll"
                                    :disabled="isRunning"
                                    size="small"
                                    icon="el-icon-delete"
                                    class="composer-clear">
                                    清空对话
                                </el-button>
                            </div>
                            <div class="composer-right">
                                <el-button
                                    v-if="!isRunning"
                                    type="primary"
                                    @click="startGeneration"
                                    :disabled="!userInput.trim()"
                                    icon="el-icon-caret-right">
                                    发送
                                </el-button>
                                <el-button
                                    v-else
                                    type="danger"
                                    @click="abortGeneration"
                                    icon="el-icon-close">
                                    停止生成
                                </el-button>
                            </div>
                        </div>
                    </div>
                </div>
            </el-col>

            <!-- 右侧：监控面板（执行跟踪 + 工具调用） -->
            <el-col :xs="0" :sm="0" :md="9" :lg="9" class="right-col">
                <div class="monitor-panel" :class="{ 'is-collapsed': toolPanelCollapsed }">
                    <!-- 面板头部 — 标签切换 -->
                    <div class="monitor-panel-header">
                        <div class="monitor-tabs">
                            <span
                                class="monitor-tab"
                                :class="{ 'is-active': monitorTab === 'tree' }"
                                @click="monitorTab = 'tree'">
                                <i class="el-icon-share"></i> 执行跟踪
                                <em v-if="activeTreeCount" class="monitor-tab-count">{{ activeTreeCount }}</em>
                            </span>
                            <span
                                class="monitor-tab"
                                :class="{ 'is-active': monitorTab === 'tools' }"
                                @click="monitorTab = 'tools'">
                                <i class="el-icon-setting"></i> 工具调用
                                <em v-if="activeToolCount" class="monitor-tab-count running">{{ activeToolCount }}</em>
                            </span>
                        </div>
                        <el-button
                            type="text"
                            size="mini"
                            @click="toolPanelCollapsed = !toolPanelCollapsed"
                            :icon="toolPanelCollapsed ? 'el-icon-d-arrow-left' : 'el-icon-d-arrow-right'"
                            class="monitor-panel-toggle">
                        </el-button>
                    </div>

                    <div v-if="!toolPanelCollapsed" class="monitor-panel-body">
                        <!-- ═══ 执行跟踪 Tab ═══ -->
                        <div v-show="monitorTab === 'tree'" class="monitor-tree">
                            <div v-if="agentTree.length === 0" class="monitor-empty">
                                <i class="el-icon-s-data"></i>
                                <span>等待智能体启动...</span>
                            </div>
                            <div v-else class="agent-tree">
                                <div v-for="group in agentTree" :key="group.id" class="tree-group">
                                    <!-- Orchestrator 节点 -->
                                    <div v-if="group.type === 'orchestrator'" class="tree-item tree-orch"
                                         :class="{ 'is-active': group.status === 'running', 'is-done': group.status === 'completed' }">
                                        <div class="tree-dot orch-dot">
                                            <i v-if="group.status === 'completed'" class="el-icon-check"></i>
                                            <i v-else-if="group.status === 'running'" class="el-icon-loading"></i>
                                        </div>
                                        <i class="tree-node-icon el-icon-discover"></i>
                                        <span class="tree-label">{{ group.label }}</span>
                                    </div>

                                    <!-- 子智能体：可展开分组 -->
                                    <div v-else-if="group.type === 'sub_agent'" class="tree-sub-agent"
                                         :class="{ 'is-active': group.status === 'running' }">
                                        <div class="tree-item tree-sub-header"
                                             :class="{ 'is-done': group.status === 'completed', 'is-error': group.status === 'error' }"
                                             @click="toggleSubAgent(group)">
                                            <i class="el-icon-arrow-right tree-arrow"
                                               :class="{ 'is-open': group.expanded }"></i>
                                            <div class="tree-dot sub-dot"
                                                 :class="{ 'is-done': group.status === 'completed', 'is-running': group.status === 'running' }">
                                                <i v-if="group.status === 'completed'" class="el-icon-check"></i>
                                                <i v-else-if="group.status === 'error'" class="el-icon-close"></i>
                                                <i v-else-if="group.status === 'running'" class="el-icon-loading"></i>
                                            </div>
                                            <i class="tree-node-icon" :class="getNodeIcon(group.key)"></i>
                                            <span class="tree-label sub-label">{{ group.label }}</span>
                                            <span class="tree-badge">{{ group.children.length }} 步</span>
                                        </div>
                                        <!-- 子智能体的内部节点 -->
                                        <div v-show="group.expanded" class="tree-children">
                                            <div v-for="child in group.children" :key="child.id"
                                                 class="tree-item tree-node"
                                                 :class="{
                                                     'is-active': child.status === 'running',
                                                     'is-done': child.status === 'completed',
                                                     'is-error': child.status === 'error',
                                                     'is-filtered': monitorTab === 'tools' && activeToolFilter === child.key
                                                 }"
                                                 @click="focusToolNode(child.key)">
                                                <div class="tree-dot node-dot"
                                                     :class="{ 'is-done': child.status === 'completed', 'is-running': child.status === 'running' }">
                                                    <i v-if="child.status === 'completed'" class="el-icon-check"></i>
                                                    <i v-else-if="child.status === 'running'" class="el-icon-loading"></i>
                                                </div>
                                                <i class="tree-node-icon" :class="getNodeIcon(child.key)"></i>
                                                <span class="tree-label node-label">{{ child.label }}</span>
                                                <span v-if="child.toolCount" class="tree-tool-count">{{ child.toolCount }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- ═══ 工具调用 Tab ═══ -->
                        <div v-show="monitorTab === 'tools'" class="monitor-tools">
                            <!-- 节点筛选提示条 -->
                            <div v-if="toolCallLog.length > 0 && activeToolFilter !== '__all__'" class="tool-filter-banner">
                                <i class="el-icon-connection"></i>
                                <span>筛选自「{{ getNodeLabel(activeToolFilter) }}」</span>
                                <span class="tool-filter-banner-count">{{ filteredGroupedToolCalls.reduce((s, g) => s + g.tools.length, 0) }} 个工具</span>
                                <el-button type="text" size="mini" @click="activeToolFilter = '__all__'; monitorTab = 'tools'" class="tool-filter-clear">
                                    <i class="el-icon-close"></i> 清除
                                </el-button>
                            </div>
                            <div v-if="toolCallLog.length === 0" class="monitor-empty">
                                <i class="el-icon-s-tools"></i>
                                <span>暂无工具调用</span>
                            </div>

                            <!-- 节点筛选标签 -->
                            <div v-if="toolCallLog.length > 0" class="tool-panel-filters">
                                <span class="tool-filter-chip"
                                    :class="{ 'is-active': activeToolFilter === '__all__' }"
                                    @click="activeToolFilter = '__all__'">
                                    全部 <em class="tool-filter-count">{{ toolCallLog.length }}</em>
                                </span>
                                <span v-for="node in availableToolNodes" :key="node.nodeKey"
                                    class="tool-filter-chip"
                                    :class="{ 'is-active': activeToolFilter === node.nodeKey }"
                                    @click="activeToolFilter = node.nodeKey">
                                    {{ node.nodeLabel }} <em class="tool-filter-count">{{ node.count }}</em>
                                </span>
                            </div>

                            <template v-for="group in filteredGroupedToolCalls">
                                <div :key="group.nodeKey" class="tool-panel-group">
                                    <div class="tool-panel-group-header">
                                        <span class="tool-panel-group-dot"></span>
                                        <span class="tool-panel-group-label">{{ group.nodeLabel }}</span>
                                        <span class="tool-panel-group-count">{{ group.tools.length }}</span>
                                    </div>
                                    <div v-for="tc in group.tools" :key="tc.id"
                                        class="tool-panel-item"
                                        :class="{ 'is-running': tc.status === 'start', 'is-expanded': tc._expanded }">
                                        <div class="tool-panel-item-header" @click="toggleToolPanelItem(tc)">
                                            <span class="tool-panel-item-indicator">
                                                <i v-if="tc.status === 'start'" class="el-icon-loading"></i>
                                                <i v-else class="el-icon-check tool-done-icon"></i>
                                            </span>
                                            <span class="tool-panel-item-name">{{ getToolLabel(tc.tool) }}</span>
                                            <span class="tool-panel-item-status">{{ tc.status === 'start' ? '执行中' : '完成' }}</span>
                                            <i class="tool-panel-item-arrow"
                                                :class="tc._expanded ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"></i>
                                        </div>
                                        <div v-if="tc._expanded" class="tool-panel-item-body">
                                            <div v-if="tc.input !== undefined" class="tool-panel-section">
                                                <div class="tool-panel-label">调用参数</div>
                                                <pre class="tool-panel-json">{{ formatToolData(tc.input) }}</pre>
                                            </div>
                                            <div v-else-if="tc.status === 'start'" class="tool-panel-section">
                                                <div class="tool-panel-label">调用参数</div>
                                                <pre class="tool-panel-json tool-panel-json-empty">等待工具参数...</pre>
                                            </div>
                                            <div v-if="tc.output !== undefined" class="tool-panel-section">
                                                <div class="tool-panel-label">返回结果</div>
                                                <pre class="tool-panel-json">{{ formatToolData(tc.output) }}</pre>
                                            </div>
                                            <div v-else-if="tc.status === 'end'" class="tool-panel-section">
                                                <div class="tool-panel-label">返回结果</div>
                                                <pre class="tool-panel-json tool-panel-json-empty">无返回数据</pre>
                                            </div>
                                            <div class="tool-panel-section">
                                                <span class="tool-panel-time">{{ formatTime(tc.timestamp) }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </el-col>
        </el-row>
    </section>
</template>

<script>
    import { aiTestCase } from '../../../api/api'

    export default {
        name: "ai-test-case",
        data() {
            return {
                userInput: '',
                threadId: this.generateUUID(),
                enableDeepThinking: false,
                isRunning: false,
                abortController: null,

                // 对话消息列表
                // { id, role: 'user'|'ai'|'system', nodeKey, nodeLabel, content,
                //   status: 'streaming'|'completed'|'error', toolCalls: [],
                //   interruptData: null|{message, available_apis}, isReport, summary, timestamp }
                messages: [],

                // 分层执行树（右侧监控面板）— 动态填充
                // [{ id, key, label, type:'orchestrator'|'sub_agent'|'node',
                //    status, summary, children:[...], expanded }]
                agentTree: [],
                // 当前活跃的子智能体 ID（用于挂载子节点）
                activeSubAgentId: null,
                // 工作流模式：null=未检测, 'single'=单接口, 'scenario'=场景
                activeWorkflowMode: null,

                // 工具名称映射
                toolLabelMap: {
                    'list_project_apis': '查询接口列表',
                    'add_automation_api': '创建测试用例',
                    'update_automation_api': '修改测试用例',
                    'start_automation_test': '启动测试执行',
                    'execute_scenario_step': '执行场景步骤',
                    'Search_Api_Info': '查询接口详情',
                    'api_doc_info': '查询接口文档',
                    'create_global_variable': '创建全局变量',
                    'list_global_variables': '查询全局变量',
                    'search_knowledge_base': '检索知识库',
                },

                // 工具调用日志（独立于 messages，用于右侧面板）
                toolCallLog: [],
                toolPanelCollapsed: false,
                monitorTab: 'tree',             // 右侧面板当前标签：'tree' | 'tools'
                activeToolFilter: '__all__',   // 当前筛选的节点，'__all__' 表示全部

                // 流结束标记
                _streamEndedNaturally: false,

                // 中断交互状态
                selectedApiIndices: [],
                isResuming: false,

                // 场景模式状态
                scenarioConfirmData: null,       // 当前 scenario_confirm 中断数据
                modifyFeedback: '',              // 修改反馈文本
                showModifyInput: false,          // 是否显示修改输入框
                scenarioExecSteps: [],           // [{ step, api_name, status, case_id }]
            }
        },
        computed: {
            shortThreadId() {
                if (this.threadId.length <= 16) return this.threadId
                return this.threadId.substr(0, 16) + '...'
            },
            /** 是否有活跃的中断消息（取最新一条） */
            activeInterruptMsg() {
                return [...this.messages].reverse().find(m => m.role === 'ai' && m.interruptData)
            },
            /** 正在执行中的工具调用数量 */
            activeToolCount() {
                return this.toolCallLog.filter(t => t.status === 'start').length
            },
            /** 正在运行中的智能体节点数量 */
            activeTreeCount() {
                let count = 0
                this._forEachTreeNode(n => { if (n.status === 'running') count++ })
                return count
            },
            /** 按节点分组后的工具调用（保持首次出现顺序） */
            groupedToolCalls() {
                const groups = []
                const seenNodes = new Set()
                for (const tc of this.toolCallLog) {
                    const key = tc.nodeKey || '__unknown__'
                    if (!seenNodes.has(key)) {
                        seenNodes.add(key)
                        groups.push({
                            nodeKey: key,
                            nodeLabel: key === '__unknown__' ? '未分类' : this.getNodeLabel(key),
                            tools: [tc],
                        })
                    } else {
                        const group = groups.find(g => g.nodeKey === key)
                        if (group) group.tools.push(tc)
                    }
                }
                return groups
            },
            /** 有工具调用的节点列表（用于筛选标签） */
            availableToolNodes() {
                return this.groupedToolCalls.map(g => ({
                    nodeKey: g.nodeKey,
                    nodeLabel: g.nodeLabel,
                    count: g.tools.length,
                }))
            },
            /** 按 activeToolFilter 筛选后的分组 */
            filteredGroupedToolCalls() {
                if (this.activeToolFilter === '__all__') return this.groupedToolCalls
                return this.groupedToolCalls.filter(g => g.nodeKey === this.activeToolFilter)
            }
        },
        methods: {
            generateUUID() {
                return 'conv_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 9)
            },
            formatTime(ts) {
                const d = new Date(ts)
                const pad = n => String(n).padStart(2, '0')
                return pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds())
            },
            getToolLabel(tool) {
                return this.toolLabelMap[tool] || tool
            },
            getStatusText(status) {
                const map = {
                    'pending': '等待中',
                    'streaming': '生成中',
                    'completed': '已完成',
                    'error': '失败',
                    'skipped': '已跳过'
                }
                return map[status] || status
            },
            /** 节点图标映射 */
            getNodeIcon(key) {
                const icons = {
                    'intent_recognition': 'el-icon-discover',
                    'general_response': 'el-icon-chat-dot-round',
                    'case_gen': 'el-icon-document',
                    'scenario_gen': 'el-icon-share',
                    'code_quality': 'el-icon-data-analysis',
                    'rag_qa': 'el-icon-reading',
                    'select_apis': 'el-icon-s-grid',
                    'case_generate': 'el-icon-document-add',
                    'case_run': 'el-icon-video-play',
                    'case_update': 'el-icon-edit-outline',
                    'final_report': 'el-icon-data-line',
                    'scenario_design': 'el-icon-s-operation',
                    'scenario_generate': 'el-icon-document-add',
                    'scenario_run': 'el-icon-video-play',
                    'scenario_fix': 'el-icon-edit-outline',
                    'scenario_report': 'el-icon-data-line',
                }
                return icons[key] || 'el-icon-caret-right'
            },

            /** 动态节点的显示标签 */
            /** 在 agentTree 中查找任意节点（包括子智能体的 children） */
            _findTreeNode(key) {
                for (const g of this.agentTree) {
                    if (g.key === key) return g
                    if (g.children) {
                        const c = g.children.find(ch => ch.key === key)
                        if (c) return c
                    }
                }
                return null
            },
            /** 遍历 agentTree 所有节点（包括 children） */
            _forEachTreeNode(fn) {
                this.agentTree.forEach(g => {
                    fn(g)
                    if (g.children) g.children.forEach(fn)
                })
            },
            getNodeLabel(key) {
                const known = this._findTreeNode(key)
                return known ? known.label : this.getDefaultNodeLabel(key)
            },
            /** 节点标签后备映射 */
            getDefaultNodeLabel(key) {
                const labels = {
                    // Orchestrator
                    'intent_recognition': '意图识别',
                    'general_response': '智能回答',
                    // Sub-agent entry nodes
                    'case_gen': '单接口用例生成',
                    'scenario_gen': '场景用例生成',
                    'code_quality': '代码质量分析',
                    // Case gen internal
                    'select_apis': '选取接口',
                    'case_generate': '生成单接口用例',
                    'case_run': '执行测试',
                    'case_update': '修复用例',
                    'final_report': '输出测试报告',
                    // Scenario gen internal
                    'scenario_design': '设计业务场景',
                    'scenario_generate': '生成场景用例',
                    'scenario_run': '执行场景',
                    'scenario_fix': '修复场景',
                    'scenario_report': '场景报告',
                    // Code quality internal
                    'analyze_code': '分析代码',
                    'generate_report': '生成报告',
                    // RAG QA
                    'rag_qa': '知识库问答',
                    'rag_qa_agent': '知识库检索问答',
                }
                return labels[key] || key
            },
            /** 判断节点类型：orchestrator / sub_agent / node */
            _nodeType(key) {
                if (key === 'intent_recognition' || key === 'general_response') return 'orchestrator'
                const subAgents = ['case_gen', 'scenario_gen', 'code_quality', 'rag_qa']
                if (subAgents.includes(key)) return 'sub_agent'
                return 'node'
            },
            refreshThread() {
                if (this.isRunning) return
                this.threadId = this.generateUUID()
            },

            // ─── 重置 ─────────────────────────────────
            resetNodes() {
                this.agentTree = []
                this.activeSubAgentId = null
                this.activeWorkflowMode = null
                this.scenarioConfirmData = null
                this.modifyFeedback = ''
                this.showModifyInput = false
                this.scenarioExecSteps = []
            },
            /** 查找或创建 agentTree 中的项 */
            _ensureTreeItem(key, label, type) {
                let item = this.agentTree.find(t => t.key === key)
                if (!item) {
                    item = {
                        id: 'tree_' + key,
                        key, label, type,
                        status: 'pending',
                        summary: '',
                        expanded: true,
                        children: type === 'sub_agent' ? [] : undefined
                    }
                    this.agentTree.push(item)
                }
                if (label && !item.label) item.label = label
                return item
            },
            /** 完成 tree 中指定 key 之前的所有 pending 项 */
            _completeTreeBefore(key) {
                let found = false
                for (let i = this.agentTree.length - 1; i >= 0; i--) {
                    const g = this.agentTree[i]
                    if (g.key === key) { found = true; continue }
                    if (!found) continue
                    if (g.status === 'pending') g.status = 'completed'
                    if (g.children) {
                        g.children.forEach(c => { if (c.status === 'pending') c.status = 'completed' })
                    }
                }
            },
            /** 展开/收起子智能体 */
            toggleSubAgent(group) {
                group.expanded = !group.expanded
            },

            // ─── 创建 AI 消息 ─────────────────────────
            createAiMessage(nodeKey, nodeLabel, options = {}) {
                const msg = {
                    id: 'msg_' + Date.now() + '_' + nodeKey,
                    role: 'ai',
                    nodeKey: nodeKey,
                    nodeLabel: nodeLabel || this.getNodeLabel(nodeKey),
                    content: options.content || '',
                    status: options.status || 'streaming',
                    toolCalls: options.toolCalls || [],
                    interruptData: options.interruptData || null,
                    isReport: options.isReport || (nodeKey === 'final_report' || nodeKey === 'scenario_report'),
                    summary: options.summary || '',
                    timestamp: Date.now(),
                }
                this.messages.push(msg)
                return msg
            },

            // ─── SSE 流处理 ──────────────────────────
            async runSSEStream(payload, isResume = false) {
                if (!isResume) {
                    this.resetNodes()
                    this.toolCallLog = []
                }
                this.isRunning = true
                this.isResuming = false
                this._streamEndedNaturally = false

                this.abortController = new AbortController()
                let isAborted = false

                try {
                    const res = await fetch(aiTestCase, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                        signal: this.abortController.signal,
                    })

                    if (!res.ok) {
                        if (res.status === 400) {
                            throw new Error('请求格式错误：缺少 user 角色的消息')
                        } else if (res.status === 500) {
                            throw new Error('服务端异常，请稍后重试')
                        }
                        throw new Error(`HTTP ${res.status}: 请求失败`)
                    }

                    const reader = res.body.getReader()
                    const decoder = new TextDecoder()
                    let buffer = ''

                    while (true) {
                        const { done, value } = await reader.read()
                        if (done) break

                        buffer += decoder.decode(value, { stream: true })
                        const lines = buffer.split('\n')
                        buffer = lines.pop()

                        let eventType = ''
                        for (const line of lines) {
                            if (line.startsWith('event: ')) {
                                eventType = line.slice(7).trim()
                            } else if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.slice(6))
                                    this.handleSSEEvent(eventType, data)
                                } catch (e) {
                                    // 跳过解析失败的行
                                }
                            }
                        }
                    }
                } catch (err) {
                    if (err.name === 'AbortError') {
                        isAborted = true
                        this._forEachTreeNode(n => {
                            if (n.status === 'running') {
                                n.status = 'error'
                                n.summary = '用户手动停止'
                            }
                        })
                        this.messages.forEach(m => {
                            if (m.role === 'ai' && m.status === 'streaming') {
                                m.status = 'error'
                            }
                        })
                        this.toolCallLog.forEach(t => {
                            if (t.status === 'start') t.status = 'end'
                        })
                    } else {
                        const errMsg = err.message || '连接失败，请检查后端服务'
                        this._forEachTreeNode(n => {
                            if (n.status === 'running') n.status = 'error'
                        })
                        this.messages.forEach(m => {
                            if (m.role === 'ai' && m.status === 'streaming') m.status = 'error'
                        })
                        this.toolCallLog.forEach(t => {
                            if (t.status === 'start') t.status = 'end'
                        })
                        this.addSystemMessage('error', errMsg)
                    }
                } finally {
                    this.isRunning = false
                    this.abortController = null

                    // 非 abort、非 error、非 done、非 interrupt 的自然结束：补全剩余状态
                    if (!isAborted && !this._streamEndedNaturally) {
                        const hasInterrupt = this.messages.some(m => m.role === 'ai' && m.interruptData)
                        const hasError = this.messages.some(m => m.role === 'system' && m.nodeKey === 'error')
                        const hasDone = this.messages.some(m => m.role === 'system' && m.nodeKey === 'done')

                        if (!hasInterrupt && !hasError && !hasDone) {
                            // Bug 3 修复：把所有 streaming/running 的项补全为 completed
                            this.messages.forEach(m => {
                                if (m.role === 'ai' && m.status === 'streaming') {
                                    m.status = 'completed'
                                }
                            })
                            this._forEachTreeNode(n => {
                                if (n.status === 'running') {
                                    n.status = 'completed'
                                }
                            })
                            this.toolCallLog.forEach(t => {
                                if (t.status === 'start') t.status = 'end'
                            })
                            this.addSystemMessage('done', '测试用例生成流程已完成')
                        }
                    }
                }
            },

            // ─── 添加系统消息 ────────────────────────
            addSystemMessage(key, content) {
                // 避免重复
                if (this.messages.some(m => m.role === 'system' && m.nodeKey === key && m.content === content)) return
                this.messages.push({
                    id: 'msg_' + Date.now() + '_sys_' + key,
                    role: 'system',
                    nodeKey: key,
                    content: content,
                    timestamp: Date.now(),
                })
                this.scrollToBottom()
            },

            // ─── 输入框按键 ──────────────────────────
            onComposerKeydown(e) {
                if (e.shiftKey) {
                    // Shift+Enter → 换行，不做处理
                    return
                }
                // Enter → 发送
                e.preventDefault()
                this.startGeneration()
            },

            // ─── 快速入口 ────────────────────────────
            quickEntry(label, prompt) {
                this.userInput = prompt
                this.$nextTick(() => {
                    const ta = this.$el.querySelector('.composer-textarea textarea')
                    if (ta) ta.focus()
                })
            },

            // ─── 首次请求 ────────────────────────────
            async startGeneration() {
                if (!this.userInput.trim() || this.isRunning) return

                const input = this.userInput.trim()

                // 添加用户消息
                this.messages.push({
                    id: 'msg_' + Date.now() + '_user',
                    role: 'user',
                    content: input,
                    timestamp: Date.now(),
                })
                this.userInput = ''
                this.scrollToBottom()

                const payload = {
                    messages: [
                        { role: 'user', content: input }
                    ],
                    thread_id: this.threadId,
                    project_id: String(this.$route.params.project_id || ''),
                    enable_deep_thinking: this.enableDeepThinking
                }

                await this.runSSEStream(payload, false)
            },

            // ─── 中断恢复 ────────────────────────────
            async resumeGeneration() {
                if (this.isRunning) return

                // 先从活跃中断消息中提取数据（在清除前）
                const msg = this.activeInterruptMsg
                const interruptPayload = msg ? msg.interruptData : null
                if (!interruptPayload) {
                    this.$message.warning('没有活跃的中断')
                    return
                }

                const interruptType = interruptPayload.type || 'select_apis'
                this.isResuming = true

                // 提取后立即清除中断 UI
                if (msg) {
                    this.$set(msg, 'interruptData', null)
                }

                let payload = {
                    thread_id: this.threadId,
                    project_id: String(this.$route.params.project_id || '')
                }

                if (interruptType === 'select_apis') {
                    const apis = interruptPayload.available_apis || []
                    const selection = this.selectedApiIndices.map(i => apis[i]).filter(Boolean)
                    if (selection.length === 0) {
                        this.$message.warning('未选中任何接口，请重新选择')
                        this.isResuming = false
                        return
                    }
                    payload.selection = selection
                } else if (interruptType === 'scenario_confirm') {
                    payload.scenario_confirm = { action: 'confirm' }
                }

                await this.runSSEStream(payload, true)
                this.isResuming = false
            },

            // ─── SSE 事件分发 ───────────────────────
            handleSSEEvent(type, data) {
                switch (type) {
                    case 'node_start':
                        this.onNodeStart(data)
                        break
                    case 'message':
                        this.onMessage(data)
                        break
                    case 'tool_call':
                        this.onToolCall(data)
                        break
                    case 'tool_result':
                        this.onToolResult(data)
                        break
                    case 'node_end':
                        this.onNodeEnd(data)
                        break
                    case 'interrupt':
                        this.onInterrupt(data)
                        break
                    case 'done':
                        this.onDone(data)
                        break
                    case 'error':
                        this.onError(data)
                        break
                }
            },

            // ─── node_start ──────────────────────────
            onNodeStart(data) {
                const key = data.node
                if (!key) return
                const label = data.label || this.getDefaultNodeLabel(key)
                const nodeType = this._nodeType(key)

                // 模式检测
                if (!this.activeWorkflowMode) {
                    if (key === 'scenario_gen') this.activeWorkflowMode = 'scenario'
                    else if (key === 'case_gen') this.activeWorkflowMode = 'single'
                    else if (key === 'code_quality') this.activeWorkflowMode = 'code_quality'
                }

                if (nodeType === 'sub_agent') {
                    // 子智能体入口：创建顶层组
                    this.activeSubAgentId = key
                    const group = this._ensureTreeItem(key, label, 'sub_agent')
                    group.status = 'running'
                    group.expanded = true
                } else if (nodeType === 'orchestrator') {
                    this._ensureTreeItem(key, label, 'orchestrator').status = 'running'
                } else {
                    // 普通节点：挂到当前活跃的子智能体下
                    const parent = this.agentTree.find(t => t.type === 'sub_agent' && t.key === this.activeSubAgentId)
                    if (parent) {
                        let child = parent.children.find(c => c.key === key)
                        if (!child) {
                            child = {
                                id: 'node_' + parent.key + '_' + key,
                                key, label,
                                type: 'node',
                                status: 'running',
                                summary: '',
                                toolCount: 0
                            }
                            parent.children.push(child)
                        } else {
                            child.status = 'running'
                        }
                    }
                }

                // 场景执行节点重置
                if (key === 'scenario_run') this.scenarioExecSteps = []

                // 创建 AI 对话消息（避免重复）
                const exists = this.messages.some(m => m.role === 'ai' && m.nodeKey === key && m.status === 'streaming')
                if (!exists) {
                    this.createAiMessage(key, label)
                }
                this.scrollToBottom()
            },

            // ─── message（流式文本）────────────────────
            onMessage(data) {
                const content = data.content || ''
                const nodeKey = data.node || ''
                if (!content) return

                let msg = [...this.messages].reverse().find(m => m.role === 'ai' && m.nodeKey === nodeKey)
                if (!msg) {
                    msg = this.createAiMessage(nodeKey, null, { content: '' })
                }
                msg.content += content

                // 确保对应节点处于 running 状态
                const node = this._findTreeNode(nodeKey)
                if (node && node.status === 'pending') {
                    node.status = 'running'
                }
                this.scrollToBottom()
            },

            // ─── tool_call（工具调用开始）───────────────
            onToolCall(data) {
                // 提取输入参数（排除已知的元字段）
                const metaKeys = ['tool', 'status', 'node', 'timestamp']
                const extractPayload = (raw) => {
                    const filtered = {}
                    for (const key of Object.keys(raw)) {
                        if (!metaKeys.includes(key)) {
                            filtered[key] = raw[key]
                        }
                    }
                    return Object.keys(filtered).length > 0 ? filtered : undefined
                }

                // SSE 可能不带 node 字段，从上下文推导当前所属节点
                const nodeKey = this.resolveCurrentNodeKey(data.node)
                // 递增子节点的工具计数
                const child = this._findTreeNode(nodeKey)
                if (child && child.type === 'node' && child.toolCount !== undefined) {
                    child.toolCount++
                }
                const inputData = extractPayload(data)

                // 场景步骤执行追踪
                if (data.tool === 'execute_scenario_step' && data.status === 'start') {
                    this.trackScenarioStepStart(inputData)
                }

                // 始终更新右侧工具面板（独立于 AI 消息状态）
                if (data.status === 'start') {
                    this.addToolCallEntry(data.tool, 'start', inputData, undefined, nodeKey)
                } else if (data.status === 'end') {
                    this.updateToolCallEntry(data.tool, 'end', extractPayload(data))
                }

                // Attach to the newest AI message for this node
                let activeMsg = [...this.messages].reverse().find(m => m.role === 'ai' && m.nodeKey === nodeKey)
                if (!activeMsg) {
                    activeMsg = [...this.messages].reverse().find(m => m.role === 'ai' && m.status === 'streaming')
                }
                if (!activeMsg) return

                if (data.status === 'start') {
                    activeMsg.toolCalls.push({
                        tool: data.tool,
                        status: 'start',
                        input: inputData,
                        output: undefined,
                        _expanded: false,
                        timestamp: Date.now(),
                    })
                } else if (data.status === 'end') {
                    const tc = activeMsg.toolCalls.find(t => t.tool === data.tool && t.status === 'start')
                    if (tc) {
                        tc.status = 'end'
                        tc.output = extractPayload(data)
                        tc._expanded = false
                    }
                }
            },

            // ─── tool_result（工具返回结果）──────────────
            onToolResult(data) {
                const result = data.result
                const outputData = result ? (result.content !== undefined ? result.content : result) : undefined

                // 场景步骤执行结果追踪
                if (data.tool === 'execute_scenario_step' && result) {
                    this.trackScenarioStepResult(result)
                }

                // 始终更新右侧工具面板（独立于 AI 消息状态）
                this.updateToolCallEntry(data.tool, 'end', outputData)

                // Attach to the newest AI message for this node
                let activeMsg = [...this.messages].reverse().find(m => m.role === 'ai' && m.nodeKey === data.node)
                if (!activeMsg) {
                    activeMsg = [...this.messages].reverse().find(m => m.role === 'ai' && m.status === 'streaming')
                }
                if (!activeMsg) return

                const tc = activeMsg.toolCalls.find(t => t.tool === data.tool && t.status === 'start')
                if (tc) {
                    tc.status = 'end'
                    tc.output = outputData
                    tc._expanded = false
                } else {
                    activeMsg.toolCalls.push({
                        tool: data.tool,
                        status: 'end',
                        input: undefined,
                        output: outputData,
                        _expanded: false,
                        timestamp: Date.now(),
                    })
                }
            },

            // ─── 切换工具卡片展开/收起（消息内嵌）─────
            toggleToolExpand(tc) {
                this.$set(tc, '_expanded', !tc._expanded)
            },

            // ─── 工具调用日志（右侧面板）─────────────
            /**
             * 解析当前工具调用所属的节点。
             * 优先级：SSE data.node → 活跃 AI 消息的 nodeKey → running 状态的 workflow 节点
             */
            resolveCurrentNodeKey(ssEventNode) {
                if (ssEventNode) return ssEventNode
                const activeMsg = [...this.messages].reverse().find(
                    m => m.role === 'ai' && m.status === 'streaming'
                )
                if (activeMsg && activeMsg.nodeKey) return activeMsg.nodeKey
                let runningKey = ''
                this._forEachTreeNode(n => { if (n.status === 'running') runningKey = n.key })
                return runningKey
            },
            addToolCallEntry(tool, status, input, output, nodeKey) {
                const entry = {
                    id: 'tl_' + Date.now() + '_' + tool + '_' + Math.random().toString(36).substr(2, 5),
                    tool: tool,
                    status: status,
                    input: input,
                    output: output,
                    nodeKey: nodeKey || '',
                    _expanded: false,
                    timestamp: Date.now(),
                }
                this.toolCallLog.push(entry)
            },
            updateToolCallEntry(tool, status, output) {
                // 找到最近一个匹配的 start 状态条目
                const entry = [...this.toolCallLog].reverse().find(
                    t => t.tool === tool && t.status === 'start'
                )
                if (entry) {
                    // Vue 2: 用 $set 确保响应式更新
                    this.$set(entry, 'status', status)
                    if (output !== undefined) this.$set(entry, 'output', output)
                } else {
                    // 没找到 start 条目，从上下文推导节点后创建已完成条目
                    const nodeKey = this.resolveCurrentNodeKey('')
                    this.addToolCallEntry(tool, status, undefined, output, nodeKey)
                }
            },
            toggleToolPanelItem(tc) {
                this.$set(tc, '_expanded', !tc._expanded)
            },
            /** 场景步骤执行开始追踪 */
            trackScenarioStepStart(inputData) {
                if (!inputData) return
                // 尝试从输入参数推断步骤信息
                const stepIdx = inputData.step_index !== undefined ? inputData.step_index : this.scenarioExecSteps.length
                const apiName = inputData.api_name || ('步骤 ' + (stepIdx + 1))
                const existing = this.scenarioExecSteps.find(s => s.step === stepIdx)
                if (!existing) {
                    this.scenarioExecSteps.push({
                        step: stepIdx,
                        api_name: apiName,
                        status: 'running',
                        case_id: inputData.case_id || null,
                    })
                } else {
                    this.$set(existing, 'status', 'running')
                }
            },
            /** 场景步骤执行结果追踪 */
            trackScenarioStepResult(result) {
                if (!result || !result.data || !result.data.result) return
                const stepResults = result.data.result
                stepResults.forEach(r => {
                    const existing = this.scenarioExecSteps.find(s => s.case_id === r.case_id)
                    if (existing) {
                        this.$set(existing, 'status', r.success ? 'success' : 'error')
                    } else {
                        // 按 case_id 找不到，尝试按步骤数匹配未命名的项
                        const pendingItem = this.scenarioExecSteps.find(s => !s.case_id && s.status === 'running')
                        if (pendingItem) {
                            this.$set(pendingItem, 'status', r.success ? 'success' : 'error')
                            if (r.case_id) this.$set(pendingItem, 'case_id', r.case_id)
                        }
                    }
                })
            },
            /** 点击执行树节点 → 切换到工具标签并筛选 */
            focusToolNode(nodeKey) {
                if (this.toolPanelCollapsed) {
                    this.toolPanelCollapsed = false
                }
                this.monitorTab = 'tools'
                this.activeToolFilter = this.activeToolFilter === nodeKey ? '__all__' : nodeKey
            },

            // ─── 格式化工具数据 ──────────────────────
            formatToolData(data) {
                if (data === undefined || data === null) return ''
                try {
                    if (typeof data === 'string') {
                        // 尝试解析 JSON 字符串
                        try {
                            return JSON.stringify(JSON.parse(data), null, 2)
                        } catch (e) {
                            return data
                        }
                    }
                    return JSON.stringify(data, null, 2)
                } catch (e) {
                    return String(data)
                }
            },

            // ─── node_end ────────────────────────────
            onNodeEnd(data) {
                const key = data.node
                const nodeType = this._nodeType(key)
                const label = data.label || this.getDefaultNodeLabel(key)

                // 更新 agentTree
                if (nodeType === 'sub_agent') {
                    const group = this.agentTree.find(t => t.key === key)
                    if (group) {
                        group.status = 'completed'
                        if (data.summary) group.summary = data.summary
                    }
                } else if (nodeType === 'orchestrator') {
                    const item = this.agentTree.find(t => t.key === key)
                    if (item) {
                        item.status = 'completed'
                        if (data.summary) item.summary = data.summary
                    }
                } else {
                    // 普通节点：挂在父级子智能体下
                    const parent = this.agentTree.find(t => t.type === 'sub_agent' && t.key === this.activeSubAgentId)
                    if (parent) {
                        let child = parent.children.find(c => c.key === key)
                        if (!child) {
                            child = {
                                id: 'node_' + parent.key + '_' + key,
                                key, label, type: 'node',
                                status: 'completed', summary: data.summary || '', toolCount: 0
                            }
                            parent.children.push(child)
                        } else {
                            child.status = 'completed'
                            if (data.summary) child.summary = data.summary
                        }
                    }
                }

                // 更新对话消息（取最新一条，多轮对话可能有同 key 的多条消息）
                const msg = [...this.messages].reverse().find(m => m.role === 'ai' && m.nodeKey === key)
                if (msg) {
                    msg.status = 'completed'
                    if (data.summary) {
                        msg.summary = data.summary
                        if (!msg.content && data.summary) msg.content = data.summary
                    }
                }
                this.scrollToBottom()
            },

            // ─── interrupt（内联选择）──────────────────
            onInterrupt(data) {
                this.isRunning = false
                const interruptPayload = data.data || data
                const interruptType = interruptPayload.type || 'select_apis'
                this.selectedApiIndices = []

                if (interruptType === 'select_apis') {
                    // ── API 选择中断：创建独立消息置于底部 ──
                    this._completeTreeBefore('select_apis')

                    const apis = interruptPayload.available_apis || []
                    if (apis.length > 0) {
                        this.selectedApiIndices = apis.map((_, i) => i)
                    }

                    // 完成原有的 select_apis 节点消息
                    const selectNode = this._findTreeNode('select_apis')
                    if (selectNode) {
                        selectNode.status = 'completed'
                        if (interruptPayload.message) selectNode.summary = interruptPayload.message
                    }
                    const selectMsg = this.messages.find(m => m.role === 'ai' && m.nodeKey === 'select_apis')
                    if (selectMsg) {
                        selectMsg.status = 'completed'
                    }

                    // 创建全新的中断消息置于对话底部，确保用户无需滚动
                    const interruptMsg = this.createAiMessage('select_apis__interrupt', '选取接口', {
                        status: 'completed',
                        content: interruptPayload.message || ''
                    })
                    this.$set(interruptMsg, 'interruptData', interruptPayload)

                } else if (interruptType === 'scenario_confirm') {
                    // ── 场景确认中断：创建独立消息置于底部 ──
                    this._completeTreeBefore('scenario_design')
                    this.scenarioConfirmData = interruptPayload
                    this.showModifyInput = false
                    this.modifyFeedback = ''

                    // 完成原有的 scenario_design 节点消息（保留其流式内容）
                    const designNode = this._findTreeNode('scenario_design')
                    if (designNode) {
                        designNode.status = 'completed'
                        if (interruptPayload.message) designNode.summary = interruptPayload.message
                    }
                    const designMsg = this.messages.find(m => m.role === 'ai' && m.nodeKey === 'scenario_design')
                    if (designMsg) {
                        designMsg.status = 'completed'
                    }

                    // 创建全新的中断消息置于对话底部，确保用户无需滚动
                    const confirmMsg = this.createAiMessage('scenario_design__confirm', '设计场景', {
                        status: 'completed',
                        content: interruptPayload.message || ''
                    })
                    this.$set(confirmMsg, 'interruptData', interruptPayload)
                }

                this.scrollToBottom()
            },

            // ─── 确认选择 ─────────────────────────────
            confirmSelection() {
                if (this.selectedApiIndices.length === 0) {
                    this.$message.warning('请至少选择一个接口')
                    return
                }
                // resumeGeneration 会从 activeInterruptMsg 提取数据并清除
                this.resumeGeneration()
            },

            // ─── 取消选择 ─────────────────────────────
            cancelSelection() {
                const msg = this.activeInterruptMsg
                if (msg) {
                    this.$set(msg, 'interruptData', null)
                }
                this.selectedApiIndices = []
                this.addSystemMessage('cancelled', '已取消接口选择')
                this.$message.info('已取消选择')
            },

            // ─── 场景确认 / 修改 / 取消 ──────────────
            confirmScenario() {
                const msg = this.messages.find(m => m.role === 'ai' && m.interruptData && m.interruptData.type === 'scenario_confirm')
                if (msg) this.$set(msg, 'interruptData', null)
                this.scenarioConfirmData = null
                this.resumeWithScenarioConfirm('confirm')
            },
            cancelScenario() {
                const msg = this.messages.find(m => m.role === 'ai' && m.interruptData && m.interruptData.type === 'scenario_confirm')
                if (msg) this.$set(msg, 'interruptData', null)
                this.scenarioConfirmData = null
                this.showModifyInput = false
                this.addSystemMessage('cancelled', '已取消场景方案')
                this.$message.info('已取消')
            },
            submitModifyScenario() {
                if (!this.modifyFeedback.trim()) {
                    this.$message.warning('请输入修改意见')
                    return
                }
                const msg = this.messages.find(m => m.role === 'ai' && m.interruptData && m.interruptData.type === 'scenario_confirm')
                if (msg) this.$set(msg, 'interruptData', null)
                this.scenarioConfirmData = null
                this.showModifyInput = false
                this.resumeWithScenarioConfirm('modify', this.modifyFeedback.trim())
            },
            async resumeWithScenarioConfirm(action, feedback) {
                if (this.isRunning) return
                this.isResuming = true
                const payload = {
                    thread_id: this.threadId,
                    project_id: String(this.$route.params.project_id || ''),
                    scenario_confirm: { action }
                }
                if (feedback) payload.scenario_confirm.feedback = feedback
                await this.runSSEStream(payload, true)
                this.isResuming = false
            },

            // ─── 切换 API 选中 ───────────────────────
            toggleApiSelection(index) {
                const pos = this.selectedApiIndices.indexOf(index)
                if (pos > -1) {
                    this.selectedApiIndices.splice(pos, 1)
                } else {
                    this.selectedApiIndices.push(index)
                }
            },

            // ─── done ────────────────────────────────
            onDone(data) {
                this._streamEndedNaturally = true
                this._forEachTreeNode(n => {
                    if (n.status === 'running') n.status = 'completed'
                })
                this.messages.forEach(m => {
                    if (m.role === 'ai' && m.status === 'streaming') m.status = 'completed'
                })
                this.toolCallLog.forEach(t => {
                    if (t.status === 'start') t.status = 'end'
                })
                this.isRunning = false
                this.addSystemMessage('done', '测试用例生成流程已完成')
            },

            // ─── error ───────────────────────────────
            onError(data) {
                const errMsg = data.message || '未知错误'
                this._forEachTreeNode(n => {
                    if (n.status === 'running') n.status = 'error'
                })
                this.messages.forEach(m => {
                    if (m.role === 'ai' && m.status === 'streaming') m.status = 'error'
                })
                this.addSystemMessage('error', errMsg)
            },

            // ─── 重试最后一条用户消息 ────────────────
            retryLast() {
                const lastUser = [...this.messages].reverse().find(m => m.role === 'user')
                if (!lastUser) {
                    this.$message.warning('没有可重试的消息')
                    return
                }
                const content = lastUser.content
                // Remove the user message and everything after it
                const idx = this.messages.indexOf(lastUser)
                this.messages = this.messages.slice(0, idx)
                // Reset execution state
                this.resetNodes()
                this.toolCallLog = []
                this.toolPanelCollapsed = false
                this.activeToolFilter = '__all__'
                this.monitorTab = 'tree'
                this.selectedApiIndices = []
                this.isResuming = false
                this._streamEndedNaturally = false
                this.scenarioConfirmData = null
                this.modifyFeedback = ''
                this.showModifyInput = false
                this.scenarioExecSteps = []
                // Resubmit
                this.userInput = content
                this.$nextTick(() => this.startGeneration())
            },

            // ── 中止生成 ────────────────────────────
            abortGeneration() {
                if (this.abortController) {
                    this.abortController.abort()
                }
                this.isRunning = false
                this.$message.info('已停止生成')
            },

            // ─── 简易 Markdown 渲染 ──────────────────
            renderMarkdown(text) {
                if (!text) return ''
                let html = text
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
                html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
                html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')
                html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
                html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
                html = html.replace(/\n/g, '<br>')
                html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
                html = html.replace(/^---$/gm, '<hr>')
                return html
            },

            // ─── 滚动 ────────────────────────────────
            scrollToBottom() {
                this.$nextTick(() => {
                    const el = this.$refs.chatMessages
                    if (el) {
                        el.scrollTop = el.scrollHeight
                    }
                })
            },

            // ─── 清空 ────────────────────────────────
            clearAll() {
                this.userInput = ''
                this.threadId = this.generateUUID()
                this.resetNodes()
                this.messages = []
                this.toolCallLog = []
                this.toolPanelCollapsed = false
                this.activeToolFilter = '__all__'
                this.monitorTab = 'tree'
                this.selectedApiIndices = []
                this.isResuming = false
                this.isRunning = false
                this._streamEndedNaturally = false
                this.scenarioConfirmData = null
                this.modifyFeedback = ''
                this.showModifyInput = false
                this.scenarioExecSteps = []
                if (this.abortController) {
                    this.abortController.abort()
                    this.abortController = null
                }
            },

            // ─── 重置并新建 ──────────────────────────
            resetAndNew() {
                this.userInput = ''
                this.threadId = this.generateUUID()
                this.resetNodes()
                this.messages = []
                this.toolCallLog = []
                this.toolPanelCollapsed = false
                this.activeToolFilter = '__all__'
                this.monitorTab = 'tree'
                this.selectedApiIndices = []
                this.isResuming = false
                this._streamEndedNaturally = false
                this.scenarioConfirmData = null
                this.modifyFeedback = ''
                this.showModifyInput = false
                this.scenarioExecSteps = []
            }
        },
        beforeDestroy() {
            if (this.abortController) {
                this.abortController.abort()
            }
        }
    }
</script>

<style scoped>
/* ================================================================
   "Precision Chat" — Light theme aligned with the Precision Console
   design system. Clean, professional AI agent workspace.
   ================================================================ */

/* ── Design tokens (local, derived from vars.scss) ── */
.ai-testcase-container {
    --pc-primary: #4F6EF7;
    --pc-primary-hover: #3D5CE5;
    --pc-primary-soft: rgba(79, 110, 247, 0.07);
    --pc-primary-wash: rgba(79, 110, 247, 0.11);
    --pc-page-bg: #F3F4F6;
    --pc-surface: #FFFFFF;
    --pc-surface-raised: #F9FAFB;
    --pc-border: #E5E7EB;
    --pc-border-light: #F3F4F6;
    --pc-text: #111827;
    --pc-text-secondary: #4B5563;
    --pc-text-muted: #9CA3AF;
    --pc-success: #0EAD69;
    --pc-warning: #F59E0B;
    --pc-danger: #EF4444;
    --pc-shadow-xs: 0 1px 2px rgba(0,0,0,0.03);
    --pc-shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
    --pc-shadow-md: 0 4px 6px -1px rgba(0,0,0,0.04), 0 10px 15px -3px rgba(0,0,0,0.06);
    --pc-radius-sm: 6px;
    --pc-radius-md: 8px;
    --pc-radius-lg: 10px;
    --pc-radius-xl: 12px;
}

.ai-testcase-container {
    padding: 12px 20px;
    background: var(--pc-page-bg);
    min-height: calc(100vh - 84px);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: var(--pc-text);
}

.main-row { margin: 0 !important; }

/* ===== Left panel — removed (merged into right monitor panel) ===== */

/* ===== Agent tree (inside monitor panel) ===== */
.monitor-tree { padding: 8px 8px; }
.agent-tree { display: flex; flex-direction: column; gap: 1px; }

.tree-item { display: flex; align-items: center; gap: 6px; padding: 5px 4px; cursor: pointer; position: relative; transition: all 0.2s; border-radius: 6px; }
.tree-item:hover { background: rgba(79,110,247,.04); }

.tree-dot { width: 16px; height: 16px; border-radius: 50%; background: #E5E7EB; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.3s; position: relative; z-index: 1; }
.tree-dot i { font-size: 8px; color: #fff; }

/* ── Tree node icons ── */
.tree-node-icon { font-size: 13px; color: var(--pc-text-muted); flex-shrink: 0; width: 16px; text-align: center; transition: color 0.2s; }
.tree-item.is-active .tree-node-icon { color: var(--pc-primary); }
.tree-item.is-done .tree-node-icon { color: var(--pc-success); }
.tree-item.is-error .tree-node-icon { color: var(--pc-danger); }

/* Orchestrator */
.tree-orch { padding: 6px 6px; gap: 7px; }
.orch-dot { width: 8px; height: 8px; }
.tree-orch.is-done .orch-dot { background: #9CA3AF; }
.tree-orch.is-active .orch-dot { background: var(--pc-primary); box-shadow: 0 0 0 4px rgba(79,110,247,.2); }
.tree-orch .tree-label { font-size: 12px; color: var(--pc-text-muted); font-weight: 500; }

/* Sub-agent header */
.tree-sub-header { padding: 6px 4px; margin-top: 3px; border-radius: 8px; }
.tree-arrow { font-size: 10px; color: var(--pc-text-muted); transition: transform 0.15s; flex-shrink: 0; }
.tree-arrow.is-open { transform: rotate(90deg); }
.sub-dot { width: 20px; height: 20px; border: 2px solid var(--pc-primary); background: #fff; }
.sub-dot.is-done { background: var(--pc-primary); border-color: var(--pc-primary); }
.sub-dot.is-running { border-color: var(--pc-primary); box-shadow: 0 0 0 4px rgba(79,110,247,.2); animation: tree-pulse 1.8s infinite; }
.sub-label { font-weight: 700; color: var(--pc-text); font-size: 13px; }
.tree-badge { font-size: 10px; color: var(--pc-primary); background: var(--pc-primary-soft); padding: 2px 7px; border-radius: 8px; margin-left: auto; font-weight: 500; }

/* Children */
.tree-children { padding-left: 18px; border-left: 1.5px solid var(--pc-border); margin-left: 9px; }
.tree-node { gap: 5px; padding: 5px 4px; border-radius: 6px; }
.node-dot { width: 10px; height: 10px; }
.node-dot.is-done { background: var(--pc-success); }
.node-dot.is-running { background: var(--pc-primary); box-shadow: 0 0 0 4px rgba(79,110,247,.2); animation: tree-pulse 2s infinite; }
.node-label { font-size: 12px; color: var(--pc-text-secondary); }
.tree-node.is-done .node-label { color: var(--pc-text-muted); }
.tree-node.is-active .node-label { color: var(--pc-text); font-weight: 600; }
.tree-node.is-error .node-dot { background: var(--pc-danger); }
.tree-node.is-error .node-label { color: var(--pc-danger); }

/* ── Node filtered (active in tool tab) ── */
.tree-node.is-filtered { background: var(--pc-primary-soft); border: 1px solid rgba(79,110,247,.15); }
.tree-node.is-filtered .node-label { color: var(--pc-primary); font-weight: 600; }
.tree-node.is-filtered .tree-node-icon { color: var(--pc-primary); }

.tree-tool-count { font-size: 10px; color: var(--pc-text-muted); background: #F3F4F6; padding: 1px 6px; border-radius: 6px; margin-left: auto; font-weight: 500; }
.tree-node.is-filtered .tree-tool-count { color: var(--pc-primary); background: rgba(79,110,247,.1); }
.tree-line-v { display: none; }

@keyframes tree-pulse {
    0% { box-shadow: 0 0 0 0 rgba(79,110,247,.25); }
    70% { box-shadow: 0 0 0 10px rgba(79,110,247,0); }
    100% { box-shadow: 0 0 0 0 rgba(79,110,247,0); }
}

/* ================================================================
   中间面板 — 对话区域
   ================================================================ */
.center-col { display: flex; flex-direction: column; }
.right-col { display: flex; flex-direction: column; }

.chat-container {
    display: flex; flex-direction: column;
    height: calc(100vh - 156px); min-height: 480px;
    background: var(--pc-surface);
    border-radius: var(--pc-radius-xl);
    box-shadow: var(--pc-shadow-md);
    overflow: hidden;
    border: 1px solid var(--pc-border);
}

/* ── 对话头部 ── */
.chat-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 20px;
    border-bottom: 1px solid var(--pc-border);
    background: var(--pc-surface);
    flex-shrink: 0;
}
.chat-header-left { display: flex; align-items: center; gap: 16px; }
.chat-header-title {
    font-size: 15px; font-weight: 600; color: var(--pc-text);
    display: flex; align-items: center; gap: 7px;
}
.chat-header-title i { color: var(--pc-primary); font-size: 16px; }
.header-think-switch { font-size: 12px; }
.chat-header-right { display: flex; align-items: center; gap: 6px; }
.thread-label { font-size: 11px; color: var(--pc-text-muted); }
.thread-tag { font-family: 'Fira Code', 'Consolas', monospace; font-size: 10px; }
.thread-refresh { padding: 0 2px; color: var(--pc-text-muted); }
.thread-refresh:hover { color: var(--pc-primary); }

/* ── 消息列表 ── */
.chat-messages {
    flex: 1; overflow-y: auto; padding: 20px 24px;
    display: flex; flex-direction: column; gap: 16px;
    scroll-behavior: smooth;
    background: #FAFBFC;
}

/* ── 欢迎界面 ── */
.welcome-area {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    flex: 1; gap: 16px;
}
.welcome-header {
    display: flex; flex-direction: column;
    align-items: center; gap: 4px;
}
.welcome-title { font-size: 16px; font-weight: 700; color: var(--pc-text); }
.welcome-sub { font-size: 12px; color: var(--pc-text-muted); }

/* ── 智能体快速入口卡 ── */
.quick-entries {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 8px; max-width: 520px; width: 100%;
}
.quick-card {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 14px;
    background: var(--pc-surface);
    border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius-md);
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
    flex: 0 0 auto;
}
.quick-card:hover {
    border-color: var(--pc-primary);
    box-shadow: 0 2px 8px rgba(79,110,247,.08);
    transform: translateY(-1px);
}
.quick-card:active { transform: translateY(0); }
.quick-card-icon {
    width: 32px; height: 32px; border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.quick-card-icon i { font-size: 15px; color: #fff; }
.qc-case { background: linear-gradient(135deg, #4F6EF7, #3D5CE5); }
.qc-scenario { background: linear-gradient(135deg, #0EAD69, #0A8A52); }
.qc-knowledge { background: linear-gradient(135deg, #F59E0B, #D97706); }
.quick-card-body { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.quick-card-title { font-size: 13px; font-weight: 600; color: var(--pc-text); white-space: nowrap; }
.quick-card-desc { font-size: 11px; color: var(--pc-text-muted); white-space: nowrap; }
.quick-card-arrow { display: none; }

/* ── 消息包裹器 ── */
.chat-msg-wrapper {
    display: flex; flex-direction: column;
    animation: msg-fade-in 0.28s ease-out;
}
.msg-role-user { align-items: flex-end; }
.msg-role-ai { align-items: flex-start; }
.msg-role-system { align-items: center; }

@keyframes msg-fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── 用户消息 ── */
.msg-user { max-width: 78%; display: flex; flex-direction: column; align-items: flex-end; }
.msg-user-bubble {
    background: var(--pc-primary);
    color: #fff;
    padding: 10px 16px;
    border-radius: 14px 6px 14px 14px;
    font-size: 13px; line-height: 1.6;
    white-space: pre-wrap; word-break: break-word;
    box-shadow: 0 2px 8px rgba(79,110,247,.18);
}
.msg-user-text { font-size: 13px; }
.msg-user-meta { margin-top: 3px; padding-right: 6px; }

/* ── AI 消息卡片 ── */
.msg-ai { max-width: 92%; display: flex; flex-direction: column; }
.msg-ai-card {
    background: var(--pc-surface);
    border-radius: var(--pc-radius-md);
    border: 1px solid var(--pc-border);
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.msg-ai-card.is-streaming { border-color: var(--pc-primary); box-shadow: 0 0 0 1px rgba(79,110,247,.12); }
.msg-ai-card.is-done { border-color: var(--pc-border); }
.msg-ai-card.is-error { border-color: var(--pc-danger); }

.msg-ai-header {
    display: flex; align-items: center; gap: 7px;
    padding: 8px 14px;
    background: var(--pc-surface-raised);
    border-bottom: 1px solid var(--pc-border-light);
}
.msg-ai-dot { width: 7px; height: 7px; border-radius: 50%; background: #D1D5DB; flex-shrink: 0; }
.msg-ai-dot.dot-running { background: var(--pc-primary); animation: dot-pulse 1.5s infinite; }
.msg-ai-dot.dot-done { background: var(--pc-success); }
.msg-ai-dot.dot-error { background: var(--pc-danger); }
@keyframes dot-pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

.msg-ai-node-label { font-size: 12px; font-weight: 600; color: var(--pc-text); flex: 1; }
.msg-ai-status { font-size: 10px; color: var(--pc-text-muted); background: #F3F4F6; padding: 2px 8px; border-radius: 8px; }
.msg-ai-card.is-streaming .msg-ai-status { color: var(--pc-primary); background: var(--pc-primary-soft); }
.msg-ai-card.is-done .msg-ai-status { color: var(--pc-success); }
.msg-ai-card.is-error .msg-ai-status { color: var(--pc-danger); }
.msg-ai-body { padding: 12px 16px; }
.msg-text { font-size: 13px; line-height: 1.7; color: var(--pc-text); white-space: pre-wrap; word-break: break-word; }
.msg-summary { font-size: 12px; color: var(--pc-text-secondary); }
.cursor-blink { display: inline-block; width: 2px; height: 15px; background: var(--pc-primary); margin-left: 2px; animation: dot-pulse 0.8s infinite; vertical-align: text-bottom; }

/* Markdown 报告 */
.msg-report { font-size: 14px; line-height: 1.8; color: var(--pc-text); }
.msg-report ::v-deep h2 { font-size: 17px; font-weight: 700; color: var(--pc-text); border-bottom: 2px solid var(--pc-primary); padding-bottom: 6px; margin: 14px 0 10px; }
.msg-report ::v-deep h3 { font-size: 15px; font-weight: 600; color: var(--pc-text); margin: 12px 0 6px; }
.msg-report ::v-deep h4 { font-size: 13px; font-weight: 600; color: var(--pc-text); margin: 8px 0 4px; }
.msg-report ::v-deep strong { color: var(--pc-text); font-weight: 600; }
.msg-report ::v-deep code { background: #F3F4F6; padding: 1px 5px; border-radius: 3px; font-family: 'Fira Code','Consolas',monospace; font-size: 11px; color: #e83e8c; }
.msg-report ::v-deep li { margin: 3px 0; padding-left: 4px; list-style: disc inside; }
.msg-report ::v-deep hr { border: none; border-top: 1px solid var(--pc-border); margin: 10px 0; }
.msg-ai-meta { margin-top: 4px; padding-left: 6px; }

/* ── 消息时间 ── */
.msg-time { font-size: 10px; color: var(--pc-text-muted); }

/* ── Inline tool cards ── */
.msg-ai-tools { margin-top: 4px; padding: 0 14px 8px; display: flex; flex-direction: column; gap: 5px; }
.inline-tool {
    background: #F9FAFB; border: 1px solid var(--pc-border);
    border-radius: var(--pc-radius-sm); overflow: hidden;
    cursor: pointer; transition: border-color 0.2s;
}
.inline-tool:hover { border-color: #D1D5DB; }
.inline-tool.is-expanded { border-color: var(--pc-primary); }
.inline-tool-header { display: flex; align-items: center; gap: 7px; padding: 6px 10px; font-size: 11px; }
.inline-tool-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--pc-warning); flex-shrink: 0; }
.inline-tool-dot.dot-end { background: var(--pc-success); }
.inline-tool-name { color: var(--pc-text); font-weight: 500; flex: 1; }
.inline-tool-status { color: var(--pc-text-muted); font-size: 10px; }
.inline-tool.is-end .inline-tool-status { color: var(--pc-success); }
.inline-tool-arrow { font-size: 9px; color: var(--pc-text-muted); transition: transform 0.2s; }
.inline-tool-arrow.is-open { transform: rotate(180deg); }
.inline-tool-body { padding: 0 10px 8px; border-top: 1px solid var(--pc-border); }
.inline-tool-section { margin-top: 6px; }
.inline-tool-section-label { font-size: 9px; color: var(--pc-text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; display: block; }
.inline-tool-pre {
    background: #F3F4F6; color: var(--pc-text-secondary); font-size: 10px;
    padding: 6px 8px; border-radius: 4px; max-height: 140px;
    overflow-y: auto; margin: 0;
    font-family: 'SF Mono','Fira Code','Consolas',monospace;
    white-space: pre-wrap; word-break: break-all;
}
.inline-tool-empty { color: var(--pc-text-muted); font-size: 10px; padding: 6px 0; }

/* ── 内联 API 选择 ── */
.msg-ai-select { border-top: 1px solid var(--pc-border); }
.select-notice {
    display: flex; align-items: flex-start; gap: 8px;
    padding: 10px 16px;
    background: var(--pc-primary-soft);
    color: var(--pc-primary); font-size: 12px; line-height: 1.5;
    border-bottom: 1px solid rgba(79,110,247,.1);
}
.select-notice i { margin-top: 1px; flex-shrink: 0; font-size: 14px; }
.select-list { max-height: 260px; overflow-y: auto; padding: 10px 14px; background: #FAFBFC; }
.select-api-item {
    padding: 10px 12px; margin-bottom: 5px;
    border: 1px solid var(--pc-border); border-radius: var(--pc-radius-md);
    background: var(--pc-surface); transition: all 0.15s ease; cursor: pointer;
}
.select-api-item:last-child { margin-bottom: 0; }
.select-api-item:hover { border-color: #C7CDE8; background: #FAFBFF; }
.select-api-item.is-selected {
    border-color: var(--pc-primary); background: var(--pc-primary-soft);
    box-shadow: 0 0 0 1px rgba(79,110,247,.1);
}
.select-checkbox { display: block; width: 100%; }
.select-checkbox ::v-deep .el-checkbox__label { width: 100%; padding-left: 8px; }
.select-api-content { width: 100%; }
.select-api-top { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.select-api-method { flex-shrink: 0; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; }
.select-api-path { font-family: 'Fira Code','Consolas',monospace; font-size: 12px; color: var(--pc-text); font-weight: 500; }
.select-api-bottom { display: flex; align-items: center; gap: 8px; margin-top: 2px; }
.select-api-name { font-size: 11px; color: var(--pc-text-secondary); }
.select-api-type { font-size: 9px; color: var(--pc-text-muted); background: #F3F4F6; padding: 1px 5px; border-radius: 3px; }
.select-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 16px; background: var(--pc-surface);
    border-top: 1px solid var(--pc-border);
}
.select-count { font-size: 12px; color: var(--pc-text-secondary); }
.select-count strong { color: var(--pc-primary); font-weight: 700; }
.select-actions { display: flex; gap: 6px; }

/* ── 系统消息 ── */
.msg-system { max-width: 65%; }
.msg-system-bubble {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 16px; font-size: 12px; font-weight: 500;
}
.sys-done { background: #f0faf4; color: var(--pc-success); border: 1px solid #d4f0e0; }
.sys-done i { font-size: 16px; flex-shrink: 0; }
.sys-done .el-button { margin-left: 6px; flex-shrink: 0; }
.sys-error { background: #fef5f5; color: var(--pc-danger); border: 1px solid #fde2e2; flex-wrap: wrap; }
.sys-error i { font-size: 14px; flex-shrink: 0; }
.sys-msg-text { flex: 1; min-width: 0; word-break: break-word; }
.sys-info { background: #F9FAFB; color: var(--pc-text-secondary); border: 1px solid var(--pc-border); }

/* ── 底部输入区域 ── */
.chat-composer {
    flex-shrink: 0; border-top: 1px solid var(--pc-border);
    background: var(--pc-surface);
}
.composer-input-row { padding: 10px 16px 0 16px; }
.composer-textarea ::v-deep .el-textarea__inner {
    border-radius: var(--pc-radius-lg); border-color: var(--pc-border);
    background: #FAFBFC; font-size: 13px; line-height: 1.55;
    resize: none; transition: border-color 0.25s, box-shadow 0.25s;
    padding: 8px 12px; color: var(--pc-text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.composer-textarea ::v-deep .el-textarea__inner::placeholder { color: var(--pc-text-muted); }
.composer-textarea ::v-deep .el-textarea__inner:focus {
    border-color: var(--pc-primary);
    box-shadow: 0 0 0 3px rgba(79,110,247,.08);
}
.composer-textarea ::v-deep .el-textarea__inner:disabled { background: #F3F4F6; color: var(--pc-text-muted); }
.composer-bar { display: flex; justify-content: space-between; align-items: center; padding: 6px 16px 10px 16px; }
.composer-left { display: flex; align-items: center; gap: 6px; }
.composer-clear { color: var(--pc-text-muted); font-size: 12px; }
.composer-right { display: flex; gap: 6px; }

/* ================================================================
   右侧面板 — 监控面板（执行跟踪 + 工具调用）
   ================================================================ */
.monitor-panel {
    display: flex; flex-direction: column;
    height: calc(100vh - 156px); min-height: 480px;
    background: var(--pc-surface); border-radius: var(--pc-radius-lg);
    border: 1px solid var(--pc-border); overflow: hidden;
    box-shadow: var(--pc-shadow-sm); transition: all 0.3s;
}
.monitor-panel.is-collapsed { width: 40px; min-width: 40px; max-width: 40px; }

/* ── Panel header with tabs ── */
.monitor-panel-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 8px; border-bottom: 1px solid var(--pc-border);
    background: var(--pc-surface-raised); flex-shrink: 0; min-height: 40px;
}
.monitor-panel.is-collapsed .monitor-panel-header { flex-direction: column; justify-content: center; padding: 6px 2px; }
.monitor-tabs { display: flex; align-items: center; gap: 0; flex: 1; }
.monitor-tab {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 10px 14px; font-size: 12px; font-weight: 500;
    color: var(--pc-text-secondary); cursor: pointer;
    border-bottom: 2px solid transparent; transition: all 0.2s;
    white-space: nowrap; user-select: none;
}
.monitor-tab:hover { color: var(--pc-text); background: rgba(79,110,247,.03); }
.monitor-tab.is-active { color: var(--pc-primary); font-weight: 600; border-bottom-color: var(--pc-primary); }
.monitor-tab i { font-size: 13px; }
.monitor-tab-count {
    font-size: 9px; font-weight: 600; color: var(--pc-text-muted);
    background: #F3F4F6; padding: 1px 6px; border-radius: 8px; min-width: 16px; text-align: center;
}
.monitor-tab-count.running { color: var(--pc-warning); background: rgba(245,158,11,.1); }
.monitor-panel.is-collapsed .monitor-tabs { display: none; }
.monitor-panel-toggle { color: var(--pc-text-muted); padding: 2px 4px; font-size: 15px; flex-shrink: 0; }
.monitor-panel-toggle:hover { color: var(--pc-primary); }

/* ── Panel body ── */
.monitor-panel-body { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.monitor-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 30px 12px; color: var(--pc-text-muted); font-size: 11px; }
.monitor-empty i { font-size: 24px; color: #D1D5DB; }

/* ── Tool filter banner ── */
.tool-filter-banner {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; margin: 0 4px 6px;
    background: var(--pc-primary-soft); border: 1px solid rgba(79,110,247,.15);
    border-radius: var(--pc-radius-md); font-size: 12px;
}
.tool-filter-banner i { color: var(--pc-primary); font-size: 13px; }
.tool-filter-banner span { color: var(--pc-text); font-weight: 500; flex: 1; }
.tool-filter-banner-count { font-size: 10px; color: var(--pc-text-muted); background: #fff; padding: 1px 6px; border-radius: 6px; }
.tool-filter-clear { color: var(--pc-text-muted); font-size: 11px; padding: 0; }
.tool-filter-clear:hover { color: var(--pc-danger); }

/* ── Tool panel (inside tools tab) ── */
.monitor-tools { padding: 4px; display: flex; flex-direction: column; gap: 3px; }

/* Filter chips */
.tool-panel-filters { display: flex; flex-wrap: wrap; gap: 4px; padding: 0 2px 6px; border-bottom: 1px solid var(--pc-border); margin-bottom: 4px; }
.tool-filter-chip {
    display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px;
    border-radius: 10px; font-size: 10px; color: var(--pc-text-secondary);
    background: #F3F4F6; cursor: pointer; transition: all 0.15s;
    border: 1px solid transparent; white-space: nowrap;
}
.tool-filter-chip:hover { color: var(--pc-primary); background: var(--pc-primary-soft); border-color: rgba(79,110,247,.15); }
.tool-filter-chip.is-active { color: #fff; background: var(--pc-primary); border-color: var(--pc-primary); }
.tool-filter-count { font-size: 9px; color: var(--pc-text-muted); background: #E5E7EB; padding: 0 4px; border-radius: 6px; min-width: 14px; text-align: center; }
.tool-filter-chip.is-active .tool-filter-count { color: #fff; background: rgba(255,255,255,.25); }

/* Tool groups */
.tool-panel-group { display: flex; flex-direction: column; }
.tool-panel-group + .tool-panel-group { margin-top: 4px; padding-top: 4px; border-top: 1px solid var(--pc-border-light); }
.tool-panel-group-header { display: flex; align-items: center; gap: 5px; padding: 3px 6px; margin-bottom: 3px; }
.tool-panel-group-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--pc-primary); flex-shrink: 0; }
.tool-panel-group-label { font-size: 10px; font-weight: 600; color: var(--pc-text-secondary); flex: 1; }
.tool-panel-group-count { font-size: 9px; color: var(--pc-text-muted); background: #F3F4F6; padding: 1px 5px; border-radius: 8px; }

/* Tool items */
.tool-panel-item { border-radius: var(--pc-radius-sm); overflow: hidden; border: 1px solid var(--pc-border); background: var(--pc-surface); transition: all 0.15s; }
.tool-panel-item:hover { border-color: #D1D5DB; }
.tool-panel-item.is-running { border-color: var(--pc-warning); background: #FFFDF5; }
.tool-panel-item.is-expanded { border-color: var(--pc-primary); }
.tool-panel-item-header {
    display: flex; align-items: center; gap: 5px; padding: 5px 8px;
    background: #FAFBFC; color: var(--pc-text); cursor: pointer;
    user-select: none; font-size: 11px; transition: background 0.1s;
}
.tool-panel-item-header:hover { background: #F3F4F6; }
.tool-panel-item.is-running .tool-panel-item-header { background: #FFFDF5; }
.tool-panel-item-indicator .el-icon-loading { color: var(--pc-warning); }
.tool-done-icon { color: var(--pc-success); }
.tool-panel-item-name {
    flex: 1; font-size: 11px; font-weight: 600; color: var(--pc-text);
    font-family: 'SF Mono','Fira Code','Consolas',monospace;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0;
}
.tool-panel-item-status {
    font-size: 9px; color: var(--pc-text-muted);
    background: #F3F4F6; padding: 1px 6px; border-radius: 8px; flex-shrink: 0;
}
.tool-panel-item.is-running .tool-panel-item-status { color: var(--pc-warning); background: rgba(245,158,11,.08); }
.tool-panel-item-arrow { font-size: 9px; color: var(--pc-text-muted); flex-shrink: 0; }
.tool-panel-item-body { background: #FAFBFC; border-top: 1px solid var(--pc-border); }
.tool-panel-section { padding: 6px 10px; }
.tool-panel-section + .tool-panel-section { border-top: 1px solid var(--pc-border-light); }
.tool-panel-label { font-size: 9px; font-weight: 600; color: var(--pc-text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }
.tool-panel-json {
    margin: 0; padding: 6px 8px; background: #fff; border: 1px solid var(--pc-border);
    border-radius: 4px; font-family: 'SF Mono','Fira Code','Consolas',monospace;
    font-size: 10px; line-height: 1.5; color: var(--pc-text-secondary);
    white-space: pre-wrap; word-break: break-all; max-height: 140px; overflow-y: auto;
}
.tool-panel-json-empty { color: var(--pc-text-muted); font-style: italic; }
.tool-panel-time { font-size: 9px; color: var(--pc-text-muted); }

/* ================================================================
   场景确认面板 — Scenario Confirmation Panel
   ================================================================ */
.msg-ai-scenario { border-top: 1px solid var(--pc-border); }
.scenario-confirm-panel { background: var(--pc-surface); border-radius: var(--pc-radius-lg); overflow: hidden; }
.scenario-header {
    padding: 14px 16px 10px;
    background: linear-gradient(135deg, var(--pc-primary-soft), rgba(79,110,247,.04));
    border-bottom: 1px solid rgba(79,110,247,.1);
}
.scenario-name { font-size: 15px; font-weight: 700; color: var(--pc-text); display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.scenario-name i { color: var(--pc-primary); font-size: 18px; }
.scenario-description { font-size: 12px; color: var(--pc-text-secondary); line-height: 1.55; padding-left: 4px; }

/* ── 步骤垂直流 ── */
.scenario-steps-flow { padding: 16px 16px 8px; max-height: 440px; overflow-y: auto; }
.scenario-step-wrapper { display: flex; gap: 0; position: relative; }
.scenario-step-connector { display: flex; flex-direction: column; align-items: center; width: 32px; flex-shrink: 0; padding-top: 2px; }
.scenario-step-dot {
    width: 26px; height: 26px; border-radius: 50%;
    background: var(--pc-primary); color: #fff; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    z-index: 1; flex-shrink: 0; box-shadow: 0 2px 6px rgba(79,110,247,.25);
}
.scenario-step-line { width: 2px; flex: 1; min-height: 20px; background: rgba(79,110,247,.2); margin: 4px 0; }

/* ── 步骤卡片 ── */
.scenario-step-card {
    flex: 1; padding: 10px 14px; margin-bottom: 12px; margin-left: 10px;
    background: #FAFBFC; border: 1px solid var(--pc-border); border-radius: var(--pc-radius-lg);
    border-left: 3px solid var(--pc-primary); transition: all 0.2s;
}
.scenario-step-card:hover { border-color: #C7CDE8; box-shadow: 0 2px 8px rgba(79,110,247,.06); }
.step-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }
.step-number-label { font-size: 11px; font-weight: 700; color: var(--pc-primary); background: var(--pc-primary-soft); padding: 2px 8px; border-radius: var(--pc-radius-sm); letter-spacing: .02em; }
.step-api-name { font-size: 13px; font-weight: 600; color: var(--pc-text); }
.step-card-desc { font-size: 12px; color: var(--pc-text-secondary); line-height: 1.55; margin-bottom: 2px; }

/* ── 依赖关系标签 ── */
.step-card-deps { margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--pc-border); }
.deps-label { font-size: 11px; font-weight: 600; color: var(--pc-text); margin-bottom: 5px; }
.dep-item { display: flex; align-items: center; flex-wrap: wrap; gap: 5px; font-size: 11px; color: var(--pc-text-secondary); padding: 3px 0 3px 2px; }
.dep-arrow-icon { color: var(--pc-primary); font-size: 12px; transform: rotate(45deg); flex-shrink: 0; }
.dep-desc { color: var(--pc-text-muted); font-style: italic; }
.dep-path { background: var(--pc-primary-soft); padding: 1px 6px; border-radius: 3px; font-family: 'Fira Code','Consolas',monospace; font-size: 10px; color: var(--pc-primary); white-space: nowrap; }
.dep-arrow { color: var(--pc-text-muted); font-size: 10px; flex-shrink: 0; }

/* ── 场景操作栏 ── */
.scenario-actions { display: flex; justify-content: flex-end; gap: 8px; padding: 10px 16px; border-top: 1px solid var(--pc-border); background: #FAFBFC; }
.modify-input-area { width: 100%; }
.modify-input-area .el-textarea { margin-bottom: 8px; }
.modify-input-actions { display: flex; justify-content: flex-end; gap: 8px; }

/* ================================================================
   场景执行进度表 — Execution Progress Table
   ================================================================ */
.msg-ai-exec { border-top: 1px solid var(--pc-border); padding: 10px 16px; }
.scenario-exec-panel { border: 1px solid var(--pc-border); border-radius: var(--pc-radius-lg); overflow: hidden; }
.exec-header {
    display: flex; background: #FAFBFC; font-size: 11px; font-weight: 600;
    color: var(--pc-text-secondary); padding: 9px 14px;
    border-bottom: 1px solid var(--pc-border); letter-spacing: .02em;
}
.exec-row { display: flex; align-items: center; padding: 9px 14px; font-size: 12px; border-bottom: 1px solid var(--pc-border-light); transition: background 0.15s; }
.exec-row:last-child { border-bottom: none; }
.exec-status-success { background: #f0faf4; }
.exec-status-error { background: #fef5f5; }
.exec-status-running { background: var(--pc-primary-soft); }
.exec-col-step { width: 44px; flex-shrink: 0; font-weight: 600; color: var(--pc-text); }
.exec-col-api { flex: 1; min-width: 0; color: var(--pc-text); font-weight: 500; }
.exec-col-status { width: 90px; flex-shrink: 0; display: flex; align-items: center; gap: 5px; font-size: 11px; }
.exec-ok { color: var(--pc-success); font-size: 14px; }
.exec-running-icon { color: var(--pc-primary); font-size: 13px; }
.exec-fail { color: var(--pc-danger); font-size: 14px; }
.exec-pending-text { color: var(--pc-text-muted); }
.exec-status-text { font-size: 11px; }

/* ===== 动画 ===== */
@keyframes cursor-blink-anim { 0%,100%{opacity:1} 50%{opacity:0} }

/* ===== 响应式 ===== */
@media (max-width: 768px) {
    .ai-testcase-container { padding: 8px; }
    .right-col { display: none; }
    .center-col { max-width: 100%; flex: 0 0 100%; }
    .chat-container { height: auto; min-height: 500px; }
    .chat-messages { padding: 16px 14px; gap: 14px; }
    .msg-user { max-width: 88%; }
    .msg-ai { max-width: 96%; }
    .msg-system { max-width: 80%; }
    .composer-bar { flex-wrap: wrap; gap: 6px; }
    .quick-entries { flex-direction: column; max-width: 100%; }
}
</style>
