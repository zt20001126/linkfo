# Linkfox Product Agent

这是一个选品 Agent 原型项目，当前包含前端静态页面和后端基础框架。

## 项目结构

```text
linkfox/
  frontend/   前端页面原型
  backend/    后端 Node.js 服务骨架
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

后端使用 Node.js 原生 HTTP 服务，当前不需要安装第三方依赖。

进入后端目录：

```bash
cd backend
```

启动服务：

```bash
npm start
```

默认后端地址：

```text
http://127.0.0.1:8787
```

## 后端检查

检查 JS 语法：

```bash
npm run check
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

`POST /api/agent/product-search` 当前只返回占位数据，EchoTik API 调用尚未实现。

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
