import { readJsonBody, sendJson } from "../utils/http.js";
import {
  buildEchoTikProductListParams,
  parseProductSearchPrompt
} from "../services/prompt-parser.service.js";
import { searchEchoTikProducts } from "../services/echotik-product.service.js";

export async function handleProductSearch(req, res) {
  const body = await readJsonBody(req);
  const prompt = typeof body.prompt === "string" ? body.prompt.trim() : "";

  if (!prompt) {
    sendJson(res, 400, {
      code: "INVALID_PROMPT",
      message: "请传入 prompt 字段"
    });
    return;
  }

  const query = parseProductSearchPrompt(prompt);
  const echotikParams = buildEchoTikProductListParams(query);
  const result = await searchEchoTikProducts(echotikParams);

  sendJson(res, 200, {
    code: "BACKEND_SKELETON_READY",
    message: "后端基础框架已连通，EchoTik API 调用尚未实现",
    data: {
      prompt,
      query,
      echotikParams,
      items: result.items
    }
  });
}
