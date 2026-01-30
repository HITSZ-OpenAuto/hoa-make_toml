#!/usr/bin/env python3
"""
统一格式化 TOML 文件到标准格式
仅处理 repo_type="normal" 的 TOML 文件
按照用户提供的 Prompt 格式重新组织所有 TOML 文件
"""

import os
from pathlib import Path
import tomli
import re
from typing import Any, Dict, List

# 目录配置
DOWNLOADED_FILES_DIR = "./normal_repo"


def escape_toml_string(text: str) -> str:
    """转义 TOML 字符串中的特殊字符"""
    # 转义反斜杠（必须首先处理）
    text = text.replace('\\', '\\\\')
    # 转义双引号
    text = text.replace('"', '\\"')
    return text


def format_multiline_text(text: str, indent: int = 0) -> str:
    """格式化多行文本为 triple-quoted 格式"""
    lines = text.strip().split('\n')
    indent_str = ' ' * indent
    
    if len(lines) == 1:
        # 单行文本
        return f'"""{lines[0]}"""'
    else:
        # 多行文本
        formatted_lines = [f'{indent_str}"""']
        for line in lines:
            formatted_lines.append(f'{indent_str}{line}')
        formatted_lines.append(f'{indent_str}"""')
        return '\n'.join(formatted_lines)


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
        # 如果标准解析失败，尝试修复未转义的反斜杠
        print(f"    [WARNING] {toml_path} 解析失败，尝试修复...")
        try:
            with open(toml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在三引号字符串内转义反斜杠
            # 先找到所有 """...""" 块
            def escape_backslash_in_triple_quotes(match):
                text = match.group(1)
                # 只转义尚未转义的反斜杠（不是 \\ 的反斜杠）
                text = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', text)
                return f'"""{text}"""'
            
            content = re.sub(r'"""(.*?)"""', escape_backslash_in_triple_quotes, content, flags=re.DOTALL)
            
            # 写回临时文件再解析
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
    
    # 1. 基本信息
    if 'course_name' in data:
        lines.append(f'course_name = "{escape_toml_string(data["course_name"])}"')
    if 'repo_type' in data:
        lines.append(f'repo_type = "{escape_toml_string(data["repo_type"])}"')
    if 'course_code' in data:
        lines.append(f'course_code = "{escape_toml_string(data["course_code"])}"')
    
    lines.append('')
    
    # 2. Description
    if 'description' in data and data['description']:
        lines.append('# 全局注意事项/简介 (多行文本)')
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
    
    # 3. Lecturers
    if 'lecturers' in data and data['lecturers']:
        lines.append('# 授课教师 (Lecturers)')
        for lecturer in data['lecturers']:
            lines.append('[[lecturers]]')
            if 'name' in lecturer:
                lines.append(f'name = "{escape_toml_string(lecturer["name"])}"')
            
            # Reviews
            if 'reviews' in lecturer:
                for review in lecturer['reviews']:
                    lines.append('')
                    lines.append('  [[lecturers.reviews]]')
                    if 'content' in review:
                        content = review['content']
                        content_lines = content.strip().split('\n')
                        if len(content_lines) == 1:
                            lines.append(f'  content = """{content}"""')
                        else:
                            lines.append('  content = """')
                            for line in content_lines:
                                lines.append(f'  {line}')
                            lines.append('  """')
                    
                    author = review.get('author', {})
                    author_str = format_author(author)
                    lines.append(f'  author = {author_str}')
        lines.append('')
    
    # 4. Textbooks
    if 'textbooks' in data and data['textbooks']:
        lines.append('# 教材与参考书(不需要author)')
        for book in data['textbooks']:
            lines.append('[[textbooks]]')
            if 'title' in book:
                lines.append(f'title = "{escape_toml_string(book["title"])}"')
            if 'book_author' in book:
                lines.append(f'book_author = "{escape_toml_string(book["book_author"])}"')
            if 'publisher' in book:
                lines.append(f'publisher = "{escape_toml_string(book["publisher"])}"')
            if 'edition' in book:
                lines.append(f'edition = "{escape_toml_string(book["edition"])}"')
            if 'type' in book:
                lines.append(f'type = "{escape_toml_string(book["type"])}"')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 5. Online Resources
    if 'online_resources' in data and data['online_resources']:
        lines.append('# 网络资源（电子书、网课等）')
        for resource in data['online_resources']:
            lines.append('[[online_resources]]')
            if 'title' in resource:
                lines.append(f'title = "{escape_toml_string(resource["title"])}"')
            if 'url' in resource:
                lines.append(f'url = "{escape_toml_string(resource["url"])}"')
            if 'description' in resource:
                lines.append(f'description = "{escape_toml_string(resource["description"])}"')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 6. Course
    if 'course' in data and data['course']:
        lines.append('# 核心课程评价区块')
        for item in data['course']:
            lines.append('[[course]]')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            author = item.get('author', {})
            author_str = format_author(author)
            lines.append(f'author = {author_str}')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 7. Exam
    if 'exam' in data and data['exam']:
        for item in data['exam']:
            lines.append('[[exam]]')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            author = item.get('author', {})
            author_str = format_author(author)
            lines.append(f'author = {author_str}')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 8. Lab
    if 'lab' in data and data['lab']:
        for item in data['lab']:
            lines.append('[[lab]]')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            author = item.get('author', {})
            author_str = format_author(author)
            lines.append(f'author = {author_str}')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 9. Advice
    if 'advice' in data and data['advice']:
        for item in data['advice']:
            lines.append('[[advice]]')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            # advice 可能有 author，也可能没有
            if 'author' in item:
                author = item.get('author', {})
                author_str = format_author(author)
                lines.append(f'author = {author_str}')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 10. Schedule
    if 'schedule' in data and data['schedule']:
        lines.append('# 课程安排')
        for item in data['schedule']:
            lines.append('[[schedule]]')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 11. Related Links
    if 'related_links' in data and data['related_links']:
        lines.append('# 相关链接')
        for item in data['related_links']:
            lines.append('[[related_links]]')
            if 'content' in item:
                lines.append(f'content = "{escape_toml_string(item["content"])}"')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
        lines.append('')
    
    # 12. Misc
    if 'misc' in data and data['misc']:
        lines.append('# 兜底板块')
        for item in data['misc']:
            lines.append('[[misc]]')
            if 'topic' in item:
                lines.append(f'topic = "{escape_toml_string(item["topic"])}"')
            if 'content' in item:
                content = item['content']
                content_lines = content.strip().split('\n')
                if len(content_lines) == 1:
                    lines.append(f'content = """{content}"""')
                else:
                    lines.append('content = """')
                    for line in content_lines:
                        lines.append(line)
                    lines.append('"""')
            author = item.get('author', {})
            author_str = format_author(author)
            lines.append(f'author = {author_str}')
            lines.append('')
        if lines[-1] == '':
            lines.pop()
    
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
        
        # 检查 repo_type，只处理 "normal" 类型
        repo_type = data.get('repo_type', '').strip()
        if repo_type != 'normal':
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
    print("TOML 格式化工具 (normal_repo 专用)")
    print("=" * 60)
    print("将所有 repo_type=normal 的 TOML 文件格式化为标准格式")
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
    print(f"成功处理:     {stats['success']}")
    print(f"已跳过:       {stats['skipped']}")
    print(f"处理失败:     {stats['failed']}")


if __name__ == "__main__":
    main()
