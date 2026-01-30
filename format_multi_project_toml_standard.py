#!/usr/bin/env python3
"""
统一格式化 TOML 文件到标准格式
仅处理 repo_type="multi-project" 的 TOML 文件
按照 multi-project 的规范格式重新组织所有 TOML 文件
"""

import os
from pathlib import Path
import tomli
import re
from typing import Any, Dict, List

# 目录配置
DOWNLOADED_FILES_DIR = "./multi-project_repo"


def escape_toml_string(text: str) -> str:
    """转义 TOML 字符串中的特殊字符"""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text


def format_author(author_dict: Dict[str, str]) -> str:
    """格式化 author 字典"""
    if not author_dict or all(not v for v in author_dict.values()):
        return '{ name = "", link = "", date = "" }'
    
    return (f'{{ name = "{escape_toml_string(author_dict.get("name", ""))}", '
            f'link = "{escape_toml_string(author_dict.get("link", ""))}", '
            f'date = "{escape_toml_string(author_dict.get("date", ""))}" }}')


def parse_toml_file(toml_path: str) -> Dict[str, Any]:
    """解析 TOML 文件，如果标准解析失败则尝试修复"""
    try:
        with open(toml_path, 'rb') as f:
            return tomli.load(f)
    except Exception as e:
        print(f"    [WARNING] {toml_path} 解析失败，尝试修复...")
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
        except Exception as e2:
            print(f"  [ERROR] 无法解析 {toml_path}: {e2}")
            return {}


def format_toml_content(data: Dict[str, Any]) -> str:
    """将数据转换为标准 TOML 格式"""
    lines = []
    
    # 1. course_code、repo_type、course_name 和 category
    if 'course_code' in data:
        lines.append(f'course_code = "{escape_toml_string(data["course_code"])}"')
    lines.append('repo_type = "multi-project"')
    if 'course_name' in data:
        lines.append(f'course_name = "{escape_toml_string(data["course_name"])}"')
    if 'category' in data:
        lines.append(f'category = "{escape_toml_string(data["category"])}"')
    
    lines.append('')
    
    # 2. Description
    if 'description' in data and data['description']:
        desc_text = data['description']
        if isinstance(desc_text, str):
            desc_lines = desc_text.strip().split('\n')
            if len(desc_lines) == 1:
                lines.append(f'description = """{desc_text}"""')
            else:
                lines.append('description = """')
                for line in desc_lines:
                    lines.append(line)
                lines.append('"""')
        lines.append('')
    
    # 3. Courses
    if 'courses' in data and data['courses']:
        for course in data['courses']:
            if not isinstance(course, dict):
                continue
            
            lines.append('[[courses]]')
            if 'name' in course:
                lines.append(f'name = "{escape_toml_string(course["name"])}"')
            if 'code' in course:
                lines.append(f'code = "{escape_toml_string(course["code"])}"')
            
            # Course Reviews
            if 'reviews' in course and course['reviews']:
                for review in course['reviews']:
                    if not isinstance(review, dict):
                        continue
                    
                    lines.append('')
                    lines.append('  [[courses.reviews]]')
                    
                    if 'topic' in review:
                        lines.append(f'  topic = "{escape_toml_string(review["topic"])}"')
                    
                    if 'content' in review:
                        content = review['content']
                        import textwrap
                        normalized = textwrap.dedent(content).strip()
                        content_lines = normalized.split('\n')
                        if len(content_lines) == 1 and content_lines[0]:
                            lines.append('  content = """' + content_lines[0] + '"""')
                        else:
                            lines.append('  content = """')
                            for line in content_lines:
                                clean_line = line.lstrip()
                                lines.append('  ' + clean_line)
                            lines.append('  """')
                    
                    author = review.get('author', {})
                    author_str = format_author(author)
                    lines.append(f'  author = {author_str}')
            
            # Course Teachers
            if 'teachers' in course and course['teachers']:
                for teacher in course['teachers']:
                    if not isinstance(teacher, dict):
                        continue
                    
                    lines.append('')
                    lines.append('  [[courses.teachers]]')
                    if 'name' in teacher:
                        lines.append(f'  name = "{escape_toml_string(teacher["name"])}"')
                    
                    # Teacher Reviews
                    if 'reviews' in teacher and teacher['reviews']:
                        for treview in teacher['reviews']:
                            if not isinstance(treview, dict):
                                continue
                            
                            lines.append('')
                            lines.append('    [[courses.teachers.reviews]]')
                            
                            if 'content' in treview:
                                content = treview['content']
                                import textwrap
                                normalized = textwrap.dedent(content).strip()
                                content_lines = normalized.split('\n')
                                if len(content_lines) == 1 and content_lines[0]:
                                    lines.append('    content = """' + content_lines[0] + '"""')
                                else:
                                    lines.append('    content = """')
                                    for line in content_lines:
                                        clean_line = line.lstrip()
                                        lines.append('    ' + clean_line)
                                    lines.append('    """')
                            
                            author = treview.get('author', {})
                            author_str = format_author(author)
                            lines.append(f'    author = {author_str}')
            
            lines.append('')
    
    # 4. Misc
    if 'misc' in data and data['misc']:
        lines.append('# 杂项信息')
        for item in data['misc']:
            if not isinstance(item, dict):
                continue
            
            lines.append('[[misc]]')
            if 'topic' in item:
                lines.append(f'topic = "{escape_toml_string(item["topic"])}"')
            if 'content' in item:
                content = item['content']
                import textwrap
                normalized = textwrap.dedent(content).strip()
                content_lines = normalized.split('\n')
                if len(content_lines) == 1 and content_lines[0]:
                    lines.append('content = """' + content_lines[0] + '"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        clean_line = line.lstrip()
                        lines.append(clean_line)
                    lines.append('"""')
            author = item.get('author', {})
            author_str = format_author(author)
            lines.append(f'author = {author_str}')
            lines.append('')
    
    # 移除末尾多余空行
    while lines and lines[-1] == '':
        lines.pop()
    
    return '\n'.join(lines) + '\n'


def process_toml_file(toml_path: str) -> bool:
    """处理单个 TOML 文件"""
    try:
        # 解析原始 TOML
        data = parse_toml_file(str(toml_path))
        if not data:
            return False
        
        # 检查 repo_type，只处理 "multi-project" 类型
        repo_type = data.get('repo_type', '').strip()
        if repo_type != 'multi-project':
            return None  # 返回 None 表示跳过
        
        # 格式化内容
        formatted_content = format_toml_content(data)
        
        # 写入文件
        with open(toml_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        return True
    
    except Exception as e:
        print(f"  [ERROR] 处理失败 {toml_path}: {e}")
        return False


def main():
    print("=" * 60)
    print("TOML 格式化工具 (multi-project_repo 专用)")
    print("=" * 60)
    print("将所有 repo_type=multi-project 的 TOML 文件格式化为标准格式")
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
        result = process_toml_file(str(toml_path))
        
        if result is True:
            print(f"  [OK] 已格式化: {filename}")
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
    print(f"成功处理:     {stats['success']}")
    print(f"已跳过:       {stats['skipped']}")
    print(f"处理失败:     {stats['failed']}")


if __name__ == "__main__":
    main()
