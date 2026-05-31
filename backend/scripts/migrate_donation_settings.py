#!/usr/bin/env python3
"""
Execute donation settings table migration
"""
import pymysql

# Database configuration
config = {
    'host': '114.55.165.189',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'blog_db',
    'charset': 'utf8mb4'
}

# SQL script - Create table
create_table_sql = """
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打赏配置表'
"""

# SQL script - Insert default data
insert_data_sql = """
INSERT INTO `donation_settings` (`title`, `description`, `enabled`) 
VALUES (
    '支持博主',
    '代码编织梦想，分享传递价值\\n每一分支持，都是前行的光',
    1
)
"""

try:
    # Connect to database
    connection = pymysql.connect(**config)
    cursor = connection.cursor()
    
    # Execute CREATE TABLE
    cursor.execute(create_table_sql)
    connection.commit()
    print("✅ Table created successfully!")
    
    # Execute INSERT
    cursor.execute(insert_data_sql)
    connection.commit()
    print("✅ Default data inserted successfully!")
    
    # Verify table structure
    print("\n📋 Table structure:")
    cursor.execute("DESC donation_settings")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # Verify data
    print("\n📊 Default data:")
    cursor.execute("SELECT id, title, enabled FROM donation_settings")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Title: {row[1]}, Enabled: {row[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
