#!/usr/bin/env python3
"""
将 TOML 文件转换为格式化的 README.md
仅处理 repo_type="normal" 的 TOML 文件
简洁清晰版本
"""

import os
from pathlib import Path
import tomli
import re
import shutil
from typing import Any, Dict, List

# 目录配置
DOWNLOADED_FILES_DIR = "./normal_repo"
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
    
    # 格式化日期（YYYY-MM 格式转为 YYYY.M）
    if date:
        try:
            # 尝试解析日期
            if len(date) >= 7:  # 至少 YYYY-MM 格式
                year = date[:4]
                month = date[5:7].lstrip('0') or "0"  # 移除前导零
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
        # 如果解析失败，尝试修复反斜杠
        try:
            with open(toml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
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
    
    # 标题：课程名称
    if 'course_name' in data:
        lines.append(f"# {data['course_name']}")
        lines.append("")
    
    # 课程代码
    if 'course_code' in data:
        lines.append(f"**课程代码:** {data['course_code']}")
        lines.append("")
    
    # Description（全局介绍）
    if 'description' in data and data['description']:
        desc = data['description']
        if isinstance(desc, str):
            lines.append(desc.strip())
            lines.append("")
    
    # Lecturers（授课教师）
    if 'lecturers' in data and data['lecturers']:
        lines.append("## 授课教师")
        lines.append("")
        lecturers = data['lecturers']
        if isinstance(lecturers, list):
            for lecturer in lecturers:
                if isinstance(lecturer, dict) and 'name' in lecturer:
                    lines.append(f"### {lecturer['name']}")
                    lines.append("")
                    
                    # 教师的reviews
                    if 'reviews' in lecturer and lecturer['reviews']:
                        for review in lecturer['reviews']:
                            if isinstance(review, dict):
                                content = review.get('content', '').strip()
                                if content:
                                    content_lines = content.split('\n')
                                    for line in content_lines:
                                        lines.append(line)
                                    lines.append("")
                                
                                author = review.get('author', {})
                                author_str = format_author_markdown(author)
                                if author_str:
                                    lines.append(f"> {author_str}")
                                    lines.append("")
        lines.append("")
    
    # Textbooks（教材与参考书）
    if 'textbooks' in data and data['textbooks']:
        lines.append("## 教材与参考书")
        lines.append("")
        textbooks = data['textbooks']
        if isinstance(textbooks, list):
            for book in textbooks:
                if isinstance(book, dict):
                    title = book.get('title', '')
                    book_author = book.get('book_author', '')
                    publisher = book.get('publisher', '')
                    edition = book.get('edition', '')
                    
                    if title:
                        lines.append(f"**{title}**")
                    details = []
                    if book_author:
                        details.append(f"作者：{book_author}")
                    if publisher:
                        details.append(f"出版社：{publisher}")
                    if edition:
                        details.append(f"版本：{edition}")
                    if details:
                        lines.append(" | ".join(details))
                    lines.append("")
        lines.append("")
    
    # Online Resources（在线资源）
    if 'online_resources' in data and data['online_resources']:
        lines.append("## 在线资源")
        lines.append("")
        resources = data['online_resources']
        if isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict):
                    title = resource.get('title', '')
                    url = resource.get('url', '')
                    description = resource.get('description', '')
                    
                    if url:
                        lines.append(f"- [{title}]({url})")
                    else:
                        lines.append(f"- {title}")
                    
                    if description:
                        lines.append(f"  {description}")
                    lines.append("")
        lines.append("")
    
    # Course（课程评价）
    if 'course' in data and data['course']:
        lines.append("## 课程评价")
        lines.append("")
        course_items = data['course']
        if isinstance(course_items, list):
            for item in course_items:
                if isinstance(item, dict):
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
    
    # Homework（作业）
    if 'homework' in data and data['homework']:
        lines.append("## 作业")
        lines.append("")
        homework_items = data['homework']
        if isinstance(homework_items, list):
            for item in homework_items:
                if isinstance(item, dict):
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
    
    # Exam（考试）
    if 'exam' in data and data['exam']:
        lines.append("## 考试")
        lines.append("")
        exam_items = data['exam']
        if isinstance(exam_items, list):
            for item in exam_items:
                if isinstance(item, dict):
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
    
    # Lab（实验）
    if 'lab' in data and data['lab']:
        lines.append("## 实验")
        lines.append("")
        lab_items = data['lab']
        if isinstance(lab_items, list):
            for item in lab_items:
                if isinstance(item, dict):
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
    
    # Advice（建议）
    if 'advice' in data and data['advice']:
        lines.append("## 建议")
        lines.append("")
        advice_items = data['advice']
        if isinstance(advice_items, list):
            for item in advice_items:
                if isinstance(item, dict):
                    content = item.get('content', '').strip()
                    if content:
                        content_lines = content.split('\n')
                        for line in content_lines:
                            lines.append(line)
                        lines.append("")
        lines.append("")
    
    # Schedule（课程安排）
    if 'schedule' in data and data['schedule']:
        lines.append("## 课程安排")
        lines.append("")
        schedule_items = data['schedule']
        if isinstance(schedule_items, list):
            for item in schedule_items:
                if isinstance(item, dict):
                    content = item.get('content', '').strip()
                    if content:
                        content_lines = content.split('\n')
                        for line in content_lines:
                            lines.append(line)
                        lines.append("")
        lines.append("")
    
    # Related Links（相关链接）
    if 'related_links' in data and data['related_links']:
        lines.append("## 相关链接")
        lines.append("")
        links_items = data['related_links']
        if isinstance(links_items, list):
            for item in links_items:
                if isinstance(item, dict):
                    content = item.get('content', '').strip()
                    if content:
                        if content.startswith('http'):
                            lines.append(f"- [{content}]({content})")
                        else:
                            lines.append(f"- {content}")
                        lines.append("")
        lines.append("")
    
    # Misc（杂项）
    if 'misc' in data and data['misc']:
        lines.append("## 其他信息")
        lines.append("")
        misc_items = data['misc']
        if isinstance(misc_items, list):
            for item in misc_items:
                if isinstance(item, dict):
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
        
        # 检查 repo_type，只处理 "normal" 类型
        repo_type = data.get('repo_type', '').strip()
        if repo_type != 'normal':
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
    print("TOML 转 README 工具 (normal_repo 专用)")
    print("=" * 60)
    print("将所有 repo_type=normal 的 TOML 文件转换为格式化的 README.md")
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
        course_code = filename.replace('.toml', '')
        output_path = os.path.join(OUTPUT_DIR, course_code, "README.md")
        
        result = process_toml_file(str(toml_path), output_path)
        
        if result is True:
            print(f"  [OK] 已生成: {course_code}/README.md + readme.toml")
            stats['success'] += 1
        elif result is None:
            print(f"  [SKIP] 非 normal 类型，已跳过: {filename}")
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
