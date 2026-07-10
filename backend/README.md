# Linkfox 选品 Agent 后端

后端使用 Python FastAPI，实现选品 Agent 的基础接口、提示词解析、EchoTik 商品列表参数构造、可选真实 EchoTik API 调用、可选 PostgreSQL 查询记录和可选 Redis 缓存。

## 目录

- `app/main.py`：FastAPI 应用入口、CORS 和异常处理。
- `app/api/v1/routes/agent.py`：Agent 路由，保持请求绑定和 service 调用。
- `app/common/`：统一响应、常量等基础能力。
- `app/core/config.py`：环境变量和运行配置读取。
- `app/db/`：SQLAlchemy 异步引擎、会话和开发建表入口。
- `app/models/`：SQLAlchemy ORM 持久化模型。
- `app/repositories/`：数据库查询和写入逻辑。
- `app/cache/`：Redis 查询结果和分类映射缓存。
- `app/schemas/product_search.py`：Pydantic 请求、响应和内部 DTO。
- `app/services/`：提示词解析、EchoTik 调用和选品搜索编排。
- `tests/test_agent_api.py`：接口和关键 service 行为测试。

## 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 本地 Docker 服务

在项目根目录启动 PostgreSQL 和 Redis：

```bash
docker compose up -d linkfox-postgres linkfox-redis
```

默认连接：

```text
DATABASE_URL=postgresql+asyncpg://linkfox:linkfox_dev_password@127.0.0.1:15432/linkfox
REDIS_URL=redis://127.0.0.1:16379/0
```

数据库和 Redis 默认关闭。需要使用时设置：

```text
DATABASE_ENABLED=true
REDIS_ENABLED=true
```

初始化表结构：

```bash
python -m app.db.init_db
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

`POST /api/agent/product-search` 默认返回占位结果：

```json
{
  "code": "BACKEND_SKELETON_READY",
  "message": "后端基础框架已连通，EchoTik API 调用默认未启用",
  "data": {
    "prompt": "原始提示词",
    "query": {},
    "echotikParams": {},
    "items": []
  }
}
```

## EchoTik 配置

商品列表 API 使用：

```text
GET https://open.echotik.live/api/v3/echotik/product/list
Authorization: Basic <base64(username:password)>
```

启用真实调用：

```text
ECHOTIK_ENABLE_REAL_API=true
ECHOTIK_USERNAME=你的 EchoTik 用户名
ECHOTIK_PASSWORD=你的 EchoTik 密码
```

当前只提交官方商品列表文档中已确认的字段：

- `region`
- `page_num`
- `page_size`
- `product_sort_field`
- `sort_type`
- `category_id` / `category_l2_id` / `category_l3_id`，仅在本地分类映射命中时提交

商品关键词只保留在内部 `query.keyword`，不提交给 EchoTik 商品列表 API。

## 检查

```bash
python -m compileall app tests
python -m pytest
```
