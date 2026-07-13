# QualiAutoAgent — AI 自动化测试平台

Django + FastAPI + Vue 全栈 API 自动化测试平台，集成 LangGraph 多智能体系统。

---

## 系统架构

```
Nginx (:80) ── 静态文件 + 反向代理
  ├─ /api/*, /admin/*  →  Django (:8000)
  ├─ /agent/*          →  Agent FastAPI (:9000)
  └─ /*                →  Vue SPA

Django (:8000)          Agent (:9000)
  REST API (DRF)          LangGraph 多智能体
  自动化测试执行           SSE 流式响应
  定时任务调度             RAG 知识库
  └─ MySQL :3306          └─ Qdrant (向量库)
  └─ Redis :6379

外部: Qwen3.7-Max (DashScope) / LangFuse / 飞书 / 邮件
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 2 + Element UI + ECharts |
| 后端 | Django 4.2 + DRF + APScheduler |
| Agent | FastAPI + LangGraph 0.6 + LangChain 0.3 |
| LLM | Qwen3.7-Max + text-embedding-v3 (DashScope) |
| 向量库 | Qdrant |
| 存储 | MySQL + Redis |
| 部署 | Docker 多阶段构建 |

---

## 快速开始

```bash
# Docker 部署
docker build -t qualiautoagent .
docker run -d -p 80:80 --env-file inferfince-backend/.env qualiautoagent

# 手动部署
cd inferfince-backend && pip install -r requirements.txt && python manage.py runserver 0.0.0.0:8000
cd inferfince-backend/agent && python server.py --port 9000
cd Interfince-front && npm install && npm run dev
```

配置: `inferfince-backend/.env` (数据库/Redis/Agent/RAG) + `agent/conf_dev.yaml` (LLM)

---

## 功能

### API 管理 & 测试
- 接口 CRUD、分组、Mock | form-data / JSON / XML
- Swagger 2.0 / OpenAPI 3.0 一键导入
- 单接口快速测试、历史追溯

### 自动化测试
- 多步骤顺序执行，`$N.field` 步骤间数据引用
- 并行 + 串行两种模式
- 4 级断言：状态码 / JSON 字段（≥≤=包含非空）/ 全量对比 / 正则
- 全局变量（Python 动态生成）、数据库断言（MySQL/Redis/MQ）
- 定时任务：一次性 + 循环（分钟~周间隔）

### AI 智能体（核心）

| 子智能体 | 功能 | 流程 |
|----------|------|------|
| case_gen | 单接口用例生成 | 选择 API → 生成 12+ 用例(6 维度) → 执行 → 修复(≤5轮) → 报告 |
| scenario_gen | 多 API 场景测试 | 依赖分析 → 场景设计 → 生成 → 执行 → 修复 → 报告 |
| code_quality | 代码质量分析 | 分析 → 报告 |
| rag_qa | 知识库问答 | ReAct 检索 → 回答 |

- 6 测试维度: 功能/边界/安全/异常/幂等/契约
- 人机协同: 关键节点暂停等待确认
- SSE 流式输出，支持会话恢复

---

## 项目结构

```
inferfince-backend/
├── api_automation_test/     # Django 配置 (settings/urls/wsgi)
├── api_test/                # 核心应用
│   ├── models.py            # 24 个数据模型
│   ├── api/                 # 15 个视图模块 (account/ApiDoc/automationCase/...)
│   ├── common/              # 测试引擎/HTTP客户端/断言/导入导出/任务调度
│   └── config/              # DB/Redis 配置
├── agent/                   # AI Agent 服务
│   ├── server.py            # FastAPI 入口 (:9000)
│   ├── conf_dev.yaml        # LLM 配置
│   └── src/
│       ├── agents/          # 4 个子智能体 (case_gen/scenario_gen/code_quality/rag_qa)
│       ├── framework/       # 编排/注册/流式/状态/检查点
│       ├── shared/tools.py  # 9 个 LangChain 工具
│       ├── rag/             # Qdrant 向量检索
│       └── prompts/         # 中文提示词模板
├── requirements.txt
└── .env

Interfince-front/src/
├── views/                   # 页面 (Project/api/automation/task/global)
│   └── project/automation/AiTestCase.vue  # AI 对话界面
├── api/api.js               # ~60 个后端 API 调用
└── routes.js                # 路由 + Token 守卫
```

---

## 核心 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/user/login` | 登录 (Token) |
| GET/POST | `/api/project/projection` | 项目 CRUD |
| GET/POST | `/api/api/api_list`, `/add_api` | API 管理 |
| POST | `/api/api/lead_swagger` | Swagger 导入 |
| POST | `/api/api/fast_test` | 快速测试 |
| POST | `/api/automation/start_test` | 并行执行 |
| POST | `/api/automation/start_test_sequential` | 串行执行 |
| GET | `/api/automation/test_report` | 测试报告 |
| POST | `/api/automation/add_time_task` | 定时任务 |
| POST | `/agent/api/chat/test_case` | AI 生成用例 (SSE) |
| GET | `/api/swagger/` | OpenAPI 文档 |
