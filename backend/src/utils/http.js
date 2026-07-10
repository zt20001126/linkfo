const DEFAULT_HEADERS = {
  "Content-Type": "application/json; charset=utf-8"
};

export function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    ...DEFAULT_HEADERS,
    ...corsHeaders()
  });
  res.end(JSON.stringify(payload));
}

export function sendNoContent(res) {
  res.writeHead(204, corsHeaders());
  res.end();
}

export async function readJsonBody(req) {
  const chunks = [];

  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const rawBody = Buffer.concat(chunks).toString("utf8").trim();
  if (!rawBody) {
    return {};
  }

  try {
    return JSON.parse(rawBody);
  } catch {
    const error = new Error("请求体不是合法 JSON");
    error.statusCode = 400;
    throw error;
  }
}

export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
  };
}

export function getRequestUrl(req) {
  return new URL(req.url, `http://${req.headers.host || "localhost"}`);
}

export function handleOptions(req, res) {
  if (req.method !== "OPTIONS") {
    return false;
  }

  sendNoContent(res);
  return true;
}

export function notFound(res) {
  sendJson(res, 404, {
    code: "NOT_FOUND",
    message: "接口不存在"
  });
}

export function methodNotAllowed(res, allowedMethods) {
  res.writeHead(405, {
    ...DEFAULT_HEADERS,
    ...corsHeaders(),
    Allow: allowedMethods.join(", ")
  });
  res.end(JSON.stringify({
    code: "METHOD_NOT_ALLOWED",
    message: `仅支持 ${allowedMethods.join(", ")}`
  }));
}
