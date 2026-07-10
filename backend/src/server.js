import http from "node:http";
import { createApp } from "./app.js";
import { env } from "./config/env.js";

const server = http.createServer(createApp());

server.listen(env.port, env.host, () => {
  console.log(`Product Agent backend listening on http://${env.host}:${env.port}`);
});
