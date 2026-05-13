-- ========================================
-- DML (Data Manipulation Language)
-- 站点设置初始化脚本
-- 新增字段：site_avatar (站点头像)
-- ========================================

-- 1. 初始化站点设置默认值
-- 如果设置不存在则插入，如果存在则跳过

-- 站点头像 (新增字段)
INSERT INTO site_settings (key_name, key_value, description, created_at, updated_at)
VALUES (
    'site_avatar', 
    '', 
    '站点头像 URL，用于博客侧边栏显示',
    NOW(),
    NOW()
)
ON DUPLICATE KEY UPDATE key_name = key_name;

-- 确保其他基本设置存在
INSERT INTO site_settings (key_name, key_value, description, created_at, updated_at)
VALUES 
    ('site_name', '我的博客', '博客站点名称', NOW(), NOW()),
    ('site_description', '技术分享平台', '博客站点描述', NOW(), NOW()),
    ('site_logo', '', '博客站点 Logo URL', NOW(), NOW()),
    ('site_url', '', '博客站点 URL', NOW(), NOW()),
    ('site_keywords', '', '博客站点关键词，多个用逗号分隔', NOW(), NOW()),
    ('og_image', '', '默认 OG 图片 URL，用于社交媒体分享', NOW(), NOW()),
    ('github_url', '', 'GitHub 主页链接', NOW(), NOW()),
    ('twitter_url', '', 'Twitter 主页链接', NOW(), NOW()),
    ('weibo_url', '', '微博主页链接', NOW(), NOW()),
    ('email', '', '联系邮箱', NOW(), NOW())
ON DUPLICATE KEY UPDATE key_name = key_name;

-- 确保关于页面设置存在
INSERT INTO site_settings (key_name, key_value, description, created_at, updated_at)
VALUES 
    ('about_welcome_title', '欢迎来到我的博客', '关于页面欢迎标题', NOW(), NOW()),
    ('about_welcome_content', '这是一个技术分享平台，主要记录我在学习和工作中的技术心得和经验总结。', '关于页面欢迎内容', NOW(), NOW()),
    ('about_author_title', '关于博主', '关于页面作者标题', NOW(), NOW()),
    ('about_author_content', '一名热爱技术的开发者，专注于 Web 开发领域。', '关于页面作者内容', NOW(), NOW()),
    ('about_tech_stack_title', '技术栈', '关于页面技术栈标题', NOW(), NOW()),
    ('about_tech_stack_items', '["Vue.js", "React", "TypeScript", "Node.js"]', '关于页面技术栈列表（JSON 格式）', NOW(), NOW()),
    ('about_contact_title', '联系方式', '关于页面联系标题', NOW(), NOW()),
    ('about_contact_email', '', '关于页面联系邮箱', NOW(), NOW()),
    ('about_contact_github', '', '关于页面 GitHub 链接', NOW(), NOW()),
    ('about_contact_github_label', 'GitHub', '关于页面 GitHub 显示文本', NOW(), NOW())
ON DUPLICATE KEY UPDATE key_name = key_name;

-- 确保评论设置存在
INSERT INTO site_settings (key_name, key_value, description, created_at, updated_at)
VALUES 
    ('comment_require_review', 'true', '评论是否需要审核（true/false）', NOW(), NOW()),
    ('comment_enabled', 'true', '是否启用评论功能（true/false）', NOW(), NOW())
ON DUPLICATE KEY UPDATE key_name = key_name;

-- ========================================
-- 查询验证脚本
-- ========================================

-- 查看所有站点设置
-- SELECT key_name, key_value, description FROM site_settings ORDER BY key_name;

-- 查看新增的头像设置
-- SELECT key_name, key_value, description FROM site_settings WHERE key_name = 'site_avatar';

-- ========================================
-- 回滚脚本 (Downgrade)
-- ========================================

-- 删除新增的站点头像设置
-- DELETE FROM site_settings WHERE key_name = 'site_avatar';

-- 删除所有站点设置（谨慎使用）
-- DELETE FROM site_settings;

-- ========================================
-- 部署说明
-- ========================================
-- 1. 此脚本会在云部署时自动执行
-- 2. 使用 ON DUPLICATE KEY UPDATE 确保幂等性
-- 3. 已存在的设置不会被覆盖，只插入缺失的设置
-- 4. 所有时间字段使用 NOW() 自动设置
-- ========================================
