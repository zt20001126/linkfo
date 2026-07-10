# Linkfox - AI Coding Agent Guide

## 项目概览

Linkfox 当前是一个“选品 Agent”前后端分离原型项目：

- `backend`：Python FastAPI 服务，支持可选 EchoTik 真实 API、可选 PostgreSQL 查询记录和可选 Redis 缓存。
- `frontend`：原生 HTML/CSS/JavaScript 静态前端原型。
- 当前核心能力是把用户的选品提示词解析成 EchoTik 商品查询参数；真实 EchoTik API 通过 `ECHOTIK_ENABLE_REAL_API` 启用，默认关闭。

Codex 接手开发时，必须先读现有同类代码，再按本项目已有结构实现。不要照搬大型后端项目的复杂分层，也不要为当前原型引入不必要的框架、依赖或抽象。

## 必须遵守的核心规范

1. 开发前先阅读同类代码和 README。
2. 保持项目轻量，未经明确要求不要新增框架或依赖。
3. 后端遵守 `routes -> schemas -> services -> repositories/cache/db/models -> common/core/exceptions` 分层。
4. 前端遵守 `index.html -> styles -> scripts` 的组织方式。
5. 路由层只做 FastAPI 请求绑定、依赖注入和 service 调用。
6. Schema 负责 Pydantic 请求、响应和内部数据边界。
7. Service 负责业务逻辑、提示词解析、外部 API 参数组装和 API 调用编排。
8. Repository 只放 SQLAlchemy 查询和持久化逻辑。
9. Cache 只放 Redis key 构造、读取和写入逻辑。
10. 禁止把原始异常、堆栈、密钥、第三方响应敏感信息直接返回给前端。
11. 涉及真实 EchoTik API、鉴权、密钥、计费或数据持久化时，必须先确认现有配置和安全边界。

## 项目结构

```text
.
├── docker-compose.yml
├── backend/
│   ├── requirements.txt
│   ├── README.md
│   ├── .env.example
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/routes/
│   │   │   ├── agent.py
│   │   │   └── health.py
│   │   ├── cache/
│   │   │   ├── product_category_cache.py
│   │   │   └── product_search_cache.py
│   │   ├── common/
│   │   │   ├── constants.py
│   │   │   └── result.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── init_db.py
│   │   │   └── session.py
│   │   ├── exceptions/
│   │   │   └── business_exception.py
│   │   ├── models/
│   │   │   └── product_search.py
│   │   ├── repositories/
│   │   │   ├── product_category_repository.py
│   │   │   └── product_search_repository.py
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
        └── scripts/
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
- `echotik_product_service.py` 负责 EchoTik 商品 API 调用、鉴权、超时和安全错误转换。
- `product_search_service.py` 负责选品搜索流程编排、缓存读取和查询记录保存调度。
- 外部 API 接入时，优先在 service 内封装，不要散落在 route 或 frontend。
- 复杂映射用常量表表达，避免魔法数字散落。

### `app/repositories`

- 只放 SQLAlchemy 查询、过滤、写入和事务提交。
- 不返回 SQLAlchemy 模型给 API route。
- 不读取环境变量，不写第三方 HTTP 调用。

### `app/cache`

- 只放 Redis 缓存 key 构造、读取和写入。
- 缓存失败必须降级为未命中，不影响主查询流程。
- 缓存 key 不包含密钥、token、cookie 或用户敏感凭据。

### `app/db` 和 `app/models`

- `db` 负责 SQLAlchemy 引擎、会话和开发环境建表。
- `models` 只表达持久化表结构，不写业务流程。
- 数据库默认通过 `DATABASE_ENABLED=false` 关闭，避免普通测试强依赖本地 PostgreSQL。

## EchoTik API 接入规范

- 商品列表接口：`GET /api/v3/echotik/product/list`。
- 鉴权方式：`Authorization: Basic <base64(username:password)>`。
- 鉴权信息只能来自 `ECHOTIK_USERNAME` 和 `ECHOTIK_PASSWORD`。
- `page_num` 最大 `100000`，`page_size` 最大 `10`。
- 排序字段使用 `product_sort_field`，排序方向使用 `sort_type`。
- 商品列表 API 未确认普通关键词参数时，关键词只保留在内部 `query.keyword`，不提交给 EchoTik。
- 分类参数只能在本地分类映射命中时提交：`category_id`、`category_l2_id`、`category_l3_id`。
- 外部错误统一转换为安全业务错误，不把 EchoTik 原始敏感响应直接透传给前端。

## 前端开发规范

- 保持原生 HTML/CSS/JavaScript 结构，未经明确要求不要引入 React/Vue/构建工具。
- `index.html` 只放页面结构和脚本/样式引用。
- 全局变量、基础 reset、设计 token 放在 `src/styles/base.css`。
- 页面专属布局和组件样式放在 `src/styles/product-agent.css`。
- 前端业务状态、渲染、交互放在 `src/scripts/product-agent.js`。
- 前端提示词解析放在 `src/scripts/prompt-parser.js`；后端解析规则变更时必须同步评估两边是否需要一致。
- 模拟数据只放在 `src/scripts/mock-products.js`，不要混入真实 API 调用。
- 渲染用户输入或接口返回文本时必须做 HTML 转义，参考现有 `escapeHtml`。

## API 响应规范

后端 JSON 响应保持当前结构：

```json
{
  "code": "SUCCESS",
  "message": "可选提示",
  "data": {}
}
```

- 成功使用稳定字符串 `code`，例如 `SUCCESS` 或默认占位的 `BACKEND_SKELETON_READY`。
- 参数错误使用明确错误码，例如 `INVALID_PROMPT`。
- 未找到接口使用 `NOT_FOUND`。
- 方法不允许使用 `METHOD_NOT_ALLOWED`。
- 未知异常使用安全错误码和安全提示，不返回 `error.stack`。

## 配置规范

- 环境变量读取集中在 `backend/app/core/config.py`。
- 新增配置时先扩展 `Settings`，再由业务模块引用。
- 不要在 service/route 中直接读取散落的 `os.environ`。
- 本地默认值只能用于无敏感性的开发配置，例如 host、port、本地 Docker 端口。

## 开发命令

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787
```

本地 PostgreSQL 和 Redis：

```bash
docker compose up -d linkfox-postgres linkfox-redis
cd backend
python -m app.db.init_db
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

## Codex 开发前自检清单

- 是否已阅读相关 README 和同类代码。
- 是否保持当前轻量架构，没有无故新增依赖。
- 是否放在正确目录：route、schema、service、repository、cache、db/model、common/core、frontend scripts/styles。
- 是否没有在 route 中写复杂业务。
- 是否没有把数据库查询放进 service 或 route。
- 是否没有把 Redis 读写散落到 service 之外的 cache 以外目录。
- 是否没有把原始异常或敏感信息返回给前端。
- 是否同步考虑了前端和后端提示词解析规则的一致性。
- 是否运行了与改动相关的最小检查；后端 Python 改动至少运行 `python -m compileall app tests`，依赖可用时运行 `python -m pytest`。

## 文档维护

- 新增重要模块时，同步更新本文件的目录说明。
- 新增接口时，同步更新 `backend/README.md` 的接口列表。
- 修改前端主要交互时，同步更新 `frontend/README.md`。
- 接入真实第三方服务时，同步补充配置、失败处理和安全注意事项。
