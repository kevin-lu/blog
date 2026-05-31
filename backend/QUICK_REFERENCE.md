# 云部署快速参考

## 一键部署命令

```bash
# 进入 backend 目录
cd /path/to/blog/backend

# 设置环境变量
export DB_HOST="114.55.165.189"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="Root@123456"
export DB_NAME="blog_db"

# 执行一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 验证命令

```bash
# 查看站点设置
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -e "SELECT key_name, key_value FROM site_settings ORDER BY key_name;"

# 查看头像设置
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -e "SELECT key_name, key_value FROM site_settings WHERE key_name = 'site_avatar';"
```

## 配置头像

### 方式 1：后台界面
```
访问：http://your-domain.com/admin
进入：站点设置 → 基本信息 → 站点头像
操作：上传头像 → 保存
```

### 方式 2：命令行
```bash
python scripts/init_site_settings.py \
  --update-avatar "https://example.com/avatar.png"
```

### 方式 3：SQL
```sql
UPDATE site_settings 
SET key_value = 'https://example.com/avatar.png', 
    updated_at = NOW() 
WHERE key_name = 'site_avatar';
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 权限不足 | 检查 DB_PASSWORD 是否正确 |
| 数据库不存在 | `CREATE DATABASE blog_db` |
| 找不到文件 | 确保在 backend 目录下执行 |
| Python 依赖缺失 | `pip install pymysql` |

## 回滚命令

```bash
# 删除头像设置
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  -e "DELETE FROM site_settings WHERE key_name = 'site_avatar';"
```

## 文件位置

```
backend/
├── database/dml/
│   ├── 002_site_settings.sql    # DML 脚本
│   └── README.md                 # DML 说明
├── scripts/
│   ├── deploy.sh                 # 一键部署脚本
│   ├── init_site_settings.py     # Python 初始化工具
│   └── DEPLOYMENT.md             # 详细部署文档
└── DEPLOYMENT_SUMMARY.md         # 总结文档（项目根目录）
```

## 新增字段

- `site_avatar` - 站点头像 URL（前端侧边栏显示）

## 相关文档

- 详细部署指南：`backend/scripts/DEPLOYMENT.md`
- DML 说明：`backend/database/dml/README.md`
- 总结文档：`DEPLOYMENT_SUMMARY.md`
