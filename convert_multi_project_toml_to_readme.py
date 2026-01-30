#!/usr/bin/env python3
"""
将 TOML 文件转换为格式化的 README.md
仅处理 repo_type="multi-project" 的 TOML 文件
"""

import os
from pathlib import Path
import tomli
import re
import shutil
from typing import Any, Dict, List

# 目录配置
DOWNLOADED_FILES_DIR = "./multi-project_repo"
OUTPUT_DIR = "./readme_output"


def format_author_markdown(author_dict: Dict[str, str]) -> str:
    """
    格式化 author 为 Markdown 引用格式
    格式：文 / [姓名](链接), 年份.月
    """
    if not author_dict:
        return ""
    
    # 如果 author 不是字典（比如是字符串），直接返回空
    if not isinstance(author_dict, dict):
        return ""
    
    name = author_dict.get("name", "").strip()
    link = author_dict.get("link", "").strip()
    date = author_dict.get("date", "").strip()
    
    # 如果都为空，不输出
    if not name and not link and not date:
        return ""
    
    # 构建作者字符串
    author_str = ""
    if link and name:
        author_str = f"[{name}]({link})"
    elif name:
        author_str = name
    else:
        author_str = "匿名"
    
    # 格式化日期（YYYY-MM-DD 格式转为 YYYY.M）
    if date:
        try:
            if len(date) >= 7:
                year = date[:4]
                month = date[5:7].lstrip('0') or "0"
                date_str = f"{year}.{month}"
            else:
                date_str = date
        except:
            date_str = date
    else:
        date_str = ""
    
    # 拼接最终格式
    if date_str:
        return f"文 / {author_str}, {date_str}"
    else:
        return f"文 / {author_str}"


def parse_toml_file(toml_path: str) -> Dict[str, Any]:
    """解析 TOML 文件，带容错"""
    try:
        with open(toml_path, 'rb') as f:
            return tomli.load(f)
    except Exception as e:
        try:
            with open(toml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            def escape_backslash_in_triple_quotes(match):
                text = match.group(1)
                text = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', text)
                return f'"""{text}"""'
            
            content = re.sub(r'"""(.*?)"""', escape_backslash_in_triple_quotes, content, flags=re.DOTALL)
            
            with open(toml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            with open(toml_path, 'rb') as f:
                return tomli.load(f)
        except:
            print(f"  [ERROR] 无法解析 {toml_path}")
            return {}


def generate_markdown(data: Dict[str, Any], filename: str) -> str:
    """将 TOML 数据转换为 Markdown"""
    lines = []
    
    # 标题：课程名称（course_name 作为 H1）
    if 'course_name' in data:
        lines.append(f"# {data['course_name']}")
        lines.append("")
    
    # Description（全局介绍，放在标题下方）
    if 'description' in data and data['description']:
        desc = data['description']
        if isinstance(desc, str):
            lines.append(desc.strip())
            lines.append("")
    
    # 课程列表
    if 'courses' in data and data['courses']:
        for course in data['courses']:
            if not isinstance(course, dict):
                continue
            
            # 课程标题
            course_name = course.get('name', '未知课程')
            course_code = course.get('code', '')
            
            lines.append(f"## {course_name}")
            if course_code:
                lines.append(f"**课程代码:** {course_code}")
            lines.append("")
            
            # 课程通用评价 (reviews)
            if 'reviews' in course and course['reviews']:
                for review in course['reviews']:
                    if not isinstance(review, dict):
                        continue
                    
                    # 如果有 topic，作为小标题
                    topic = review.get('topic', '').strip()
                    if topic:
                        lines.append(f"### {topic}")
                        lines.append("")
                    
                    # 内容
                    content = review.get('content', '').strip()
                    if content:
                        content_lines = content.split('\n')
                        for line in content_lines:
                            lines.append(line)
                        lines.append("")
                    
                    # 作者
                    author = review.get('author', {})
                    author_str = format_author_markdown(author)
                    if author_str:
                        lines.append(f"> {author_str}")
                        lines.append("")
            
            # 教师评价 (teachers)
            if 'teachers' in course and course['teachers']:
                for teacher in course['teachers']:
                    if not isinstance(teacher, dict):
                        continue
                    
                    teacher_name = teacher.get('name', '')
                    if teacher_name:
                        lines.append(f"### 教师：{teacher_name}")
                        lines.append("")
                    
                    # 教师的评价
                    if 'reviews' in teacher and teacher['reviews']:
                        for treview in teacher['reviews']:
                            if not isinstance(treview, dict):
                                continue
                            
                            content = treview.get('content', '').strip()
                            if content:
                                content_lines = content.split('\n')
                                for line in content_lines:
                                    lines.append(line)
                                lines.append("")
                            
                            author = treview.get('author', {})
                            author_str = format_author_markdown(author)
                            if author_str:
                                lines.append(f"> {author_str}")
                                lines.append("")
            
            lines.append("")
    
    # 杂项信息
    if 'misc' in data and data['misc']:
        lines.append("## 其他信息")
        lines.append("")
        for item in data['misc']:
            if not isinstance(item, dict):
                continue
            
            topic = item.get('topic', '').strip()
            if topic:
                lines.append(f"### {topic}")
                lines.append("")
            
            content = item.get('content', '').strip()
            if content:
                content_lines = content.split('\n')
                for line in content_lines:
                    lines.append(line)
                lines.append("")
            
            author = item.get('author', {})
            author_str = format_author_markdown(author)
            if author_str:
                lines.append(f"> {author_str}")
                lines.append("")
        
        lines.append("")
    
    # 清理末尾多余空行
    while lines and lines[-1] == '':
        lines.pop()
    
    s = '\n'.join(lines) + '\n'
    
    # 将裸 URL 转为 Markdown 链接
    s = re.sub(r"(?P<url>https?://[^\s\)\]\">]+)", lambda m: f"[{m.group('url')}]({m.group('url')})", s)
    
    # 合并多个空行为最多一个
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s


def process_toml_file(toml_path: str, output_path: str) -> bool:
    """处理单个 TOML 文件生成 README"""
    try:
        # 解析 TOML
        data = parse_toml_file(str(toml_path))
        if not data:
            return False
        
        # 检查 repo_type，只处理 "multi-project" 类型
        repo_type = data.get('repo_type', '').strip()
        if repo_type != 'multi-project':
            return None  # 返回 None 表示跳过
        
        # 生成 Markdown
        markdown = generate_markdown(data, os.path.basename(toml_path))
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 写入 README.md 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        # 复制原 TOML 文件到输出目录并重命名为 readme.toml
        toml_output_path = os.path.join(os.path.dirname(output_path), "readme.toml")
        shutil.copy2(str(toml_path), toml_output_path)
        
        return True
    
    except Exception as e:
        import traceback
        print(f"  [ERROR] 处理失败 {toml_path}: {e}")
        print(f"  {traceback.format_exc()}")
        return False


def main():
    print("=" * 60)
    print("TOML 转 README 工具 (multi-project_repo 专用)")
    print("=" * 60)
    print("将所有 repo_type=multi-project 的 TOML 文件转换为格式化的 README.md")
    print()

    toml_files = sorted(Path(DOWNLOADED_FILES_DIR).glob("*.toml"))
    print(f"找到 {len(toml_files)} 个 .toml 文件\n")

    stats = {
        'total': len(toml_files),
        'success': 0,
        'skipped': 0,
        'failed': 0
    }

    for toml_path in toml_files:
        filename = os.path.basename(toml_path)
        # 获取 course_code 或 category 作为输出目录名
        data = parse_toml_file(str(toml_path))
        output_folder = data.get('course_code', data.get('category', filename.replace('.toml', ''))) if data else filename.replace('.toml', '')
        
        output_path = os.path.join(OUTPUT_DIR, output_folder, "README.md")
        
        result = process_toml_file(str(toml_path), output_path)
        
        if result is True:
            print(f"  [OK] 已生成: {output_folder}/README.md + readme.toml")
            stats['success'] += 1
        elif result is None:
            print(f"  [SKIP] 非 multi-project 类型，已跳过: {filename}")
            stats['skipped'] += 1
        else:
            print(f"  [ERROR] 处理失败: {filename}")
            stats['failed'] += 1

    print()
    print("=" * 60)
    print("处理完成! 统计信息:")
    print("=" * 60)
    print(f"总文件数:     {stats['total']}")
    print(f"成功生成:     {stats['success']}")
    print(f"已跳过:       {stats['skipped']}")
    print(f"处理失败:     {stats['failed']}")
    print()
    print(f"输出目录:     ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
