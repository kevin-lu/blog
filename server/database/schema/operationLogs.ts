import { pgTable, serial, varchar, integer, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { admins } from './admins';

export const operationLogs = pgTable('operation_logs', {
  id: serial('id').primaryKey(),
  adminId: integer('admin_id').notNull().references(() => admins.id),
  action: varchar('action', { length: 50 }).notNull(),
  resource: varchar('resource', { length: 50 }),
  resourceId: integer('resource_id'),
  details: jsonb('details'),
  ipAddress: varchar('ip_address', { length: 45 }),
  userAgent: varchar('user_agent', { length: 255 }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});

export type OperationLog = typeof operationLogs.$inferSelect;
export type NewOperationLog = typeof operationLogs.$inferInsert;
