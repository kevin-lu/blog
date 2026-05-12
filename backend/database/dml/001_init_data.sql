-- ========================================
-- DML (Data Manipulation Language)
-- 数据库数据变更脚本
-- ========================================

-- 1. 初始化浏览次数 (如果已有数据)
-- 将所有现有文章的浏览次数设置为 0
UPDATE article_meta 
SET view_count = COALESCE(view_count, 0) 
WHERE view_count IS NULL;

-- 2. 初始化评论数据（如果需要）
-- 示例：插入测试评论数据
-- INSERT INTO comments (article_slug, content, author_name, status) 
-- VALUES 
--     ('test-article', '这是一条测试评论', '测试用户', 'approved'),
--     ('test-article', '这是另一条评论', '另一位用户', 'approved');

-- 3. 数据清理脚本（可选）
-- 删除标记为 deleted 的评论
-- DELETE FROM comments WHERE status = 'deleted';

-- 4. 数据迁移脚本（如果需要从旧表迁移）
-- 示例：从旧评论表迁移数据
-- INSERT INTO comments (article_slug, content, author_name, created_at)
-- SELECT article_slug, content, author_name, created_at
-- FROM old_comments
-- WHERE NOT EXISTS (
--     SELECT 1 FROM comments c2 
--     WHERE c2.article_slug = old_comments.article_slug 
--     AND c2.content = old_comments.content
-- );

-- ========================================
-- 回滚脚本 (Downgrade)
-- ========================================

-- 重置浏览次数为 0
-- UPDATE article_meta SET view_count = 0;

-- 删除测试评论数据
-- DELETE FROM comments WHERE author_name = '测试用户';
