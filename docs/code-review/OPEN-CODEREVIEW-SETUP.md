# OpenCodeReview 配置指南

## 概述

OpenCodeReview 是一个轻量级的代码规范检查工具，用于在 CI/CD 流程中进行快速代码质量检查。

## 配置说明

### 配置文件

位置：`.github/configs/open-code-review-config.json`

```json
{
  "rules": {
    "python": {
      "flake8": true,    // Python 语法和错误检查
      "black": true,     // Python 代码格式化
      "isort": true,     // Python 导入排序
      "mypy": true       // Python 类型检查
    },
    "javascript": {
      "eslint": true,    // JavaScript 语法检查
      "prettier": true   // JavaScript 格式化
    }
  },
  "threshold": {
    "blocker": 0,        // 阻塞性问题数量上限
    "critical": 0,       // 严重问题数量上限
    "major": 10          // 主要问题数量上限
  }
}
```

## 本地运行

### 安装依赖

```bash
# Python 检查工具
pip install flake8 black isort mypy

# JavaScript 检查工具（如需要）
npm install -g eslint prettier
```

### 运行检查

```bash
# 运行 OpenCodeReview
python .github/scripts/run_open_code_review.py
```

### 输出结果

检查结果保存为 `open-code-review-result.json`：

```json
{
  "status": "passed",
  "issues": [],
  "summary": "发现 0 个规范问题",
  "checks": {
    "flake8": "completed",
    "black": "completed",
    "isort": "completed"
  }
}
```

## 修复问题

### Flake8 问题

```bash
# 查看详细报告
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# 自动修复（部分问题）
autopep8 --in-place --aggressive <file.py>
```

### Black 格式问题

```bash
# 自动格式化
black .
```

### isort 导入问题

```bash
# 自动排序导入
isort .
```

## GitHub Actions 集成

在 workflow 中使用：

```yaml
- name: Run OpenCodeReview
  run: |
    pip install flake8 black isort
    python .github/scripts/run_open_code_review.py
```

## 阈值说明

| 级别 | 说明 | 默认值 |
|------|------|--------|
| blocker | 阻塞性问题，必须修复 | 0 |
| critical | 严重问题，必须修复 | 0 |
| major | 主要问题，可以有一定数量 | 10 |

## 常见问题

### Q: 如何忽略某些文件？

在 `.flake8` 配置文件中添加：

```ini
[flake8]
exclude = .git,__pycache__,venv,.venv,node_modules
```

### Q: 如何自定义规则？

修改 `.flake8` 配置文件：

```ini
[flake8]
max-line-length = 120
ignore = E501,W503
```

### Q: 检查失败怎么办？

1. 查看 `open-code-review-result.json` 了解详细问题
2. 根据问题类型运行对应的修复命令
3. 重新提交代码
