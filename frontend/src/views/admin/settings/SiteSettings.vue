<template>
  <div class="site-settings-page">
    <div class="page-header">
      <div class="header-left">
        <h1>站点设置</h1>
        <p>配置博客基本信息</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="handleSave" :loading="saving">
          保存设置
        </n-button>
      </div>
    </div>

    <n-space vertical size="large">
      <!-- Basic Settings -->
      <n-card title="基本信息">
        <n-form
          ref="formRef"
          :model="formData"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="站点名称">
            <n-input
              v-model:value="formData.siteName"
              placeholder="请输入站点名称"
            />
          </n-form-item>

          <n-form-item label="站点描述">
            <n-input
              v-model:value="formData.siteDescription"
              type="textarea"
              placeholder="请输入站点描述"
              :rows="3"
            />
          </n-form-item>

          <n-form-item label="站点 Logo">
            <div class="upload-field">
              <n-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                :show-file-list="false"
                @finish="handleLogoUpload"
              >
                <n-button>
                  <template #icon>
                    <n-icon :component="CloudUploadOutline" />
                  </template>
                  上传 Logo
                </n-button>
              </n-upload>
              <div v-if="formData.siteLogo" class="preview">
                <img :src="formData.siteLogo" alt="Logo" />
                <n-button
                  size="small"
                  type="error"
                  @click="formData.siteLogo = ''"
                >
                  移除
                </n-button>
              </div>
            </div>
          </n-form-item>

          <n-form-item label="站点 URL">
            <n-input
              v-model:value="formData.siteUrl"
              placeholder="请输入站点 URL"
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- SEO Settings -->
      <n-card title="SEO 设置">
        <n-form
          :model="formData"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="站点关键词">
            <n-input
              v-model:value="formData.siteKeywords"
              placeholder="请输入站点关键词，多个用逗号分隔"
            />
          </n-form-item>

          <n-form-item label="默认 OG 图片">
            <div class="upload-field">
              <n-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                :show-file-list="false"
                @finish="handleOgImageUpload"
              >
                <n-button>
                  <template #icon>
                    <n-icon :component="CloudUploadOutline" />
                  </template>
                  上传 OG 图片
                </n-button>
              </n-upload>
              <div v-if="formData.ogImage" class="preview">
                <img :src="formData.ogImage" alt="OG Image" />
                <n-button
                  size="small"
                  type="error"
                  @click="formData.ogImage = ''"
                >
                  移除
                </n-button>
              </div>
            </div>
          </n-form-item>
        </n-form>
      </n-card>

      <!-- Social Links -->
      <n-card title="社交媒体链接">
        <n-form
          :model="formData"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="GitHub">
            <n-input
              v-model:value="formData.githubUrl"
              placeholder="请输入 GitHub 地址"
            />
          </n-form-item>

          <n-form-item label="Twitter">
            <n-input
              v-model:value="formData.twitterUrl"
              placeholder="请输入 Twitter 地址"
            />
          </n-form-item>

          <n-form-item label="微博">
            <n-input
              v-model:value="formData.weiboUrl"
              placeholder="请输入微博地址"
            />
          </n-form-item>

          <n-form-item label="邮箱">
            <n-input
              v-model:value="formData.email"
              placeholder="请输入联系邮箱"
            />
          </n-form-item>
        </n-form>
      </n-card>

      <!-- Comment Settings -->
      <n-card title="评论设置">
        <n-form
          :model="formData"
          label-placement="left"
          label-width="100px"
        >
          <n-form-item label="评论审核">
            <n-switch v-model:value="formData.commentRequireReview">
              <template #checked>
                需要审核
              </template>
              <template #unchecked>
                自动通过
              </template>
            </n-switch>
          </n-form-item>

          <n-form-item label="允许评论">
            <n-switch v-model:value="formData.commentEnabled">
              <template #checked>
                开启
              </template>
              <template #unchecked>
                关闭
              </template>
            </n-switch>
          </n-form-item>
        </n-form>
      </n-card>

      <!-- About Page Settings -->
      <n-card title="关于页面设置">
        <n-divider title-style="margin-top: 0; margin-bottom: 20px;">
          欢迎模块
        </n-divider>
        
        <n-form
          :model="formData"
          label-placement="left"
          label-width="120px"
        >
          <n-form-item label="欢迎标题">
            <n-input
              v-model:value="formData.aboutWelcomeTitle"
              placeholder="例如：欢迎来到我的博客"
            />
          </n-form-item>

          <n-form-item label="欢迎内容">
            <n-input
              v-model:value="formData.aboutWelcomeContent"
              type="textarea"
              placeholder="请输入欢迎内容"
              :rows="3"
            />
          </n-form-item>
        </n-form>

        <n-divider title-style="margin-top: 0; margin-bottom: 20px;">
          博主介绍模块
        </n-divider>

        <n-form
          :model="formData"
          label-placement="left"
          label-width="120px"
        >
          <n-form-item label="博主标题">
            <n-input
              v-model:value="formData.aboutAuthorTitle"
              placeholder="例如：关于博主"
            />
          </n-form-item>

          <n-form-item label="博主介绍">
            <n-input
              v-model:value="formData.aboutAuthorContent"
              type="textarea"
              placeholder="请输入博主介绍"
              :rows="3"
            />
          </n-form-item>
        </n-form>

        <n-divider title-style="margin-top: 0; margin-bottom: 20px;">
          技术栈模块
        </n-divider>

        <n-form
          :model="formData"
          label-placement="left"
          label-width="120px"
        >
          <n-form-item label="技术栈标题">
            <n-input
              v-model:value="formData.aboutTechStackTitle"
              placeholder="例如：技术栈"
            />
          </n-form-item>

          <n-form-item label="技术栈列表">
            <div class="tech-stack-editor">
              <n-dynamic-tags
                v-model:value="formData.aboutTechStackItems"
                placeholder="输入技术栈后按回车"
              />
              <p class="help-text">
                输入技术栈名称后按回车键添加，例如：Vue.js、React、TypeScript
              </p>
            </div>
          </n-form-item>
        </n-form>

        <n-divider title-style="margin-top: 0; margin-bottom: 20px;">
          联系方式模块
        </n-divider>

        <n-form
          :model="formData"
          label-placement="left"
          label-width="120px"
        >
          <n-form-item label="联系方式标题">
            <n-input
              v-model:value="formData.aboutContactTitle"
              placeholder="例如：联系方式"
            />
          </n-form-item>

          <n-form-item label="联系邮箱">
            <n-input
              v-model:value="formData.aboutContactEmail"
              placeholder="请输入联系邮箱"
            />
          </n-form-item>

          <n-form-item label="GitHub 地址">
            <n-input
              v-model:value="formData.aboutContactGithub"
              placeholder="请输入 GitHub 地址"
            />
          </n-form-item>

          <n-form-item label="GitHub 显示文本">
            <n-input
              v-model:value="formData.aboutContactGithubLabel"
              placeholder="例如：GitHub"
            />
          </n-form-item>
        </n-form>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { CloudUploadOutline } from '@vicons/ionicons5'
import { settingApi } from '@/api/setting'

const message = useMessage()
const saving = ref(false)

const formRef = ref(null)

const formData = reactive({
  // Basic Settings
  siteName: '',
  siteDescription: '',
  siteLogo: '',
  siteUrl: '',
  siteKeywords: '',
  ogImage: '',
  
  // Social Links
  githubUrl: '',
  twitterUrl: '',
  weiboUrl: '',
  email: '',
  
  // About Page Settings
  aboutWelcomeTitle: '',
  aboutWelcomeContent: '',
  aboutAuthorTitle: '',
  aboutAuthorContent: '',
  aboutTechStackTitle: '',
  aboutTechStackItems: [] as string[],
  aboutContactTitle: '',
  aboutContactEmail: '',
  aboutContactGithub: '',
  aboutContactGithubLabel: '',
  
  // Comment Settings
  commentRequireReview: true,
  commentEnabled: true,
})

const uploadUrl = '/api/v1/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
}))

const handleLogoUpload = ({ event }: any) => {
  const response = JSON.parse(event.target.response)
  formData.siteLogo = response.url
  message.success('Logo 上传成功')
}

const handleOgImageUpload = ({ event }: any) => {
  const response = JSON.parse(event.target.response)
  formData.ogImage = response.url
  message.success('OG 图片上传成功')
}

const handleSave = async () => {
  saving.value = true
  try {
    const data: any = {
      // Basic Settings
      site_name: formData.siteName,
      site_description: formData.siteDescription,
      site_logo: formData.siteLogo,
      site_url: formData.siteUrl,
      site_keywords: formData.siteKeywords,
      og_image: formData.ogImage,
      
      // Social Links
      github_url: formData.githubUrl,
      twitter_url: formData.twitterUrl,
      weibo_url: formData.weiboUrl,
      email: formData.email,
      
      // About Page Settings
      about_welcome_title: formData.aboutWelcomeTitle,
      about_welcome_content: formData.aboutWelcomeContent,
      about_author_title: formData.aboutAuthorTitle,
      about_author_content: formData.aboutAuthorContent,
      about_tech_stack_title: formData.aboutTechStackTitle,
      about_tech_stack_items: formData.aboutTechStackItems,
      about_contact_title: formData.aboutContactTitle,
      about_contact_email: formData.aboutContactEmail,
      about_contact_github: formData.aboutContactGithub,
      about_contact_github_label: formData.aboutContactGithubLabel,
      
      // Comment Settings
      comment_require_review: formData.commentRequireReview,
      comment_enabled: formData.commentEnabled,
    }

    await settingApi.update(data)
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

const loadSettings = async () => {
  try {
    const response = await settingApi.get()
    const settings = response.settings
    Object.assign(formData, {
      // Basic Settings
      siteName: settings.site_name,
      siteDescription: settings.site_description,
      siteLogo: settings.site_logo,
      siteUrl: settings.site_url,
      siteKeywords: settings.site_keywords,
      ogImage: settings.og_image,
      
      // Social Links
      githubUrl: settings.github_url,
      twitterUrl: settings.twitter_url,
      weiboUrl: settings.weibo_url,
      email: settings.email,
      
      // About Page Settings
      aboutWelcomeTitle: settings.about_welcome_title,
      aboutWelcomeContent: settings.about_welcome_content,
      aboutAuthorTitle: settings.about_author_title,
      aboutAuthorContent: settings.about_author_content,
      aboutTechStackTitle: settings.about_tech_stack_title,
      aboutTechStackItems: settings.about_tech_stack_items || [],
      aboutContactTitle: settings.about_contact_title,
      aboutContactEmail: settings.about_contact_email,
      aboutContactGithub: settings.about_contact_github,
      aboutContactGithubLabel: settings.about_contact_github_label,
      
      // Comment Settings
      commentRequireReview: settings.comment_require_review,
      commentEnabled: settings.comment_enabled,
    })
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.site-settings-page {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-left p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  gap: 12px;
}

.upload-field {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview img {
  max-height: 80px;
  border-radius: 4px;
}

.tech-stack-editor {
  width: 100%;
}

.tech-stack-editor .help-text {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #999;
}
</style>
