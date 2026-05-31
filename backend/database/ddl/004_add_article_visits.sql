-- ========================================
-- DDL (Data Definition Language)
-- 数据库结构变更脚本
-- ========================================

-- 1. 创建文章访问记录表 (2026-05-23)
-- 用于记录每次文章访问的详细信息，支持数据分析和安全防护
CREATE TABLE article_visits (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    article_id BIGINT NOT NULL,
    article_slug VARCHAR(200) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    user_agent VARCHAR(500),
    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_article_id (article_id),
    INDEX idx_article_slug (article_slug),
    INDEX idx_ip_address (ip_address),
    INDEX idx_visited_at (visited_at),
    INDEX idx_article_ip_date (article_id, ip_address, visited_at),
    FOREIGN KEY (article_id) REFERENCES article_meta(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 回滚脚本 (Downgrade)
-- ========================================

-- 删除文章访问记录表
-- DROP TABLE IF EXISTS article_visits;
