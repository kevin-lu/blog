#!/usr/bin/env python3
"""
创建修复 PR
"""

import os
import sys
import argparse
from github import Github


def create_fix_pr(branch: str, original_pr_number: int):
    """创建修复 PR"""
    
    gh = Github(os.getenv("GITHUB_TOKEN"))
    repo = gh.get_repo(os.getenv("GITHUB_REPOSITORY"))
    original_pr = repo.get_pull(original_pr_number)
    
    # PR 标题和描述
    title = f"🤖 AI Fix: 自动修复 PR #{original_pr_number} 的 Critical 问题"
    body = f"""## AI 自动修复

此 PR 自动修复 PR #{original_pr_number} 中发现的 Critical 问题。

### 修复内容

- 自动识别的 Critical/High 优先级问题
- 由 AI SRE 系统生成并应用修复
- 已通过基础编译检查

### 原始 PR

- 原始 PR: #{original_pr_number}
- 触发原因：代码审查发现 Critical 问题
- 修复分支：{branch}

### 审核清单

- [ ] 修复正确，未引入新问题
- [ ] 代码逻辑符合预期
- [ ] 测试通过（如有）

---

*此 PR 由 AI SRE 自动生成 | 审核人：@{repo.owner.login}*
"""
    
    # 创建 PR
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch,
        base=original_pr.base.ref,
        draft=True  # 先创建为 Draft PR
    )
    
    # 添加标签
    pr.add_to_labels("ai-fix", "auto-generated")
    
    # 评论到原始 PR
    original_pr.create_issue_comment(f"""🤖 AI 已自动创建修复 PR: #{pr.number}

针对审查中发现的 Critical 问题，AI 已尝试自动修复。

请审核：{pr.html_url}""")
    
    print(f"已创建修复 PR: {pr.html_url}")


def main():
    parser = argparse.ArgumentParser(description="创建修复 PR")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--original-pr", type=int, required=True)
    
    args = parser.parse_args()
    
    create_fix_pr(args.branch, args.original_pr)


if __name__ == "__main__":
    main()
