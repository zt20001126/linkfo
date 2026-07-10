# 选品Agent 前端原型

这是 EchoTik 选品功能的静态前端原型，当前只包含页面结构、提示词解析预览、模拟商品数据和表格交互。

## 目录

- `index.html`：页面骨架
- `src/styles/base.css`：全局变量和基础样式
- `src/styles/product-agent.css`：选品页面样式
- `src/scripts/mock-products.js`：前端模拟数据
- `src/scripts/prompt-parser.js`：提示词解析和 EchoTik 查询参数映射
- `src/scripts/prompt-builder.js`：选品工具参数到提示词模板的生成逻辑
- `src/scripts/product-agent.js`：页面状态、渲染和交互逻辑

## 后端接入

`product-agent.js` 点击“运行选品”时会请求后端选品接口。如果页面从后端根路径打开，例如 `http://127.0.0.1:8787/`，会默认请求同一个后端服务：

```js
fetch("http://127.0.0.1:8787/api/agent/product-search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: elements.promptInput.value })
});
```

如果后端启动在其它端口，可以在打开静态页面时通过 `api` 查询参数覆盖，例如：

```text
index.html?api=http://127.0.0.1:8789
```
