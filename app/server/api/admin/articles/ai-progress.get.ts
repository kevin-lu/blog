// app/server/api/admin/articles/ai-progress.get.ts

import { defineEventHandler, getQuery } from 'h3';
import { getAITask, listAITasks } from '~/server/stores/ai-tasks';

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const { taskId } = query;

    if (taskId) {
      // 查询单个任务
      const task = getAITask(taskId as string);
      if (!task) {
        return {
          success: false,
          message: '任务不存在',
        };
      }

      return {
        success: true,
        data: task,
      };
    } else {
      // 查询任务列表
      const tasks = listAITasks();
      return {
        success: true,
        data: {
          tasks,
          total: tasks.length,
        },
      };
    }
  } catch (error: any) {
    console.error('查询任务进度失败:', error);
    return {
      success: false,
      message: '查询失败',
    };
  }
});
