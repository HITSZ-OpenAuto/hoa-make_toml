#!/usr/bin/env python3
"""
将 README.md 转换为 .toml 文件
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
import tomli

# 目录配置
DOWNLOADED_FILES_DIR = "./downloaded_files"


def extract_course_info(readme_content: str) -> dict:
    """提取课程基本信息"""
    info = {}

    # 提取课程名称和代码
    # 格式: # COMP2051 - 数字逻辑设计
    title_match = re.search(r'^#\s+(\S+)\s+-\s+(.+)$', readme_content, re.MULTILINE)
    if title_match:
        info['course_code'] = title_match.group(1)
        info['course_name'] = title_match.group(2)

    return info


def extract_repo_type(readme_content: str) -> str:
    """从 README 开头提取 repo_type 注释"""
    # 格式: <!-- repo_type: normal -->
    match = re.search(r'<!--\s*repo_type:\s*(\w+)\s*-->', readme_content)
    if match:
        return match.group(1)
    return ""


def extract_textbooks(readme_content: str) -> List[dict]:
    """提取教材信息"""
    textbooks = []

    # 查找教材部分
    if "## 教材和参考书" not in readme_content:
        return textbooks

    # 提取教材部分
    section_start = readme_content.find("## 教材和参考书")
    if section_start == -1:
        return textbooks

    # 找到下一个二级标题
    next_section = readme_content.find("\n## ", section_start + 1)
    if next_section == -1:
        section_text = readme_content[section_start:]
    else:
        section_text = readme_content[section_start:next_section]

    # 解析教材列表项
    lines = section_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('-'):
            # 解析教材信息
            # 格式: - 书名/作者-版本-出版社:出版社，年份，ISBN:xxx
            # 简化处理，提取主要信息
            match = re.match(r'-\s*(.+?)\s*/', line)
            if match:
                title = match.group(1).strip()

                # 提取作者
                author_match = re.search(r'/\s*(.+?)\s*著', line)
                book_author = author_match.group(1).strip() if author_match else ""

                # 提取版本
                edition_match = re.search(r'(\d+版)', line)
                edition = edition_match.group(0) if edition_match else ""

                # 提取出版社
                publisher_match = re.search(r'-\s*([^,，]+?)[,，]', line)
                publisher = publisher_match.group(1).strip() if publisher_match else ""

                textbooks.append({
                    'title': title,
                    'book_author': book_author,
                    'publisher': publisher,
                    'edition': edition,
                    'type': 'reference' if '参考' in line else 'textbook'
                })

    return textbooks


def extract_lecturers(readme_content: str) -> List[dict]:
    """提取授课教师信息"""
    lecturers = []

    # 查找授课教师部分
    if "## 授课教师" not in readme_content:
        return lecturers

    section_start = readme_content.find("## 授课教师")
    next_section = readme_content.find("\n## ", section_start + 1)
    section_text = readme_content[section_start:next_section] if next_section != -1 else readme_content[section_start:]

    lines = section_text.split('\n')
    current_lecturer = None
    current_review_content = []

    for line in lines:
        stripped = line.strip()

        # 教师名字（一级列表项，只以 "- " 开头，不以 "-  " 开头）
        # 同时检查是否包含"文 /"模式，以避免将review内容误识别为教师名
        is_lecturer_name = stripped.startswith('- ') and not stripped.startswith('-  ') and not '> 文 /' in stripped
        if is_lecturer_name:
            # 保存上一个教师的最后一个评价
            if current_lecturer and current_review_content:
                review_text = '\n'.join(current_review_content).strip()
                # 提取作者信息（如果有引用）
                author_name, link, date = "", "", ""
                # 从最后一行找引用
                for rev_line in reversed(current_review_content):
                    if '>' in rev_line:
                        author_match = re.search(r'>\s*文\s*/\s*\[([^\]]+)\]\(([^)]+)\)(?:,\s*(\d{4}\.?\d*\.?\d*))?', rev_line)
                        if author_match:
                            author_name = author_match.group(1).strip()
                            link = author_match.group(2).strip()
                            date_str = author_match.group(3) if len(author_match.groups()) > 2 else ""
                            if date_str:
                                date_str = date_str.replace('.', '-')
                                if re.match(r'\d{4}-\d{1,2}$', date_str):
                                    date_str += '-01'
                                date = date_str
                        # 移除引用行
                        review_text = '\n'.join([l for l in current_review_content if not l.strip().startswith('>')]).strip()
                        break

                if review_text:
                    current_lecturer['reviews'].append({
                        'content': review_text,
                        'author': {
                            'name': author_name,
                            'link': link,
                            'date': date
                        }
                    })
                current_review_content = []
                lecturers.append(current_lecturer)

            # 开始新教师
            current_lecturer = {'name': stripped[2:].strip(), 'reviews': []}

        # 收集评价内容
        elif current_lecturer:
            if stripped:
                # 去除行首的 "-" 前缀（如果是缩进列表项）
                if stripped.startswith('-  ') or stripped.startswith('-   ') or stripped.startswith('-    '):
                    # 去掉 "-  "、"-   " 或 "-    "，保留文本内容
                    content = stripped[3:] if stripped.startswith('-  ') else (stripped[4:] if stripped.startswith('-   ') else stripped[5:])
                    # 如果这是第一行，不添加前缀
                    if not current_review_content:
                        current_review_content.append(content)
                    else:
                        current_review_content.append(content)
                else:
                    # 普通文本，直接添加
                    current_review_content.append(stripped if current_review_content else line)
            # 空行也添加进来，保持格式
            elif not stripped and current_review_content:
                current_review_content.append('')

    # 保存最后一个教师的最后一个评价
    if current_lecturer and current_review_content:
        review_text = '\n'.join(current_review_content).strip()
        author_name, link, date = "", "", ""
        for rev_line in reversed(current_review_content):
            if '>' in rev_line:
                author_match = re.search(r'>\s*文\s*/\s*\[([^\]]+)\]\(([^)]+)\)(?:,\s*(\d{4}\.?\d*\.?\d*))?', rev_line)
                if author_match:
                    author_name = author_match.group(1).strip()
                    link = author_match.group(2).strip()
                    date_str = author_match.group(3) if len(author_match.groups()) > 2 else ""
                    if date_str:
                        date_str = date_str.replace('.', '-')
                        if re.match(r'\d{4}-\d{1,2}$', date_str):
                            date_str += '-01'
                        date = date_str
                review_text = '\n'.join([l for l in current_review_content if not l.strip().startswith('>')]).strip()
                break

        if review_text:
            current_lecturer['reviews'].append({
                'content': review_text,
                'author': {
                    'name': author_name,
                    'link': link,
                    'date': date
                }
            })
        lecturers.append(current_lecturer)
    elif current_lecturer:
        lecturers.append(current_lecturer)

    return lecturers


def extract_online_resources(readme_content: str) -> List[dict]:
    """提取在线资源（不需要 author）"""
    resources = []

    if "## 在线资源" not in readme_content:
        return resources

    section_start = readme_content.find("## 在线资源")
    next_section = readme_content.find("\n## ", section_start + 1)
    section_text = readme_content[section_start:next_section] if next_section != -1 else readme_content[section_start:]

    lines = section_text.split('\n')
    current_resource = None

    for line in lines:
        line_stripped = line.strip()

        # 提取 Markdown 链接格式: - [标题](URL)
        if line_stripped.startswith('- [') and '](' in line_stripped:
            match = re.match(r'-\s*\[([^\]]+)\]\(([^)]+)\)', line_stripped)
            if match:
                title = match.group(1)
                url = match.group(2)
                current_resource = {
                    'title': title,
                    'url': url,
                    'description': ''
                }
                resources.append(current_resource)

        # 提取描述（行首的普通文本）
        elif current_resource and not line_stripped.startswith('-') and not line_stripped.startswith('>') and line_stripped:
            if current_resource['description']:
                current_resource['description'] += '\n' + line_stripped
            else:
                current_resource['description'] = line_stripped

    return resources


def extract_citations_with_author(readme_content: str) -> List[dict]:
    """从正文中提取带作者引用的内容"""
    items = []

    # 查找所有引用格式: > 文 / [name](link), date
    pattern = r'^(.+?)\n>\s*文\s*/\s*\[([^\]]+)\](?:,\s*(\d{4}\.?\d*\.?\d*))?'
    matches = re.findall(pattern, readme_content, re.MULTILINE)

    for match in matches:
        content = match[0].strip()
        link = match[1]
        date_str = match[2] if len(match) > 2 else ""

        # 提取作者名
        name_match = re.search(r'/([^/]+)$', link)
        author_name = name_match.group(1) if name_match else ""

        # 格式化日期
        if date_str:
            date_str = date_str.replace('.', '-')
            if re.match(r'\d{4}-\d{1,2}$', date_str):
                date_str += '-01'

        items.append({
            'content': content,
            'author': {
                'name': author_name,
                'link': f"https://github.com/{author_name}" if author_name and not link.startswith('http') else link,
                'date': date_str
            }
        })

    return items


def extract_section_with_citations(readme_content: str, section_title: str) -> List[dict]:
    """提取指定二级标题下的所有内容（包括带引用和不带引用的）"""
    lines = readme_content.split('\n')
    section_pattern = f'## {section_title}'

    items = []
    in_section = False
    current_content = []
    current_author = None

    for line in lines:
        stripped = line.strip()

        # 检测是否进入目标章节
        if stripped == section_pattern:
            in_section = True
            continue

        # 如果在章节中，检查是否遇到下一个章节
        if in_section and stripped.startswith('## '):
            # 保存当前内容
            if current_content:
                author_name = current_author['name'] if current_author and current_author['name'] else ''
                link = current_author['link'] if current_author else ''
                date = current_author['date'] if current_author else ''
                items.append({
                    'content': '\n'.join(current_content).strip(),
                    'author': {'name': author_name, 'link': link, 'date': date}
                })
                current_content = []
                current_author = None
            break

        # 收集内容
        if in_section:
            # 检查是否有引用标记
            if stripped.startswith('> 文 /'):
                # 保存之前收集的内容（如果有）
                if current_content:
                    author_name = current_author['name'] if current_author and current_author['name'] else ''
                    link = current_author['link'] if current_author else ''
                    date = current_author['date'] if current_author else ''
                    items.append({
                        'content': '\n'.join(current_content).strip(),
                        'author': {'name': author_name, 'link': link, 'date': date}
                    })
                    current_content = []
                # 提取作者信息
                author_match = re.search(r'>\s*文\s*/\s*\[([^\]]+)\](?:,\s*(\d{4}\.?\d*\.?\d*))?', stripped)
                if author_match:
                    link = author_match.group(1)
                    name_match = re.search(r'/([^/]+)$', link)
                    author_name = name_match.group(1) if name_match else ""
                    date_str = author_match.group(2) if len(author_match.groups()) > 1 else ""
                    if date_str:
                        date_str = date_str.replace('.', '-')
                        if re.match(r'\d{4}-\d{1,2}$', date_str):
                            date_str += '-01'
                    current_author = {'name': author_name, 'link': link, 'date': date_str}
                else:
                    current_author = None
            elif stripped:  # 非空行才添加
                current_content.append(line)

    # 保存最后一个内容
    if in_section and current_content:
        author_name = current_author['name'] if current_author and current_author['name'] else ''
        link = current_author['link'] if current_author else ''
        date = current_author['date'] if current_author else ''
        items.append({
            'content': '\n'.join(current_content).strip(),
            'author': {'name': author_name, 'link': link, 'date': date}
        })

    return items


def extract_misc(readme_content: str) -> List[dict]:
    """提取其他板块（除了已知章节外的所有 ## 标题）"""
    lines = readme_content.split('\n')
    known_sections = ['教材和参考书', '授课教师', '在线资源', '课程评价', '关于实验', '关于考试', '学习建议', '课程安排', '相关链接']

    items = []
    current_topic = None
    current_content = []
    current_author = None

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('## '):
            # 检查是否是已知章节
            section_name = stripped[3:].strip()
            if section_name not in known_sections:
                # 保存上一个板块
                if current_topic and current_content:
                    author_name = current_author['name'] if current_author and current_author['name'] else ''
                    link = current_author['link'] if current_author else ''
                    date = current_author['date'] if current_author else ''
                    items.append({
                        'topic': current_topic,
                        'content': '\n'.join(current_content).strip(),
                        'author': {'name': author_name, 'link': link, 'date': date}
                    })

                # 开始新板块
                current_topic = section_name
                current_content = []
                current_author = None
            else:
                # 遇到已知章节，结束当前 misc 板块
                if current_topic and current_content:
                    author_name = current_author['name'] if current_author and current_author['name'] else ''
                    link = current_author['link'] if current_author else ''
                    date = current_author['date'] if current_author else ''
                    items.append({
                        'topic': current_topic,
                        'content': '\n'.join(current_content).strip(),
                        'author': {'name': author_name, 'link': link, 'date': date}
                    })
                    current_topic = None
                    current_content = []
                    current_author = None
        elif current_topic:
            # 提取作者引用
            if stripped.startswith('> 文 /'):
                author_match = re.search(r'>\s*文\s*/\s*\[([^\]]+)\]\(([^)]+)\)(?:,\s*(\d{4}\.?\d*\.?\d*))?', stripped)
                if author_match:
                    author_name = author_match.group(1).strip()
                    link = author_match.group(2).strip()
                    date_str = author_match.group(3) if len(author_match.groups()) > 2 else ""
                    if date_str:
                        date_str = date_str.replace('.', '-')
                        if re.match(r'\d{4}-\d{1,2}$', date_str):
                            date_str += '-01'
                    current_author = {'name': author_name, 'link': link, 'date': date_str}
            else:
                current_content.append(line)

    # 保存最后一个板块
    if current_topic and current_content:
        author_name = current_author['name'] if current_author and current_author['name'] else ''
        link = current_author['link'] if current_author else ''
        date = current_author['date'] if current_author else ''
        items.append({
            'topic': current_topic,
            'content': '\n'.join(current_content).strip(),
            'author': {'name': author_name, 'link': link, 'date': date}
        })

    return items


def extract_related_links(readme_content: str) -> List[dict]:
    """提取相关链接"""
    links = []

    if "## 相关链接" not in readme_content:
        return links

    section_start = readme_content.find("## 相关链接")
    next_section = readme_content.find("\n## ", section_start + 1)
    section_text = readme_content[section_start:next_section] if next_section != -1 else readme_content[section_start:]

    lines = section_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('- '):
            content = line[2:].strip()
            # 提取链接
            if '](' in content:
                match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', content)
                if match:
                    links.append({'content': match.group(2)})
            else:
                links.append({'content': content})

    return links


def extract_description(readme_content: str) -> str:
    """提取课程描述（正文第一段）"""
    lines = readme_content.split('\n')

    # 跳过标题、徽章行和 repo_type 注释
    description_lines = []
    in_description = False
    empty_line_count = 0

    for line in lines:
        stripped = line.strip()

        # 跳过标题、徽章和 repo_type 注释
        if stripped.startswith('#') or stripped.startswith('![') or '<!-- repo_type:' in stripped:
            continue

        # 遇到二级标题停止
        if stripped.startswith('##'):
            break

        # 遇到列表项（- 开头）停止（可能是教师列表、链接列表等）
        if stripped.startswith('-'):
            break

        if stripped:
            in_description = True
            description_lines.append(line)
        elif in_description and not stripped:
            empty_line_count += 1
            if empty_line_count >= 2:  # 遇到连续两个空行后停止
                break
            description_lines.append('')  # 保留空行
        elif in_description:
            break

    return '\n'.join(description_lines).strip()


def escape_toml_string(content: str) -> str:
    """
    转义 TOML basic string 中的特殊字符

    我们使用 f'content = \"\"\"{content}\"\"\"' 格式,这会在 TOML 文件中生成:
        content = \"\"\"actual content\"\"\"

    这是 TOML 的 basic string,需要转义:
    - 反斜杠 -> \\\\
    - 双引号 -> \\\"
    - 控制字符如 \\n \\t \\r 等

    注意: TOML 不允许在 basic string 中包含未转义的控制字符
    """
    # 需要转义的特殊字符
    content = content.replace('\\', '\\\\')  # 反斜杠必须先转义
    content = content.replace('\"', '\\"')    # 双引号
    # Basic string 不允许未转义的控制字符
    content = content.replace('\n', '\\n')   # 换行符
    content = content.replace('\r', '\\r')   # 回车符
    content = content.replace('\t', '\\t')   # 制表符
    content = content.replace('\b', '\\b')   # 退格符
    content = content.replace('\f', '\\f')   # 换页符
    return content


def build_toml_content(course_code: str, readme_content: str) -> str:
    """构建 TOML 内容"""
    lines = []

    # 0. 提取 repo_type 注释
    repo_type = extract_repo_type(readme_content)

    # 1. 基本信息
    info = extract_course_info(readme_content)
    lines.append(f'course_name = "{info.get("course_name", "")}"')
    if repo_type:
        lines.append(f'repo_type = "{repo_type}"')
    lines.append(f'course_code = "{course_code}"')
    lines.append('')

    # 2. 课程描述 (description)
    description = extract_description(readme_content)
    if description:
        lines.append('description = """')
        lines.append(description)  # 多行 literal string,不需要转义
        lines.append('"""')
        lines.append('')

    # 3. 授课教师
    lecturers = extract_lecturers(readme_content)
    if lecturers:
        for lecturer in lecturers:
            lines.append(f'[[lecturers]]')
            lines.append(f'name = "{lecturer["name"]}"')
            if lecturer['reviews']:
                for review in lecturer['reviews']:
                    lines.append('  [[lecturers.reviews]]')
                    lines.append(f'  content = """{escape_toml_string(review["content"])}"""')
                    lines.append(f'  author = {{ name = "{review["author"]["name"]}", link = "{review["author"]["link"]}", date = "{review["author"]["date"]}" }}')
            lines.append('')
        lines.append('')

    # 5. 教材
    textbooks = extract_textbooks(readme_content)
    if textbooks:
        for book in textbooks:
            lines.append('[[textbooks]]')
            lines.append(f'title = "{book["title"]}"')
            lines.append(f'book_author = "{book["book_author"]}"')
            lines.append(f'publisher = "{book["publisher"]}"')
            lines.append(f'edition = "{book["edition"]}"')
            lines.append(f'type = "{book["type"]}"')
        lines.append('')

    # 6. 在线资源（不需要 author）
    online_resources = extract_online_resources(readme_content)
    if online_resources:
        for res in online_resources:
            lines.append('[[online_resources]]')
            lines.append(f'title = "{res["title"]}"')
            lines.append(f'url = "{res["url"]}"')
            lines.append(f'description = """{escape_toml_string(res["description"])}"""')
        lines.append('')

    # 7. 课程评价
    course_reviews = extract_section_with_citations(readme_content, '课程评价')
    if course_reviews:
        for review in course_reviews:
            lines.append('[[course]]')
            lines.append(f'content = """{escape_toml_string(review["content"])}"""')
            # 只有 author 有实际信息时才添加，不自动填充"佚名"
            if review["author"]["name"] or review["author"]["link"] or review["author"]["date"]:
                author_name = review["author"]["name"] or "佚名"
                lines.append(f'author = {{ name = "{author_name}", link = "{review["author"]["link"]}", date = "{review["author"]["date"]}" }}')
            lines.append('')
        lines.append('')

    # 8. 实验
    labs = extract_section_with_citations(readme_content, '关于实验')
    if labs:
        for lab in labs:
            lines.append('[[lab]]')
            lines.append(f'content = """{escape_toml_string(lab["content"])}"""')
            # 只有 author 有实际信息时才添加，不自动填充"佚名"
            if lab["author"]["name"] or lab["author"]["link"] or lab["author"]["date"]:
                author_name = lab["author"]["name"] or "佚名"
                lines.append(f'author = {{ name = "{author_name}", link = "{lab["author"]["link"]}", date = "{lab["author"]["date"]}" }}')
            lines.append('')
        lines.append('')

    # 9. 考试
    exams = extract_section_with_citations(readme_content, '关于考试')
    if exams:
        for exam in exams:
            lines.append('[[exam]]')
            lines.append(f'content = """{escape_toml_string(exam["content"])}"""')
            # 只有 author 有实际信息时才添加，不自动填充"佚名"
            if exam["author"]["name"] or exam["author"]["link"] or exam["author"]["date"]:
                author_name = exam["author"]["name"] or "佚名"
                lines.append(f'author = {{ name = "{author_name}", link = "{exam["author"]["link"]}", date = "{exam["author"]["date"]}" }}')
            lines.append('')
        lines.append('')

    # 10. 建议（不需要 author）
    advices = extract_section_with_citations(readme_content, '学习建议')
    if advices:
        for advice in advices:
            lines.append('[[advice]]')
            lines.append(f'content = """{escape_toml_string(advice["content"])}"""')
            lines.append('')
        lines.append('')

    # 11. 课程安排（不需要 author）
    schedules = extract_section_with_citations(readme_content, '课程安排')
    if schedules:
        for schedule in schedules:
            lines.append('[[schedule]]')
            lines.append(f'content = """{escape_toml_string(schedule["content"])}"""')
            lines.append('')
        lines.append('')

    # 12. 相关链接
    related_links = extract_related_links(readme_content)
    if related_links:
        for link in related_links:
            lines.append('[[related_links]]')
            lines.append(f'content = "{link["content"]}"')
        lines.append('')

    # 13. 兜底板块（misc）
    misc_items = extract_misc(readme_content)
    if misc_items:
        for item in misc_items:
            lines.append('[[misc]]')
            lines.append(f'topic = "{item["topic"]}"')
            lines.append(f'content = """{escape_toml_string(item["content"])}"""')
            # 只有 author 有实际信息时才添加，不自动填充"佚名"
            if item["author"]["name"] or item["author"]["link"] or item["author"]["date"]:
                author_name = item["author"]["name"] or "佚名"
                lines.append(f'author = {{ name = "{author_name}", link = "{item["author"]["link"]}", date = "{item["author"]["date"]}" }}')
            lines.append('')
        lines.append('')

    return '\n'.join(lines)


def convert_single_readme(readme_path: str, toml_path: str) -> bool:
    """转换单个 README 到 TOML"""
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # 从 README 的标题中提取原始课程代码
        info = extract_course_info(readme_content)
        course_code = info.get('course_code', '')
        toml_content = build_toml_content(course_code, readme_content)

        with open(toml_path, 'w', encoding='utf-8') as f:
            f.write(toml_content)

        print(f"  [OK] 已转换: {os.path.basename(readme_path)} → {os.path.basename(toml_path)}")
        return True

    except Exception as e:
        print(f"  [ERROR] 转换失败 {readme_path}: {e}")
        return False


def main():
    print("=" * 60)
    print("README.md → TOML 转换工具")
    print("=" * 60)
    print()

    readme_files = list(Path(DOWNLOADED_FILES_DIR).glob("*_README.md"))
    print(f"找到 {len(readme_files)} 个 README.md 文件\n")

    stats = {
        'total': len(readme_files),
        'success': 0,
        'failed': 0
    }

    for readme_path in readme_files:
        toml_path = str(readme_path).replace('_README.md', '.toml')
        if convert_single_readme(str(readme_path), toml_path):
            stats['success'] += 1
        else:
            stats['failed'] += 1

    print()
    print("=" * 60)
    print("转换完成! 统计信息:")
    print("=" * 60)
    print(f"总文件数:     {stats['total']}")
    print(f"成功转换:     {stats['success']}")
    print(f"转换失败:     {stats['failed']}")


if __name__ == "__main__":
    main()
