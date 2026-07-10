# Linkfox 选品 Agent 后端

当前后端使用 Python FastAPI，实现选品 Agent 的基础接口、提示词解析和 EchoTik 商品查询参数占位构造。真实 EchoTik API 调用尚未实现。

## 目录

- `app/main.py`：FastAPI 应用入口、CORS、中间件和异常处理。
- `app/api/v1/router.py`：API 路由聚合入口，当前挂载在 `/api` 下。
- `app/api/v1/routes/health.py`：健康检查路由。
- `app/api/v1/routes/agent.py`：Agent 相关路由。
- `app/common/result.py`：统一 JSON 响应结构。
- `app/common/constants.py`：无敏感业务常量。
- `app/core/config.py`：环境变量和运行配置读取。
- `app/exceptions/business_exception.py`：业务异常。
- `app/schemas/product_search.py`：Pydantic 请求、响应和内部数据边界。
- `app/services/prompt_parser_service.py`：提示词解析和 EchoTik 参数构造。
- `app/services/echotik_product_service.py`：EchoTik 商品服务占位实现。
- `app/services/product_search_service.py`：选品搜索业务编排。
- `tests/test_agent_api.py`：后端接口测试。

## 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 启动

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8787
```

默认服务地址：

```text
http://127.0.0.1:8787
```

## 当前接口

```http
GET /api/health
GET /api/agent/capabilities
POST /api/agent/product-search
```

`POST /api/agent/product-search` 现在只返回占位数据，后续确认 EchoTik 鉴权、参数、限流和失败格式后再接入真实 API。

## 检查

```bash
python -m compileall app tests
python -m pytest
```
