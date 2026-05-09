import { drizzle } from 'drizzle-orm/libsql';
import { createClient } from '@libsql/client';
import * as schema from './schema';
import path from 'path';

const sqlitePath = process.env.SQLITE_DB_PATH || path.join(process.cwd(), 'blog.db');

const sqlite = createClient({
  url: `file:${sqlitePath}`,
});

export const db = drizzle(sqlite, { schema });

export type DB = typeof db;
