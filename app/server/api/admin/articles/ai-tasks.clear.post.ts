// app/server/api/admin/articles/ai-tasks.clear.post.ts

import { defineEventHandler } from 'h3';
import { clearCompletedTasks } from '~/server/stores/ai-tasks';

export default defineEventHandler(async (event) => {
  try {
    const count = clearCompletedTasks();
    
    return {
      success: true,
      message: `已清理 ${count} 个已完成任务`,
    };
  } catch (error: any) {
    console.error('清理任务失败:', error);
    return {
      success: false,
      message: '清理失败',
    };
  }
});
