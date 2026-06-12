-- ========================================
-- DDL (Data Definition Language)
-- 数据库结构变更脚本
-- ========================================

-- 1. 添加浏览次数统计字段 (2026-05-12)
-- 为文章元数据表添加 view_count 字段
ALTER TABLE article_meta 
ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL;

-- 添加浏览次数索引
CREATE INDEX idx_article_view_count ON article_meta(view_count);

-- 2. 创建评论系统表 (2026-05-12)
-- 如果评论表不存在则创建
CREATE TABLE IF NOT EXISTS comments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    article_slug VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    author_email VARCHAR(255),
    parent_id BIGINT,
    reply_to VARCHAR(100),
    status ENUM('pending', 'approved', 'spam', 'deleted') DEFAULT 'approved',
    is_pinned BOOLEAN DEFAULT FALSE,
    github_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_article_slug (article_slug),
    INDEX idx_parent_id (parent_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 添加评论相关索引
CREATE INDEX idx_comments_article ON comments(article_slug, status);
CREATE INDEX idx_comments_parent ON comments(parent_id) WHERE parent_id IS NOT NULL;

-- ========================================
-- 回滚脚本 (Downgrade)
-- ========================================

-- 移除评论表索引
-- DROP INDEX idx_comments_article ON comments;
-- DROP INDEX idx_comments_parent ON comments;

-- 删除评论表
-- DROP TABLE IF EXISTS comments;

-- 移除浏览次数索引
-- DROP INDEX idx_article_view_count ON article_meta;

-- 移除浏览次数字段
-- ALTER TABLE article_meta DROP COLUMN view_count;
