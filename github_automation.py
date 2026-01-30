#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键执行所有GitHub自动化操作的脚本
1. 上传readme.toml和README.md文件到各仓库（创建PR）
2. 部署GitHub工作流文件到各仓库

使用方法：
    python github_automation.py --push              # 只上传文件
    python github_automation.py --deploy            # 只部署工作流
    python github_automation.py --all              # 两者都执行
    python github_automation.py --help              # 显示帮助
"""

import os
import sys
import argparse
from pathlib import Path

# 导入子模块
sys.path.insert(0, str(Path(__file__).parent))

try:
    from push_to_github import GitHubAPIPusher, determine_repo_type as determine_type_push
    from deploy_workflows import WorkflowDeployer, determine_repo_type as determine_type_deploy
except ImportError as e:
    print(f"❌ 错误: 无法导入必要的模块: {e}")
    print("请确保push_to_github.py和deploy_workflows.py在同一目录中")
    sys.exit(1)


class GitHubAutomation:
    def __init__(self, github_token: str):
        self.token = github_token
        self.pusher = GitHubAPIPusher(github_token)
        self.deployer = WorkflowDeployer(github_token)
        self.script_dir = Path(__file__).parent
        self.readme_output = self.script_dir / "readme_output"
        self.workflows_dir = self.script_dir / "workflow_templates"
    
    def get_courses(self):
        """获取所有课程列表"""
        if not self.readme_output.exists():
            print(f"❌ readme_output目录不存在: {self.readme_output}")
            return []
        return sorted([d.name for d in self.readme_output.iterdir() if d.is_dir()])
    
    def push_all_files(self):
        """推送所有文件到GitHub"""
        courses = self.get_courses()
        if not courses:
            print("❌ 没有找到课程目录")
            return False
        
        print("=" * 70)
        print("第一步: 上传文件到GitHub")
        print("=" * 70)
        print(f"找到 {len(courses)} 个课程仓库")
        print()
        
        stats = {
            "success": 0,
            "failed": 0,
            "normal": 0,
            "multi-project": 0,
            "unknown": 0
        }
        
        for i, course_code in enumerate(courses, 1):
            course_dir = self.readme_output / course_code
            repo_type = determine_type_push(course_code, self.readme_output)
            
            if repo_type == "unknown":
                print(f"[{i:3d}/{len(courses)}] ⚠️  {course_code}: 无法判断仓库类型，跳过")
                stats["unknown"] += 1
                continue
            
            toml_path = course_dir / "readme.toml"
            readme_path = course_dir / "README.md"
            
            print(f"[{i:3d}/{len(courses)}] 处理 {course_code}...")
            
            if self.pusher.push_course(course_code, repo_type, str(toml_path), str(readme_path)):
                stats["success"] += 1
                stats[repo_type] += 1
            else:
                stats["failed"] += 1
            
            print()
        
        # 统计信息
        print("=" * 70)
        print("上传完成! 统计信息:")
        print("=" * 70)
        print(f"总课程数:       {len(courses)}")
        print(f"成功上传:       {stats['success']}")
        print(f"上传失败:       {stats['failed']}")
        print(f"无法识别:       {stats['unknown']}")
        print()
        print(f"  Normal类型:       {stats['normal']} 个")
        print(f"  Multi-project类型: {stats['multi-project']} 个")
        print()
        
        return stats["failed"] == 0
    
    def deploy_all_workflows(self):
        """部署工作流到所有仓库"""
        # 验证工作流文件
        normal_workflow_path = self.workflows_dir / "format-readme-normal.yml"
        multi_workflow_path = self.workflows_dir / "format-readme-multi-project.yml"
        
        if not normal_workflow_path.exists() or not multi_workflow_path.exists():
            print("❌ 错误: 工作流模板文件不存在")
            print("请先运行: python generate_workflows.py")
            return False
        
        # 读取模板
        with open(normal_workflow_path, 'r', encoding='utf-8') as f:
            normal_workflow = f.read()
        with open(multi_workflow_path, 'r', encoding='utf-8') as f:
            multi_workflow = f.read()
        
        # 获取课程列表
        courses = self.get_courses()
        if not courses:
            print("❌ 没有找到课程目录")
            return False
        
        print("=" * 70)
        print("第二步: 部署GitHub工作流")
        print("=" * 70)
        print(f"找到 {len(courses)} 个课程仓库")
        print()
        
        stats = {
            "success": 0,
            "failed": 0,
            "normal": 0,
            "multi-project": 0,
            "unknown": 0
        }
        
        for i, course_code in enumerate(courses, 1):
            repo_type = determine_type_deploy(course_code, self.readme_output)
            
            if repo_type == "unknown":
                print(f"[{i:3d}/{len(courses)}] ⚠️  {course_code}: 无法判断仓库类型，跳过")
                stats["unknown"] += 1
                continue
            
            workflow_content = normal_workflow if repo_type == "normal" else multi_workflow
            
            print(f"[{i:3d}/{len(courses)}] {course_code:20s} ({repo_type:15s})...", end=" ")
            
            try:
                if self.deployer.deploy_workflow(
                    course_code,
                    workflow_content,
                    f"ci: Add automatic format and update workflow for {repo_type} repos"
                ):
                    print("✓")
                    stats["success"] += 1
                    stats[repo_type] += 1
                else:
                    print("❌")
                    stats["failed"] += 1
            except Exception as e:
                print(f"❌ ({e})")
                stats["failed"] += 1
        
        # 统计信息
        print()
        print("=" * 70)
        print("工作流部署完成! 统计信息:")
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
    
    def run_all(self):
        """执行所有操作"""
        print()
        print("🚀 GitHub自动化工具 - 完全执行模式")
        print()
        
        # 第一步：上传文件
        push_success = self.push_all_files()
        
        print()
        input("按Enter继续部署工作流...")
        print()
        
        # 第二步：部署工作流
        deploy_success = self.deploy_all_workflows()
        
        print()
        if push_success and deploy_success:
            print("✅ 所有操作完成！")
            return True
        else:
            print("⚠️  有些操作失败，请检查日志")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="HITSZ-OpenAuto GitHub自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python github_automation.py --push              # 只上传文件
  python github_automation.py --deploy            # 只部署工作流
  python github_automation.py --all               # 两者都执行
  
必需的环境变量:
  GITHUB_TOKEN - GitHub Personal Access Token
        """
    )
    
    parser.add_argument(
        "--push",
        action="store_true",
        help="只执行上传文件操作"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="只执行部署工作流操作"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="执行所有操作（上传+部署）"
    )
    parser.add_argument(
        "--token",
        help="GitHub Personal Access Token（可选，默认从GITHUB_TOKEN环境变量读取）"
    )
    
    args = parser.parse_args()
    
    # 获取token
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ 错误: 请设置 GITHUB_TOKEN 环境变量或使用 --token 参数")
        print()
        print("获取Token方法:")
        print("1. 访问 https://github.com/settings/tokens")
        print("2. 创建新token (classic)")
        print("3. 授予 repo 和 workflow 权限")
        print("4. 复制token并设置环境变量")
        print()
        print("设置环境变量:")
        print("  PowerShell: $env:GITHUB_TOKEN = 'your_token_here'")
        print("  Bash: export GITHUB_TOKEN='your_token_here'")
        sys.exit(1)
    
    # 初始化自动化工具
    automation = GitHubAutomation(token)
    
    # 执行指定操作
    if args.push:
        automation.push_all_files()
    elif args.deploy:
        automation.deploy_all_workflows()
    elif args.all:
        automation.run_all()
    else:
        # 默认：交互式菜单
        print()
        print("=" * 70)
        print("HITSZ-OpenAuto GitHub自动化工具")
        print("=" * 70)
        print()
        print("选择操作:")
        print("  1. 只上传文件 (readme.toml + README.md)")
        print("  2. 只部署工作流")
        print("  3. 执行所有操作")
        print("  4. 退出")
        print()
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            automation.push_all_files()
        elif choice == "2":
            automation.deploy_all_workflows()
        elif choice == "3":
            automation.run_all()
        else:
            print("已退出")


if __name__ == "__main__":
    main()
