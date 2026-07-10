import { handleAgentRoutes } from "./routes/agent.routes.js";
import {
  getRequestUrl,
  handleOptions,
  notFound,
  sendJson
} from "./utils/http.js";

export function createApp() {
  return async function app(req, res) {
    try {
      if (handleOptions(req, res)) {
        return;
      }

      const url = getRequestUrl(req);

      if (url.pathname === "/api/health") {
        sendJson(res, 200, {
          code: "SUCCESS",
          data: {
            service: "linkfox-product-agent-backend",
            status: "ok"
          }
        });
        return;
      }

      if (url.pathname.startsWith("/api/agent/")) {
        await handleAgentRoutes(req, res, url);
        return;
      }

      notFound(res);
    } catch (error) {
      sendJson(res, error.statusCode || 500, {
        code: error.code || "INTERNAL_ERROR",
        message: error.message || "服务器内部错误"
      });
    }
  };
}
