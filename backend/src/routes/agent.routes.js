import { handleProductSearch } from "../controllers/product-search.controller.js";
import { methodNotAllowed, notFound, sendJson } from "../utils/http.js";

export async function handleAgentRoutes(req, res, url) {
  if (url.pathname === "/api/agent/capabilities") {
    if (req.method !== "GET") {
      methodNotAllowed(res, ["GET"]);
      return;
    }

    sendJson(res, 200, {
      code: "SUCCESS",
      data: {
        tools: [
          {
            id: "echotik_product_search",
            name: "EchoTik 商品搜索",
            status: "planned"
          }
        ]
      }
    });
    return;
  }

  if (url.pathname === "/api/agent/product-search") {
    if (req.method !== "POST") {
      methodNotAllowed(res, ["POST"]);
      return;
    }

    await handleProductSearch(req, res);
    return;
  }

  notFound(res);
}
