# 变量引用机制设计文档

## 1. 概述

测试用例中的参数值支持动态引用，统一使用 `$` 前缀语法。无需 `interrelate` 标志——系统根据前缀自动识别引用类型。

## 2. 语法

| 类型 | 语法 | 示例 | 说明 |
|------|------|------|------|
| **步骤引用** | `$N.字段路径` | `$1.data.token` | `$` 后是数字 → 引用场景第 N 步的响应 |
| **全局变量** | `$变量名` | `$reg_username` | `$` 后非数字 → 引用全局变量 |

### 步骤引用示例

```
场景：Step1 登录 → Step2 查询用户 → Step3 更新用户

Step2 需要 Step1 的 token：
  head_dict: [{"name":"Authorization","value":"$1.data.token"}]

Step3 需要 Step2 的 user_id：
  request_list: {"userId":"$2.data.user_id"}

取顶层字段：
  "$1.code"          → 取 Step1 响应的 code 字段
  "$1.msg"           → 取 Step1 响应的 msg 字段

取嵌套字段：
  "$1.data.token"    → 取 Step1 响应的 data.token
  "$2.data.list.0.id" → 取 Step2 响应的 data.list[0].id
```

### 全局变量示例

```
注册接口需要随机用户名：
  先创建全局变量 reg_username（Code: print('user_'+str(random.randint(1000,9999)))）
  引用: request_list: {"username":"$reg_username"}
```

## 3. 后端解析流程

```
HTTP 请求参数/Header → scan values
  ├── 匹配 $N.xxx  → 查 step→api_id 映射 → 查前置步骤响应 → get_json 提取
  ├── 匹配 $var.xxx → 查 OnlineCode → 执行 Python → 替换
  └── 无 $ 前缀      → 保持原值
```

## 4. 前端 UI 设计

### 4.1 参数/Header 值输入框

在参数值输入框中直接输入 `$1.data.token` 或 `$reg_username`。

建议增加**变量选择器**辅助输入：
- 下拉列表列出可用变量：`$1.*`（步骤1的响应字段）、`$2.*`、`$var.xxx`（已创建的全局变量）
- 选中后自动填入输入框

### 4.2 步骤引用的智能提示

前端可以从 API 文档的 `response` 字段（`ApiInfoDetail` 接口返回）获取响应结构：

```json
// GET /api/api/api_info 返回的 response 字段：
"response": [
  {"name":"code","tier":"","_type":"String"},
  {"name":"msg","tier":"","_type":"String"},
  {"name":"data","tier":"","_type":"String"},
  {"name":"key","tier":"data","_type":"String"},
  {"name":"user_id","tier":"data","_type":"Int"}
]
```

根据 `tier` 字段还原层级，生成 `$1.data.key`、`$1.data.user_id` 等候选路径。

### 4.3 场景执行顺序展示

前端在执行场景时展示步骤顺序，帮助用户确认 `$N` 中的 N 对应哪个步骤：

```
Step 1: 用户登录     (id=101)  →  引用为 $1.xxx
Step 2: 获取用户信息  (id=102)  →  引用为 $2.xxx  
Step 3: 更新用户     (id=103)  →  引用为 $3.xxx
```

### 4.4 全局变量管理

前端已有全局变量管理页面（`/api/global/global_variables`），创建后在参数值中通过 `$var.变量名` 引用即可。

## 5. 兼容性

旧的 `{api_id}|json_path` 格式和 `interrelate` 标志仍然有效，系统会自动识别。但推荐新数据使用统一 `$` 语法。

## 6. 全局变量 Code 编写指南

全局变量的 `Code` 字段为 Python 代码，`print()` 输出的值即为变量值：

| 用途 | Code 示例 |
|------|----------|
| 随机用户名 | `print('user_'+str(__import__('random').randint(1000,9999)))` |
| 随机邮箱 | `print('test'+str(__import__('random').randint(100,999))+'@test.com')` |
| 时间戳 | `import time; print(str(int(time.time())))` |
| 固定Token | `print('Bearer abc123def456')` |
