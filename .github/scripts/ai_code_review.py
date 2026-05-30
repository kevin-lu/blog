#!/usr/bin/env python3
"""
AI 深度代码审查脚本
集成 gstack-review skill，执行生产级代码审查
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class AICodeReviewer:
    """AI 代码审查器"""
    
    def __init__(self, pr_number: int, diff_file: str, static_analysis_dir: str):
        self.pr_number = pr_number
        self.diff_file = diff_file
        self.static_analysis_dir = static_analysis_dir
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_api_url = os.getenv("LLM_API_URL", "https://api.moonshot.cn/v1/chat/completions")
        self.llm_model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
        
        # 审查重点（来自 gstack-review skill）
        self.high_priority_checks = [
            "N+1 查询",
            "竞态条件",
            "信任边界违规",
            "逃逸 bug（未捕获异常）",
            "不变量破坏",
            "陈旧读取（缓存问题）",
            "重试逻辑缺陷"
        ]
        
        self.medium_priority_checks = [
            "内存泄漏",
            "索引缺失",
            "死锁风险",
            "幂等性问题"
        ]
    
    def read_diff(self) -> str:
        """读取 PR diff 内容"""
        with open(self.diff_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_static_analysis(self) -> Dict[str, Any]:
        """读取静态分析结果"""
        results = {
            "flake8": [],
            "black": [],
            "mypy": []
        }
        
        static_dir = Path(self.static_analysis_dir)
        
        # 读取 flake8 输出
        flake8_file = static_dir / "flake8.txt"
        if flake8_file.exists():
            with open(flake8_file, 'r') as f:
                results["flake8"] = f.readlines()[:50]  # 限制 50 行
        
        # 读取 mypy 输出
        mypy_file = static_dir / "mypy.txt"
        if mypy_file.exists():
            with open(mypy_file, 'r') as f:
                results["mypy"] = f.readlines()[:50]
        
        return results
    
    def analyze_with_ai(self, diff_content: str, static_results: Dict) -> Dict[str, Any]:
        """使用 AI 进行深度代码审查"""
        
        # 构建审查 prompt（基于 gstack-review skill）
        prompt = f"""你是一位经历过生产事故的偏执型高级工程师。请审查以下代码变更。

## 审查重点（高优先级 - 必须找出）

1. **N+1 查询**: 循环中查询数据库
2. **竞态条件**: 并发访问共享资源
3. **信任边界违规**: 未验证的外部输入
4. **逃逸 bug**: 异常未捕获导致崩溃
5. **不变量破坏**: 关键状态被意外修改
6. **陈旧读取**: 缓存/数据库读取过期数据
7. **重试逻辑缺陷**: 重试没有指数退避

## 审查重点（中优先级）

1. 内存泄漏：未关闭的资源
2. 索引缺失：数据库查询无索引
3. 死锁风险：锁获取顺序不一致
4. 幂等性问题：重复调用结果不同

## 忽略项（低优先级）

- 变量命名
- 代码格式
- 注释风格
- TODO 注释

## PR Diff

```diff
{diff_content[:50000]}  # 限制 5 万字符，避免 token 超限
```

## 静态分析结果

Flake8 问题：{len(static_results['flake8'])} 个
Mypy 问题：{len(static_results['mypy'])} 个

## 输出格式

请返回 JSON 格式的审查结果：

```json
{{
    "summary": "一句话总结整体质量",
    "verdict": "LGTM/Needs Work/Has Critical Issues",
    "critical_issues": [
        {{
            "type": "问题类型",
            "file": "文件路径",
            "line": 行号,
            "description": "详细描述",
            "severity": "critical/high/medium/low",
            "code_snippet": "问题代码",
            "suggestion": "修复建议",
            "fixed_code": "修复后的代码（可选）"
        }}
    ],
    "positive_points": ["做得好的地方"],
    "recommendations": ["改进建议"],
    "files_reviewed": ["文件列表"],
    "confidence_score": 0.0-1.0
}}
```

请严格审查，寻找能通过 CI 但在生产环境会爆炸的 bug。
"""
        
        # 调用 LLM API
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.llm_model,  # Kimi 模型
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位经历过生产事故的偏执型高级工程师，专门寻找结构性 bug。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }
        
        response = requests.post(
            self.llm_api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 解析 JSON 结果
            try:
                # 提取 JSON 部分
                start_idx = content.find("```json")
                if start_idx >= 0:
                    start_idx += 7
                    end_idx = content.find("```", start_idx)
                    content = content[start_idx:end_idx].strip()
                
                review_result = json.loads(content)
                return review_result
            except json.JSONDecodeError:
                return {
                    "summary": "AI 审查完成",
                    "verdict": "Needs Work",
                    "critical_issues": [],
                    "raw_analysis": content
                }
        else:
            print(f"AI 审查失败：{response.text}")
            return {
                "summary": "AI 审查失败",
                "verdict": "Needs Work",
                "critical_issues": [],
                "error": response.text
            }
    
    def run(self) -> Dict[str, Any]:
        """执行完整的审查流程"""
        print(f"开始 AI 代码审查 - PR #{self.pr_number}")
        
        # Step 1: 读取 diff
        diff_content = self.read_diff()
        print(f"读取到 {len(diff_content)} 字符的 diff")
        
        # Step 2: 读取静态分析结果
        static_results = self.read_static_analysis()
        print(f"读取到 Flake8 问题：{len(static_results['flake8'])} 个")
        print(f"读取到 Mypy 问题：{len(static_results['mypy'])} 个")
        
        # Step 3: AI 深度审查
        print("正在进行 AI 深度审查...")
        review_result = self.analyze_with_ai(diff_content, static_results)
        
        # Step 4: 添加元数据
        review_result["metadata"] = {
            "pr_number": self.pr_number,
            "review_time": datetime.now().isoformat(),
            "diff_size": len(diff_content),
            "files_count": diff_content.count("diff --git")
        }
        
        # Step 5: 输出结果
        print(f"\n审查结果:")
        print(f"  总结：{review_result.get('summary', 'N/A')}")
        print(f"  结论：{review_result.get('verdict', 'N/A')}")
        print(f"  Critical 问题：{len(review_result.get('critical_issues', []))}")
        print(f"  置信度：{review_result.get('confidence_score', 0):.2f}")
        
        return review_result


def main():
    parser = argparse.ArgumentParser(description="AI 代码审查")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--diff-file", required=True)
    parser.add_argument("--static-analysis-dir", required=True)
    parser.add_argument("--output-file", default="/tmp/ai-review-result.json")
    
    args = parser.parse_args()
    
    # 创建审查器
    reviewer = AICodeReviewer(
        pr_number=args.pr_number,
        diff_file=args.diff_file,
        static_analysis_dir=args.static_analysis_dir
    )
    
    # 执行审查
    result = reviewer.run()
    
    # 保存结果
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n审查结果已保存到：{output_path}")
    
    # 输出 GitHub Actions 变量
    critical_count = len(result.get("critical_issues", []))
    has_critical = "true" if critical_count > 0 else "false"
    
    print(f"::set-output name=summary::{result.get('summary', '')}")
    print(f"::set-output name=critical_issues::{critical_count}")
    print(f"::set-output name=has_critical::{has_critical}")


if __name__ == "__main__":
    main()
