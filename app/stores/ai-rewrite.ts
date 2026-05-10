// app/stores/ai-rewrite.ts

import { defineStore } from 'pinia';

interface AITask {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  sourceUrl: string;
  rewriteStrategy: string;
  templateType: string;
  articleId?: number;
  articleSlug?: string;
  error?: string;
  tokenUsage?: number;
  cost?: number;
  createdAt: string;
  completedAt?: string;
}

export const useAIRewriteStore = defineStore('ai-rewrite', {
  state: () => ({
    tasks: [] as AITask[],
    currentTask: null as AITask | null,
    isLoading: false,
  }),

  actions: {
    async submitRewrite(data: {
      sourceUrl: string;
      rewriteStrategy: string;
      templateType: string;
      autoPublish: boolean;
    }) {
      this.isLoading = true;
      try {
        const response = await fetch('/api/admin/articles/ai-rewrite', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const result = await response.json();
        
        if (result.success) {
          this.currentTask = result.data;
          this.pollTaskStatus(result.data.taskId);
        } else {
          throw new Error(result.message);
        }
      } finally {
        this.isLoading = false;
      }
    },

    async pollTaskStatus(taskId: string) {
      const poll = async () => {
        const response = await fetch(`/api/admin/articles/ai-progress?taskId=${taskId}`);
        const result = await response.json();
        
        if (result.success) {
          this.currentTask = result.data;
          
          if (result.data.status === 'completed' || result.data.status === 'failed') {
            this.loadTasks();
            return;
          }
          
          setTimeout(poll, 3000);
        }
      };
      
      poll();
    },

    async loadTasks() {
      const response = await fetch('/api/admin/articles/ai-progress');
      const result = await response.json();
      
      if (result.success) {
        this.tasks = result.data.tasks;
      }
    },
  },
});
