# Linkfox - AI Coding Agent Guide

## 项目概览

Linkfox 当前是一个“选品 Agent”前后端分离原型项目：

- `backend`：Python FastAPI 服务，当前不接入数据库。
- `frontend`：原生 HTML/CSS/JavaScript 静态前端原型。
- 当前核心能力是把用户的选品提示词解析成 EchoTik 商品查询参数，并返回占位搜索结果；真实 EchoTik API 接入仍属于后续工作。

Codex 接手开发时，必须先读现有同类代码，再按本项目已有结构实现。不要照搬大型后端项目的复杂分层，也不要为当前原型引入不必要的框架、依赖或抽象。

## 必须遵守的核心规范

1. 开发前先阅读同类代码和 README。
2. 保持项目轻量，未经明确要求不要新增框架或依赖。
3. 后端遵守 `routes -> schemas -> services -> common/core/exceptions` 分层。
4. 前端遵守 `index.html -> styles -> scripts` 的组织方式。
5. 路由层只做 FastAPI 请求绑定、依赖注入和 service 调用。
6. Schema 负责 Pydantic 请求、响应和内部数据边界。
7. Service 负责业务逻辑、提示词解析、外部 API 参数组装和后续 API 调用。
8. Common/Core 只放统一响应、常量、配置等基础能力。
9. 禁止把原始异常、堆栈、密钥、第三方响应敏感信息直接返回给前端。
10. 涉及真实 EchoTik API、鉴权、密钥、计费或数据持久化时，必须先确认现有配置和安全边界。

## 项目结构

```text
.
├── backend/
│   ├── requirements.txt
│   ├── README.md
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── routes/
│   │   │           ├── agent.py
│   │   │           └── health.py
│   │   ├── common/
│   │   │   ├── constants.py
│   │   │   └── result.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── exceptions/
│   │   │   └── business_exception.py
│   │   ├── schemas/
│   │   │   └── product_search.py
│   │   └── services/
│   │       ├── prompt_parser_service.py
│   │       ├── echotik_product_service.py
│   │       └── product_search_service.py
│   └── tests/
│       └── test_agent_api.py
└── frontend/
    ├── README.md
    ├── index.html
    └── src/
        ├── styles/
        │   ├── base.css
        │   └── product-agent.css
        └── scripts/
            ├── mock-products.js
            ├── prompt-parser.js
            └── product-agent.js
```

## 后端分层规范

### `app/main.py`

- 负责创建 FastAPI 应用、注册 CORS、挂载路由和兜底异常处理。
- 不写业务逻辑、第三方 API 调用或提示词解析。
- 兜底异常返回必须是安全信息，不能直接暴露堆栈。

### `app/api/v1/routes`

- 只做 HTTP 路径声明、请求绑定、依赖注入和分发。
- 不在 route 中写复杂业务，不直接组装 EchoTik 参数。
- 统一使用 `ApiResponse` 响应结构。

### `app/schemas`

- 放 Pydantic 请求、响应和内部数据边界。
- 请求 schema、响应 schema、内部 DTO 不要混用。
- 字段必须有清晰的中文业务含义说明。

### `app/services`

- `prompt_parser_service.py` 负责提示词解析、字段映射、EchoTik 参数构造。
- `echotik_product_service.py` 负责 EchoTik 商品服务调用或占位实现。
- `product_search_service.py` 负责选品搜索流程编排。
- 外部 API 接入时，优先在 service 内封装，不要散落在 route 或 frontend。
- 复杂映射用常量表表达，避免魔法数字散落。

### `app/common` 和 `app/core`

- `common` 放统一响应、常量等基础能力。
- `core/config.py` 集中读取环境变量。
- 不把业务规则塞进 common/core。

## 前端开发规范

- 保持原生 HTML/CSS/JavaScript 结构，未经明确要求不要引入 React/Vue/构建工具。
- `index.html` 只放页面结构和脚本/样式引用。
- 全局变量、基础 reset、设计 token 放在 `src/styles/base.css`。
- 页面专属布局和组件样式放在 `src/styles/product-agent.css`。
- 前端业务状态、渲染、交互放在 `src/scripts/product-agent.js`。
- 前端提示词解析放在 `src/scripts/prompt-parser.js`；后端也有一份解析逻辑，修改解析规则时必须同步评估两边是否需要一致。
- 模拟数据只放在 `src/scripts/mock-products.js`，不要混入真实 API 调用。
- 渲染用户输入或接口返回文本时必须做 HTML 转义，参考现有 `escapeHtml`。
- 按钮、表格、筛选、toast 等交互要保持当前风格，不做无关 UI 重设计。

## API 响应规范

后端 JSON 响应保持当前结构：

```json
{
  "code": "SUCCESS",
  "message": "可选提示",
  "data": {}
}
```

约定：

- 成功使用稳定的字符串 `code`，例如 `SUCCESS` 或当前占位的 `BACKEND_SKELETON_READY`。
- 参数错误使用明确错误码，例如 `INVALID_PROMPT`。
- 未找到接口使用 `NOT_FOUND`。
- 方法不允许使用 `METHOD_NOT_ALLOWED`。
- 未知异常使用安全错误码和安全提示，不返回 `error.stack`。

## 错误处理和安全规范

- 不要把 `error.stack`、第三方完整报错、密钥、请求签名、认证 token 返回给前端。
- 捕获异常时可以在服务端日志中记录必要细节，但响应给前端必须是安全信息。
- 请求体或参数校验失败时返回安全业务错误码。
- 接入 EchoTik API 时，API key、cookie、token 等只能来自环境变量或安全配置，不能写死在代码、README 或 AGENTS.md。
- 不要提交真实生产数据、账号、密钥、私有接口凭据。

## 配置规范

- 环境变量读取集中在 `backend/app/core/config.py`。
- 新增配置时先扩展 `Settings`，再由业务模块引用。
- 不要在 service/route 中直接读取散落的 `os.environ`。
- 本地默认值只能用于无敏感性的开发配置，例如 host、port。

## EchoTik API 接入规范

接入真实 EchoTik API 前必须确认：

- API 鉴权方式。
- 请求参数字段、分页限制、排序字段枚举和地区枚举。
- 失败响应格式和限流策略。
- 是否需要缓存、重试、超时、降级。
- 是否允许前端直接展示第三方返回的错误信息。

实现时要求：

- HTTP 调用封装在 `backend/app/services/echotik_product_service.py` 或专门 service 中。
- Route 只拿 service 返回的标准结果。
- 外部错误统一转换为安全业务错误。
- 不把 EchoTik 原始敏感响应直接透传给前端。

## 代码风格

- Python 代码使用类型标注。
- 文件名保持 snake_case，例如 `product_search_service.py`。
- 常量使用 `UPPER_SNAKE_CASE`。
- 函数和变量使用 `snake_case`。
- 优先使用清晰的小函数，但不要为一次性逻辑过度拆分。
- 注释使用中文，解释业务原因、参数映射原因或临时兼容原因。
- 不写无意义注释，例如“调用函数”“赋值给变量”。

## 开发命令

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787
```

后端检查：

```bash
cd backend
python -m compileall app tests
python -m pytest
```

前端：

```text
frontend/index.html 可以直接用浏览器打开。
```

如果后续引入构建工具或测试框架，必须同步更新本文件和对应 README。

## Codex 开发前自检清单

Codex 修改代码前必须确认：

- 是否已阅读相关 README 和同类代码。
- 是否保持了当前轻量架构，没有无故新增依赖。
- 是否放在正确目录：route、schema、service、common/core、frontend scripts/styles。
- 是否没有在 route 中写复杂业务。
- 是否没有把原始异常或敏感信息返回给前端。
- 是否同步考虑了前端和后端提示词解析规则的一致性。
- 是否运行了与改动相关的最小检查；后端 Python 改动至少运行 `python -m compileall app tests`，依赖可用时运行 `python -m pytest`。

## 文档维护

- 新增重要模块时，同步更新本文件的目录说明。
- 新增接口时，同步更新 `backend/README.md` 的接口列表。
- 修改前端主要交互时，同步更新 `frontend/README.md`。
- 接入真实第三方服务时，同步补充配置、失败处理和安全注意事项。
