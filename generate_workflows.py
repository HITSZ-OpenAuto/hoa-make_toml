#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成GitHub工作流文件
- 为normal类型仓库生成 format_and_update_readme.yml
- 为multi-project类型仓库生成 format_and_update_readme.yml

工作流在readme.toml被更新时自动触发：
1. 检出代码
2. 设置Python
3. 安装依赖 (tomli)
4. 运行格式化脚本
5. 运行转换脚本
6. 提交更改
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

# ============================================================================
# NORMAL 类型仓库工作流
# ============================================================================
NORMAL_WORKFLOW = '''name: Format and Update README

on:
  pull_request:
    paths:
      - 'readme.toml'

jobs:
  update-readme:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.head_ref }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Format readme.toml
        run: |
          # 下载格式化脚本
          python3 << 'EOF'
          import tomli
          import re
          from pathlib import Path
          
          # 读取readme.toml
          toml_file = Path("readme.toml")
          with open(toml_file, 'rb') as f:
              data = tomli.load(f)
          
          # 格式化并保存
          formatted = format_toml_content(data)
          with open(toml_file, 'w', encoding='utf-8') as f:
              f.write(formatted)
          
          print("✓ readme.toml 已格式化")
          
          def format_toml_content(data):
              """格式化TOML内容为标准格式"""
              lines = []
              
              # 标题和基本字段顺序
              field_order = ['course_code', 'repo_type', 'category', 'description']
              
              # 写入基本字段
              for field in field_order:
                  if field in data:
                      value = data[field]
                      if isinstance(value, str):
                          # 多行字符串使用三引号
                          if '\\n' in value or len(value) > 50:
                              escaped = value.replace('\\', '\\\\')
                              lines.append(f'{field} = """\\n{escaped}\\n"""')
                          else:
                              escaped = value.replace('\\', '\\\\').replace('"', '\\\\"')
                              lines.append(f'{field} = "{escaped}"')
              
              # 处理数组表 (lecturers, textbooks等)
              table_sections = [
                  'lecturers', 'textbooks', 'online_resources', 'course',
                  'homework', 'exam', 'lab', 'advice', 'schedule', 'related_links', 'misc'
              ]
              
              for section in table_sections:
                  if section in data and data[section]:
                      items = data[section]
                      if not isinstance(items, list):
                          items = [items]
                      for item in items:
                          if isinstance(item, dict):
                              lines.append(f'\\n[[{section}]]')
                              for k, v in item.items():
                                  if isinstance(v, str):
                                      escaped = v.replace('\\', '\\\\').replace('"', '\\\\"')
                                      lines.append(f'{k} = "{escaped}"')
                                  elif isinstance(v, list):
                                      lines.append(f'{k} = [')
                                      for subitem in v:
                                          if isinstance(subitem, dict):
                                              lines.append('  {')
                                              for sk, sv in subitem.items():
                                                  if isinstance(sv, str):
                                                      escaped = sv.replace('\\', '\\\\').replace('"', '\\\\"')
                                                      lines.append(f'    {sk} = "{escaped}"')
                                              lines.append('  }')
                                      lines.append(']')
              
              return '\\n'.join(lines)
          
          EOF
          
      - name: Update README.md
        run: |
          # 下载转换脚本并生成README
          python3 << 'EOF'
          import tomli
          from pathlib import Path
          
          # 读取readme.toml
          with open('readme.toml', 'rb') as f:
              data = tomli.load(f)
          
          # 生成markdown内容
          markdown = generate_markdown(data)
          
          # 写入README.md
          with open('README.md', 'w', encoding='utf-8') as f:
              f.write(markdown)
          
          print("✓ README.md 已更新")
          
          def generate_markdown(data):
              """从TOML生成Markdown"""
              lines = []
              
              # 标题
              if 'course_code' in data:
                  lines.append(f"# {data['course_code']}")
                  lines.append("")
              
              # 描述
              if 'description' in data and data['description']:
                  desc = data['description']
                  if isinstance(desc, str):
                      lines.append(desc)
                      lines.append("")
              
              # 讲师部分
              if 'lecturers' in data and data['lecturers']:
                  lines.append("## 讲师")
                  lines.append("")
                  lecturers = data['lecturers']
                  if not isinstance(lecturers, list):
                      lecturers = [lecturers]
                  for lecturer in lecturers:
                      if isinstance(lecturer, dict):
                          if 'name' in lecturer:
                              lines.append(f"### {lecturer['name']}")
                              lines.append("")
                          if 'reviews' in lecturer and lecturer['reviews']:
                              for review in lecturer['reviews']:
                                  if isinstance(review, dict) and 'content' in review:
                                      lines.append(review['content'])
                                      lines.append("")
                                  if 'author' in review:
                                      author_str = format_author(review['author'])
                                      if author_str:
                                          lines.append(f"> {author_str}")
                                          lines.append("")
              
              # 其他部分
              sections = {
                  'textbooks': '教材',
                  'online_resources': '线上资源',
                  'course': '课程',
                  'homework': '作业',
                  'exam': '考试',
                  'lab': '实验',
                  'advice': '建议',
                  'schedule': '日程',
                  'related_links': '相关链接'
              }
              
              for key, title in sections.items():
                  if key in data and data[key]:
                      lines.append(f"## {title}")
                      lines.append("")
                      items = data[key]
                      if not isinstance(items, list):
                          items = [items]
                      for item in items:
                          if isinstance(item, dict):
                              if 'content' in item:
                                  lines.append(item['content'])
                                  lines.append("")
                              if 'author' in item:
                                  author_str = format_author(item['author'])
                                  if author_str:
                                      lines.append(f"> {author_str}")
                                      lines.append("")
              
              return '\\n'.join(lines)
          
          def format_author(author):
              """格式化作者信息"""
              if not isinstance(author, dict):
                  return ""
              name = author.get('name', '')
              link = author.get('link', '')
              year = author.get('year', '')
              
              if link:
                  author_str = f"文 / [{name}]({link})"
              else:
                  author_str = f"文 / {name}"
              
              if year:
                  author_str += f", {year}"
              
              return author_str
          
          EOF
          
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add readme.toml README.md
          git commit -m "ci: Format readme.toml and update README.md" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''

# ============================================================================
# MULTI-PROJECT 类型仓库工作流
# ============================================================================
MULTI_PROJECT_WORKFLOW = '''name: Format and Update README

on:
  pull_request:
    paths:
      - 'readme.toml'

jobs:
  update-readme:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          ref: ${{ github.head_ref }}
          
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Format readme.toml
        run: |
          python3 << 'EOF'
          import tomli
          from pathlib import Path
          
          # 读取readme.toml
          toml_file = Path("readme.toml")
          with open(toml_file, 'rb') as f:
              data = tomli.load(f)
          
          # 格式化并保存
          formatted = format_toml_content(data)
          with open(toml_file, 'w', encoding='utf-8') as f:
              f.write(formatted)
          
          print("✓ readme.toml 已格式化")
          
          def format_toml_content(data):
              """格式化multi-project TOML内容"""
              lines = []
              
              # 基本字段顺序
              field_order = ['course_code', 'repo_type', 'course_name', 'category', 'description']
              
              # 写入基本字段
              for field in field_order:
                  if field in data:
                      value = data[field]
                      if isinstance(value, str):
                          if '\\n' in value or len(value) > 50:
                              escaped = value.replace('\\', '\\\\')
                              lines.append(f'{field} = """\\n{escaped}\\n"""')
                          else:
                              escaped = value.replace('\\', '\\\\').replace('"', '\\\\"')
                              lines.append(f'{field} = "{escaped}"')
              
              # 处理courses数组
              if 'courses' in data and data['courses']:
                  lines.append('')
                  for course in data['courses']:
                      if isinstance(course, dict):
                          lines.append('[[courses]]')
                          for k, v in course.items():
                              if isinstance(v, str):
                                  escaped = v.replace('\\', '\\\\').replace('"', '\\\\"')
                                  lines.append(f'{k} = "{escaped}"')
                              elif k == 'teachers' and isinstance(v, list):
                                  lines.append(f'{k} = [')
                                  for teacher in v:
                                      if isinstance(teacher, dict):
                                          lines.append('  {')
                                          for tk, tv in teacher.items():
                                              if tk == 'reviews' and isinstance(tv, list):
                                                  lines.append('    reviews = [')
                                                  for review in tv:
                                                      if isinstance(review, dict):
                                                          lines.append('      {')
                                                          for rk, rv in review.items():
                                                              if isinstance(rv, str):
                                                                  escaped = rv.replace('\\', '\\\\').replace('"', '\\\\"')
                                                                  lines.append(f'        {rk} = "{escaped}"')
                                                          lines.append('      }')
                                                  lines.append('    ]')
                                              elif isinstance(tv, str):
                                                  escaped = tv.replace('\\', '\\\\').replace('"', '\\\\"')
                                                  lines.append(f'    {tk} = "{escaped}"')
                                          lines.append('  }')
                                  lines.append(']')
              
              return '\\n'.join(lines)
          
          EOF
          
      - name: Update README.md
        run: |
          python3 << 'EOF'
          import tomli
          from pathlib import Path
          
          # 读取readme.toml
          with open('readme.toml', 'rb') as f:
              data = tomli.load(f)
          
          # 生成markdown内容
          markdown = generate_markdown(data)
          
          # 写入README.md
          with open('README.md', 'w', encoding='utf-8') as f:
              f.write(markdown)
          
          print("✓ README.md 已更新")
          
          def generate_markdown(data):
              """从multi-project TOML生成Markdown"""
              lines = []
              
              # 标题 (使用course_name)
              if 'course_name' in data:
                  lines.append(f"# {data['course_name']}")
                  lines.append("")
              
              # 描述
              if 'description' in data and data['description']:
                  lines.append(data['description'])
                  lines.append("")
              
              # 课程列表
              if 'courses' in data and data['courses']:
                  for course in data['courses']:
                      if isinstance(course, dict):
                          if 'name' in course:
                              lines.append(f"## {course['name']}")
                              lines.append("")
                          
                          if 'teachers' in course and course['teachers']:
                              lines.append("### 课程评价")
                              lines.append("")
                              teachers = course['teachers']
                              if not isinstance(teachers, list):
                                  teachers = [teachers]
                              for teacher in teachers:
                                  if isinstance(teacher, dict):
                                      if 'reviews' in teacher and teacher['reviews']:
                                          for review in teacher['reviews']:
                                              if isinstance(review, dict):
                                                  if 'content' in review:
                                                      lines.append(review['content'])
                                                      lines.append("")
                                                  if 'author' in review:
                                                      author_str = format_author(review['author'])
                                                      if author_str:
                                                          lines.append(f"> {author_str}")
                                                          lines.append("")
              
              return '\\n'.join(lines)
          
          def format_author(author):
              """格式化作者信息"""
              if not isinstance(author, dict):
                  return ""
              name = author.get('name', '')
              link = author.get('link', '')
              year = author.get('year', '')
              
              if link:
                  author_str = f"文 / [{name}]({link})"
              else:
                  author_str = f"文 / {name}"
              
              if year:
                  author_str += f", {year}"
              
              return author_str
          
          EOF
          
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add readme.toml README.md
          git commit -m "ci: Format readme.toml and update README.md" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''


def generate_workflows(readme_output_path: Path):
    """为所有课程仓库生成工作流文件"""
    print("=" * 60)
    print("GitHub 工作流生成工具")
    print("=" * 60)
    
    if not readme_output_path.exists():
        print(f"❌ readme_output不存在: {readme_output_path}")
        return
    
    courses = sorted([d.name for d in readme_output_path.iterdir() if d.is_dir()])
    print(f"找到 {len(courses)} 个课程仓库")
    print()
    
    stats = {
        "normal": 0,
        "multi-project": 0,
        "unknown": 0
    }
    
    for course_code in courses:
        # 判断仓库类型
        readme_toml = readme_output_path / course_code / "readme.toml"
        
        if not readme_toml.exists():
            print(f"⚠️  {course_code}: readme.toml不存在，跳过")
            stats["unknown"] += 1
            continue
        
        try:
            with open(readme_toml, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'repo_type = "normal"' in content:
                    repo_type = "normal"
                elif 'repo_type = "multi-project"' in content:
                    repo_type = "multi-project"
                else:
                    print(f"⚠️  {course_code}: 无法判断仓库类型")
                    stats["unknown"] += 1
                    continue
        except Exception as e:
            print(f"❌ {course_code}: 读取readme.toml失败 - {e}")
            stats["unknown"] += 1
            continue
        
        # 选择对应的工作流模板
        workflow_content = NORMAL_WORKFLOW if repo_type == "normal" else MULTI_PROJECT_WORKFLOW
        
        # 生成工作流内容
        workflow_yaml = f"""# 此文件由自动化工具生成，请勿手动编辑
# 在 readme.toml 被更新时自动触发，格式化TOML并更新README.md

{workflow_content.strip()}
"""
        
        # 输出信息
        print(f"✓ {course_code:20s} ({repo_type:15s})")
        print(f"  工作流应放在: .github/workflows/format-readme.yml")
        print()
        
        stats[repo_type] += 1
    
    # 打印统计信息
    print("=" * 60)
    print("工作流生成完成!")
    print("=" * 60)
    print(f"Normal类型:       {stats['normal']} 个")
    print(f"Multi-project类型: {stats['multi-project']} 个")
    print()
    print("📝 下一步操作:")
    print("1. 在每个仓库创建 .github/workflows/format-readme.yml 文件")
    print("2. 复制上面对应类型的工作流内容到文件中")
    print("3. 提交并推送到GitHub")
    print()


def save_workflow_templates(output_dir: Path):
    """保存工作流模板到本地"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存normal类型工作流
    normal_path = output_dir / "format-readme-normal.yml"
    with open(normal_path, 'w', encoding='utf-8') as f:
        f.write(NORMAL_WORKFLOW.strip())
    print(f"✓ Normal类型工作流模板: {normal_path}")
    
    # 保存multi-project类型工作流
    multi_path = output_dir / "format-readme-multi-project.yml"
    with open(multi_path, 'w', encoding='utf-8') as f:
        f.write(MULTI_PROJECT_WORKFLOW.strip())
    print(f"✓ Multi-project类型工作流模板: {multi_path}")
    
    print()


def main():
    """主函数"""
    import sys
    
    # 当前脚本目录
    script_dir = Path(__file__).parent
    readme_output = script_dir / "readme_output"
    workflows_dir = script_dir / "workflow_templates"
    
    # 保存工作流模板
    print("保存工作流模板...\n")
    save_workflow_templates(workflows_dir)
    
    # 生成工作流信息
    generate_workflows(readme_output)
    
    print("您可以参考 workflow_templates 目录中的模板文件")
    print("将对应的工作流复制到每个仓库的 .github/workflows/ 目录中")


if __name__ == "__main__":
    main()
