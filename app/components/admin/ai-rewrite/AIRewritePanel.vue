<!-- app/components/admin/ai-rewrite/AIRewritePanel.vue -->

<template>
  <div class="ai-rewrite-panel">
    <n-card title="🤖 AI 智能改写" size="large">
      <n-form ref="formRef" :model="formData" label-placement="top">
        <n-form-item label="参考文章链接" required>
          <n-input
            v-model:value="formData.sourceUrl"
            placeholder="请输入微信公众号文章链接，如：https://mp.weixin.qq.com/s/xxx"
            clearable
          />
        </n-form-item>

        <n-form-item label="改写策略" required>
          <n-radio-group v-model:value="formData.rewriteStrategy">
            <n-space>
              <n-radio value="standard">
                标准改写
                <n-text depth="3" style="font-size: 12px">
                  （保留核心观点）
                </n-text>
              </n-radio>
              <n-radio value="deep">
                深度改写
                <n-text depth="3" style="font-size: 12px">
                  （添加案例分析）
                </n-text>
              </n-radio>
              <n-radio value="creative">
                创意改写
                <n-text depth="3" style="font-size: 12px">
                  （完全重新创作）
                </n-text>
              </n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="文章模板" required>
          <n-radio-group v-model:value="formData.templateType">
            <n-space>
              <n-radio value="tutorial">教程类</n-radio>
              <n-radio value="concept">概念类</n-radio>
              <n-radio value="comparison">对比类</n-radio>
              <n-radio value="practice">实战类</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="发布设置" required>
          <n-radio-group v-model:value="formData.autoPublish">
            <n-space>
              <n-radio :value="false">
                保存到草稿箱
                <n-text depth="3" style="font-size: 12px">
                  （推荐，人工审核后发布）
                </n-text>
              </n-radio>
              <n-radio :value="true">
                立即发布
                <n-text depth="3" style="font-size: 12px">
                  （自动发布到前台）
                </n-text>
              </n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-alert type="info" title="预计成本" style="margin-bottom: 20px">
          预计消耗：¥0.016 | 预计时间：2-3 分钟
        </n-alert>

        <n-space>
          <n-button
            type="primary"
            :loading="store.isLoading"
            @click="handleSubmit"
          >
            🚀 开始改写
          </n-button>
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useMessage } from 'naive-ui';
import { useAIRewriteStore } from '@/stores/ai-rewrite';

const message = useMessage();
const store = useAIRewriteStore();
const formRef = ref(null);

const formData = reactive({
  sourceUrl: '',
  rewriteStrategy: 'standard',
  templateType: 'tutorial',
  autoPublish: false,
});

const handleSubmit = () => {
  if (!formData.sourceUrl) {
    message.error('请输入文章链接');
    return;
  }

  store.submitRewrite(formData);
  message.success('开始改写，请在任务列表中查看进度');
};

const handleReset = () => {
  formData.sourceUrl = '';
  formData.rewriteStrategy = 'standard';
  formData.templateType = 'tutorial';
  formData.autoPublish = false;
};
</script>

<style scoped>
.ai-rewrite-panel {
  max-width: 800px;
  margin: 0 auto;
}
</style>
