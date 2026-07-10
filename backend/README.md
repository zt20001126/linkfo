# Linkfox 选品Agent 后端骨架

当前后端只提供基础框架，不调用 EchoTik API，不实现真实提示词解析。

## 目录

- `src/server.js`：启动 HTTP 服务
- `src/app.js`：应用入口、基础路由分发、CORS、错误兜底
- `src/config/env.js`：环境变量读取
- `src/routes/agent.routes.js`：Agent 相关路由
- `src/controllers/product-search.controller.js`：选品搜索控制器
- `src/services/prompt-parser.service.js`：提示词解析服务占位
- `src/services/echotik-product.service.js`：EchoTik 商品服务占位
- `src/utils/http.js`：HTTP 工具函数

## 启动

```bash
npm start
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

`POST /api/agent/product-search` 现在只返回占位数据，后续确认需求后再接入 EchoTik API。
