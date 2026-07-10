# Linkfox - AI Coding Agent Guide

## 项目概览

Linkfox 当前是一个“选品 Agent”前后端分离原型项目：

- `backend`：Node.js 原生 HTTP 服务，使用 ES Modules，不依赖 Express/Koa 等框架。
- `frontend`：原生 HTML/CSS/JavaScript 静态前端原型。
- 当前核心能力是把用户的选品提示词解析成 EchoTik 商品查询参数，并返回占位搜索结果；真实 EchoTik API 接入仍属于后续工作。

Codex 接手开发时，必须先读现有同类代码，再按本项目已有结构实现。不要照搬大型后端项目的复杂分层，也不要为当前原型引入不必要的框架、依赖或抽象。

## 必须遵守的核心规范

1. 开发前先阅读同类代码和 README。
2. 保持项目轻量，未经明确要求不要新增框架或依赖。
3. 后端遵守 `routes -> controllers -> services -> utils/config` 分层。
4. 前端遵守 `index.html -> styles -> scripts` 的组织方式。
5. 路由层只做路径匹配、HTTP 方法判断和分发。
6. Controller 负责读取请求、校验入参、组织响应。
7. Service 负责业务逻辑、提示词解析、外部 API 参数组装和后续 API 调用。
8. Utils 只放通用 HTTP、序列化、请求体解析等基础能力。
9. 禁止把原始异常、堆栈、密钥、第三方响应敏感信息直接返回给前端。
10. 涉及真实 EchoTik API、鉴权、密钥、计费或数据持久化时，必须先确认现有配置和安全边界。

## 项目结构

```text
.
├── backend/
│   ├── package.json
│   ├── README.md
│   └── src/
│       ├── server.js
│       ├── app.js
│       ├── config/
│       │   └── env.js
│       ├── routes/
│       │   └── agent.routes.js
│       ├── controllers/
│       │   └── product-search.controller.js
│       ├── services/
│       │   ├── prompt-parser.service.js
│       │   └── echotik-product.service.js
│       └── utils/
│           └── http.js
└── frontend/
    ├── README.md
    ├── index.html
    └── src/
        ├── styles/
        │   ├── base.css
        │   └── product-agent.css
        └── scripts/
            ├── mock-products.js
            ├── prompt-parser.js
            └── product-agent.js
```

## 后端分层规范

### `server.js`

- 只负责创建 HTTP server、读取环境配置、启动监听。
- 不写路由分发、业务逻辑、第三方 API 调用。

### `app.js`

- 负责应用入口、基础路由分发、CORS 预检、兜底错误处理。
- 新增业务路由时，优先在 `routes` 中增加路由模块，再从 `app.js` 挂载。
- 兜底异常返回必须是安全信息，不能直接暴露堆栈。

### `routes`

- 只判断 URL、HTTP method，并调用 controller。
- 方法不匹配时使用 `methodNotAllowed`。
- 找不到接口时使用 `notFound`。
- 不在 route 中解析复杂请求体，不写业务逻辑。

### `controllers`

- 负责读取请求体、基础参数校验、调用 service、返回 JSON。
- 统一使用 `sendJson` 返回。
- 入参错误返回明确的业务错误码和中文提示。
- 不直接写 EchoTik HTTP 调用逻辑。

### `services`

- `prompt-parser.service.js` 负责提示词解析、字段映射、EchoTik 参数构造。
- `echotik-product.service.js` 负责 EchoTik 商品服务调用或占位实现。
- 外部 API 接入时，优先在 service 内封装，不要散落在 controller 或 frontend。
- 复杂映射用常量表表达，避免魔法数字散落。

### `utils`

- 只放项目内通用基础工具，例如 JSON 响应、CORS、请求体解析、URL 构造。
- 不把业务规则塞进 utils。

## 前端开发规范

- 保持原生 HTML/CSS/JavaScript 结构，未经明确要求不要引入 React/Vue/构建工具。
- `index.html` 只放页面结构和脚本/样式引用。
- 全局变量、基础 reset、设计 token 放在 `src/styles/base.css`。
- 页面专属布局和组件样式放在 `src/styles/product-agent.css`。
- 前端业务状态、渲染、交互放在 `src/scripts/product-agent.js`。
- 前端提示词解析放在 `src/scripts/prompt-parser.js`；后端也有一份解析逻辑，修改解析规则时必须同步评估两边是否需要一致。
- 模拟数据只放在 `src/scripts/mock-products.js`，不要混入真实 API 调用。
- 渲染用户输入或接口返回文本时必须做 HTML 转义，参考现有 `escapeHtml`。
- 按钮、表格、筛选、toast 等交互要保持当前风格，不做无关 UI 重设计。

## API 响应规范

后端 JSON 响应保持当前结构：

```json
{
  "code": "SUCCESS",
  "message": "可选提示",
  "data": {}
}
```

约定：

- 成功使用稳定的字符串 `code`，例如 `SUCCESS` 或当前占位的 `BACKEND_SKELETON_READY`。
- 参数错误使用明确错误码，例如 `INVALID_PROMPT`。
- 未找到接口使用 `NOT_FOUND`。
- 方法不允许使用 `METHOD_NOT_ALLOWED`。
- 未知异常使用安全错误码和安全提示，不返回 `error.stack`。

## 错误处理和安全规范

- 不要把 `error.stack`、第三方完整报错、密钥、请求签名、认证 token 返回给前端。
- 捕获异常时可以在服务端日志中记录必要细节，但响应给前端必须是安全信息。
- 读取 JSON 请求体失败时返回 400。
- 接入 EchoTik API 时，API key、cookie、token 等只能来自环境变量或安全配置，不能写死在代码、README 或 AGENTS.md。
- 不要提交真实生产数据、账号、密钥、私有接口凭据。

## 配置规范

- 环境变量读取集中在 `backend/src/config/env.js`。
- 新增配置时先扩展 `env.js`，再由业务模块引用。
- 不要在 service/controller 中直接读取散落的 `process.env.X`。
- 本地默认值只能用于无敏感性的开发配置，例如 host、port。

## EchoTik API 接入规范

接入真实 EchoTik API 前必须确认：

- API 鉴权方式。
- 请求参数字段、分页限制、排序字段枚举和地区枚举。
- 失败响应格式和限流策略。
- 是否需要缓存、重试、超时、降级。
- 是否允许前端直接展示第三方返回的错误信息。

实现时要求：

- HTTP 调用封装在 `backend/src/services/echotik-product.service.js` 或专门 service 中。
- Controller 只拿 service 返回的标准结果。
- 外部错误统一转换为安全业务错误。
- 不把 EchoTik 原始敏感响应直接透传给前端。

## 代码风格

- 使用 ES Modules：`import/export`。
- 文件名保持 kebab-case 或现有命名风格，例如 `product-search.controller.js`。
- 常量使用 `UPPER_SNAKE_CASE`。
- 函数和变量使用 `camelCase`。
- 优先使用清晰的小函数，但不要为一次性逻辑过度拆分。
- 注释使用中文，解释业务原因、参数映射原因或临时兼容原因。
- 不写无意义注释，例如“调用函数”“赋值给变量”。

## 开发命令

后端：

```bash
cd backend
npm start
npm run check
```

前端：

```text
frontend/index.html 可以直接用浏览器打开。
```

如果后续引入构建工具或测试框架，必须同步更新本文件和对应 README。

## Codex 开发前自检清单

Codex 修改代码前必须确认：

- 是否已阅读相关 README 和同类代码。
- 是否保持了当前轻量架构，没有无故新增依赖。
- 是否放在正确目录：route、controller、service、utils、frontend scripts/styles。
- 是否没有在 route 中写复杂业务。
- 是否没有在 controller 中写第三方 API 细节。
- 是否没有把原始异常或敏感信息返回给前端。
- 是否同步考虑了前端和后端提示词解析规则的一致性。
- 是否运行了与改动相关的最小检查；后端 JS 改动至少运行 `npm run check`。

## 文档维护

- 新增重要模块时，同步更新本文件的目录说明。
- 新增接口时，同步更新 `backend/README.md` 的接口列表。
- 修改前端主要交互时，同步更新 `frontend/README.md`。
- 接入真实第三方服务时，同步补充配置、失败处理和安全注意事项。
