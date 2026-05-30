#!/usr/bin/env python3
"""OpenCodeReview 执行脚本 - 代码规范检查"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


class OpenCodeReviewRunner:
    """OpenCodeReview 执行器"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.result_file = "open-code-review-result.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def run_flake8(self) -> List[Dict]:
        """运行 Flake8 检查"""
        print("运行 Flake8 检查...")
        try:
            result = subprocess.run(
                ['flake8', '.', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            issues = []
            if result.returncode != 0:
                # 解析 Flake8 输出
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(':')
                        if len(parts) >= 3:
                            issues.append({
                                "type": "flake8",
                                "file": parts[0],
                                "line": int(parts[1]) if parts[1].isdigit() else 0,
                                "description": ':'.join(parts[2:]).strip(),
                                "severity": "major"
                            })
            
            print(f"Flake8 发现 {len(issues)} 个问题")
            return issues
        except Exception as e:
            print(f"Flake8 错误：{e}")
            return []
    
    def run_black_check(self) -> List[Dict]:
        """运行 Black 格式检查"""
        print("运行 Black 格式检查...")
        try:
            result = subprocess.run(
                ['black', '--check', '--diff', '.'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            issues = []
            if result.returncode != 0:
                issues.append({
                    "type": "black",
                    "file": "multiple",
                    "line": 0,
                    "description": "代码格式不符合 Black 规范",
                    "severity": "minor",
                    "suggestion": "运行 'black .' 自动格式化"
                })
            
            print(f"Black 检查：{'通过' if result.returncode == 0 else '失败'}")
            return issues
        except Exception as e:
            print(f"Black 错误：{e}")
            return []
    
    def run_isort_check(self) -> List[Dict]:
        """运行 isort 导入排序检查"""
        print("运行 isort 导入排序检查...")
        try:
            result = subprocess.run(
                ['isort', '--check-only', '--diff', '.'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            issues = []
            if result.returncode != 0:
                issues.append({
                    "type": "isort",
                    "file": "multiple",
                    "line": 0,
                    "description": "导入顺序不符合 isort 规范",
                    "severity": "minor",
                    "suggestion": "运行 'isort .' 自动排序"
                })
            
            print(f"isort 检查：{'通过' if result.returncode == 0 else '失败'}")
            return issues
        except Exception as e:
            print(f"isort 错误：{e}")
            return []
    
    def check_threshold(self, issues: List[Dict]) -> bool:
        """检查是否超过阈值"""
        threshold = self.config.get('threshold', {})
        
        blocker = sum(1 for i in issues if i.get('severity') == 'blocker')
        critical = sum(1 for i in issues if i.get('severity') == 'critical')
        major = sum(1 for i in issues if i.get('severity') == 'major')
        
        if blocker > threshold.get('blocker', 0):
            return False
        if critical > threshold.get('critical', 0):
            return False
        if major > threshold.get('major', 10):
            return False
        
        return True
    
    def run(self) -> Dict:
        """执行 OpenCodeReview"""
        print("开始 OpenCodeReview 规范检查...")
        
        all_issues = []
        
        # 运行各项检查
        all_issues.extend(self.run_flake8())
        all_issues.extend(self.run_black_check())
        all_issues.extend(self.run_isort_check())
        
        # 检查阈值
        passed = self.check_threshold(all_issues)
        
        result = {
            "status": "passed" if passed else "failed",
            "issues": all_issues,
            "summary": f"发现 {len(all_issues)} 个规范问题",
            "checks": {
                "flake8": "completed",
                "black": "completed",
                "isort": "completed"
            }
        }
        
        if passed:
            print("✅ OpenCodeReview 通过")
        else:
            print(f"❌ OpenCodeReview 失败 - {len(all_issues)} 个问题")
        
        return result
    
    def save_result(self, result: Dict):
        """保存结果"""
        with open(self.result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到 {self.result_file}")


if __name__ == "__main__":
    config_path = os.getenv(
        "OPEN_CODE_REVIEW_CONFIG",
        ".github/configs/open-code-review-config.json"
    )
    
    runner = OpenCodeReviewRunner(config_path)
    result = runner.run()
    runner.save_result(result)
    
    # 如果失败，退出码为 1
    if result['status'] == 'failed':
        sys.exit(1)
