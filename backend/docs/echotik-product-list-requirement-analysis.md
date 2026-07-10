# EchoTik 商品列表 API 需求分析

## 1. 需求背景

用户希望在选品 Agent 中输入自然语言提示词，由后端解析出 EchoTik 商品列表 API 所需请求参数，并调用商品列表 API 返回商品结果。当前阶段暂不配置数据库，也不要求把接口返回数据持久化。

本需求基于当前后端实际结构分析：`backend` 目前是 FastAPI 项目，核心链路为 `routes -> service -> prompt parser -> EchoTik service -> response`。

## 2. 用户输入示例

```text
@EchoTik-TikTok商品搜索 在 TikTok Shop，美国站，商品关键词 公路自行车，商品分类 运动与户外，按 总销量 排序，排序方式 降序，第 1 页，每页 3 条。
```

## 3. 目标用户与输入输出

- 目标用户：通过 Linkfox 前端或 API 使用选品 Agent 的运营、选品人员。
- 输入：用户自然语言提示词。
- 输出：统一 JSON 响应，包含原始提示词、解析后的查询条件、准备传给 EchoTik 的请求参数和商品列表结果。
- 核心流程：接收提示词 -> 校验 prompt -> 解析字段 -> 组装 EchoTik 参数 -> 调用商品列表 API -> 直接返回商品列表。

## 4. 参数提取规则

根据当前提示词，可明确提取到以下字段：

| 提示词片段 | 业务含义 | EchoTik 参数 | 值 | 处理说明 |
| --- | --- | --- | --- | --- |
| 美国站 | 区域 | `region` | `US` | 必传 |
| 第 1 页 | 分页页码 | `page_num` | `"1"` | 必传；API 文档类型为 `str` |
| 每页 3 条 | 分页页数 | `page_size` | `"3"` | 必传；API 文档类型为 `str`，最大 10 |
| 排序方式 降序 | 排序方向 | `sort_type` | `1` | 可选；`0=asc`，`1=desc` |
| 商品分类 运动与户外 | 商品一级分类 | `product_category_id` | 待映射 | 可选；必须由分类名称映射为 EchoTik 分类 ID |

当前提示词中有两个信息不能直接映射到你提供的参数列表：

- `商品关键词 公路自行车`：提供的 API 参数列表里没有关键词字段，不能安全构造请求参数。需要确认真实商品列表 API 是否存在关键词参数，例如 `keyword`、`product_keyword` 或 `search_keyword`。
- `按 总销量 排序`：提供的排序字段是 `influencer_sort_field_v2`，枚举描述偏“达人排序”，不包含商品总销量字段。需要确认商品列表 API 的商品排序字段名称和枚举值。若沿用当前项目旧逻辑，`总销量` 曾映射为商品排序字段 `1`，但它不在本次参数列表中，需要以 EchoTik 最新接口文档为准。

## 5. 建议请求参数结构

在真实 API 字段未补齐前，建议只传已确认且安全的参数：

```json
{
  "region": "US",
  "page_num": "1",
  "page_size": "3",
  "sort_type": 1
}
```

如果补齐分类 ID 映射，并确认 `运动与户外` 的 EchoTik 一级分类 ID，则可以增加：

```json
{
  "product_category_id": "<EchoTik category id>"
}
```

如果后续确认关键词和商品排序字段，则再增加对应参数，不建议把无法确认的字段硬塞进现有 API 参数。

## 6. 后端模块职责

- `app/api/v1/routes/agent.py`：保留路由入口，只负责接收 `POST /api/agent/product-search` 并委托 service。
- `app/schemas/product_search.py`：扩展 EchoTik 请求参数模型，字段类型需和真实 API 保持一致；本次参数表中 `page_num`、`page_size` 是字符串。
- `app/services/prompt_parser_service.py`：负责从中文提示词中解析区域、分页、分类、排序方向，并组装 EchoTik 请求参数。
- `app/services/echotik_product_service.py`：负责真实 EchoTik 商品列表 API 调用、超时、鉴权、错误转换和结果标准化。
- `app/services/product_search_service.py`：负责编排提示词解析和 EchoTik 服务调用，不处理第三方接口细节。

## 7. 无数据库时的数据放置方案

当前阶段推荐不存储商品列表结果，直接通过接口响应返回给前端：

```text
EchoTik API response -> 后端标准化 -> HTTP response -> 前端渲染
```

可选方案如下：

| 方案 | 适用场景 | 优点 | 风险 |
| --- | --- | --- | --- |
| 仅接口返回，不落盘 | 当前原型和无数据库阶段 | 最简单，无数据一致性问题 | 刷新后结果丢失 |
| 进程内内存缓存 | 短时间重复查看同一次查询 | 实现轻量，无需新服务 | 服务重启丢失，多进程不共享 |
| 本地临时 JSON 文件 | 本地调试、问题复现 | 方便查看请求与响应样例 | 需要脱敏和清理，不适合生产 |
| Redis 等缓存 | 后续需要缓存和复用搜索结果 | 可设置 TTL，跨进程共享 | 需要新增基础设施和配置 |

结论：本阶段优先选择“仅接口返回”。如果需要前端短时间重复展示，由前端状态保存当前响应；如果需要后端临时复查，可在开发环境写入脱敏日志，不把原始第三方敏感响应返回给前端。

## 8. 风险与待确认项

- 真实 EchoTik 商品列表 API 的关键词字段缺失，需要确认。
- `product_category_id` 需要分类名称到分类 ID 的来源，不能只传中文分类名。
- `influencer_sort_field_v2` 看起来是达人排序字段，不能直接代表商品“总销量”排序。
- EchoTik 鉴权、超时、限流、错误响应格式仍需确认。
- 第三方响应需要标准化后返回，不能把原始错误、签名、token、完整异常堆栈暴露给前端。

## 9. 验收标准

- 输入示例提示词后，后端能解析出 `region=US`、`page_num=1`、`page_size=3`、`sort_type=1`。
- 未确认的关键词字段不被伪造成不存在的 API 参数。
- 未确认分类 ID 时，响应中可以保留分类名称用于调试，但不强行传 `product_category_id`。
- EchoTik 调用失败时返回安全业务错误，不返回第三方原始敏感信息。
- 无数据库阶段商品结果只通过接口返回，不做持久化。
