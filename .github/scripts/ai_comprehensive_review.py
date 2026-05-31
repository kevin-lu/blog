#!/usr/bin/env python3
"""AI 综合分析脚本 - 整合 OpenCodeReview + SonarQube + 代码 diff"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List


class AIComprehensiveReviewer:
    """AI 综合审查器"""
    
    def __init__(self):
        self.pr_number = int(os.getenv("PR_NUMBER", "0"))
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_api_url = os.getenv("LLM_API_URL")
        self.llm_model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
        self.results_dir = Path("./review-results")
        self.diff_file = "pr-diff.txt"
    
    def load_open_code_review_result(self) -> Dict:
        """加载 OpenCodeReview 结果"""
        result_file = self.results_dir / "open-code-review-result" / "open-code-review-result.json"
        if result_file.exists():
            with open(result_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"status": "not_found", "summary": "未找到结果"}
    
    def load_sonarqube_result(self) -> Dict:
        """加载 SonarQube 结果"""
        result_file = self.results_dir / "sonarqube-result" / "sonarqube-result.json"
        if result_file.exists():
            with open(result_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"status": "not_found", "summary": "未找到结果"}
    
    def read_diff(self) -> str:
        """读取 PR diff"""
        if not os.path.exists(self.diff_file):
            return ""
        with open(self.diff_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 限制在 6000 字符以内
            return content[:6000]
    
    def build_prompt(self, open_review: Dict, sonar_result: Dict, diff: str) -> str:
        """构建综合分析 prompt"""
        return f"""你是一位经验丰富的代码质量专家，需要综合分析三层审查结果。

## 第一层：OpenCodeReview（代码规范）
状态：{open_review.get('status', 'unknown')}
总结：{open_review.get('summary', '无')}
问题数：{len(open_review.get('issues', []))}

## 第二层：SonarQube（质量门禁）
状态：{sonar_result.get('status', 'unknown')}
总结：{sonar_result.get('summary', '无')}

## PR 变更内容
```diff
{diff}
```

## 任务

请综合分析以上信息，回答以下问题：

1. **整体质量评估**：代码质量如何？（LGTM / Needs Work / Has Critical Issues）
2. **规范符合度**：是否符合代码规范？
3. **质量门禁**：SonarQube 质量门禁是否通过？
4. **结构性问题**：是否存在 N+1 查询、竞态条件、信任边界违规等结构性 bug？
5. **业务逻辑**：代码变更是否符合业务逻辑？
6. **改进建议**：有哪些具体的改进建议？

请以 JSON 格式返回：
```json
{{
    "summary": "一句话总结",
    "verdict": "LGTM/Needs Work/Has Critical Issues",
    "open_code_review_status": "通过/失败",
    "sonarqube_status": "通过/失败",
    "critical_issues": [],
    "positive_points": [],
    "recommendations": [],
    "confidence_score": 0.0-1.0
}}
```
"""
    
    def call_llm(self, prompt: str) -> Dict:
        """调用 LLM API"""
        headers = {"Authorization": f"Bearer {self.llm_api_key}"}
        payload = {
            "model": self.llm_model,
            "messages": [
                {"role": "system", "content": "你是一位代码质量专家"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        # 重试逻辑
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.llm_api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 解析 JSON
                    try:
                        start_idx = content.find("```json")
                        if start_idx >= 0:
                            start_idx += 7
                            end_idx = content.find("```", start_idx)
                            content = content[start_idx:end_idx].strip()
                        return json.loads(content)
                    except:
                        return {"summary": "AI 分析完成", "verdict": "Needs Work"}
                else:
                    error_msg = response.text
                    print(f"AI 失败（尝试 {attempt + 1}/{max_retries}）: {error_msg}")
                    
                    if "overloaded" in error_msg.lower():
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                    
                    return {"summary": "AI 失败", "verdict": "Needs Work"}
            except Exception as e:
                print(f"网络错误（尝试 {attempt + 1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                return {"summary": "网络连接失败", "verdict": "Needs Work"}
        
        return {"summary": "AI 失败", "verdict": "Needs Work"}
    
    def run(self) -> Dict:
        """执行综合分析"""
        print("开始 AI 综合分析...")
        
        # 加载各层结果
        open_review = self.load_open_code_review_result()
        sonar_result = self.load_sonarqube_result()
        diff = self.read_diff()
        
        print(f"OpenCodeReview: {open_review.get('status')}")
        print(f"SonarQube: {sonar_result.get('status')}")
        
        # 构建 prompt 并调用 AI
        prompt = self.build_prompt(open_review, sonar_result, diff)
        result = self.call_llm(prompt)
        
        # 保存结果
        with open("ai-review-result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"AI 综合分析完成：{result.get('verdict')}")
        return result


if __name__ == "__main__":
    reviewer = AIComprehensiveReviewer()
    reviewer.run()
