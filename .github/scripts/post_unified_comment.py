#!/usr/bin/env python3
"""统一评论发布脚本 - 发布三层审查的综合报告"""

import os
import json
from github import Github


class UnifiedCommentPoster:
    """统一评论发布器"""
    
    def __init__(self):
        self.pr_number = int(os.getenv("PR_NUMBER", "0"))
        self.gh = Github(os.getenv("GITHUB_TOKEN"))
        self.repo = self.gh.get_repo(os.getenv("GITHUB_REPOSITORY"))
        self.pr = self.repo.get_pull(self.pr_number)
        self.results_dir = "./review-results"
    
    def load_results(self) -> dict:
        """加载所有审查结果"""
        results = {}
        
        # OpenCodeReview
        try:
            with open(f"{self.results_dir}/open-code-review-result/open-code-review-result.json", 'r') as f:
                results['open_code_review'] = json.load(f)
        except Exception as e:
            print(f"加载 OpenCodeReview 结果失败：{e}")
            results['open_code_review'] = {"status": "error"}
        
        # SonarQube
        try:
            with open(f"{self.results_dir}/sonarqube-result/sonarqube-result.json", 'r') as f:
                results['sonarqube'] = json.load(f)
        except Exception as e:
            print(f"加载 SonarQube 结果失败：{e}")
            results['sonarqube'] = {"status": "error"}
        
        # AI Review
        try:
            with open("ai-review-result.json", 'r') as f:
                results['ai_review'] = json.load(f)
        except Exception as e:
            print(f"加载 AI 审查结果失败：{e}")
            results['ai_review'] = {"status": "error"}
        
        return results
    
    def generate_comment(self, results: dict) -> str:
        """生成评论内容"""
        ocr = results.get('open_code_review', {})
        sq = results.get('sonarqube', {})
        ai = results.get('ai_review', {})
        
        # 状态图标
        ocr_icon = "✅" if ocr.get('status') == 'passed' else "❌" if ocr.get('status') == 'failed' else "⚠️"
        sq_icon = "✅" if sq.get('status') == 'passed' else "❌" if sq.get('status') == 'failed' else "⚠️"
        ai_icon = "✅" if ai.get('verdict') == 'LGTM' else "⚠️" if ai.get('verdict') == 'Needs Work' else "❌"
        
        comment = f"""## 🤖 AI 代码审查报告

### 第一层：OpenCodeReview（代码规范）
{ocr_icon} **{ocr.get('status', '未知')}** - {ocr.get('summary', '无')}

### 第二层：SonarQube（质量门禁）
{sq_icon} **{sq.get('status', '未知')}** - {sq.get('summary', '无')}

### 第三层：AI 深度审查
{ai_icon} **{ai.get('verdict', '未知')}**

**总结：** {ai.get('summary', '无')}

---

### 综合结论

"""
        
        # 根据结果给出结论
        if ai.get('verdict') == 'LGTM' and ocr.get('status') == 'passed':
            comment += "✅ **批准合并** - 代码质量良好，符合规范"
        elif ai.get('verdict') == 'Needs Work':
            comment += "⚠️ **需要改进** - 请参考上述建议进行修改"
        elif ai.get('verdict') == 'Has Critical Issues':
            comment += "❌ **存在严重问题** - 请先修复 Critical Issues"
        else:
            comment += "⚠️ **待审查** - 请等待 AI 审查完成"
        
        # 添加详细问题（如果有）
        if ai.get('critical_issues'):
            comment += "\n\n### Critical Issues\n"
            for i, issue in enumerate(ai['critical_issues'], 1):
                comment += f"\n**{i}. {issue.get('type', '问题')}**\n"
                comment += f"- 文件：{issue.get('file', '未知')}\n"
                comment += f"- 描述：{issue.get('description', '无')}\n"
                comment += f"- 建议：{issue.get('suggestion', '无')}\n"
        
        # 添加正面评价
        if ai.get('positive_points'):
            comment += "\n\n### 亮点\n"
            for i, point in enumerate(ai['positive_points'], 1):
                comment += f"{i}. {point}\n"
        
        # 添加改进建议
        if ai.get('recommendations'):
            comment += "\n\n### 改进建议\n"
            for i, rec in enumerate(ai['recommendations'], 1):
                comment += f"{i}. {rec}\n"
        
        comment += f"\n\n---\n*审查时间：{self.pr.updated_at}*\n"
        
        return comment
    
    def post_comment(self, comment: str):
        """发布评论"""
        self.pr.create_issue_comment(comment)
        print(f"✅ 评论已发布到 PR #{self.pr_number}")
    
    def run(self):
        """执行"""
        print("开始发布统一评论...")
        results = self.load_results()
        comment = self.generate_comment(results)
        self.post_comment(comment)


if __name__ == "__main__":
    poster = UnifiedCommentPoster()
    poster.run()
