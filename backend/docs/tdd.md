# EchoTik 商品列表 API 接入 TDD

## 系统架构设计

采用方案B：FastAPI 标准生产方案。

- Web 框架：FastAPI。
- 数据库：PostgreSQL，开发环境使用本地 Docker PostgreSQL，默认通过 `DATABASE_ENABLED=false` 关闭。
- 缓存：Redis，可选启用，用于短期查询结果和分类映射缓存。
- 消息队列：暂不引入，EchoTik 查询先采用同步调用。
- 任务调度：暂不引入。
- 架构模式：单体应用，保持 `routes -> schemas -> services -> repositories/db -> common/core` 分层。
- 第三方服务：EchoTik 商品列表 API。

整体调用链：

```text
Frontend
  -> FastAPI route
  -> ProductSearchService
  -> PromptParserService
  -> EchoTikProductService
  -> EchoTik API
  -> Standardized response
```

## 模块划分

### API Route 层

位置：`backend/app/api/v1/routes/agent.py`

职责：

- 声明 `POST /api/agent/product-search`。
- 绑定 Pydantic 请求对象。
- 注入业务 service。
- 返回统一 `ApiResponse`。
- 不写提示词解析、EchoTik HTTP 调用、缓存或数据库逻辑。

### Schema 层

位置：`backend/app/schemas/product_search.py`

职责：

- 定义 `ProductSearchRequest`。
- 定义提示词解析后的 query schema。
- 定义 EchoTik 请求参数 schema。
- 定义 EchoTik 响应标准化 schema。
- 区分请求 schema、响应 schema 和内部 DTO。

### Service 层

位置：

- `backend/app/services/product_search_service.py`
- `backend/app/services/prompt_parser_service.py`
- `backend/app/services/echotik_product_service.py`

职责：

- `ProductSearchService` 编排完整选品查询流程。
- `PromptParserService` 解析自然语言提示词并构造 EchoTik 参数。
- `EchoTikProductService` 封装第三方 HTTP 请求、鉴权、超时和错误转换。

### Repository 层

方案B预留：

- `backend/app/repositories/product_search_repository.py`
- `backend/app/repositories/product_category_repository.py`

职责：

- 保存查询记录、调用状态、脱敏响应摘要。
- 维护分类名称到 EchoTik 分类 ID 的映射。
- 不在 route 或 service 中直接写 SQL。

### Cache 层

方案B预留：

- `backend/app/cache/product_search_cache.py`
- `backend/app/cache/product_category_cache.py`

职责：

- 缓存短期重复查询结果。
- 缓存分类映射。
- 所有缓存 key 必须由稳定参数构造，不包含敏感信息。

### Core/Common 层

位置：

- `backend/app/core/config.py`
- `backend/app/common/result.py`
- `backend/app/common/constants.py`
- `backend/app/exceptions/business_exception.py`

职责：

- 统一配置读取。
- 统一响应结构。
- 常量和错误码管理。
- 业务异常转换。

## 数据库设计

当前需求文档要求无数据库阶段可直接返回商品结果；方案B预留以下表结构，后续开启持久化时使用。

### product_search_record

用途：保存选品查询记录和 EchoTik 调用状态。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint / uuid | 查询记录 ID |
| prompt | text | 用户原始提示词 |
| region | varchar(16) | EchoTik 地区编码 |
| page_num | varchar(16) | EchoTik 页码 |
| page_size | varchar(16) | EchoTik 每页数量 |
| sort_type | int | 排序方向 |
| category_name | varchar(128) | 用户输入分类名称 |
| product_category_id | varchar(64) | EchoTik 分类 ID，可为空 |
| request_params | json | 脱敏后的 EchoTik 请求参数 |
| response_summary | json | 脱敏后的响应摘要 |
| status | varchar(32) | `success`、`failed`、`skipped` |
| error_code | varchar(64) | 安全业务错误码 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### product_category_mapping

用途：维护分类名称和 EchoTik 分类 ID 的映射。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint / uuid | 映射记录 ID |
| region | varchar(16) | 地区编码 |
| category_name | varchar(128) | 中文分类名称 |
| product_category_id | varchar(64) | EchoTik 分类 ID |
| source | varchar(32) | 映射来源 |
| enabled | bool | 是否启用 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## API 设计

### POST /api/agent/product-search

请求：

```json
{
  "prompt": "@EchoTik-TikTok商品搜索 在 TikTok Shop，美国站，商品关键词 公路自行车，商品分类 运动与户外，按 总销量 排序，排序方式 降序，第 1 页，每页 3 条。"
}
```

成功响应：

```json
{
  "code": "SUCCESS",
  "message": null,
  "data": {
    "prompt": "原始提示词",
    "query": {
      "platform": "TikTok Shop",
      "region": "US",
      "keyword": "公路自行车",
      "categoryName": "运动与户外",
      "sortOrder": "desc",
      "page": 1,
      "pageSize": 3
    },
    "echotikParams": {
      "region": "US",
      "page_num": 1,
      "page_size": 3,
      "product_sort_field": 1,
      "sort_type": 1
    },
    "items": []
  }
}
```

参数错误响应：

```json
{
  "code": "INVALID_PROMPT",
  "message": "请传入 prompt 字段"
}
```

第三方失败响应：

```json
{
  "code": "ECHOTIK_REQUEST_FAILED",
  "message": "EchoTik 商品查询失败，请稍后重试"
}
```

### GET /api/agent/capabilities

用于返回当前 Agent 工具能力。

### GET /api/health

用于健康检查。

## 技术选型确认

选择方案B：标准生产方案。

选择原因：

- 当前项目已迁移到 FastAPI，保留现有轻量单体结构最稳。
- 需求文档明确当前阶段可不落库，但后续需要生产化能力。
- PostgreSQL 和 Redis 作为预留能力，可以支持查询记录、分类映射和短期缓存。
- 暂不引入消息队列和任务调度，避免在 EchoTik 字段尚未确认前过度设计。

## 核心流程图（文字版）

```text
1. 前端提交 prompt
2. FastAPI route 接收 ProductSearchRequest
3. ProductSearchService 校验业务边界
4. PromptParserService 解析地区、分页、分类、排序方向
5. PromptParserService 构造已确认的 EchoTik 参数
6. ProductSearchService 查询缓存
7. 缓存命中则返回标准化结果
8. 缓存未命中则调用 EchoTikProductService
9. EchoTikProductService 读取配置并发起 HTTP 请求
10. EchoTikProductService 标准化第三方响应或转换安全错误
11. ProductSearchService 可选保存查询记录和响应摘要
12. FastAPI 返回统一 JSON 响应
```

## 异步/任务设计

当前阶段不引入异步任务队列。

同步调用策略：

- EchoTik HTTP 请求设置连接和读取超时。
- 失败后返回安全错误，不做长时间阻塞。
- 限流、重试和熔断暂放在 `EchoTikProductService` 内部预留。

后续扩展条件：

- 批量选品、批量关键词查询或多地区查询时，引入任务队列。
- 定时刷新商品趋势或缓存预热时，引入任务调度。
- 大量重复查询时，优先启用 Redis 缓存。

## 错误处理设计

- 请求校验错误：返回 `INVALID_PROMPT` 或 `INVALID_REQUEST`。
- EchoTik 配置缺失：返回 `ECHOTIK_CONFIG_MISSING`。
- EchoTik 超时：返回 `ECHOTIK_TIMEOUT`。
- EchoTik 限流：返回 `ECHOTIK_RATE_LIMITED`。
- EchoTik 业务失败：返回 `ECHOTIK_REQUEST_FAILED`。
- 未知异常：返回 `INTERNAL_ERROR`。

所有响应必须是安全信息，不包含第三方原始敏感响应。

## 测试设计

- 单元测试：提示词解析、EchoTik 参数构造、分类映射。
- API 测试：健康检查、能力接口、商品搜索成功、空 prompt、方法不允许、接口不存在。
- Service 测试：EchoTik 超时、失败响应、配置缺失、缓存命中。
- 安全测试：错误响应不包含 stack、token、cookie、签名。
