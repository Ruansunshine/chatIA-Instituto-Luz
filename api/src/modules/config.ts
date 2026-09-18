// Configuracao lida do ambiente (variaveis injetadas pelo docker-compose) -
// so valores de porta/host/origem, sem logica de rota (ver index.ts).

export const PORT = Number(process.env.PORT ?? 4000);
export const HOST = process.env.HOST ?? "0.0.0.0";
export const IS_DEV = (process.env.NODE_ENV ?? "development") !== "production";

const DEFAULT_CORS_ORIGINS = [
  "http://localhost:5173",
  "http://localhost:3000",
  "http://localhost:5500",
  "http://127.0.0.1:5500",
  "http://localhost:8080",
];

export const CORS_ORIGINS = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(",").map((origin) => origin.trim())
  : DEFAULT_CORS_ORIGINS;

export const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL ?? "http://backend-python:8001";
