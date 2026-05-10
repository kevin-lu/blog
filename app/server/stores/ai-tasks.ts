// app/server/stores/ai-tasks.ts

interface AITask {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  sourceUrl: string;
  rewriteStrategy: 'standard' | 'deep' | 'creative';
  templateType: 'tutorial' | 'concept' | 'comparison' | 'practice';
  autoPublish: boolean;
  articleId?: number;
  articleSlug?: string;
  error?: string;
  tokenUsage?: number;
  cost?: number;
  createdAt: Date;
  completedAt?: Date;
}

const tasks = new Map<string, AITask>();

export function createAITask(task: Omit<AITask, 'id' | 'createdAt'>): AITask {
  const id = `task_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  const newTask: AITask = {
    ...task,
    id,
    createdAt: new Date(),
  };
  tasks.set(id, newTask);
  return newTask;
}

export function getAITask(taskId: string): AITask | undefined {
  return tasks.get(taskId);
}

export function updateAITask(taskId: string, updates: Partial<AITask>): AITask | undefined {
  const task = tasks.get(taskId);
  if (!task) return undefined;
  
  const updated = { ...task, ...updates };
  tasks.set(taskId, updated);
  return updated;
}

export function listAITasks(limit = 20): AITask[] {
  return Array.from(tasks.values())
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    .slice(0, limit);
}
