#!/usr/bin/env python3
"""
将 .toml 文件转换为 README.md 文件
"""

import os
import re
from pathlib import Path
import tomli

# 目录配置
DOWNLOADED_FILES_DIR = "./downloaded_files"


def build_readme_content(data: dict) -> str:
    """构建 README 内容"""
    lines = []

    # 0. 仓库类型注释（放在最前面）
    repo_type = data.get('repo_type', '')
    if repo_type:
        lines.append(f'<!-- repo_type: {repo_type} -->')
        lines.append('')

    # 1. 标题
    course_code = data.get('course_code', '')
    course_name = data.get('course_name', '')
    lines.append(f'# {course_code} - {course_name}')
    lines.append('')

    # 2. 课程描述
    description = data.get('description', '')
    if description:
        lines.append(description)

    # 4. 教材和参考书
    textbooks = data.get('textbooks', [])
    if textbooks:
        lines.append('## 教材和参考书')
        lines.append('')
        for book in textbooks:
            title = book.get('title', '')
            book_author = book.get('book_author', '')
            publisher = book.get('publisher', '')
            edition = book.get('edition', '')
            lines.append(f'- {title}/{book_author}-{edition}-{publisher}')

    # 5. 授课教师
    lecturers = data.get('lecturers', [])
    if lecturers:
        lines.append('## 授课教师')
        lines.append('')
        for lecturer in lecturers:
            name = lecturer.get('name', '')
            lines.append(f'- {name}')

            reviews = lecturer.get('reviews', [])
            for review in reviews:
                content = review.get('content', '')
                author = review.get('author', {})

                # 处理多行 review 内容
                content_lines = content.split('\n')
                if content_lines:
                    # 第一行添加 "-   " 前缀（3个空格+连字符+1个空格）
                    lines.append(f'  -   {content_lines[0]}')
                    # 后续行都直接添加（带2个空格缩进）
                    for line in content_lines[1:]:
                        lines.append(f'  {line}')
                if author.get('name'):
                    link = author.get('link', '')
                    date = author.get('date', '')
                    lines.append(f'    > 文 / [{author["name"]}]({link}), {date}')

            lines.append('')

    # 6. 在线资源
    online_resources = data.get('online_resources', [])
    if online_resources:
        lines.append('## 在线资源')
        lines.append('')
        for res in online_resources:
            title = res.get('title', '')
            url = res.get('url', '')
            desc = res.get('description', '')
            author = res.get('author', {})

            if url:
                lines.append(f'- [{title}]({url})')
            if desc:
                lines.append(f'  {desc}')
            if author.get('name'):
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'  > 文 / [{author["name"]}]({link}), {date}')

    # 7. 课程评价
    course_reviews = data.get('course', [])
    if course_reviews:
        lines.append('## 课程评价')
        for review in course_reviews:
            content = review.get('content', '')
            author = review.get('author', {})
            if content:
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    # 8. 实验
    labs = data.get('lab', [])
    if labs:
        lines.append('## 关于实验')
        for lab in labs:
            content = lab.get('content', '')
            author = lab.get('author', {})
            if content:
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    # 9. 考试
    exams = data.get('exam', [])
    if exams:
        lines.append('## 关于考试')
        for exam in exams:
            content = exam.get('content', '')
            author = exam.get('author', {})
            if content:
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    # 10. 建议
    advices = data.get('advice', [])
    if advices:
        lines.append('## 学习建议')
        for advice in advices:
            content = advice.get('content', '')
            author = advice.get('author', {})
            if content:
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    # 11. 课程安排
    schedules = data.get('schedule', [])
    if schedules:
        lines.append('## 课程安排')
        for schedule in schedules:
            content = schedule.get('content', '')
            author = schedule.get('author', {})
            if content:
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    # 12. 相关链接
    related_links = data.get('related_links', [])
    if related_links:
        lines.append('## 相关链接')
        for link in related_links:
            content = link.get('content', '')
            if content.startswith('http'):
                lines.append(f'- [{content}]({content})')
            else:
                lines.append(f'- {content}')

    # 13. 其他（misc）
    misc_items = data.get('misc', [])
    if misc_items:
        for item in misc_items:
            topic = item.get('topic', '其他')
            content = item.get('content', '')
            author = item.get('author', {})

            lines.append(f'## {topic}')
            if content:
                lines.append('')
                lines.append(content)
            # 只有 author 不为空时才显示引用
            if author.get('name') or author.get('link') or author.get('date'):
                author_name = author.get('name', '') or '佚名'
                link = author.get('link', '')
                date = author.get('date', '')
                lines.append(f'> 文 / [{author_name}]({link}), {date}')
            if content or (author.get('name') or author.get('link') or author.get('date')):
                lines.append('')

    return '\n'.join(lines)


def convert_single_toml(toml_path: str, readme_path: str) -> bool:
    """转换单个 TOML 到 README"""
    try:
        with open(toml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        data = tomli.loads(content)
        readme_content = build_readme_content(data)

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"  ✓ 已转换: {os.path.basename(toml_path)} → {os.path.basename(readme_path)}")
        return True

    except Exception as e:
        print(f"  ❌ 转换失败 {toml_path}: {e}")
        return False


def main():
    print("=" * 60)
    print("TOML → README.md 转换工具")
    print("=" * 60)
    print()

    toml_files = list(Path(DOWNLOADED_FILES_DIR).glob("*.toml"))
    print(f"找到 {len(toml_files)} 个 .toml 文件\n")

    stats = {
        'total': len(toml_files),
        'success': 0,
        'failed': 0
    }

    for toml_path in toml_files:
        readme_path = str(toml_path).replace('.toml', '_README.md')
        if convert_single_toml(str(toml_path), readme_path):
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
