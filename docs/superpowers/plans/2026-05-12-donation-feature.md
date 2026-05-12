# 打赏功能实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 在博客首页侧边栏添加打赏卡片，支持微信/支付宝收款码展示和后台管理

**架构：** 
- 后端：新增 DonationSetting 模型和 CRUD API
- 前端：创建 DonationCard 组件集成到 Sidebar，后台添加设置页面
- 数据库：MySQL 新增 donation_settings 表

**技术栈：** Flask + SQLAlchemy（后端），Vue 3 + TypeScript + Naive UI（前端），MySQL 8（数据库）

---

## 文件结构

**后端文件：**
- 创建：`backend/app/models/donation.py` - 打赏配置模型
- 创建：`backend/app/api/v1/donations.py` - 打赏配置 API
- 创建：`backend/database/ddl/002_add_donation_settings.sql` - 数据库迁移脚本
- 修改：`backend/app/api/v1/__init__.py` - 注册新路由

**前端文件：**
- 创建：`frontend/src/components/donation/DonationCard.vue` - 打赏展示卡片
- 创建：`frontend/src/components/donation/DonationModal.vue` - 二维码放大查看
- 创建：`frontend/src/views/admin/donation/DonationSettings.vue` - 后台设置页面
- 修改：`frontend/src/components/article/Sidebar.vue` - 集成打赏卡片
- 修改：`frontend/src/router/index.ts` - 添加后台路由
- 修改：`frontend/src/views/admin/Layout.vue` - 添加菜单项

---

## 任务分解

### 任务 1：数据库迁移

**文件：**
- 创建：`backend/database/ddl/002_add_donation_settings.sql`

- [ ] **步骤 1：创建数据库迁移脚本**

```sql
-- ========================================
-- 添加打赏配置表
-- ========================================

CREATE TABLE IF NOT EXISTS `donation_settings` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(100) DEFAULT '支持博主' COMMENT '标题',
    `description` TEXT COMMENT '描述文案',
    `wechat_qr` VARCHAR(500) COMMENT '微信收款码 URL',
    `alipay_qr` VARCHAR(500) COMMENT '支付宝收款码 URL',
    `enabled` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_enabled (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打赏配置表';

-- 插入默认数据
INSERT INTO `donation_settings` (`title`, `description`, `enabled`) 
VALUES (
    '支持博主',
    '代码编织梦想，分享传递价值\n每一分支持，都是前行的光',
    1
);
```

- [ ] **步骤 2：运行迁移脚本**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog/backend
mysql -h 114.55.165.189 -u root -p'Root@123456' blog_db < database/ddl/002_add_donation_settings.sql
```

预期：成功执行，创建 `donation_settings` 表并插入默认数据

- [ ] **步骤 3：验证表创建成功**

```bash
mysql -h 114.55.165.189 -u root -p'Root@123456' blog_db -e "DESC donation_settings; SELECT * FROM donation_settings;"
```

预期：显示表结构和默认数据

- [ ] **步骤 4：Commit**

```bash
git add database/ddl/002_add_donation_settings.sql
git commit -m "feat: add donation_settings table"
```

---

### 任务 2：后端模型

**文件：**
- 创建：`backend/app/models/donation.py`

- [ ] **步骤 1：创建 DonationSetting 模型**

```python
"""
Donation Setting Model
"""
from datetime import datetime
from app.extensions import db


class DonationSetting(db.Model):
    """Donation setting model"""
    
    __tablename__ = 'donation_settings'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), default='支持博主', nullable=False)
    description = db.Column(db.Text, comment='描述文案')
    wechat_qr = db.Column(db.String(500), comment='微信收款码 URL')
    alipay_qr = db.Column(db.String(500), comment='支付宝收款码 URL')
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'wechat_qr': self.wechat_qr,
            'alipay_qr': self.alipay_qr,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def get_current(cls):
        """Get current donation setting"""
        return cls.query.filter_by(enabled=True).first()
```

- [ ] **步骤 2：在 models/__init__.py 中导出**

```python
# 在文件末尾添加
from app.models.donation import DonationSetting
```

- [ ] **步骤 3：Commit**

```bash
git add app/models/donation.py app/models/__init__.py
git commit -m "feat: add DonationSetting model"
```

---

### 任务 3：后端 API

**文件：**
- 创建：`backend/app/api/v1/donations.py`
- 修改：`backend/app/api/v1/__init__.py`

- [ ] **步骤 1：创建 donations API 路由**

```python
"""
Donation Settings API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.donation import DonationSetting
from app.utils.upload import save_uploaded_file
import os

bp = Blueprint('donations', __name__, url_prefix='/api/v1/donations')


@bp.route('', methods=['GET'])
def get_donation_settings():
    """
    Get donation settings (public)
    
    Returns:
        {
            "settings": { ...donation settings... }
        }
    """
    settings = DonationSetting.get_current()
    
    if not settings:
        return jsonify({'settings': None}), 404
    
    return jsonify({
        'settings': settings.to_dict()
    }), 200


@bp.route('', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per hour")
def update_donation_settings():
    """
    Update donation settings (requires authentication)
    
    Request JSON:
        {
            "title": "支持博主",
            "description": "文案...",
            "enabled": true
        }
    
    Returns:
        {
            "settings": { ...updated settings... }
        }
    """
    settings = DonationSetting.get_current()
    
    if not settings:
        # Create new if not exists
        settings = DonationSetting()
        db.session.add(settings)
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'title' in data:
        settings.title = data['title']
    if 'description' in data:
        settings.description = data['description']
    if 'enabled' in data:
        settings.enabled = data['enabled']
    
    db.session.commit()
    
    return jsonify({
        'settings': settings.to_dict()
    }), 200


@bp.route('/upload-qr', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_qr_code():
    """
    Upload QR code image
    
    Form Data:
        type: 'wechat' or 'alipay'
        file: image file
    
    Returns:
        {
            "url": "file url"
        }
    """
    data = request.form
    
    qr_type = data.get('type')
    if not qr_type or qr_type not in ['wechat', 'alipay']:
        return jsonify({'error': 'Invalid QR code type'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = save_uploaded_file(file, 'donation/qrcodes')
    file_url = f'/uploads/{filename}'
    
    # Update donation settings
    settings = DonationSetting.get_current()
    if not settings:
        settings = DonationSetting()
        db.session.add(settings)
        db.session.commit()
    
    if qr_type == 'wechat':
        settings.wechat_qr = file_url
    else:
        settings.alipay_qr = file_url
    
    db.session.commit()
    
    return jsonify({
        'url': file_url,
        'type': qr_type
    }), 200
```

- [ ] **步骤 2：注册路由**

```python
# 在 backend/app/api/v1/__init__.py 中添加
from app.api.v1.donations import bp as donations_bp

def register_blueprints(app):
    app.register_blueprint(bp, url_prefix='/api/v1')
    app.register_blueprint(donations_bp)  # 添加此行
```

- [ ] **步骤 3：测试 API**

```bash
# 测试获取配置（公开接口）
curl http://127.0.0.1:5001/api/v1/donations

# 测试更新配置（需要登录）
curl -X PUT http://127.0.0.1:5001/api/v1/donations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试标题"}'
```

预期：返回更新后的配置

- [ ] **步骤 4：Commit**

```bash
git add app/api/v1/donations.py app/api/v1/__init__.py
git commit -m "feat: add donation settings API"
```

---

### 任务 4：前端类型定义

**文件：**
- 创建：`frontend/src/types/donation.ts`

- [ ] **步骤 1：创建 TypeScript 类型定义**

```typescript
export interface DonationSetting {
  id: number
  title: string
  description: string | null
  wechat_qr: string | null
  alipay_qr: string | null
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface DonationSettingUpdate {
  title?: string
  description?: string
  enabled?: boolean
  wechat_qr?: string
  alipay_qr?: string
}
```

- [ ] **步骤 2：在 types/index.ts 中导出**

```typescript
// 在文件末尾添加
export type { DonationSetting, DonationSettingUpdate } from './donation'
```

- [ ] **步骤 3：Commit**

```bash
git add src/types/donation.ts src/types/index.ts
git commit -m "feat: add donation types"
```

---

### 任务 5：前端 API 客户端

**文件：**
- 创建：`frontend/src/api/donation.ts`

- [ ] **步骤 1：创建 API 客户端**

```typescript
import request from '@/utils/request'
import type { DonationSetting, DonationSettingUpdate } from '@/types'

export const donationApi = {
  /**
   * Get donation settings (public)
   */
  getSettings(): Promise<DonationSetting | null> {
    return request.get('/donations').then(res => res.data.settings)
  },

  /**
   * Update donation settings
   */
  updateSettings(data: DonationSettingUpdate): Promise<DonationSetting> {
    return request.put('/donations', data).then(res => res.data.settings)
  },

  /**
   * Upload QR code image
   */
  uploadQRCode(type: 'wechat' | 'alipay', file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('type', type)
    formData.append('file', file)
    
    return request.post('/donations/upload-qr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}
```

- [ ] **步骤 2：在 api/index.ts 中导出**

```typescript
// 在文件末尾添加
export { donationApi } from './donation'
```

- [ ] **步骤 3：Commit**

```bash
git add src/api/donation.ts src/api/index.ts
git commit -m "feat: add donation API client"
```

---

### 任务 6：DonationCard 组件

**文件：**
- 创建：`frontend/src/components/donation/DonationCard.vue`
- 创建：`frontend/src/components/donation/DonationModal.vue`

- [ ] **步骤 1：创建 DonationModal 组件（二维码放大查看）**

```vue
<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="扫码支持"
    :style="{ width: '400px' }"
  >
    <div class="donation-modal">
      <div class="qr-container">
        <img :src="currentQr" alt="收款码" class="qr-image" />
      </div>
      <n-space justify="center" style="margin-top: 16px">
        <n-tag
          :type="qrType === 'wechat' ? 'success' : 'warning'"
          size="large"
        >
          {{ qrType === 'wechat' ? '微信' : '支付宝' }}
        </n-tag>
      </n-space>
      <n-text depth="3" style="margin-top: 12px; display: block; text-align: center">
        扫码后完成支付
      </n-text>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const showModal = ref(false)
const currentQr = ref('')
const qrType = ref<'wechat' | 'alipay'>('wechat')

const open = (qr: string, type: 'wechat' | 'alipay') => {
  currentQr.value = qr
  qrType.value = type
  showModal.value = true
}

const close = () => {
  showModal.value = false
}

defineExpose({ open, close })
</script>

<style scoped>
.donation-modal {
  padding: 20px;
}

.qr-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.qr-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}
</style>
```

- [ ] **步骤 2：创建 DonationCard 组件**

```vue
<template>
  <n-card
    v-if="settings && settings.enabled"
    class="donation-card"
    title="❤️ 支持博主"
    content-style="padding: 16px;"
  >
    <div class="donation-content">
      <!-- 诗意文案 -->
      <div class="donation-text">
        <p v-if="settings.description">
          {{ settings.description }}
        </p>
        <p v-else>
          代码编织梦想，分享传递价值<br />
          每一分支持，都是前行的光
        </p>
      </div>

      <!-- 收款码展示 -->
      <div class="qr-codes">
        <div
          v-if="settings.wechat_qr"
          class="qr-item"
          @click="showQr(settings.wechat_qr, 'wechat')"
        >
          <img :src="settings.wechat_qr" alt="微信收款码" class="qr-image" />
          <n-tag type="success" size="small" style="margin-top: 8px">
            微信
          </n-tag>
        </div>
        <div
          v-if="settings.alipay_qr"
          class="qr-item"
          @click="showQr(settings.alipay_qr, 'alipay')"
        >
          <img :src="settings.alipay_qr" alt="支付宝收款码" class="qr-image" />
          <n-tag type="warning" size="small" style="margin-top: 8px">
            支付宝
          </n-tag>
        </div>
      </div>

      <!-- 感谢语 -->
      <div class="donation-footer">
        <n-text depth="3" style="font-size: 12px">
          💝 感谢您的支持
        </n-text>
      </div>
    </div>

    <!-- 二维码查看模态框 -->
    <DonationModal ref="modalRef" />
  </n-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { donationApi } from '@/api'
import type { DonationSetting } from '@/types'
import DonationModal from './DonationModal.vue'

const settings = ref<DonationSetting | null>(null)
const modalRef = ref<InstanceType<typeof DonationModal>>()

const showQr = (qr: string, type: 'wechat' | 'alipay') => {
  modalRef.value?.open(qr, type)
}

onMounted(async () => {
  try {
    const data = await donationApi.getSettings()
    settings.value = data
  } catch (error) {
    console.error('Failed to load donation settings:', error)
  }
})
</script>

<style scoped>
.donation-card {
  margin-top: 16px;
  border: 1px solid #ffd1dc;
}

.donation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.donation-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  white-space: pre-line;
}

.qr-codes {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.qr-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.qr-item:hover {
  transform: scale(1.05);
}

.qr-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #f0f0f0;
}

.donation-footer {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
</style>
```

- [ ] **步骤 3：Commit**

```bash
git add src/components/donation/DonationCard.vue src/components/donation/DonationModal.vue
git commit -m "feat: add donation card components"
```

---

### 任务 7：集成到 Sidebar

**文件：**
- 修改：`frontend/src/components/article/Sidebar.vue`

- [ ] **步骤 1：引入 DonationCard 组件**

```vue
<!-- 在 template 中添加到 sidebar 底部 -->
<template>
  <div class="sidebar">
    <!-- Profile Card -->
    <n-card class="profile-card" content-style="padding: 24px;">
      <!-- ...现有代码... -->
    </n-card>

    <!-- Categories -->
    <n-card class="categories-card" title="分类" content-style="padding: 16px;">
      <!-- ...现有代码... -->
    </n-card>

    <!-- Tags -->
    <n-card class="tags-card" title="标签" content-style="padding: 16px;">
      <!-- ...现有代码... -->
    </n-card>

    <!-- Donation Card (新增) -->
    <DonationCard />
  </div>
</template>
```

- [ ] **步骤 2：导入组件**

```typescript
// 在 script 部分添加
import DonationCard from '@/components/donation/DonationCard.vue'
```

- [ ] **步骤 3：Commit**

```bash
git add src/components/article/Sidebar.vue
git commit -m "feat: integrate donation card into sidebar"
```

---

### 任务 8：后台设置页面

**文件：**
- 创建：`frontend/src/views/admin/donation/DonationSettings.vue`

- [ ] **步骤 1：创建设置页面**

```vue
<template>
  <div class="donation-settings-page">
    <div class="page-header">
      <h1>打赏设置</h1>
      <n-button type="primary" @click="handleSave">保存设置</n-button>
    </div>

    <n-card title="基本设置" style="margin-top: 16px">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="标题" path="title">
          <n-input
            v-model:value="formData.title"
            placeholder="支持博主"
            maxlength="50"
            show-count
          />
        </n-form-item>

        <n-form-item label="描述文案" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="代码编织梦想，分享传递价值..."
            :rows="4"
            show-count
            maxlength="200"
          />
        </n-form-item>

        <n-form-item label="启用状态" path="enabled">
          <n-switch v-model:value="formData.enabled" />
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="收款码设置" style="margin-top: 16px">
      <n-grid :cols="2" :x-gap="16">
        <!-- 微信收款码 -->
        <n-grid-item>
          <div class="qr-upload-section">
            <h3>微信收款码</h3>
            <div class="qr-preview">
              <img
                v-if="formData.wechat_qr"
                :src="formData.wechat_qr"
                alt="微信收款码"
                class="qr-preview-image"
              />
              <div v-else class="qr-placeholder">
                <n-icon :component="ImageOutline" size="48" />
                <n-text depth="3">未上传</n-text>
              </div>
            </div>
            <n-upload
              :custom-request="handleWechatUpload"
              :show-file-list="false"
              accept="image/*"
            >
              <n-button style="width: 100%; margin-top: 12px">
                上传微信收款码
              </n-button>
            </n-upload>
          </div>
        </n-grid-item>

        <!-- 支付宝收款码 -->
        <n-grid-item>
          <div class="qr-upload-section">
            <h3>支付宝收款码</h3>
            <div class="qr-preview">
              <img
                v-if="formData.alipay_qr"
                :src="formData.alipay_qr"
                alt="支付宝收款码"
                class="qr-preview-image"
              />
              <div v-else class="qr-placeholder">
                <n-icon :component="ImageOutline" size="48" />
                <n-text depth="3">未上传</n-text>
              </div>
            </div>
            <n-upload
              :custom-request="handleAlipayUpload"
              :show-file-list="false"
              accept="image/*"
            >
              <n-button style="width: 100%; margin-top: 12px">
                上传支付宝收款码
              </n-button>
            </n-upload>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card title="预览" style="margin-top: 16px">
      <div class="preview-section">
        <DonationCard />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { ImageOutline } from '@vicons/ionicons5'
import { donationApi } from '@/api'
import type { DonationSetting, DonationSettingUpdate } from '@/types'
import DonationCard from '@/components/donation/DonationCard.vue'

const message = useMessage()

const formData = reactive<DonationSettingUpdate>({
  title: '支持博主',
  description: '代码编织梦想，分享传递价值\n每一分支持，都是前行的光',
  enabled: true,
  wechat_qr: undefined,
  alipay_qr: undefined,
})

const formRules = {
  title: {
    required: true,
    message: '请输入标题',
    trigger: 'blur',
  },
}

const handleSave = async () => {
  try {
    await donationApi.updateSettings({
      title: formData.title,
      description: formData.description,
      enabled: formData.enabled,
    })
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  }
}

const handleWechatUpload = async ({ file }: { file: File }) => {
  try {
    const result = await donationApi.uploadQRCode('wechat', file)
    formData.wechat_qr = result.url
    message.success('上传成功')
  } catch (error) {
    message.error('上传失败')
  }
}

const handleAlipayUpload = async ({ file }: { file: File }) => {
  try {
    const result = await donationApi.uploadQRCode('alipay', file)
    formData.alipay_qr = result.url
    message.success('上传成功')
  } catch (error) {
    message.error('上传失败')
  }
}

onMounted(async () => {
  try {
    const settings = await donationApi.getSettings()
    if (settings) {
      formData.title = settings.title
      formData.description = settings.description || ''
      formData.enabled = settings.enabled
      formData.wechat_qr = settings.wechat_qr || undefined
      formData.alipay_qr = settings.alipay_qr || undefined
    }
  } catch (error) {
    console.error('Failed to load donation settings:', error)
  }
})
</script>

<style scoped>
.donation-settings-page {
  padding: 24px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

.qr-upload-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.qr-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
}

.qr-preview-image {
  max-width: 100%;
  max-height: 180px;
  border-radius: 8px;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}

.preview-section {
  display: flex;
  justify-content: center;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add src/views/admin/donation/DonationSettings.vue
git commit -m "feat: add donation settings admin page"
```

---

### 任务 9：路由和菜单配置

**文件：**
- 修改：`frontend/src/router/index.ts`
- 修改：`frontend/src/views/admin/Layout.vue`（或相应菜单组件）

- [ ] **步骤 1：添加路由**

```typescript
// 在 admin 路由部分添加
{
  path: '/admin/donation',
  name: 'AdminDonation',
  component: () => import('@/views/admin/donation/DonationSettings.vue'),
  meta: {
    title: '打赏设置',
    requiresAuth: true,
  },
},
```

- [ ] **步骤 2：添加菜单项**

```vue
<!-- 在后台 Layout 的菜单中添加 -->
<n-menu-item key="donation">
  <template #icon>
    <n-icon :component="HeartOutline" />
  </template>
  打赏设置
</n-menu-item>
```

```typescript
// 导入图标
import { HeartOutline } from '@vicons/ionicons5'
```

- [ ] **步骤 3：Commit**

```bash
git add src/router/index.ts src/views/admin/Layout.vue
git commit -m "feat: add donation settings route and menu"
```

---

### 任务 10：测试和验证

**文件：**
- 无（测试任务）

- [ ] **步骤 1：启动后端服务**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog/backend
./venv/bin/python run.py
```

- [ ] **步骤 2：启动前端服务**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog/frontend
npm run dev
```

- [ ] **步骤 3：测试前端展示**

1. 访问 http://localhost:5173
2. 检查首页右侧边栏是否显示打赏卡片
3. 点击二维码是否能放大查看
4. 检查文案是否正确显示

- [ ] **步骤 4：测试后台设置**

1. 登录后台 http://localhost:5173/admin/login
2. 访问打赏设置页面
3. 测试上传微信/支付宝收款码
4. 测试修改标题和文案
5. 测试保存功能
6. 验证前端是否实时更新

- [ ] **步骤 5：测试 API**

```bash
# 测试公开接口
curl http://127.0.0.1:5001/api/v1/donations

# 测试上传接口（需要登录获取 token）
curl -X POST http://127.0.0.1:5001/api/v1/donations/upload-qr \
  -H "Authorization: Bearer <token>" \
  -F "type=wechat" \
  -F "file=@/path/to/qr.png"
```

- [ ] **步骤 6：验证完成**

所有功能测试通过后，执行：

```bash
git commit -m "chore: complete donation feature implementation"
```

---

## 自检清单

- [ ] 数据库表创建成功吗？
- [ ] 后端 API 能正常读写吗？
- [ ] 前端卡片能正常显示吗？
- [ ] 二维码上传功能正常吗？
- [ ] 后台设置能保存吗？
- [ ] 响应式设计在移动端正常吗？
- [ ] 所有文件都已 commit 吗？

---

计划已完成并保存到 `docs/superpowers/plans/2026-05-12-donation-feature.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
