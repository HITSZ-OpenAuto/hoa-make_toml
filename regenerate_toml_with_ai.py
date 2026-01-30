#!/usr/bin/env python3
"""
使用 AI API 根据 README.md 重新生成对应的 .toml 文件
"""

import os
from pathlib import Path
import json
import requests
from typing import Optional

# ============ 配置区域 ============

# API 配置
AI_API_KEY = "sk-owKyczGa36l4gBsJNZQoASPqM8aAp1BOQEtzJPlQ1JCa1PA0"
AI_BASE_URL = "https://api.n1n.ai/v1"
AI_MODEL = "gemini-3-pro-preview"
PROXY = "http://127.0.0.1:7897"  # 代理配置

# 目录配置
DOWNLOADED_FILES_DIR = "./downloaded_files"
REPOS_LIST_FILE = "todolist.txt"
VALIDATION_REPORT_FILE = "toml_validation_report.txt"

# ============ 提示词模板 ============

SYSTEM_PROMPT = """***
你是一个专业的资料整理助手。请阅读我提供的文本内容（通常是课程 README 或 Wiki），将其转换为符合以下严格规范的 **TOML** 格式。
注意：千万注意，你最后输出的东西必须是纯toml,并且不要用类似```toml```的东西隔起来
### ⚠️ TOML 结构核心规则（必须遵守）
1.  **文件结构顺序**：TOML 文件必须严格分为两部分：
    *   **第一部分（顶部）**：所有的简单键值对（如 `course_name`, `repo_type`, `description`）。**绝对不能**在这些键值对之前出现 `[...]` 或 `[[...]]`。
    *   **第二部分（底部）**：所有的复杂表格（Table）和数组（Array of Tables），如 `[[lecturers]]`, `[[misc]]` 等。
2.  **避免语法错误**：一旦定义了 `[[lecturers]]` 或 `[[misc]]`，后续直到文件结束或遇到新的 `[...]` 之前的内容都属于该板块。因此，**务必将 `description` 等全局信息放在文件最开头！**

### 🛠️ 内容处理规则
1.  **基础字段**：提取 `course_name` (课程名称) 和 `course_code` (课程代码)。
2.  **HTML 转 Markdown**：如果原文包含 `<table border="1">...</table>` 等 HTML 表格代码，**必须**将其转换为标准的 Markdown 表格格式写入 content 中。
3.  **多行文本**：所有长文本（如 `description`, `content`）必须使用 TOML 的三引号 `/"/"/"` 包裹。
4.  **长文本拆分**：如果原文包含长篇的"新人须知"、"选课指南"或无特定分类的说明，请将其按主题拆分为多个 `[[misc]]` 块，并自动提取 `topic`（主题）和 `content`（内容）。

### 📅 日期与作者规范
1.  **Author 结构**：
    *   `lecturers.reviews`, `course`, `exam`, `lab`, `misc` 必须包含 `author` 子对象
    *   `textbooks`, `online_resources`, `advice`, `schedule`, `related_links` 不需要 `author`
2.  **Author 字段格式**：
    *   `name`: 贡献者昵称（若无具体人名，可填"佚名"或空字符串）。
    *   `link`: 贡献者主页链接（若无则为空字符串）。
    *   `date`: 贡献日期（字符串格式，带引号）。
3.  **日期格式**：
    *   必须是**字符串格式**（带引号），例如 `date = "2024-03-01"`。
    *   如果原文只精确到月，补全为 01 日（如 2024.03 -> 2024-03-01）。
    *   如果原文完全无日期，填空字符串 `""`。

### 🚫 忽略与空值
1.  **忽略**：学分、学时、课程性质（考查/考试）、成绩构成等教务元数据，不需要提取。
2.  **空值**：如果某个板块完全没有信息，请省略该板块，或输出空数组（如 `textbooks = []`）。

---

### 目标输出模板（请严格参考此结构）

```toml
course_name = "课程名称"
repo_type = "normal"
course_code = "代码"

# 全局注意事项/简介 (多行文本)
description = /"/"/"
这里是全局的注意事项。
/"/"/"

# 授课教师 (Lecturers)
[[lecturers]]
name = "张晓峰"

  [[lecturers.reviews]]
  content = /"/"/"
  老师有工业界背景，出的题常常让学生们摸不着头脑。
  但是讲课非常细致，能够学到很多底层逻辑。
  /"/"/"
  author = { name = "19级某学长", link = "https://github.com/example-senior", date = "2024-05-20" }

  [[lecturers.reviews]]
  content = "对实验要求很高，不建议混日子。"
  author = { name = "", link = "", date = "2024-06-01" }

[[lecturers]]
name = "某老师"
  [[lecturers.reviews]]
  content = "评价内容..."
  author = { name = "提交者名称", link = "", date = "2025-01-10" }

# 教材与参考书(不需要author)
[[textbooks]]
title = "Database System Concepts"
book_author = "Abraham Silberschatz / Henry F. Korth / S. Sudarshan"
publisher = "McGraw-Hill"
edition = "7th Edition"
type = "textbook"

[[textbooks]]
title = "数据库系统概论"
book_author = "王珊 / 萨师煊"
publisher = "高等教育出版社"
edition = "第 5 版"
type = "reference"

#电子书资源
[[online_resources]]
title = "《神经网络与深度学习》书籍主页"
url = "https://nndl.github.io/"
description = "邱锡鹏 著，机械工业出版社，2019"

# 网课推荐
[[online_resources]]
title = "CMU 15-445/645 (Intro to Database Systems)"
url = "https://15445.courses.cs.cmu.edu/"
description = "数据库领域神课，建议刷完所有 Lab。"

# 核心课程评价区块
[[course]]
content = "这门课主要讲解关系型数据库、SQL语句以及索引优化。"
author = { name = "admin", link = "", date = "2023-12-01" }

[[exam]]
content = "考试开放性题很多，需要对概念有极清晰的理解。"
author = { name = "某个不愿透露姓名的同学", link = "https://github.com/anonymous", date = "2024-07-01" }

[[lab]]
content = "实验比较难，注意力"
author = { name = "某个不愿透露姓名的同学", link = "", date = "2025-07-01" }

[[advice]]
content = "建议提前预习 B 站的 CMU 15-445 课程。"

# 课程安排
[[schedule]]
content = "共 16 周，每周 4 学时，含 2 节实验课。"

# 相关链接
[[related_links]]
content = "https://github.com/HITSZ-OpenAuto/COMP3010"

# 兜底板块
[[misc]]
topic = "实验环境"
content = "每年的实验环境可能会变，建议关注群通知。"
author = { name = "", link = "", date = "2024-11-11" }```
***"""

USER_PROMPT_TEMPLATE = """请根据以下课程 README.md 内容，生成对应的 .toml 配置文件。

【当前仓库信息】
course_code:{repo_name}

【README.md 内容】
{readme_content}

请生成完整的 TOML 配置文件："""

# ============ API 调用函数 ============

def call_ai_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """调用 AI API 生成内容"""
    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": AI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        proxies = {
            "http": PROXY,
            "https": PROXY
        }

        response = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"  ❌ API 返回格式异常")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  ❌ API 调用失败: {e}")
        return None
    except Exception as e:
        print(f"  ❌ 处理响应时出错: {e}")
        return None

# ============ 辅助函数 ============

def read_file_content(file_path: str) -> Optional[str]:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  ❌ 读取文件失败: {e}")
        return None

def write_file_content(file_path: str, content: str) -> bool:
    """写入文件内容"""
    try:
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  ❌ 写入文件失败: {e}")
        return False

def validate_toml(content: str) -> bool:
    """简单的 TOML 格式验证"""
    # 检查基本的 TOML 结构
    required_sections = ["[course]", "[info]", "[resources]"]
    for section in required_sections:
        if section not in content:
            return False
    return True

# ============ 主处理逻辑 ============

def get_repos_list() -> list[str]:
    """获取仓库列表"""
    if os.path.exists(REPOS_LIST_FILE):
        with open(REPOS_LIST_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def parse_validation_report() -> dict[str, list[str]]:
    """解析验证报告，返回问题文件及其错误信息"""
    issues = {}

    if not os.path.exists(VALIDATION_REPORT_FILE):
        print(f"⚠️  验证报告文件不存在: {VALIDATION_REPORT_FILE}")
        return issues

    with open(VALIDATION_REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析报告格式
    lines = content.split('\n')
    current_file = None
    current_issues = []

    for line in lines:
        if line.startswith('📁 文件: '):
            # 保存上一个文件的问题
            if current_file and current_issues:
                issues[current_file] = current_issues
            # 开始新文件
            current_file = line.replace('📁 文件: ', '')
            current_issues = []
        elif line.strip().startswith('[') and current_file:
            # 提取问题描述
            issue = line.split(']', 1)[1].strip()
            current_issues.append(issue)

    # 保存最后一个文件的问题
    if current_file and current_issues:
        issues[current_file] = current_issues

    return issues

def process_single_repo(repo_name: str, issues: list[str] = None) -> bool:
    """处理单个仓库

    Args:
        repo_name: 仓库名称
        issues: 该文件的错误信息列表（如果有）
    """
    readme_path = os.path.join(DOWNLOADED_FILES_DIR, f"{repo_name}_README.md")
    toml_path = os.path.join(DOWNLOADED_FILES_DIR, f"{repo_name}.toml")

    # 检查 README 是否存在
    if not os.path.exists(readme_path):
        print(f"  ⚠️  README.md 不存在，跳过")
        return False

    # 读取 README 内容
    readme_content = read_file_content(readme_path)
    if not readme_content:
        return False

    # 读取旧的 TOML 文件（如果存在）
    old_toml_content = None
    if os.path.exists(toml_path):
        old_toml_content = read_file_content(toml_path)

    print(f"  → 正在生成 {repo_name}.toml...")

    # 准备提示词
    system_prompt = SYSTEM_PROMPT.format(repo_name=repo_name)

    # 如果有错误信息，构建增强的提示词
    if issues:
        issues_text = "\n".join([f"  - {issue}" for issue in issues])
        user_prompt = f"""请根据以下课程 README.md 内容和旧的 TOML 配置文件，重新生成符合规范的 .toml 配置文件。

【当前仓库信息】
course_code: {repo_name}

【README.md 内容】
{readme_content}

【旧的 TOML 配置（可能有错误，仅供参考）】
{old_toml_content if old_toml_content else '（无旧文件）'}

【检测到的问题（必须修复）】
{issues_text}

请根据上述信息生成正确的 TOML 配置文件，确保修复所有提到的问题："""
    else:
        user_prompt = USER_PROMPT_TEMPLATE.format(
            repo_name=repo_name,
            readme_content=readme_content
        )

    # 调用 AI API
    toml_content = call_ai_api(system_prompt, user_prompt)
    if not toml_content:
        return False

    # 去除可能的代码块标记（```toml ... ```）
    if toml_content.startswith('```'):
        lines = toml_content.split('\n')
        if lines[0].startswith('```'):
            # 找到结束的 ```
            end_idx = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == '```':
                    end_idx = i
                    break
            if end_idx > 0:
                toml_content = '\n'.join(lines[1:end_idx])
            else:
                toml_content = '\n'.join(lines[1:])

    # 验证生成的 TOML 格式
    if not validate_toml(toml_content):
        print(f"  ⚠️  生成的 TOML 格式可能不正确，但仍会保存")
        # 不返回 False，仍然保存结果

    # 写入 .toml 文件
    if write_file_content(toml_path, toml_content):
        print(f"  ✓ 已生成: {repo_name}.toml")
        return True
    else:
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始使用 AI 重新生成 TOML 配置文件")
    print("=" * 60)
    print(f"\nAPI 配置:")
    print(f"  - Model: {AI_MODEL}")
    print(f"  - Base URL: {AI_BASE_URL}")
    print()

    # 解析验证报告
    issues_dict = parse_validation_report()

    if issues_dict:
        print(f"找到 {len(issues_dict)} 个有问题的文件（来自验证报告）")
        print("将只处理这些文件...\n")
        repos = [file.replace('.toml', '') for file in issues_dict.keys()]
    else:
        print("未找到验证报告或报告为空")
        print("将处理所有仓库...\n")
        repos = get_repos_list()

    if not repos:
        print("❌ 未找到仓库列表")
        return

    print(f"找到 {len(repos)} 个仓库需要处理\n")

    # 检查下载目录是否存在
    if not os.path.exists(DOWNLOADED_FILES_DIR):
        print(f"❌ 下载目录 {DOWNLOADED_FILES_DIR} 不存在")
        print(f"   请先运行 download_repo_files.py 下载文件")
        return

    # 统计信息
    stats = {
        'total': len(repos),
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    # 处理每个仓库
    for i, repo_name in enumerate(repos, 1):
        print(f"[{i}/{stats['total']}] 处理仓库: {repo_name}")

        # 获取该文件的错误信息
        issues = issues_dict.get(f"{repo_name}.toml", None)
        if issues:
            print(f"  检测到 {len(issues)} 个问题")

        success = process_single_repo(repo_name, issues)

        if success:
            stats['success'] += 1
        else:
            stats['failed'] += 1

        print()

    # 打印统计信息
    print("=" * 60)
    print("处理完成! 统计信息:")
    print("=" * 60)
    print(f"总仓库数:     {stats['total']}")
    print(f"成功生成:     {stats['success']}")
    print(f"生成失败:     {stats['failed']}")
    print(f"跳过:         {stats['skipped']}")
    print(f"\n生成的 .toml 文件保存在: {os.path.abspath(DOWNLOADED_FILES_DIR)}")
    print(f"\n💡 提示: 检查生成的文件后，可以使用 validate_toml.py 再次验证")
    print(f"💡 验证通过后，可以使用 update_and_create_pr.py 创建 PR")

if __name__ == "__main__":
    main()
