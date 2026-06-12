# 关于页面设置实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 扩展现有站点设置系统，使关于页面内容可通过后台管理界面配置

**架构：** 在现有 SiteSetting 模型基础上新增关于页面相关字段，后端 API 支持获取和更新，前端 About 页面从 API 获取配置数据，管理后台添加关于页面设置入口

**技术栈：** Flask (后端), Vue 3 + Naive UI (前端), SQLAlchemy (数据库)

---

## 文件结构

**后端修改：**
- 修改：`backend/app/models/site_setting.py` - 添加辅助方法
- 修改：`backend/app/api/v1/settings.py` - 扩展 API 支持关于页面字段
- 创建：`backend/app/schemas/site_setting.py` - Pydantic 模型用于验证

**前端修改：**
- 修改：`frontend/src/views/blog/About.vue` - 从 API 获取配置数据
- 修改：`frontend/src/views/admin/settings/SiteSettings.vue` - 添加关于页面设置模块
- 修改：`frontend/src/api/setting.ts` - 添加类型定义和 API 方法

---

## 任务 1：后端数据模型扩展

**文件：**
- 修改：`backend/app/models/site_setting.py`
- 创建：`backend/app/schemas/site_setting.py`

- [ ] **步骤 1：创建 Pydantic Schema**

创建 `backend/app/schemas/site_setting.py`：

```python
"""
Site Setting Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class SiteSettingBase(BaseModel):
    """Base schema for site settings"""
    pass


class SiteSettingUpdate(BaseModel):
    """Schema for updating site settings"""
    # Basic Settings
    site_name: Optional[str] = Field(None, max_length=100)
    site_description: Optional[str] = None
    site_logo: Optional[str] = None
    site_url: Optional[str] = None
    site_keywords: Optional[str] = None
    og_image: Optional[str] = None
    
    # Social Links
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    weibo_url: Optional[str] = None
    email: Optional[str] = None
    
    # About Page Settings
    about_welcome_title: Optional[str] = Field(None, max_length=200)
    about_welcome_content: Optional[str] = None
    about_author_title: Optional[str] = Field(None, max_length=200)
    about_author_content: Optional[str] = None
    about_tech_stack_title: Optional[str] = Field(None, max_length=200)
    about_tech_stack_items: Optional[str] = None  # JSON string
    about_contact_title: Optional[str] = Field(None, max_length=200)
    about_contact_email: Optional[str] = None
    about_contact_github: Optional[str] = None
    about_contact_github_label: Optional[str] = None
    
    # Comment Settings
    comment_require_review: Optional[bool] = None
    comment_enabled: Optional[bool] = None


class SiteSettingResponse(BaseModel):
    """Schema for site settings response"""
    # Basic Settings
    site_name: str = ""
    site_description: str = ""
    site_logo: str = ""
    site_url: str = ""
    site_keywords: str = ""
    og_image: str = ""
    
    # Social Links
    github_url: str = ""
    twitter_url: str = ""
    weibo_url: str = ""
    email: str = ""
    
    # About Page Settings
    about_welcome_title: str = "欢迎来到我的博客"
    about_welcome_content: str = ""
    about_author_title: str = "关于博主"
    about_author_content: str = ""
    about_tech_stack_title: str = "技术栈"
    about_tech_stack_items: List[str] = []
    about_contact_title: str = "联系方式"
    about_contact_email: str = ""
    about_contact_github: str = ""
    about_contact_github_label: str = "GitHub"
    
    # Comment Settings
    comment_require_review: bool = True
    comment_enabled: bool = True
    
    class Config:
        from_attributes = True
```

- [ ] **步骤 2：修改 SiteSetting 模型添加辅助方法**

修改 `backend/app/models/site_setting.py`：

```python
"""
Site Setting Model
"""
from datetime import datetime
import json
from app.extensions import db


class SiteSetting(db.Model):
    """Site setting model"""
    
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_name = db.Column(db.String(100), unique=True, nullable=False)
    key_value = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'key_name': self.key_name,
            'key_value': self.key_value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def get_settings_dict(cls):
        """
        Get all settings as a dictionary with key_name as key
        Returns: {key_name: key_value, ...}
        """
        settings = cls.query.all()
        return {setting.key_name: setting.key_value for setting in settings}
    
    @classmethod
    def get_value(cls, key_name, default=None):
        """
        Get a single setting value by key_name
        """
        setting = cls.query.filter_by(key_name=key_name).first()
        return setting.key_value if setting else default
    
    @classmethod
    def set_value(cls, key_name, key_value, description=None):
        """
        Set or update a setting value
        """
        setting = cls.query.filter_by(key_name=key_name).first()
        
        if setting:
            setting.key_value = key_value
            if description:
                setting.description = description
        else:
            setting = cls(
                key_name=key_name,
                key_value=key_value,
                description=description
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<SiteSetting {self.key_name}>'
```

- [ ] **步骤 3：Commit**

```bash
cd backend
git add app/schemas/site_setting.py app/models/site_setting.py
git commit -m "feat: add site setting schemas and model helpers"
```

---

## 任务 2：后端 API 扩展

**文件：**
- 修改：`backend/app/api/v1/settings.py`

- [ ] **步骤 1：修改 settings.py 添加完整功能**

修改 `backend/app/api/v1/settings.py`：

```python
"""
Site Settings API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.site_setting import SiteSetting
from app.schemas.site_setting import SiteSettingUpdate, SiteSettingResponse
from datetime import datetime
import json

bp = Blueprint('settings', __name__)

# Default values for settings
DEFAULT_SETTINGS = {
    'site_name': '我的博客',
    'site_description': '技术分享平台',
    'site_logo': '',
    'site_url': '',
    'site_keywords': '',
    'og_image': '',
    'github_url': '',
    'twitter_url': '',
    'weibo_url': '',
    'email': '',
    'about_welcome_title': '欢迎来到我的博客',
    'about_welcome_content': '这是一个技术分享平台，主要记录我在学习和工作中的技术心得和经验总结。',
    'about_author_title': '关于博主',
    'about_author_content': '一名热爱技术的开发者，专注于 Web 开发领域。',
    'about_tech_stack_title': '技术栈',
    'about_tech_stack_items': json.dumps(['Vue.js', 'React', 'TypeScript', 'Node.js']),
    'about_contact_title': '联系方式',
    'about_contact_email': '',
    'about_contact_github': '',
    'about_contact_github_label': 'GitHub',
    'comment_require_review': 'true',
    'comment_enabled': 'true',
}


def initialize_default_settings():
    """Initialize default settings if not exist"""
    for key, value in DEFAULT_SETTINGS.items():
        if not SiteSetting.get_value(key):
            SiteSetting.set_value(key, value, f'Default {key}')


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_settings():
    """
    Get all site settings
    
    Returns:
        {
            "settings": {
                "site_name": "...",
                "site_description": "...",
                ...
            }
        }
    """
    # Initialize defaults if needed
    initialize_default_settings()
    
    settings_dict = SiteSetting.get_settings_dict()
    
    # Parse tech stack items
    tech_stack_raw = settings_dict.get('about_tech_stack_items', '[]')
    try:
        settings_dict['about_tech_stack_items'] = json.loads(tech_stack_raw)
    except (json.JSONDecodeError, TypeError):
        settings_dict['about_tech_stack_items'] = []
    
    # Convert string booleans to actual booleans
    for key in ['comment_require_review', 'comment_enabled']:
        if key in settings_dict:
            settings_dict[key] = settings_dict[key].lower() == 'true'
    
    return jsonify({
        'settings': settings_dict
    }), 200


@bp.route('', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per hour")
def update_settings():
    """
    Update site settings (requires authentication)
    
    Request JSON:
        {
            "site_name": "My Blog",
            "site_description": "...",
            "about_welcome_title": "...",
            ...
        }
    
    Returns:
        {
            "settings": {...updated settings...}
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # Validate input
    try:
        update_data = SiteSettingUpdate(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    
    # Update settings
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        # Convert special fields
        if key == 'about_tech_stack_items' and isinstance(value, list):
            value = json.dumps(value)
        elif key in ['comment_require_review', 'comment_enabled']:
            value = str(value).lower()
        
        SiteSetting.set_value(key, value)
    
    # Return updated settings
    return get_settings()


@bp.route('/reset', methods=['POST'])
@jwt_required()
@limiter.limit("3 per hour")
def reset_settings():
    """
    Reset all settings to defaults (requires authentication)
    
    Returns:
        {
            "settings": {...default settings...}
        }
    """
    # Clear all existing settings
    SiteSetting.query.delete()
    
    # Reinitialize with defaults
    initialize_default_settings()
    
    return get_settings()
```

- [ ] **步骤 2：Commit**

```bash
cd backend
git add app/api/v1/settings.py
git commit -m "feat: enhance settings API with about page support"
```

---

## 任务 3：前端 API 类型定义

**文件：**
- 修改：`frontend/src/api/setting.ts`

- [ ] **步骤 1：查看现有 setting.ts 文件**

先读取 `frontend/src/api/setting.ts` 了解现有结构

- [ ] **步骤 2：扩展类型定义和 API 方法**

修改 `frontend/src/api/setting.ts`：

```typescript
import request from '@/utils/request'

export interface SiteSettings {
  // Basic Settings
  site_name: string
  site_description: string
  site_logo: string
  site_url: string
  site_keywords: string
  og_image: string
  
  // Social Links
  github_url: string
  twitter_url: string
  weibo_url: string
  email: string
  
  // About Page Settings
  about_welcome_title: string
  about_welcome_content: string
  about_author_title: string
  about_author_content: string
  about_tech_stack_title: string
  about_tech_stack_items: string[]
  about_contact_title: string
  about_contact_email: string
  about_contact_github: string
  about_contact_github_label: string
  
  // Comment Settings
  comment_require_review: boolean
  comment_enabled: boolean
}

export interface SettingsResponse {
  settings: SiteSettings
}

export const settingApi = {
  /**
   * Get all site settings
   */
  get(): Promise<SettingsResponse> {
    return request({
      url: '/api/v1/settings',
      method: 'get',
    })
  },

  /**
   * Update site settings
   */
  update(data: Partial<SiteSettings>): Promise<SettingsResponse> {
    return request({
      url: '/api/v1/settings',
      method: 'put',
      data,
    })
  },

  /**
   * Reset settings to defaults
   */
  reset(): Promise<SettingsResponse> {
    return request({
      url: '/api/v1/settings/reset',
      method: 'post',
    })
  },
}
```

- [ ] **步骤 3：Commit**

```bash
cd frontend
git add src/api/setting.ts
git commit -m "feat: add about page settings types and API methods"
```

---

## 任务 4：前端 About 页面改造

**文件：**
- 修改：`frontend/src/views/blog/About.vue`

- [ ] **步骤 1：重写 About.vue 从 API 获取数据**

修改 `frontend/src/views/blog/About.vue`：

```vue
<template>
  <div class="about-page">
    <div class="page-header">
      <h1>关于</h1>
    </div>

    <n-card class="about-content" v-if="loading">
      <n-spin size="large" description="加载中..." />
    </n-card>

    <n-card class="about-content" v-else-if="settings">
      <!-- Welcome Section -->
      <div class="about-section" v-if="settings.about_welcome_title || settings.about_welcome_content">
        <h2>{{ settings.about_welcome_title }}</h2>
        <p>{{ settings.about_welcome_content }}</p>
      </div>

      <!-- About Author Section -->
      <div class="about-section" v-if="settings.about_author_title || settings.about_author_content">
        <h2>{{ settings.about_author_title }}</h2>
        <p>{{ settings.about_author_content }}</p>
      </div>

      <!-- Tech Stack Section -->
      <div class="about-section" v-if="settings.about_tech_stack_title && settings.about_tech_stack_items?.length">
        <h2>{{ settings.about_tech_stack_title }}</h2>
        <div class="tech-stack">
          <n-tag v-for="tech in settings.about_tech_stack_items" :key="tech" :bordered="false">
            {{ tech }}
          </n-tag>
        </div>
      </div>

      <!-- Contact Section -->
      <div class="about-section" v-if="settings.about_contact_title && (settings.about_contact_email || settings.about_contact_github)">
        <h2>{{ settings.about_contact_title }}</h2>
        <div class="contact-info">
          <p v-if="settings.about_contact_email">
            <n-icon :component="MailOutline" />
            邮箱：{{ settings.about_contact_email }}
          </p>
          <p v-if="settings.about_contact_github">
            <n-icon :component="LogoGithub" />
            {{ settings.about_contact_github_label || 'GitHub' }}:
            <a :href="settings.about_contact_github" target="_blank" rel="noopener noreferrer">
              {{ settings.about_contact_github.replace(/^https?:\/\//, '') }}
            </a>
          </p>
        </div>
      </div>
    </n-card>

    <n-card class="about-content" v-else>
      <div class="empty-state">
        <n-empty description="暂无内容" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MailOutline, LogoGithub } from '@vicons/ionicons5'
import { settingApi, type SiteSettings } from '@/api'

const loading = ref(true)
const settings = ref<SiteSettings | null>(null)

const loadSettings = async () => {
  try {
    loading.value = true
    const response = await settingApi.get()
    settings.value = response.settings
  } catch (error) {
    console.error('Failed to load about page settings:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 0;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
}

.about-content {
  border-radius: 12px;
}

.about-section {
  margin-bottom: 32px;
}

.about-section:last-child {
  margin-bottom: 0;
}

.about-section h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.about-section p {
  margin: 0;
  font-size: 15px;
  color: #666;
  line-height: 1.8;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.contact-info p:last-child {
  margin-bottom: 0;
}

.contact-info a {
  color: #18a058;
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
cd frontend
git add src/views/blog/About.vue
git commit -m "feat: make about page dynamic from API settings"
```

---

## 任务 5：管理后台添加关于页面设置

**文件：**
- 修改：`frontend/src/views/admin/settings/SiteSettings.vue`

- [ ] **步骤 1：扩展现有 SiteSettings.vue 添加关于页面模块**

在 `frontend/src/views/admin/settings/SiteSettings.vue` 中添加新模块：

在 Comment Settings 模块后添加：

```vue
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
```

- [ ] **步骤 2：更新 formData 响应式对象**

在 `frontend/src/views/admin/settings/SiteSettings.vue` 的 script 部分更新：

```typescript
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
```

- [ ] **步骤 3：更新 handleSave 函数**

```typescript
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
```

- [ ] **步骤 4：更新 loadSettings 函数**

```typescript
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
```

- [ ] **步骤 5：添加 tech-stack-editor 样式**

在 `frontend/src/views/admin/settings/SiteSettings.vue` 的 style 部分添加：

```css
.tech-stack-editor {
  width: 100%;
}

.tech-stack-editor .help-text {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #999;
}
```

- [ ] **步骤 6：Commit**

```bash
cd frontend
git add src/views/admin/settings/SiteSettings.vue
git commit -m "feat: add about page settings to admin panel"
```

---

## 任务 6：测试验证

**文件：**
- 测试：手动测试和 API 测试

- [ ] **步骤 1：启动后端服务**

```bash
cd backend
python -m flask run --port 5000
```

- [ ] **步骤 2：启动前端服务**

```bash
cd frontend
npm run dev
```

- [ ] **步骤 3：测试 API**

使用 curl 或 Postman 测试：

```bash
# 获取设置
curl http://localhost:5000/api/v1/settings

# 更新设置 (需要 JWT token)
curl -X PUT http://localhost:5000/api/v1/settings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "about_welcome_title": "欢迎来到我的博客",
    "about_welcome_content": "这是一个技术分享平台",
    "about_tech_stack_items": ["Vue.js", "React", "TypeScript"]
  }'
```

- [ ] **步骤 4：测试前端 About 页面**

访问 `http://localhost:5173/about` 查看效果

- [ ] **步骤 5：测试管理后台**

1. 登录管理后台
2. 进入 站点设置 页面
3. 修改关于页面设置
4. 保存后查看 About 页面是否更新

---

## 自检

**规格覆盖度检查：**
- ✅ 后端数据模型扩展（辅助方法）
- ✅ 后端 Schema 定义（Pydantic）
- ✅ 后端 API 扩展（GET/PUT/RESET）
- ✅ 前端 API 类型定义
- ✅ 前端 About 页面动态化
- ✅ 管理后台设置界面
- ✅ 测试验证

**占位符扫描：** 无占位符，所有步骤都有完整代码

**类型一致性检查：**
- ✅ SiteSetting 模型方法一致
- ✅ API 接口定义一致
- ✅ 前端类型定义与后端字段对应

---

**计划已完成并保存到 `docs/superpowers/plans/2026-05-12-about-page-settings.md`。两种执行方式：**

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
