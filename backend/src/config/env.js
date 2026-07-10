export const env = {
  host: process.env.HOST || "127.0.0.1",
  port: Number(process.env.PORT || 8787),
  echotik: {
    baseUrl: process.env.ECHOTIK_BASE_URL || "https://open.echotik.live",
    username: process.env.ECHOTIK_USERNAME || "",
    password: process.env.ECHOTIK_PASSWORD || ""
  }
};
