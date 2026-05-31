#!/usr/bin/env python3
"""
agents.md 自动检测功能 - 测试脚本

用于测试检测逻辑是否正确工作。
"""

import os
import json
from pathlib import Path

# 测试数据
TEST_DATA = {
    "used_commands": [
        "cd backend && python -m py_compile app/",  # 已有
        "cd backend && pytest tests/",  # 已有
        "cd backend && python scripts/test_search.py",  # 新增
        "cd backend && pytest tests/search/",  # 新增
        "cd frontend && npm run lint",  # 已有
        "ls -la",  # 临时命令，应忽略
        "cat config.py",  # 临时命令，应忽略
    ],
    "existing_commands": [
        "cd backend && python -m py_compile app/",
        "cd backend && pytest tests/",
        "cd backend && python scripts/test_*.py",
        "cd frontend && npm run build",
        "cd frontend && npm run test",
        "cd frontend && npm run lint",
    ],
    "current_directories": [
        "backend/app/",
        "backend/app/api/",
        "backend/app/models/",
        "backend/app/search/",  # 新增
        "backend/app/search/services/",  # 新增
        "backend/tests/",
        "backend/tests/search/",  # 新增
        "frontend/src/",
        "frontend/src/components/",
        "node_modules/",  # 应忽略
        ".git/",  # 应忽略
        ".cache/",  # 应忽略
    ],
    "existing_directories": [
        "backend/app/",
        "backend/app/api/",
        "backend/app/models/",
        "backend/tests/",
        "frontend/src/",
        "frontend/src/components/",
    ],
    "naming_patterns": [
        ("api_response", {"search_results": [], "total_count": 0}),  # snake_case, 新增
        ("model_class", "SearchService"),  # PascalCase, 已有模式
        ("table_name", "article_searches"),  # 复数，已有模式
    ],
    "existing_conventions": [
        "数据库表名：复数形式，蛇形命名（如 article_likes）",
        "模型类名：单数形式，大驼峰命名（如 ArticleLike）",
        "API 路由：复数形式，短横线命名（如 /articles/<id>/like）",
        "前端组件：PascalCase（如 PostDetail.vue）",
        "前端文件：组件名保持一致（如 PostDetail.vue）",
    ],
}


def is_important_command(cmd):
    """判断命令是否重要（值得添加到 agents.md）"""
    # 临时命令（忽略）- 只检查纯命令，不检查带参数的
    temporary_cmds = ['ls', 'cat', 'echo', 'pwd', 'mkdir', 'rm', 'cp', 'mv']
    
    # 重要命令关键词
    important_keywords = [
        'compile', 'build', 'test', 'lint', 'check',
        'run', 'start', 'dev', 'serve',
        'install', 'deploy', 'release', 'pytest', 'python', 'npm'
    ]
    
    # 检查是否是纯临时命令（不带参数）
    if cmd in temporary_cmds:
        return False
    
    # 检查是否包含重要关键词
    for keyword in important_keywords:
        if keyword in cmd.lower():
            return True
    
    return False


def detect_new_commands(used_commands, existing_commands):
    """检测新增构建命令"""
    new_commands = []
    
    for cmd in used_commands:
        # 检查是否是重要命令
        if not is_important_command(cmd):
            print(f"  ⚪ 忽略临时命令：{cmd}")
            continue
        
        # 检查是否已存在（支持通配符匹配）
        is_new = True
        for existing in existing_commands:
            if existing == cmd or (existing.endswith('*') and cmd.startswith(existing[:-1])):
                is_new = False
                print(f"  ⚪ 命令已存在：{cmd}")
                break
        
        if is_new:
            new_commands.append(cmd)
            print(f"  ✅ 检测到新命令：{cmd}")
    
    return new_commands


def is_important_directory(dir_path):
    """判断目录是否重要（值得添加到 agents.md）"""
    # 常见忽略目录
    ignored_dirs = [
        'node_modules', '.git', '.cache', 'dist', 'build',
        '__pycache__', '.pytest_cache', '.venv', 'venv', '.DS_Store'
    ]
    
    # 重要目录关键词
    important_keywords = [
        'test', 'spec', 'integration', 'e2e',
        'script', 'tool', 'util',
        'config', 'setting',
        'module', 'component', 'feature',
        'api', 'service', 'controller', 'model',
        'search', 'index', 'query'
    ]
    
    # 检查是否在忽略列表中
    for ignored in ignored_dirs:
        if ignored in dir_path:
            return False
    
    # 检查是否包含重要关键词
    for keyword in important_keywords:
        if keyword in dir_path.lower():
            return True
    
    # 检查是否是新模块目录（包含 __init__.py）
    init_file = Path(dir_path) / "__init__.py"
    if init_file.exists():
        return True
    
    return False


def detect_new_directories(current_dirs, existing_dirs):
    """检测新增目录结构"""
    new_directories = []
    
    for dir_path in current_dirs:
        # 检查是否是重要目录
        if not is_important_directory(dir_path):
            print(f"  ⚪ 忽略普通目录：{dir_path}")
            continue
        
        # 检查是否已存在
        if dir_path not in existing_dirs:
            new_directories.append(dir_path)
            print(f"  ✅ 检测到新目录：{dir_path}")
        else:
            print(f"  ⚪ 目录已存在：{dir_path}")
    
    return new_directories


def detect_new_conventions(naming_patterns, existing_conventions):
    """检测新增命名约定"""
    new_conventions = []
    
    for pattern_type, pattern_value in naming_patterns:
        if pattern_type == "api_response":
            # 检查 API 响应字段命名
            if isinstance(pattern_value, dict):
                keys = list(pattern_value.keys())
                if all('_' in k for k in keys):  # snake_case
                    conv = "API 响应使用 snake_case（如 search_results, total_count）"
                    if conv not in existing_conventions:
                        new_conventions.append(conv)
                        print(f"  ✅ 检测到新命名约定：{conv}")
                    else:
                        print(f"  ⚪ 命名约定已存在：{conv}")
                elif all(k[0].isupper() or '_' not in k for k in keys):  # camelCase
                    conv = "API 响应使用 camelCase（如 searchResults, totalCount）"
                    if conv not in existing_conventions:
                        new_conventions.append(conv)
                        print(f"  ✅ 检测到新命名约定：{conv}")
                    else:
                        print(f"  ⚪ 命名约定已存在：{conv}")
        
        elif pattern_type == "model_class":
            # 检查模型类命名（已有模式，不检测）
            pass
        
        elif pattern_type == "table_name":
            # 检查表命名（已有模式，不检测）
            pass
    
    return new_conventions


def generate_diff_preview(new_commands, new_directories, new_conventions):
    """生成 diff 预览"""
    preview = []
    
    if new_commands:
        preview.append("\n# 构建和测试命令")
        for cmd in new_commands:
            preview.append(f"+ {cmd}")
    
    if new_directories:
        preview.append("\n# 项目结构")
        for dir_path in new_directories:
            preview.append(f"+ - {dir_path}")
    
    if new_conventions:
        preview.append("\n# 命名约定")
        for conv in new_conventions:
            preview.append(f"+ - {conv}")
    
    return "\n".join(preview)


def main():
    """主函数"""
    print("=" * 80)
    print("agents.md 自动检测功能 - 测试脚本")
    print("=" * 80)
    print()
    
    # 测试 1: 检测新命令
    print("🔍 测试 1: 检测新增构建命令")
    print("-" * 80)
    new_commands = detect_new_commands(
        TEST_DATA["used_commands"],
        TEST_DATA["existing_commands"]
    )
    print(f"\n结果：检测到 {len(new_commands)} 个新命令")
    print()
    
    # 测试 2: 检测新目录
    print("🔍 测试 2: 检测新增目录结构")
    print("-" * 80)
    new_directories = detect_new_directories(
        TEST_DATA["current_directories"],
        TEST_DATA["existing_directories"]
    )
    print(f"\n结果：检测到 {len(new_directories)} 个新目录")
    print()
    
    # 测试 3: 检测新命名约定
    print("🔍 测试 3: 检测新增命名约定")
    print("-" * 80)
    new_conventions = detect_new_conventions(
        TEST_DATA["naming_patterns"],
        TEST_DATA["existing_conventions"]
    )
    print(f"\n结果：检测到 {len(new_conventions)} 个新命名约定")
    print()
    
    # 生成 diff 预览
    print("=" * 80)
    print("📝 生成 diff 预览")
    print("=" * 80)
    diff_preview = generate_diff_preview(new_commands, new_directories, new_conventions)
    print(diff_preview)
    print()
    
    # 测试总结
    print("=" * 80)
    print("✅ 测试总结")
    print("=" * 80)
    print(f"新命令：{len(new_commands)} 个")
    for cmd in new_commands:
        print(f"  - {cmd}")
    print(f"\n新目录：{len(new_directories)} 个")
    for dir_path in new_directories:
        print(f"  - {dir_path}")
    print(f"\n新命名约定：{len(new_conventions)} 个")
    for conv in new_conventions:
        print(f"  - {conv}")
    print()
    
    # 验证结果
    expected_commands = 2  # test_search.py 和 pytest tests/search/
    expected_directories = 3  # search/, search/services/, tests/search/
    expected_conventions = 1  # snake_case
    
    if (len(new_commands) == expected_commands and
        len(new_directories) == expected_directories and
        len(new_conventions) == expected_conventions):
        print("🎉 测试通过！所有预期结果都正确。")
    else:
        print("⚠️  测试结果与预期不符：")
        print(f"   预期：{expected_commands} 命令，{expected_directories} 目录，{expected_conventions} 约定")
        print(f"   实际：{len(new_commands)} 命令，{len(new_directories)} 目录，{len(new_conventions)} 约定")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
