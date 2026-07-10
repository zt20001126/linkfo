# Linkfox Product Agent

Linkfox 是一个“选品 Agent”前后端分离原型项目，当前包含原生静态前端和 Python FastAPI 后端。

## 项目结构

```text
linkfox/
  docker-compose.yml  本地 PostgreSQL 和 Redis
  frontend/           前端页面原型
  backend/            Python FastAPI 后端服务
```

## 本地基础设施

项目提供本地 Docker Compose 配置：

```bash
docker compose up -d linkfox-postgres linkfox-redis
```

默认端口：

```text
PostgreSQL: 127.0.0.1:15432
Redis:      127.0.0.1:16379
```

数据库和 Redis 在后端中默认关闭，避免普通开发和测试强依赖本地服务。需要启用时复制 `backend/.env.example` 并设置：

```text
DATABASE_ENABLED=true
REDIS_ENABLED=true
```

初始化当前表结构：

```bash
cd backend
python -m app.db.init_db
```

## 前端启动

前端当前是静态页面，可以直接打开 `frontend/index.html`，也可以用 Python 静态服务启动：

```bash
python -m http.server 4173 --bind 127.0.0.1 --directory frontend
```

访问：

```text
http://127.0.0.1:4173/
```

## 后端启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787
```

默认后端地址：

```text
http://127.0.0.1:8787
```

## 后端检查

```bash
cd backend
python -m compileall app tests
python -m pytest
```

## 当前接口

```text
GET  /api/health
GET  /api/agent/capabilities
POST /api/agent/product-search
```

`POST /api/agent/product-search` 默认只返回提示词解析结果和占位商品列表。设置 `ECHOTIK_ENABLE_REAL_API=true` 且配置 `ECHOTIK_USERNAME`、`ECHOTIK_PASSWORD` 后，后端会通过 Basic Auth 调用 EchoTik 商品列表 API。
