import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';
import { admins } from './admins';

export const operationLogs = sqliteTable('operation_logs', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  adminId: integer('admin_id').notNull(),
  action: text('action').notNull(),
  resource: text('resource'),
  resourceId: integer('resource_id'),
  details: text('details'),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  createdAt: text('created_at').$type<Date>(),
});

export type OperationLog = typeof operationLogs.$inferSelect;
export type NewOperationLog = typeof operationLogs.$inferInsert;
