#!/usr/bin/env python3
"""
AI 自动修复 Critical 问题
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List
from github import Github


class AIAutoFixer:
    """AI 自动修复器"""
    
    def __init__(self, pr_number: int, review_file: str):
        self.pr_number = pr_number
        self.review_file = review_file
        self.gh = Github(os.getenv("GITHUB_TOKEN"))
        self.repo = self.gh.get_repo(os.getenv("GITHUB_REPOSITORY"))
        self.llm_api_key = os.getenv("LLM_API_KEY")
    
    def load_review(self) -> Dict:
        """加载审查结果"""
        with open(self.review_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_critical_issues(self, review: Dict) -> List[Dict]:
        """获取 Critical 问题"""
        issues = review.get('critical_issues', [])
        return [i for i in issues if i.get('severity') in ['critical', 'high']]
    
    def apply_fix(self, issue: Dict) -> bool:
        """应用修复"""
        
        file_path = issue.get('file', '')
        fixed_code = issue.get('fixed_code', '')
        
        if not file_path or not fixed_code:
            print(f"跳过：缺少文件路径或修复代码")
            return False
        
        # 检查文件是否存在
        full_path = Path(file_path)
        if not full_path.exists():
            print(f"文件不存在：{file_path}")
            return False
        
        # 读取原文件
        content = full_path.read_text(encoding='utf-8')
        
        # 尝试替换代码
        code_snippet = issue.get('code_snippet', '')
        if code_snippet and code_snippet in content:
            new_content = content.replace(code_snippet, fixed_code)
            full_path.write_text(new_content, encoding='utf-8')
            print(f"已修复：{file_path}")
            return True
        else:
            # 如果找不到精确匹配，尝试 AI 重新生成
            print(f"需要 AI 重新生成修复：{file_path}")
            return self.ai_regenerate_fix(file_path, issue)
    
    def ai_regenerate_fix(self, file_path: str, issue: Dict) -> bool:
        """AI 重新生成修复"""
        # 这里可以调用 LLM API 重新生成修复
        # 简化实现：直接使用建议
        print(f"AI 重新生成修复（简化实现）：{file_path}")
        return False
    
    def create_fix_branch(self, original_pr_number: int) -> str:
        """创建修复分支"""
        original_pr = self.repo.get_pull(original_pr_number)
        base_branch = original_pr.base.ref
        
        # 分支命名
        fix_branch = f"ai-fix/pr-{original_pr_number}"
        
        try:
            # 创建并切换到修复分支
            subprocess.run(["git", "checkout", "-b", fix_branch], check=True)
            print(f"已创建修复分支：{fix_branch}")
            return fix_branch
        except subprocess.CalledProcessError as e:
            print(f"创建分支失败：{e}")
            return ""
    
    def commit_fixes(self, fix_branch: str, issues: List[Dict]) -> bool:
        """提交修复"""
        
        if not issues:
            return False
        
        # 配置 git 用户
        subprocess.run(["git", "config", "user.name", "AI SRE Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "ai-sre@github.com"], check=True)
        
        # 添加所有变更
        subprocess.run(["git", "add", "-A"], check=True)
        
        # 检查是否有变更
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("没有变更需要提交")
            return False
        
        # 构建 commit message
        commit_msg = f"""🤖 AI Auto-Fix: 修复 PR #{self.pr_number} 的 Critical 问题

修复了 {len(issues)} 个 Critical/High 优先级问题：

"""
        for i, issue in enumerate(issues, 1):
            commit_msg += f"- {issue.get('type', '问题')} ({issue.get('file', 'N/A')})\n"
        
        commit_msg += f"""
原始 PR: #{self.pr_number}
AI 审查置信度：{issue.get('confidence_score', 'N/A')}
"""
        
        # 提交
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # 推送
        subprocess.run(["git", "push", "origin", fix_branch], check=True)
        
        print(f"已提交修复：{commit_msg[:100]}...")
        return True
    
    def run(self, create_branch: bool = True) -> Dict[str, str]:
        """执行自动修复"""
        print(f"开始 AI 自动修复 - PR #{self.pr_number}")
        
        # 加载审查结果
        review = self.load_review()
        
        # 获取 Critical 问题
        critical_issues = self.get_critical_issues(review)
        print(f"发现 {len(critical_issues)} 个 Critical/High 问题")
        
        if not critical_issues:
            print("没有需要自动修复的问题")
            return {"fix_branch": ""}
        
        # 尝试应用修复
        fixed_count = 0
        for issue in critical_issues:
            if self.apply_fix(issue):
                fixed_count += 1
        
        print(f"成功修复 {fixed_count}/{len(critical_issues)} 个问题")
        
        # 创建修复分支
        fix_branch = ""
        if create_branch and fixed_count > 0:
            fix_branch = self.create_fix_branch(self.pr_number)
            
            # 提交修复
            if fix_branch:
                self.commit_fixes(fix_branch, critical_issues[:fixed_count])
        
        return {"fix_branch": fix_branch}


def main():
    parser = argparse.ArgumentParser(description="AI 自动修复")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--review-file", required=True)
    parser.add_argument("--create-fix-branch", action="store_true")
    
    args = parser.parse_args()
    
    fixer = AIAutoFixer(
        pr_number=args.pr_number,
        review_file=args.review_file
    )
    
    result = fixer.run(create_branch=args.create_fix_branch)
    
    # 输出 GitHub Actions 变量
    if result.get("fix_branch"):
        print(f"::set-output name=fix_branch::{result['fix_branch']}")


if __name__ == "__main__":
    main()
