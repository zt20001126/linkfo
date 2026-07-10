# EchoTik 商品列表 API 接入 TODO

## 需求确认

- [x] 确认 EchoTik 商品列表 API 的鉴权方式：Basic Auth。
- [x] 确认 EchoTik 商品列表 API 的真实请求路径和 HTTP 方法：`GET /api/v3/echotik/product/list`。
- [x] 确认 `page_num`、`page_size` 的字段类型和最大分页限制：`page_num<=100000`，`page_size<=10`。
- [x] 确认商品关键词字段名称：商品列表文档未发现普通关键词字段，当前不提交关键词。
- [x] 确认商品排序字段名称和“总销量”对应枚举：`product_sort_field=1`。
- [x] 确认分类名称到分类 ID 的映射来源：本地 `product_category_mapping` 表或 Redis 分类缓存。
- [ ] 确认 EchoTik 限流策略和失败响应格式。

## 配置模块

- [x] 在 `backend/app/core/config.py` 中补齐 EchoTik API 请求路径配置。
- [x] 在 `backend/app/core/config.py` 中补齐 EchoTik 超时时间配置。
- [x] 在 `backend/app/core/config.py` 中补齐是否启用 Redis 缓存的配置。
- [x] 更新 `backend/.env.example`，增加新增配置项且不写入真实密钥。
- [x] 为缺失 EchoTik 必要配置增加安全业务错误。

## Schema 模块

- [x] 根据 EchoTik 最新文档调整 `EchoTikProductListParams` 字段和限制。
- [ ] 为 EchoTik 商品响应定义标准化商品 item schema。
- [ ] 为 EchoTik 错误响应定义内部 DTO，不直接透传第三方结构。
- [ ] 为查询记录预留 request/response 摘要 schema。
- [ ] 保持所有 Pydantic 字段具备中文业务说明。

## 提示词解析模块

- [x] 补充 page_size 最大值校验。
- [x] 将分类名称解析结果和 EchoTik 分类 ID 映射流程分离。
- [x] 在关键词字段未确认前，只保留 `keyword` 到内部 query，不提交给 EchoTik。
- [x] 根据 EchoTik 文档提交已确认的 `product_sort_field` 和 `sort_type`。
- [x] 增加地区、分页、排序方向解析相关 API 测试。

## EchoTik 服务模块

- [x] 在 `backend/app/services/echotik_product_service.py` 中实现真实 HTTP 调用。
- [x] 使用配置中的 base_url、鉴权信息和超时时间。
- [x] 对 EchoTik 超时转换为 `ECHOTIK_TIMEOUT`。
- [x] 对 EchoTik 限流转换为 `ECHOTIK_RATE_LIMITED`。
- [x] 对 EchoTik 非成功响应转换为 `ECHOTIK_REQUEST_FAILED`。
- [x] 标准化 EchoTik 商品列表响应为后端统一 item 结构。
- [x] 确保日志不记录 token、cookie、签名和完整敏感响应。

## 数据库预留模块

- [x] 新增数据库配置和连接模块。
- [x] 新增 `product_search_record` 模型和开发建表入口。
- [x] 新增 `product_category_mapping` 模型和开发建表入口。
- [x] 新增查询记录 repository。
- [x] 新增分类映射 repository。
- [x] 保存查询记录时只存脱敏请求参数和响应摘要。

## Redis 缓存预留模块

- [x] 新增 Redis 配置项。
- [x] 新增商品查询缓存 key 构造函数。
- [x] 新增分类映射缓存读写函数。
- [x] 为缓存设置 TTL，避免长期保存第三方结果。
- [x] 缓存 key 不包含密钥、token、cookie 或用户敏感信息。

## API 模块

- [x] 保持 `POST /api/agent/product-search` 路由只做请求绑定和 service 调用。
- [x] 增加 EchoTik 配置缺失时的 service 测试。
- [ ] 增加 EchoTik 超时和失败响应的 API 测试。
- [x] 增加 page_size 超限时的 API 测试。
- [ ] 确认 `GET /api/agent/capabilities` 是否需要标记真实 EchoTik 接入状态。

## 前端联调

- [ ] 将前端模拟查询逐步替换为后端 `POST /api/agent/product-search` 调用。
- [ ] 增加加载态、成功态、空结果态和错误态。
- [ ] 前端展示后端返回的安全错误提示。
- [ ] 前端渲染商品标题、分类、关键词等文本时保持 HTML 转义。
- [ ] 前后端提示词解析规则变更时同步评估一致性。

## 测试与验证

- [x] 运行 `python -m compileall app tests`。
- [x] 运行 `python -m pytest`。
- [ ] 使用真实或沙箱 EchoTik 配置验证成功查询。
- [ ] 验证 EchoTik 配置缺失不会泄露环境变量。
- [ ] 验证第三方错误不会把原始响应、stack、token 返回给前端。
- [ ] 验证无数据库阶段商品结果只通过接口返回。

## 文档维护

- [x] 更新 `backend/README.md` 的 EchoTik 配置说明。
- [x] 更新 `backend/README.md` 的接口响应示例。
- [x] 更新 `AGENTS.md` 中真实 EchoTik API 接入边界。
- [x] 如果新增数据库或 Redis，补充本地启动和检查命令。
