import type { Config } from 'drizzle-kit';

export default {
  schema: './server/database/schema/index.ts',
  out: './server/database/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.POSTGRES_URL || '',
  },
} satisfies Config;
