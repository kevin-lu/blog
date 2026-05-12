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
