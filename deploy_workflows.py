#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用GitHub API为所有仓库自动创建工作流文件
- 对normal类型仓库创建format-readme-normal.yml
- 对multi-project类型仓库创建format-readme-multi-project.yml
- 文件位置：.github/workflows/format-readme.yml
"""

import os
import sys
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import requests

class WorkflowDeployer:
    def __init__(self, github_token: str, org: str = "HITSZ-OpenAuto"):
        self.token = github_token
        self.org = org
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
    def _api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"    ❌ API请求失败: {e}")
            return None
    
    def _get_file_content(self, repo: str, path: str) -> Optional[Dict[str, Any]]:
        """获取仓库中的文件信息"""
        endpoint = f"/repos/{self.org}/{repo}/contents/{path}"
        return self._api_request("GET", endpoint)
    
    def deploy_workflow(
        self,
        repo: str,
        workflow_content: str,
        commit_message: str = "ci: Add automatic format and update workflow"
    ) -> bool:
        """部署工作流文件到仓库"""
        path = ".github/workflows/format-readme.yml"
        endpoint = f"/repos/{self.org}/{repo}/contents/{path}"
        
        # 检查文件是否已存在
        file_info = self._get_file_content(repo, path)
        sha = file_info.get("sha") if file_info else None
        
        # 编码内容为base64
        encoded_content = base64.b64encode(workflow_content.encode()).decode()
        
        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": "main"
        }
        if sha:
            data["sha"] = sha
        
        result = self._api_request("PUT", endpoint, data)
        return result is not None
    
    def deploy_course(
        self,
        course_code: str,
        repo_type: str,
        workflow_content: str
    ) -> bool:
        """部署工作流到课程仓库"""
        print(f"  {course_code:20s} ({repo_type:15s})...", end=" ")
        
        try:
            if self.deploy_workflow(
                course_code,
                workflow_content,
                f"ci: Add automatic format and update workflow for {repo_type} repos"
            ):
                print("✓")
                return True
            else:
                print("❌")
                return False
        except Exception as e:
            print(f"❌ ({e})")
            return False


def determine_repo_type(course_code: str, readme_output_path: Path) -> str:
    """根据readme.toml内容判断仓库类型"""
    readme_toml = readme_output_path / course_code / "readme.toml"
    
    if not readme_toml.exists():
        return "unknown"
    
    try:
        with open(readme_toml, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'repo_type = "normal"' in content:
                return "normal"
            elif 'repo_type = "multi-project"' in content:
                return "multi-project"
    except:
        pass
    
    return "unknown"


def deploy_all_workflows(readme_output_path: Path, workflows_dir: Path, github_token: Optional[str] = None):
    """为所有课程仓库部署工作流"""
    
    if not github_token:
        github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ 错误: 请设置 GITHUB_TOKEN 环境变量或作为参数传入")
        return False
    
    # 读取工作流模板
    normal_workflow_path = workflows_dir / "format-readme-normal.yml"
    multi_workflow_path = workflows_dir / "format-readme-multi-project.yml"
    
    if not normal_workflow_path.exists() or not multi_workflow_path.exists():
        print("❌ 错误: 工作流模板文件不存在")
        print(f"  预期: {normal_workflow_path}")
        print(f"  预期: {multi_workflow_path}")
        return False
    
    with open(normal_workflow_path, 'r', encoding='utf-8') as f:
        normal_workflow = f.read()
    
    with open(multi_workflow_path, 'r', encoding='utf-8') as f:
        multi_workflow = f.read()
    
    # 初始化部署器
    deployer = WorkflowDeployer(github_token)
    
    # 收集所有课程
    courses = sorted([d.name for d in readme_output_path.iterdir() if d.is_dir()])
    
    print("=" * 70)
    print("GitHub 工作流部署工具")
    print("=" * 70)
    print(f"找到 {len(courses)} 个课程仓库")
    print()
    print("⚠️  注意: 此操作需要有效的GitHub令牌和目标仓库的push权限")
    print()
    
    stats = {
        "success": 0,
        "failed": 0,
        "normal": 0,
        "multi-project": 0,
        "unknown": 0
    }
    
    # 部署工作流
    for course_code in courses:
        repo_type = determine_repo_type(course_code, readme_output_path)
        
        if repo_type == "unknown":
            print(f"⚠️  {course_code}: 无法判断仓库类型，跳过")
            stats["unknown"] += 1
            continue
        
        workflow_content = normal_workflow if repo_type == "normal" else multi_workflow
        
        if deployer.deploy_course(course_code, repo_type, workflow_content):
            stats["success"] += 1
            stats[repo_type] += 1
        else:
            stats["failed"] += 1
    
    # 打印统计信息
    print()
    print("=" * 70)
    print("部署完成! 统计信息:")
    print("=" * 70)
    print(f"总课程数:       {len(courses)}")
    print(f"成功部署:       {stats['success']}")
    print(f"部署失败:       {stats['failed']}")
    print(f"无法识别:       {stats['unknown']}")
    print()
    print(f"  Normal类型:       {stats['normal']} 个")
    print(f"  Multi-project类型: {stats['multi-project']} 个")
    print()
    
    return stats["failed"] == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="为HITSZ-OpenAuto仓库部署GitHub工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用GITHUB_TOKEN环境变量
  python deploy_workflows.py
  
  # 显示工作流模板
  python deploy_workflows.py --show-templates
  
  # 只显示摘要，不实际部署
  python deploy_workflows.py --dry-run
        """
    )
    
    parser.add_argument(
        "--show-templates",
        action="store_true",
        help="显示工作流模板内容"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示摘要，不实际部署"
    )
    parser.add_argument(
        "--token",
        help="GitHub个人访问令牌（可选，默认从GITHUB_TOKEN环境变量读取）"
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    readme_output = script_dir / "readme_output"
    workflows_dir = script_dir / "workflow_templates"
    
    if args.show_templates:
        print("=" * 70)
        print("工作流模板 - Normal类型")
        print("=" * 70)
        normal_path = workflows_dir / "format-readme-normal.yml"
        if normal_path.exists():
            with open(normal_path, 'r', encoding='utf-8') as f:
                print(f.read())
        print()
        print("=" * 70)
        print("工作流模板 - Multi-project类型")
        print("=" * 70)
        multi_path = workflows_dir / "format-readme-multi-project.yml"
        if multi_path.exists():
            with open(multi_path, 'r', encoding='utf-8') as f:
                print(f.read())
        return
    
    if args.dry_run:
        print("=" * 70)
        print("GitHub 工作流部署工具 (干运行模式)")
        print("=" * 70)
        
        courses = sorted([d.name for d in readme_output.iterdir() if d.is_dir()])
        
        normal_count = 0
        multi_count = 0
        unknown_count = 0
        
        for course_code in courses:
            repo_type = determine_repo_type(course_code, readme_output)
            if repo_type == "normal":
                normal_count += 1
            elif repo_type == "multi-project":
                multi_count += 1
            else:
                unknown_count += 1
        
        print(f"找到 {len(courses)} 个课程仓库")
        print(f"  Normal类型:       {normal_count} 个")
        print(f"  Multi-project类型: {multi_count} 个")
        print(f"  无法识别:          {unknown_count} 个")
        print()
        print("工作流文件将部署到: .github/workflows/format-readme.yml")
        print()
        return
    
    # 实际部署
    token = args.token or os.getenv("GITHUB_TOKEN")
    deploy_all_workflows(readme_output, workflows_dir, token)


if __name__ == "__main__":
    main()
