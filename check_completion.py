#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完成清单检查脚本
验证所有必要的文件都已生成
"""

from pathlib import Path

def check_completion():
    """检查所有必要文件是否存在"""
    
    script_dir = Path(__file__).parent
    
    # 定义所有应该存在的文件
    required_files = {
        "Python脚本": {
            "push_to_github.py": script_dir / "push_to_github.py",
            "generate_workflows.py": script_dir / "generate_workflows.py",
            "deploy_workflows.py": script_dir / "deploy_workflows.py",
            "github_automation.py": script_dir / "github_automation.py",
        },
        "文档": {
            "README.md": script_dir / "README.md",
            "QUICK_START.md": script_dir / "QUICK_START.md",
            "GITHUB_AUTOMATION_GUIDE.md": script_dir / "GITHUB_AUTOMATION_GUIDE.md",
            "COMPLETION_SUMMARY.md": script_dir / "COMPLETION_SUMMARY.md",
        },
        "工作流模板": {
            "format-readme-normal.yml": script_dir / "workflow_templates" / "format-readme-normal.yml",
            "format-readme-multi-project.yml": script_dir / "workflow_templates" / "format-readme-multi-project.yml",
        }
    }
    
    print("=" * 70)
    print("GitHub自动化工具集 - 完成情况检查")
    print("=" * 70)
    print()
    
    all_complete = True
    
    for category, files in required_files.items():
        print(f"📂 {category}:")
        for name, path in files.items():
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            status = "✓" if exists else "✗"
            
            if exists:
                print(f"  {status} {name:40s} ({size:>6,} bytes)")
            else:
                print(f"  {status} {name:40s} [缺失]")
                all_complete = False
        print()
    
    # 检查输入目录
    print(f"📂 输入数据:")
    readme_output = script_dir / "readme_output"
    if readme_output.exists():
        course_dirs = [d for d in readme_output.iterdir() if d.is_dir()]
        print(f"  ✓ readme_output/            ({len(course_dirs)} 个课程)")
    else:
        print(f"  ✗ readme_output/            [缺失]")
        all_complete = False
    print()
    
    # 总结
    print("=" * 70)
    if all_complete:
        print("✅ 所有文件都已成功生成!")
        print()
        print("下一步:")
        print("  1. 阅读 QUICK_START.md")
        print("  2. 获取GitHub Token")
        print("  3. 运行 python github_automation.py --all")
    else:
        print("❌ 有些文件缺失,请重新检查")
        print()
        print("解决方案:")
        print("  1. 确保所有源脚本都已生成")
        print("  2. 运行 python generate_workflows.py 生成工作流模板")
        print("  3. 检查磁盘空间是否充足")
    print()
    print("=" * 70)
    
    return all_complete


if __name__ == "__main__":
    import sys
    success = check_completion()
    sys.exit(0 if success else 1)
