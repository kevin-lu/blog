from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print('=' * 60)
    print('数据库连接信息')
    print('=' * 60)
    print(f'数据库 URI: {app.config.get("SQLALCHEMY_DATABASE_URI")}')
    print()
    
    # 检查各个表的数据
    tables_to_check = [
        ('site_settings', 'SiteSetting'),
        ('admins', 'Admin'),
        ('articles', 'Article'),
        ('categories', 'Category'),
        ('tags', 'Tag'),
        ('comments', 'Comment'),
    ]
    
    print('=' * 60)
    print('表数据检查')
    print('=' * 60)
    
    for table_name, model_name in tables_to_check:
        try:
            result = db.session.execute(db.text(f'SELECT COUNT(*) as count FROM {table_name}'))
            count = result.scalar()
            print(f'✓ {table_name}: {count} 条数据')
        except Exception as e:
            print(f'✗ {table_name}: 查询失败 - {str(e)[:50]}')
    
    print()
    print('=' * 60)
    print('SiteSetting 表详细内容')
    print('=' * 60)
    
    try:
        result = db.session.execute(db.text('SELECT key_name, key_value FROM site_settings LIMIT 10'))
        rows = result.fetchall()
        if rows:
            for row in rows:
                value = row[1][:50] if row[1] else 'NULL'
                print(f'  {row[0]}: {value}...')
        else:
            print('  (空表)')
    except Exception as e:
        print(f'  查询失败：{e}')
