#!/usr/bin/env python3
"""
将 AI 审查结果发布为 PR 评论
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, List
from github import Github


class ReviewCommenter:
    """审查评论发布器"""
    
    def __init__(self, pr_number: int, review_file: str):
        self.pr_number = pr_number
        self.review_file = review_file
        self.gh = Github(os.getenv("GITHUB_TOKEN"))
        self.repo = self.gh.get_repo(os.getenv("GITHUB_REPOSITORY"))
        self.pr = self.repo.get_pull(pr_number)
    
    def load_review(self) -> Dict:
        """加载审查结果"""
        with open(self.review_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def post_comprehensive_comment(self, review: Dict):
        """发布综合审查评论"""
        
        # 构建评论格式
        comment = f"""## 🤖 AI 代码审查报告

**审查时间**: {review.get('metadata', {}).get('review_time', 'N/A')}
**审查文件数**: {review.get('metadata', {}).get('files_count', 0)}
**置信度**: {review.get('confidence_score', 0):.0%}

---

### 📊 总体评价

**结论**: {self._get_verdict_emoji(review.get('verdict', ''))} {review.get('verdict', 'N/A')}

**总结**: {review.get('summary', 'N/A')}

---

### 🚨 Critical 问题 ({len(review.get('critical_issues', []))} 个)

{self._format_issues(review.get('critical_issues', []))}

---

### ✅ 优点

{self._format_list(review.get('positive_points', ['审查中，未发现明显优点']))}

---

### 💡 改进建议

{self._format_list(review.get('recommendations', ['无特别建议']))}

---

### 📝 审查详情

| 文件 | 问题数 | 最严重问题 |
|------|--------|-----------|
{self._format_file_table(review.get('critical_issues', []))}

---

<details>
<summary>📋 查看详细 Diff 分析</summary>

AI 已审查 {review.get('metadata', {}).get('diff_size', 0)} 字符的代码变更

</details>

---

*此审查由 AI SRE 自动生成 | 审查重点：N+1 查询、竞态条件、信任边界、异常处理*
"""
        
        # 发布评论
        self.pr.create_issue_comment(comment)
        print(f"已发布综合审查评论到 PR #{self.pr_number}")
    
    def create_inline_comments(self, review: Dict):
        """创建行内评论（针对具体问题）"""
        
        issues = review.get('critical_issues', [])
        
        for issue in issues:
            file_path = issue.get('file', '')
            line = issue.get('line', 1)
            severity = issue.get('severity', 'medium')
            
            # 跳过没有文件信息的
            if not file_path:
                continue
            
            # 构建评论
            comment = f"""**{self._get_severity_emoji(severity)} {issue.get('type', '问题')}**

{issue.get('description', '')}

**建议**: {issue.get('suggestion', '')}
"""
            
            if issue.get('fixed_code'):
                comment += f"""
```python
{issue.get('fixed_code', '')}
```
"""
            
            # 尝试获取文件的 commit SHA
            try:
                commit = self.pr.head.sha
                
                # 创建行内评论
                self.pr.create_review_comment(
                    body=comment,
                    path=file_path,
                    position=line,
                    commit=commit
                )
                print(f"已创建行内评论：{file_path}:{line}")
            except Exception as e:
                print(f"创建行内评论失败：{e}")
    
    def _get_verdict_emoji(self, verdict: str) -> str:
        """获取结论表情"""
        emojis = {
            "LGTM": "✅",
            "Needs Work": "⚠️",
            "Has Critical Issues": "🚨"
        }
        return emojis.get(verdict, "📝")
    
    def _get_severity_emoji(self, severity: str) -> str:
        """获取严重程度表情"""
        emojis = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        return emojis.get(severity, "⚪")
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """格式化问题列表"""
        if not issues:
            return "暂无 Critical 问题"
        
        formatted = []
        for i, issue in enumerate(issues, 1):
            formatted.append(f"""
#### {i}. {issue.get('type', '问题')}
- **文件**: `{issue.get('file', 'N/A')}`:{issue.get('line', 'N/A')}
- **描述**: {issue.get('description', 'N/A')}
- **建议**: {issue.get('suggestion', 'N/A')}
""")
            if issue.get('fixed_code'):
                formatted.append(f"```python\n{issue.get('fixed_code')}\n```")
        
        return "\n".join(formatted)
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        return "\n".join([f"- {item}" for item in items])
    
    def _format_file_table(self, issues: List[Dict]) -> str:
        """格式化文件表格"""
        # 按文件分组
        file_issues = {}
        for issue in issues:
            file_path = issue.get('file', '未知文件')
            if file_path not in file_issues:
                file_issues[file_path] = 0
            file_issues[file_path] += 1
        
        # 生成表格行
        rows = []
        for file_path, count in sorted(file_issues.items(), key=lambda x: -x[1])[:10]:
            max_severity = max(
                [i for i in issues if i.get('file') == file_path],
                key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.get('severity', 'low'))
            ).get('severity', 'medium')
            
            rows.append(f"| {file_path} | {count} | {self._get_severity_emoji(max_severity)} |")
        
        return "\n".join(rows) if rows else "| 无 | 0 | - |"
    
    def run(self, create_inline: bool = True):
        """执行评论发布"""
        review = self.load_review()
        
        # 发布综合评论
        self.post_comprehensive_comment(review)
        
        # 发布行内评论
        if create_inline:
            self.create_inline_comments(review)


def main():
    parser = argparse.ArgumentParser(description="发布审查评论")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--review-file", required=True)
    parser.add_argument("--create-inline-comments", action="store_true")
    
    args = parser.parse_args()
    
    commenter = ReviewCommenter(
        pr_number=args.pr_number,
        review_file=args.review_file
    )
    
    commenter.run(create_inline=args.create_inline_comments)


if __name__ == "__main__":
    main()
