import type { Config } from 'drizzle-kit';

export default {
  schema: './server/database/schema/index.ts',
  out: './server/database/migrations',
  dialect: 'sqlite',
  dbCredentials: {
    url: process.env.SQLITE_DB_PATH || './blog.db',
  },
} satisfies Config;
