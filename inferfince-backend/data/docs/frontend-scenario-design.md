# 多接口场景用例生成 — 前端开发设计文档

## 1. 概述

本文档描述 AI Agent 新增的「多接口业务场景测试」功能的前后端交互协议，供前端开发参考。

**Agent 服务地址**: `http://<host>:9000`

---

## 2. 核心 API：`POST /api/chat/test_case`

### 2.1 请求格式

```typescript
interface ChatRequest {
  messages?: ChatMessage[];        // 对话历史
  thread_id?: string;              // 会话 ID，默认 "__default__"
  selection?: ApiSelection[];      // [恢复] API 勾选结果
  scenario_confirm?: ScenarioConfirm; // [恢复] 场景确认结果
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string | ContentItem[];
}

interface ContentItem {
  type: "text" | "image";
  text?: string;
  image_url?: string;
}
```

**三种请求模式**：

| 模式 | 触发条件 | 说明 |
|------|----------|------|
| **新对话** | `selection` 和 `scenario_confirm` 均为 null | 开启新工作流，`messages` 中最后一轮 user 消息作为输入 |
| **API 选择恢复** | `selection` 不为 null | 从 `select_apis` 中断恢复，携带用户勾选的 API 列表 |
| **场景确认恢复** | `scenario_confirm` 不为 null | 从 `scenario_design` 中断恢复，携带确认/修改/取消操作 |

### 2.2 响应格式：SSE (Server-Sent Events)

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

每条消息格式：
```
event: <event_type>
data: <json_payload>

```

---

## 3. SSE 事件类型总览

| 事件 | 说明 | 出现阶段 |
|------|------|----------|
| `node_start` | 节点开始执行 | 每个节点进入时 |
| `message` | LLM 流式文本块 | LLM 思考/输出时 |
| `tool_call` | 工具调用开始 | Agent 调用后端 API 时 |
| `tool_result` | 工具调用结束 | 后端 API 返回时 |
| `node_end` | 节点执行完毕 | 每个节点退出时 |
| `interrupt` | 流程暂停，等待用户操作 | `select_apis` / `scenario_design` |
| `done` | 整个工作流完成 | 流程正常结束 |
| `error` | 异常终止 | 流程出错 |

---

## 4. 完整交互流程（场景模式）

### 4.1 步骤 1：发起新对话

**Request:**
```json
POST /api/chat/test_case
{
  "messages": [
    { "role": "user", "content": "我要测试用户注册登录的完整流程" }
  ],
  "thread_id": "session-abc-123"
}
```

**SSE 响应流：**

```
Step 1: 意图识别
event: node_start
data: {"node":"intent_recognition","label":"意图识别"}

// LLM 判断为 scenario_test_generation
event: node_end
data: {"node":"intent_recognition","label":"意图识别","summary":""}

---

Step 2: 选取接口
event: node_start
data: {"node":"select_apis","label":"选取接口"}

// 后端查询 API 列表...

// 触发中断 — 等待用户选择 API
event: interrupt
data: {
  "type": "select_apis",
  "data": {
    "type": "select_apis",
    "message": "项目中已有 15 个API接口，请选择需要生成测试用例的接口：",
    "available_apis": [
      {
        "api_id": "10",
        "name": "用户注册",
        "api_address": "/api/user/register",
        "request_type": "POST",
        "http_type": "HTTP"
      },
      {
        "api_id": "20",
        "name": "用户登录",
        "api_address": "/api/user/login",
        "request_type": "POST",
        "http_type": "HTTP"
      },
      {
        "api_id": "30",
        "name": "获取用户信息",
        "api_address": "/api/user/info",
        "request_type": "GET",
        "http_type": "HTTP"
      }
    ],
    "user_input": "我要测试用户注册登录的完整流程"
  }
}
// ⚠️ 流在此暂停，前端必须展示 API 选择 UI
```

### 4.2 步骤 2：恢复 — API 选择

用户在前端勾选了 3 个 API（id=10, id=20, id=30），前端发送恢复请求：

**Request:**
```json
POST /api/chat/test_case
{
  "thread_id": "session-abc-123",
  "selection": [
    { "api_id": "10", "name": "用户注册", "api_address": "/api/user/register", "request_type": "POST", "http_type": "HTTP" },
    { "api_id": "20", "name": "用户登录", "api_address": "/api/user/login", "request_type": "POST", "http_type": "HTTP" },
    { "api_id": "30", "name": "获取用户信息", "api_address": "/api/user/info", "request_type": "GET", "http_type": "HTTP" }
  ]
}
```

**SSE 响应流（续）：**

```
// select_apis 节点完成，路由到 scenario_design
event: node_end
data: {"node":"select_apis","label":"选取接口","summary":"已选择 3 个接口，开始分析接口依赖并设计业务场景..."}

---

Step 3: 设计场景
event: node_start
data: {"node":"scenario_design","label":"设计场景"}

// LLM 流式输出设计思路...
event: message
data: {"content":"分析API依赖关系：注册→登录→获取用户信息","node":"scenario_design"}

// 触发中断 — 展示场景方案等待确认
event: interrupt
data: {
  "type": "scenario_confirm",
  "data": {
    "type": "scenario_confirm",
    "message": "已设计业务场景「用户注册登录流程」，请确认场景方案：",
    "scenario_name": "用户注册登录流程",
    "scenario_description": "用户先注册新账号，然后用注册的账号登录获取token，最后用token查询用户详细信息",
    "steps": [
      {
        "step": 1,
        "api_id": "10",
        "api_name": "用户注册",
        "description": "注册新用户账号，获取user_id和初始token",
        "depends_on": [],
        "dependencies": []
      },
      {
        "step": 2,
        "api_id": "20",
        "api_name": "用户登录",
        "description": "用注册的账号登录，获取访问token",
        "depends_on": [1],
        "dependencies": [
          {
            "target_field": "request_list.data.username",
            "source_step": 1,
            "source_json_path": ".data.username",
            "description": "使用注册时提交的用户名"
          }
        ]
      },
      {
        "step": 3,
        "api_id": "30",
        "api_name": "获取用户信息",
        "description": "用登录获取的token查询用户详细信息",
        "depends_on": [2],
        "dependencies": [
          {
            "target_field": "head_dict.Authorization",
            "source_step": 2,
            "source_json_path": ".data.token",
            "description": "使用登录返回的token作为认证头"
          }
        ]
      }
    ]
  }
}
// ⚠️ 流在此暂停，前端必须展示场景确认 UI
```

### 4.3 步骤 3：恢复 — 场景确认

用户点击"确认"按钮：

**Request:**
```json
POST /api/chat/test_case
{
  "thread_id": "session-abc-123",
  "scenario_confirm": {
    "action": "confirm"
  }
}
```

用户点击"修改"按钮（带反馈）：

**Request:**
```json
POST /api/chat/test_case
{
  "thread_id": "session-abc-123",
  "scenario_confirm": {
    "action": "modify",
    "feedback": "请把获取用户信息放在登录之前"
  }
}
```

用户点击"取消"按钮：

**Request:**
```json
POST /api/chat/test_case
{
  "thread_id": "session-abc-123",
  "scenario_confirm": {
    "action": "cancel"
  }
}
```

**SSE 响应流（确认后继续）：**

```
event: node_end
data: {"node":"scenario_design","label":"设计场景","summary":"场景方案确认，共 3 个步骤..."}

// Step 4: 生成场景用例
event: node_start
data: {"node":"scenario_generate","label":"生成场景用例"}

// LLM 流式输出...
event: message
data: {"content":"开始创建场景用例...","node":"scenario_generate"}

// Agent 调用 add_automation_api 工具（Step 1）
event: tool_call
data: {"tool":"add_automation_api","status":"start"}

event: tool_result
data: {"tool":"add_automation_api","status":"end","result":{"code":"999999","msg":"成功！","data":{"api_id":101},"case_group_id":5}}

// Agent 调用 add_automation_api 工具（Step 2 — 带 interrelate）
event: tool_call
data: {"tool":"add_automation_api","status":"start"}

event: tool_result
data: {"tool":"add_automation_api","status":"end","result":{"code":"999999","msg":"成功！","data":{"api_id":102},"case_group_id":5}}

// Agent 调用 add_automation_api 工具（Step 3 — 带 interrelate）
event: tool_call
data: {"tool":"add_automation_api","status":"start"}

event: tool_result
data: {"tool":"add_automation_api","status":"end","result":{"code":"999999","msg":"成功！","data":{"api_id":103},"case_group_id":5}}

event: node_end
data: {"node":"scenario_generate","label":"生成场景用例","summary":"场景测试用例已生成：共 3 个步骤用例"}

---

// Step 5: 执行场景
event: node_start
data: {"node":"scenario_run","label":"执行场景"}

// 逐步骤执行
event: tool_call
data: {"tool":"execute_scenario_step","status":"start"}

event: tool_result
data: {
  "tool":"execute_scenario_step",
  "status":"end",
  "result": {
    "code":"999999",
    "data": {
      "result": [
        {"case_id":101,"success":true,"status":"success"}
      ]
    }
  }
}

// Step 2 执行...
// Step 3 执行...

event: node_end
data: {"node":"scenario_run","label":"执行场景","summary":"场景执行完成，3/3 步骤通过"}

---

// Step 6: 场景报告
event: node_start
data: {"node":"scenario_report","label":"场景报告"}

event: message
data: {"content":"# 场景测试报告\n\n## 1. 场景概览\n...","node":"scenario_report"}

event: node_end
data: {"node":"scenario_report","label":"场景报告","summary":"..."}

---

// 完成
event: done
data: {"status":"completed"}
```

---

## 5. 关键数据结构 (TypeScript)

```typescript
// ═══════════════════════════════════════════════════════════════
// SSE 事件 Payload
// ═══════════════════════════════════════════════════════════════

interface NodeStartEvent {
  node: string;    // 节点名: "intent_recognition" | "select_apis" | "case_generate" | ...
  label: string;   // 中文标签: "意图识别" | "选取接口" | "生成用例" | ...
}

interface MessageEvent {
  content: string; // LLM 输出的文本块（流式）
  node: string;    // 当前所在节点
}

interface ToolCallEvent {
  tool: string;    // 工具名: "add_automation_api" | "execute_scenario_step" | ...
  status: "start";
}

interface ToolResultEvent {
  tool: string;
  status: "end";
  result: unknown; // 工具返回值，格式因工具而异
}

interface NodeEndEvent {
  node: string;
  label: string;
  summary: string; // 节点执行摘要（最多 500 字符）
}

interface InterruptEvent {
  type: "select_apis" | "scenario_confirm";
  data: SelectApisPayload | ScenarioConfirmPayload;
}

interface DoneEvent {
  status: "completed";
}

interface ErrorEvent {
  status: "error";
  message: string;
}

// ═══════════════════════════════════════════════════════════════
// Interrupt Payloads
// ═══════════════════════════════════════════════════════════════

/** select_apis 中断时收到的数据 */
interface SelectApisPayload {
  type: "select_apis";
  message: string;                       // 提示消息
  available_apis: AvailableApi[];        // 可选 API 列表
  user_input: string;                    // 用户原始输入
}

interface AvailableApi {
  api_id: string;
  name: string;
  api_address: string;
  request_type: "GET" | "POST" | "PUT" | "DELETE";
  http_type: "HTTP" | "HTTPS" | "DUBBO";
}

/** scenario_confirm 中断时收到的数据 */
interface ScenarioConfirmPayload {
  type: "scenario_confirm";
  message: string;                       // 提示消息
  scenario_name: string;                 // 场景名称
  scenario_description: string;          // 场景描述
  steps: ScenarioStepDisplay[];          // 步骤列表
}

interface ScenarioStepDisplay {
  step: number;                          // 步骤序号（1-indexed）
  api_id: string;                        // API ID
  api_name: string;                      // API 名称
  description: string;                   // 步骤业务说明
  depends_on: number[];                  // 依赖的前置步骤序号
  dependencies: ScenarioDependencyDisplay[];  // 数据依赖详情
}

interface ScenarioDependencyDisplay {
  target_field: string;       // 目标字段路径，如 "head_dict.Authorization"
  source_step: number;        // 数据来源步骤序号
  source_json_path: string;   // JSONPath，如 ".data.token"
  description: string;        // 人类可读描述
}

// ═══════════════════════════════════════════════════════════════
// Resume Payloads
// ═══════════════════════════════════════════════════════════════

/** API 选择恢复 */
interface ApiSelection {
  api_id: string;
  name: string;
  api_address: string;
  request_type: string;
  http_type: string;
}

/** 场景确认恢复 */
interface ScenarioConfirm {
  action: "confirm" | "modify" | "cancel";
  feedback?: string;  // action="modify" 时必填
}

// ═══════════════════════════════════════════════════════════════
// 工具返回值格式
// ═══════════════════════════════════════════════════════════════

/** add_automation_api 成功返回 */
interface AddApiSuccessResult {
  code: "999999";
  msg: "成功！";
  data: {
    api_id: number;       // 新创建的用例 ID
  };
  case_group_id: number;  // 用例组 ID
}

/** execute_scenario_step 成功返回 */
interface ExecuteStepResult {
  code: "999999";
  data: {
    result: Array<{
      case_id: number;
      success: boolean;
      status: string;       // "success" | "ERROR" | ...
    }>;
  };
}

/** 所有后端接口的错误返回格式 */
interface ApiErrorResult {
  code: string;      // 错误码（非 "999999"）
  msg: string;       // 错误消息
}

// ═══════════════════════════════════════════════════════════════
// 节点名称枚举
// ═══════════════════════════════════════════════════════════════

type NodeName =
  | "intent_recognition"   // 意图识别
  | "select_apis"          // 选取接口
  | "case_generate"        // 生成用例（单接口模式）
  | "case_run"             // 执行测试（单接口模式）
  | "case_update"          // 修复用例（单接口模式）
  | "final_report"         // 生成报告（单接口模式）
  | "general_response"     // 智能回答
  | "scenario_design"      // 设计场景（场景模式）
  | "scenario_generate"    // 生成场景用例（场景模式）
  | "scenario_run"         // 执行场景（场景模式）
  | "scenario_report";     // 场景报告（场景模式）
```

---

## 6. 完整状态机

```
                        ┌─────────────────────────┐
                        │    用户输入消息          │
                        └───────────┬─────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   intent_recognition │
                         │      意图识别        │
                         └──────┬──────┬───────┘
                                │      │
                    general_chat│      │ test_case_generation
                                │      │ 或 scenario_test_generation
                                ▼      ▼
                    ┌──────────┐  ┌──────────────────┐
                    │general_  │  │   select_apis    │
                    │response  │  │    选取接口       │
                    └────┬─────┘  └────────┬─────────┘
                         │                │
                         │       ┌────────┴──────────┐
                         │       │  [interrupt]       │ ←── 前端展示 API 列表
                         │       │  用户勾选 API       │
                         │       └────────┬──────────┘
                         │                │
                         │     ┌──────────┴──────────┐
                         │     │    路由判断          │
                         │     │  intent + API数量    │
                         │     └──────┬──────┬───────┘
                         │            │      │
                         │   单API/普通│      │ 多API+场景
                         │            ▼      ▼
                         │    ┌──────────┐  ┌──────────────────┐
                         │    │case_     │  │ scenario_design  │
                         │    │generate  │  │   设计场景        │
                         │    └────┬─────┘  └────────┬─────────┘
                         │         │                 │
                         │         │        ┌────────┴──────────┐
                         │         │        │  [interrupt]       │ ←── 前端展示场景方案
                         │         │        │  用户确认/修改/取消 │
                         │         │        └──┬───────┬────────┘
                         │         │           │       │
                         │         │     confirm│  modify│→ 返回 scenario_design
                         │         │           │   cancel│→ END
                         │         │           ▼
                         │         │    ┌──────────────────┐
                         │         │    │scenario_generate │
                         │         │    │ 生成场景用例      │
                         │         │    └────────┬─────────┘
                         │         │             │
                         │         │             ▼
                         │         │    ┌──────────────────┐
                         │         │    │  scenario_run    │
                         │         │    │  执行场景        │
                         │         │    └────────┬─────────┘
                         │         │             │
                         │         │             ▼
                         │         │    ┌──────────────────┐
                         │         │    │scenario_report   │
                         │         │    │  场景报告         │
                         │         │    └────────┬─────────┘
                         │         │             │
                         ▼         ▼             ▼
                       ┌─────────────────────────────┐
                       │            END               │
                       └─────────────────────────────┘
```

---

## 7. UI 组件设计建议

### 7.1 全局：工作流进度条

显示当前节点和已完成节点的进度。节点按流程顺序排列：

**单接口模式**: 意图识别 → 选取接口 → 生成用例 → 执行测试 → 修复用例(可循环) → 生成报告

**场景模式**: 意图识别 → 选取接口 → 设计场景 → 生成场景用例 → 执行场景 → 场景报告

```
[✓ 意图识别] → [✓ 选取接口] → [● 设计场景] → [○ 生成场景用例] → [○ 执行场景] → [○ 场景报告]
```

每个节点的状态：`pending` / `running` / `done` / `error`。

### 7.2 中断 UI 1：API 选择面板 (select_apis)

**触发**: 收到 `interrupt` 事件，`type = "select_apis"`

**展示内容**:
- 顶部：提示消息 `message`
- 主体：表格/卡片列表，每项显示：
  - ☐ 复选框
  - API 名称 (`name`)
  - 请求方法 + 地址 (`request_type` `api_address`)
  - 协议类型 (`http_type`)
- 支持搜索/筛选
- 支持全选/反选
- 底部：「确认选择」按钮（收集勾选项 → 发送 `selection` resume）

**Resume Payload 构造**:
```typescript
{
  thread_id: currentThreadId,
  selection: checkedApis.map(api => ({
    api_id: api.api_id,
    name: api.name,
    api_address: api.api_address,
    request_type: api.request_type,
    http_type: api.http_type,
  }))
}
```

### 7.3 中断 UI 2：场景确认面板 (scenario_confirm)

**触发**: 收到 `interrupt` 事件，`type = "scenario_confirm"`

**展示内容**:
- 顶部：场景名称 (`scenario_name`) + 场景描述 (`scenario_description`)
- 主体：步骤流程图，垂直排列，每个步骤卡片显示：
  - 步骤序号 (step)
  - API 名称 (api_name)
  - 步骤描述 (description)
  - 依赖关系（如有）：箭头/连线 + 来源步骤 + JSONPath
- 依赖关系可视化示例：
  ```
   Step1: 用户注册
     │
     │ .data.username ─────────┐
     ▼                         │
   Step2: 用户登录  ←──────────┘
     │ (depends_on: [1])
     │ .data.token ────────────┐
     ▼                         │
   Step3: 获取用户信息 ←───────┘
     (depends_on: [2])
  ```
- 底部三个按钮：
  - ✅ **确认方案** → `{ action: "confirm" }`
  - ✏️ **修改方案** → 弹出输入框收集反馈文字 → `{ action: "modify", feedback: "..." }`
  - ❌ **取消** → `{ action: "cancel" }`

**Resume Payload 构造**:
```typescript
// 确认
{ thread_id: currentThreadId, scenario_confirm: { action: "confirm" } }

// 修改
{ thread_id: currentThreadId, scenario_confirm: { action: "modify", feedback: "用户输入的文字" } }

// 取消
{ thread_id: currentThreadId, scenario_confirm: { action: "cancel" } }
```

### 7.4 工具调用面板 (tool_call / tool_result)

在 `scenario_generate` 和 `scenario_run` 节点中，Agent 会多次调用后端工具。建议展示：

```
┌─────────────────────────────────────────┐
│ 🔧 add_automation_api              ⏳   │
│    创建 Step1 "用户注册" 用例...         │
├─────────────────────────────────────────┤
│ ✅ add_automation_api                    │
│    api_id: 101, case_group_id: 5        │
├─────────────────────────────────────────┤
│ 🔧 add_automation_api              ⏳   │
│    创建 Step2 "用户登录" 用例(关联)...   │
├─────────────────────────────────────────┤
│ ✅ add_automation_api                    │
│    api_id: 102, case_group_id: 5        │
└─────────────────────────────────────────┘
```

### 7.5 场景执行面板 (scenario_run)

显示逐步执行进度：

```
场景：用户注册登录流程
┌──────┬──────────────┬────────┬────────┐
│ 步骤 │ API          │ 状态   │ 详情   │
├──────┼──────────────┼────────┼────────┤
│  1   │ 用户注册     │ ✅ 通过 │ 200    │
│  2   │ 用户登录     │ ⏳ 执行中...│     │
│  3   │ 获取用户信息 │ ⏳ 等待 │       │
└──────┴──────────────┴────────┴────────┘
```

### 7.6 场景报告面板 (scenario_report)

`scenario_report` 节点输出 Markdown 格式的完整测试报告。前端渲染为富文本。

报告结构：
1. 场景概览（名称、通过/失败步骤数）
2. 数据流追踪（步骤间的数据传递关系）
3. 各步骤详情（HTTP 状态码、响应摘要）
4. 失败分析（如有）
5. 总结与建议

---

## 8. 错误处理

### 8.1 SSE error 事件

```json
event: error
data: {"status":"error","message":"错误描述"}
```

收到 `error` 事件后：
- 停止当前进度展示
- 在 UI 中显示错误消息
- 允许用户"重新开始"（发起新对话）

### 8.2 工具调用失败

工具返回 `code != "999999"` 时：
- 在工具结果面板中标记为 ❌
- 显示 `msg` 字段中的错误信息
- Agent 可能会自动重试或跳过

### 8.3 超时处理

- `scenario_run` 节点中的 `execute_scenario_step` 超时时间为 120 秒
- 如果某个步骤超时或失败，后续步骤继续执行
- 前端应在长时间无 SSE 事件时显示等待提示

### 8.4 断线重连

SSE 连接断开时：
- 保存当前 `thread_id`
- 如需恢复：使用相同的 `thread_id` 发送 resume 请求
- LangGraph checkpoint 机制会恢复到上次中断状态

---

## 9. 前端 SDK 伪代码

```typescript
class ScenarioAgentClient {
  private threadId: string;
  private abortController: AbortController | null = null;

  constructor() {
    this.threadId = crypto.randomUUID();
  }

  /** 发起新对话 */
  async startConversation(userMessage: string): Promise<void> {
    const response = await fetch("http://agent:9000/api/chat/test_case", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: userMessage }],
        thread_id: this.threadId,
      }),
    });
    await this.processStream(response);
  }

  /** 恢复：API 选择 */
  async resumeWithSelection(selectedApis: ApiSelection[]): Promise<void> {
    const response = await fetch("http://agent:9000/api/chat/test_case", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        thread_id: this.threadId,
        selection: selectedApis,
      }),
    });
    await this.processStream(response);
  }

  /** 恢复：场景确认 */
  async resumeWithScenarioConfirm(action: "confirm" | "modify" | "cancel", feedback?: string): Promise<void> {
    const response = await fetch("http://agent:9000/api/chat/test_case", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        thread_id: this.threadId,
        scenario_confirm: { action, feedback },
      }),
    });
    await this.processStream(response);
  }

  /** 处理 SSE 流 */
  private async processStream(response: Response): Promise<void> {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // 解析 SSE 事件
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      let eventType = "";
      for (const line of lines) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7);
        } else if (line.startsWith("data: ")) {
          const data = JSON.parse(line.slice(6));
          this.handleEvent(eventType, data);
        }
      }
    }
  }

  /** 事件分发 */
  private handleEvent(type: string, data: any): void {
    switch (type) {
      case "node_start":   this.onNodeStart(data); break;
      case "node_end":     this.onNodeEnd(data); break;
      case "message":      this.onMessage(data); break;
      case "tool_call":    this.onToolCall(data); break;
      case "tool_result":  this.onToolResult(data); break;
      case "interrupt":    this.onInterrupt(data); break;
      case "done":         this.onDone(data); break;
      case "error":        this.onError(data); break;
    }
  }

  // 回调接口 — 由 UI 层实现
  onNodeStart(data: NodeStartEvent): void {}
  onNodeEnd(data: NodeEndEvent): void {}
  onMessage(data: MessageEvent): void {}
  onToolCall(data: ToolCallEvent): void {}
  onToolResult(data: ToolResultEvent): void {}
  onInterrupt(data: InterruptEvent): void {}
  onDone(data: DoneEvent): void {}
  onError(data: ErrorEvent): void {}
}
```

---

## 10. 前端需要新增的页面/组件清单

| 序号 | 组件 | 触发条件 | 功能 |
|------|------|----------|------|
| 1 | **工作流进度条** | 全局 | 显示当前节点进度（支撑两种模式的全部节点） |
| 2 | **API 选择面板** | `interrupt.type="select_apis"` | 展示可选 API 列表，支持搜索/全选/反选 |
| 3 | **场景确认面板** | `interrupt.type="scenario_confirm"` | 展示场景步骤流程图 + 确认/修改/取消按钮 |
| 4 | **场景步骤可视化** | 场景确认面板内 | 垂直步骤流程 + 依赖箭头连线 |
| 5 | **工具调用日志** | `tool_call` / `tool_result` | 实时展示工具调用状态和结果 |
| 6 | **场景执行面板** | `scenario_run` 节点 | 逐步显示每个步骤的执行状态 |
| 7 | **场景报告渲染** | `scenario_report` 节点 | Markdown 渲染 |
| 8 | **修改反馈输入框** | 场景确认面板中点击"修改" | 收集用户修改意见文字 |

---

## 11. 与现有单接口流程的兼容

现有的单接口测试流程（`intent_recognition → select_apis → case_generate → case_run → case_update → final_report`）**完全不受影响**。

新增的场景流程在 `select_apis` 后分叉，仅当：
1. 意图被识别为 `scenario_test_generation`
2. 用户选择了 **超过 1 个** API

时才会触发场景分支。其他情况走原有单接口流程。

前端可以通过 `node_start` 事件的 `node` 字段区分当前处于哪个分支：
- 看到 `scenario_design` → 场景模式
- 看到 `case_generate` → 单接口模式
