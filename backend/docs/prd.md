# EchoTik 商品列表 API 接入 PRD

## 产品概述

Linkfox 选品 Agent 需要支持用户通过自然语言提示词发起 EchoTik 商品列表查询。后端负责解析提示词、构造 EchoTik 商品列表 API 请求参数、调用第三方服务，并以统一 JSON 格式把商品结果返回给前端。

本阶段采用标准生产方案：FastAPI 单体应用，预留数据库和 Redis 缓存能力，用于后续保存查询记录、分类映射和短期查询缓存。当前实现边界仍以安全接入 EchoTik 商品列表 API 为核心，不在前端直接调用第三方接口。

## 用户角色

- 运营人员：输入选品条件，快速获取目标站点商品列表。
- 选品人员：按站点、分类、排序和分页筛选商品，用于候选商品判断。
- 开发/测试人员：通过 API 验证提示词解析、EchoTik 参数构造和第三方调用结果。

## 功能列表

### 1. 提示词提交

- 用户通过前端或 API 提交 `prompt`。
- 后端校验 `prompt` 是否存在、是否为空、长度是否在允许范围内。
- 参数错误返回统一业务错误码，例如 `INVALID_PROMPT`。

### 2. 提示词解析

- 解析站点地区，例如“美国站”映射为 `US`。
- 解析分页，例如“第 1 页”映射为 `page_num`。
- 解析每页数量，例如“每页 3 条”映射为 `page_size`。
- 解析排序方向，例如“降序”映射为 `sort_type=1`。
- 保留分类名称用于调试和后续分类 ID 映射。
- 对未确认字段保持保守：关键词字段、商品排序字段、分类 ID 不伪造为 EchoTik 参数。

### 3. EchoTik 参数构造

- 仅构造已确认且安全的 EchoTik 请求参数。
- `page_num`、`page_size` 类型以 EchoTik 最新文档为准。
- `page_size` 需要遵守 EchoTik 限制，当前需求文档标注最大值为 10。
- 分类名称必须通过分类映射得到 `product_category_id` 后才能提交给 EchoTik。

### 4. EchoTik 商品列表调用

- 后端服务层封装 EchoTik HTTP 调用。
- 鉴权信息只从环境变量或安全配置读取。
- 第三方错误统一转换为安全业务错误，不向前端透传原始异常、签名、token 或完整响应。
- 设置合理超时，避免接口请求长期占用。

### 5. 查询结果返回

- 后端返回统一 JSON：

```json
{
  "code": "SUCCESS",
  "message": "可选提示",
  "data": {}
}
```

- `data` 包含原始提示词、解析查询对象、EchoTik 请求参数和商品列表。
- 无数据库阶段商品结果直接返回；方案B预留查询记录和缓存能力。

### 6. 查询记录与缓存预留

- 数据库可保存查询记录、解析参数、响应摘要和调用状态。
- Redis 可缓存短期重复查询结果和分类映射。
- 敏感第三方响应不得完整落库。

## 用户流程

1. 用户在前端输入选品提示词。
2. 前端调用 `POST /api/agent/product-search`。
3. 后端校验 `prompt`。
4. 后端解析提示词字段。
5. 后端构造 EchoTik 商品列表参数。
6. 后端读取 EchoTik 鉴权配置并调用第三方 API。
7. 后端标准化商品列表结果。
8. 前端展示商品结果、解析条件和错误提示。

## 页面/模块结构

### 前端页面

- `frontend/index.html`：选品 Agent 页面结构。
- `frontend/src/scripts/product-agent.js`：用户交互、状态管理、结果渲染。
- `frontend/src/scripts/prompt-parser.js`：前端提示词预览解析，需与后端解析规则同步评估。
- `frontend/src/scripts/mock-products.js`：模拟商品数据，真实接入后逐步替换。

### 后端模块

- `backend/app/api/v1/routes/agent.py`：Agent 路由入口。
- `backend/app/schemas/product_search.py`：请求、响应和 EchoTik 参数 schema。
- `backend/app/services/prompt_parser_service.py`：提示词解析和参数构造。
- `backend/app/services/echotik_product_service.py`：EchoTik 商品 API 调用。
- `backend/app/services/product_search_service.py`：选品搜索业务编排。
- `backend/app/core/config.py`：配置和环境变量。
- `backend/app/common/result.py`：统一响应结构。

## 非功能需求

### 性能

- 单次 EchoTik 查询接口目标响应时间不超过 5 秒。
- EchoTik 超时后返回安全错误，不阻塞前端。
- 重复查询可通过 Redis 缓存降低第三方调用频率。

### 安全

- EchoTik 密钥、账号、token 只能来自环境变量或安全配置。
- 不返回原始异常、堆栈、第三方敏感响应。
- 日志必须脱敏，不能记录完整鉴权头或 token。
- 前端渲染接口文本时必须保持 HTML 转义。

### 扩展性

- 保持 FastAPI 单体分层结构，后续可增加 repository 和 db 层。
- 分类映射、排序映射、地区映射使用常量表或配置表达。
- EchoTik API 接入封装在 service 内，便于后续替换、重试、限流和降级。

### 可观测性

- 记录请求状态、EchoTik 调用耗时、失败类型和安全错误码。
- 日志使用占位符格式，避免字符串拼接和敏感信息泄露。

## 已确认项

- EchoTik 商品列表 API 文档未发现普通关键词字段，当前关键词只保留在内部 `query.keyword`。
- 商品排序字段使用 `product_sort_field`，“总销量”对应 `1`。
- 分类名称到分类 ID 的映射来源为本地 `product_category_mapping` 表或 Redis 分类缓存。
- EchoTik 鉴权方式为 Basic Auth，凭据来自环境变量。
- Redis 可缓存第三方查询结果，默认 TTL 为 `PRODUCT_SEARCH_CACHE_TTL_SECONDS=300`。

## 仍需外部确认项

- EchoTik 限流策略和业务失败响应格式的完整细节。
- 是否有其他商品搜索 API 支持关键词查询。
