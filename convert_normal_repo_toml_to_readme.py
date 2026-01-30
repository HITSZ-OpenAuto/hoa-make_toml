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


def process_content_items(items, title: str) -> List[str]:
    """处理内容项列表（支持新旧两种格式）"""
    lines = []
    
    if not items:
        return lines
    
    lines.append(f"## {title}")
    lines.append("")
    
    # 处理两种格式
    if isinstance(items, str):
        # 单字符串格式
        lines.append(items.strip())
        lines.append("")
    elif isinstance(items, list):
        # 数组格式
        for item in items:
            if isinstance(item, dict):
                if 'content' in item:
                    content = item['content'].strip()
                    content_lines = content.split('\n')
                    for line in content_lines:
                        lines.append(line)
                    lines.append("")
                
                author = item.get('author', {})
                author_str = format_author_markdown(author)
                if author_str:
                    lines.append(f"> {author_str}")
                    lines.append("")
            elif isinstance(item, str):
                # item 本身可能是字符串
                lines.append(item.strip())
                lines.append("")
    
    lines.append("")
    return lines


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
    
    # Description
    if 'description' in data and data['description']:
        lines.extend(process_content_items(data['description'], "课程描述"))
    
    # Homework
    if 'homework' in data and data['homework']:
        lines.extend(process_content_items(data['homework'], "作业"))
    
    # Exam
    if 'exam' in data and data['exam']:
        lines.extend(process_content_items(data['exam'], "考试"))
    
    # Lab
    if 'lab' in data and data['lab']:
        lines.extend(process_content_items(data['lab'], "实验"))
    
    # Advice
    if 'advice' in data and data['advice']:
        lines.extend(process_content_items(data['advice'], "建议"))
    
    # Schedule
    if 'schedule' in data and data['schedule']:
        lines.append("## 课程安排")
        lines.append("")
        for item in data['schedule']:
            if 'content' in item:
                content = item['content'].strip()
                # 直接输出内容（可能是表格、代码块或纯文本）
                lines.append(content)
                lines.append("")
        lines.append("")
    
    # Related Links
    if 'related_links' in data and data['related_links']:
        lines.append("## 相关链接")
        lines.append("")
        for item in data['related_links']:
            if 'content' in item:
                content = item['content'].strip()
                # 直接输出内容（可能是链接列表或其他格式）
                lines.append(content)
                lines.append("")
        lines.append("")
    
    # Misc
    if 'misc' in data and data['misc']:
        lines.append("## 其他")
        lines.append("")
        for item in data['misc']:
            topic = item.get('topic', '')
            content = item.get('content', '')
            
            if topic:
                lines.append(f"### {topic}")
                lines.append("")
            
            if content:
                content = content.strip()
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
    
    # 移除末尾多余空行
    while lines and lines[-1] == '':
        lines.pop()

    s = '\n'.join(lines) + '\n'
    
    # 将裸 URL 转为 Markdown 链接
    s = re.sub(r"(?P<url>https?://[^\s\)\]\">]+)", lambda m: f"[{m.group('url')}]({m.group('url')})", s)
    
    # Collapse multiple blank lines to at most one
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
