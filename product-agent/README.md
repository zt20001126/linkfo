# 选品Agent 前端原型

这是 EchoTik 选品功能的静态前端原型，当前只包含页面结构、提示词解析预览、模拟商品数据和表格交互。

## 目录

- `index.html`：页面骨架
- `src/styles/base.css`：全局变量和基础样式
- `src/styles/product-agent.css`：选品页面样式
- `src/scripts/mock-products.js`：前端模拟数据
- `src/scripts/prompt-parser.js`：提示词解析和 EchoTik 查询参数映射
- `src/scripts/product-agent.js`：页面状态、渲染和交互逻辑

## 后续接入点

后续确认 EchoTik 接口需求后，可以把 `product-agent.js` 里的模拟查询替换成后端接口调用，例如：

```js
fetch("/api/agent/product-search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: elements.promptInput.value })
});
```
