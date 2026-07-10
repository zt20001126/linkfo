# Linkfox Product Agent

这是一个“选品 Agent”前后端分离原型项目，当前包含原生静态前端和 Python FastAPI 后端。

## 项目结构

```text
linkfox/
  frontend/   前端页面原型
  backend/    Python FastAPI 后端服务
```

## 前端启动

前端目前是静态页面，可以用 Python 内置静态服务器启动。

在项目根目录执行：

```bash
python -m http.server 4173 --bind 127.0.0.1 --directory frontend
```

然后在浏览器打开：

```text
http://127.0.0.1:4173/
```

前端入口文件：

```text
frontend/index.html
```

## 后端启动

后端使用 Python FastAPI。

进入后端目录：

```bash
cd backend
```

创建虚拟环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

启动服务：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8787
```

默认后端地址：

```text
http://127.0.0.1:8787
```

## 后端检查

```bash
python -m compileall app tests
python -m pytest
```

健康检查接口：

```text
GET http://127.0.0.1:8787/api/health
```

当前占位接口：

```text
GET  http://127.0.0.1:8787/api/agent/capabilities
POST http://127.0.0.1:8787/api/agent/product-search
```

`POST /api/agent/product-search` 当前只返回提示词解析结果和占位商品数据，EchoTik API 调用尚未实现。

## 环境变量

后端环境变量示例文件：

```text
backend/.env.example
```

后续接入 EchoTik API 时，需要配置：

```text
ECHOTIK_BASE_URL
ECHOTIK_USERNAME
ECHOTIK_PASSWORD
```
