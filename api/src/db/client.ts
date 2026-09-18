import { drizzle } from "drizzle-orm/mysql2";
import mysql from "mysql2/promise";

const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
  throw new Error("DATABASE_URL nao definida (.env)");
}

const pool = mysql.createPool(DATABASE_URL);

export const db = drizzle(pool);
