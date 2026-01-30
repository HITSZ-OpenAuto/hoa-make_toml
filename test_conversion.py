#!/usr/bin/env python3
"""
测试 TOML ↔ README 互相转换的稳定性
随机选择 5 个 TOML 文件，进行多次转换，对比结果
"""

import os
import shutil
import random
from pathlib import Path
import difflib
import tomli
import hashlib

# 目录配置
DOWNLOADED_FILES_DIR = "./downloaded_files"
TEST_DIR = "./test_conversion"

def get_file_hash(file_path: str) -> str:
    """获取文件的哈希值"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def read_file_content(file_path: str) -> str:
    """读取文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_content(file_path: str, content: str):
    """写入文件内容"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def toml_to_readme(toml_path: str, readme_path: str):
    """TOML 转 README"""
    # 调用现有的转换脚本逻辑
    from convert_toml_to_readme import build_readme_content
    from convert_toml_to_readme import convert_single_toml
    convert_single_toml(toml_path, readme_path)

def readme_to_toml(readme_path: str, toml_path: str):
    """README 转 TOML"""
    # 调用现有的转换脚本逻辑
    from convert_readme_to_toml import convert_single_readme
    convert_single_readme(readme_path, toml_path)

def copy_random_tomls(count: int = 5) -> list:
    """随机复制 count 个 TOML 文件到测试目录"""
    # 清空测试目录
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # 获取所有 TOML 文件
    toml_files = list(Path(DOWNLOADED_FILES_DIR).glob("*.toml"))
    if not toml_files:
        print(f"❌ 没有找到 TOML 文件在 {DOWNLOADED_FILES_DIR}")
        return []

    # 随机选择
    selected = random.sample(toml_files, min(count, len(toml_files)))

    # 复制到测试目录
    copied = []
    for toml_path in selected:
        filename = toml_path.name
        dest_path = os.path.join(TEST_DIR, filename)
        shutil.copy2(toml_path, dest_path)
        copied.append(filename)

    print(f"✅ 已随机选择并复制 {len(copied)} 个 TOML 文件到 {TEST_DIR}")
    return copied

def test_single_file(filename: str) -> dict:
    """测试单个文件的多次转换"""
    print(f"\n{'='*60}")
    print(f"测试文件: {filename}")
    print(f"{'='*60}")

    base_name = filename.replace('.toml', '')
    results = {
        'filename': filename,
        'original_hash': '',
        'after_first_toml_hash': '',
        'after_second_toml_hash': '',
        'after_third_toml_hash': '',
        'after_first_readme_hash': '',
        'after_second_readme_hash': '',
        'after_third_readme_hash': '',
        'toml_changes': [],
        'readme_changes': []
    }

    # 原始文件路径
    original_toml = os.path.join(TEST_DIR, filename)

    # 记录原始哈希
    results['original_hash'] = get_file_hash(original_toml)
    original_toml_content = read_file_content(original_toml)
    print(f"原始 TOML 哈希: {results['original_hash']}")

    # 第一轮: TOML -> README
    readme_1 = os.path.join(TEST_DIR, f"{base_name}_1_README.md")
    toml_to_readme(original_toml, readme_1)
    readme_1_hash = get_file_hash(readme_1)
    results['after_first_readme_hash'] = readme_1_hash
    print(f"第一轮 README 哈希: {readme_1_hash}")

    # 第一轮: README -> TOML
    toml_1 = os.path.join(TEST_DIR, f"{base_name}_1.toml")
    readme_to_toml(readme_1, toml_1)
    toml_1_hash = get_file_hash(toml_1)
    results['after_first_toml_hash'] = toml_1_hash
    print(f"第一轮 TOML 哈希: {toml_1_hash}")

    # 第二轮: TOML -> README
    readme_2 = os.path.join(TEST_DIR, f"{base_name}_2_README.md")
    toml_to_readme(toml_1, readme_2)
    readme_2_hash = get_file_hash(readme_2)
    results['after_second_readme_hash'] = readme_2_hash
    print(f"第二轮 README 哈希: {readme_2_hash}")

    # 第二轮: README -> TOML
    toml_2 = os.path.join(TEST_DIR, f"{base_name}_2.toml")
    readme_to_toml(readme_2, toml_2)
    toml_2_hash = get_file_hash(toml_2)
    results['after_second_toml_hash'] = toml_2_hash
    print(f"第二轮 TOML 哈希: {toml_2_hash}")

    # 第三轮: TOML -> README
    readme_3 = os.path.join(TEST_DIR, f"{base_name}_3_README.md")
    toml_to_readme(toml_2, readme_3)
    readme_3_hash = get_file_hash(readme_3)
    results['after_third_readme_hash'] = readme_3_hash
    print(f"第三轮 README 哈希: {readme_3_hash}")

    # 第三轮: README -> TOML
    toml_3 = os.path.join(TEST_DIR, f"{base_name}_3.toml")
    readme_to_toml(readme_3, toml_3)
    toml_3_hash = get_file_hash(toml_3)
    results['after_third_toml_hash'] = toml_3_hash
    print(f"第三轮 TOML 哈希: {toml_3_hash}")

    # 对比 TOML 变化
    print(f"\nTOML 变化分析:")
    if toml_1_hash == toml_2_hash == toml_3_hash:
        print("  ✅ TOML 文件稳定，三轮转换后内容一致")
    else:
        print("  ⚠️  TOML 文件有变化:")
        # 对比原文件 vs 第一轮
        if toml_1_hash != get_file_hash(original_toml):
            diff = get_diff(original_toml_content, read_file_content(toml_1))
            results['toml_changes'].append(('original -> round1', diff))
            print(f"    原文件 -> 第一轮: 有差异")

        # 对比第一轮 vs 第二轮
        if toml_1_hash != toml_2_hash:
            diff = get_diff(read_file_content(toml_1), read_file_content(toml_2))
            results['toml_changes'].append(('round1 -> round2', diff))
            print(f"    第一轮 -> 第二轮: 有差异")

        # 对比第二轮 vs 第三轮
        if toml_2_hash != toml_3_hash:
            diff = get_diff(read_file_content(toml_2), read_file_content(toml_3))
            results['toml_changes'].append(('round2 -> round3', diff))
            print(f"    第二轮 -> 第三轮: 有差异")

    # 对比 README 变化
    print(f"\nREADME 变化分析:")
    if readme_1_hash == readme_2_hash == readme_3_hash:
        print("  ✅ README 文件稳定，三轮转换后内容一致")
    else:
        print("  ⚠️  README 文件有变化:")
        # 对比第一轮 vs 第二轮
        if readme_1_hash != readme_2_hash:
            diff = get_diff(read_file_content(readme_1), read_file_content(readme_2))
            results['readme_changes'].append(('round1 -> round2', diff))
            print(f"    第一轮 -> 第二轮: 有差异")

        # 对比第二轮 vs 第三轮
        if readme_2_hash != readme_3_hash:
            diff = get_diff(read_file_content(readme_2), read_file_content(readme_3))
            results['readme_changes'].append(('round2 -> round3', diff))
            print(f"    第二轮 -> 第三轮: 有差异")

    return results

def get_diff(content1: str, content2: str) -> list:
    """获取两个文本的差异"""
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines1, lines2, lineterm=''))
    return diff

def save_diff_report(filename: str, results: dict, report_dir: str):
    """保存差异报告"""
    report_path = os.path.join(report_dir, f"{filename}_diff_report.txt")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"转换测试报告: {filename}\n")
        f.write(f"{'='*60}\n\n")

        f.write("哈希值对比:\n")
        f.write(f"  原始 TOML: {results['original_hash']}\n")
        f.write(f"  第一轮 TOML: {results['after_first_toml_hash']}\n")
        f.write(f"  第二轮 TOML: {results['after_second_toml_hash']}\n")
        f.write(f"  第三轮 TOML: {results['after_third_toml_hash']}\n")
        f.write(f"  第一轮 README: {results['after_first_readme_hash']}\n")
        f.write(f"  第二轮 README: {results['after_second_readme_hash']}\n")
        f.write(f"  第三轮 README: {results['after_third_readme_hash']}\n\n")

        if results['toml_changes']:
            f.write("\nTOML 变化详情:\n")
            f.write(f"{'='*60}\n")
            for stage, diff in results['toml_changes']:
                f.write(f"\n--- {stage} ---\n")
                f.writelines(diff)

        if results['readme_changes']:
            f.write("\nREADME 变化详情:\n")
            f.write(f"{'='*60}\n")
            for stage, diff in results['readme_changes']:
                f.write(f"\n--- {stage} ---\n")
                f.writelines(diff)

        if not results['toml_changes'] and not results['readme_changes']:
            f.write("\n✅ 所有转换稳定，无差异！\n")

def generate_summary_report(all_results: list, report_dir: str):
    """生成汇总报告"""
    summary_path = os.path.join(report_dir, "SUMMARY_REPORT.txt")

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("转换稳定性测试汇总报告\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"测试文件数: {len(all_results)}\n")
        f.write(f"测试日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        stable_toml = 0
        stable_readme = 0

        for result in all_results:
            toml_stable = (result['after_first_toml_hash'] ==
                           result['after_second_toml_hash'] ==
                           result['after_third_toml_hash'])
            readme_stable = (result['after_first_readme_hash'] ==
                            result['after_second_readme_hash'] ==
                            result['after_third_readme_hash'])

            if toml_stable:
                stable_toml += 1
            if readme_stable:
                stable_readme += 1

            f.write(f"\n{result['filename']}:\n")
            f.write(f"  TOML 稳定: {'✅' if toml_stable else '❌'}\n")
            f.write(f"  README 稳定: {'✅' if readme_stable else '❌'}\n")

            if not toml_stable:
                f.write(f"  TOML 变化阶段: {', '.join([x[0] for x in result['toml_changes']])}\n")
            if not readme_stable:
                f.write(f"  README 变化阶段: {', '.join([x[0] for x in result['readme_changes']])}\n")

        f.write(f"\n{'='*60}\n")
        f.write(f"总体统计:\n")
        f.write(f"  TOML 稳定: {stable_toml}/{len(all_results)}\n")
        f.write(f"  README 稳定: {stable_readme}/{len(all_results)}\n")
        f.write(f"  完全稳定: {stable_toml if stable_toml == stable_readme else 0}/{len(all_results)}\n")

def main():
    print("="*60)
    print("TOML <-> README 转换稳定性测试")
    print("="*60)
    print()

    # 随机选择 5 个文件
    selected_files = copy_random_tomls(5)
    if not selected_files:
        print("❌ 没有可测试的文件")
        return

    # 创建报告目录
    report_dir = os.path.join(TEST_DIR, "diff_reports")
    os.makedirs(report_dir, exist_ok=True)

    # 测试每个文件
    all_results = []
    for filename in selected_files:
        try:
            results = test_single_file(filename)
            all_results.append(results)

            # 保存详细差异报告
            if results['toml_changes'] or results['readme_changes']:
                save_diff_report(filename.replace('.toml', ''), results, report_dir)
        except Exception as e:
            print(f"\n❌ 测试 {filename} 时出错: {e}")
            import traceback
            traceback.print_exc()

    # 生成汇总报告
    generate_summary_report(all_results, report_dir)

    print(f"\n{'='*60}")
    print("测试完成!")
    print(f"{'='*60}")
    print(f"测试文件保存在: {os.path.abspath(TEST_DIR)}")
    print(f"差异报告保存在: {os.path.abspath(report_dir)}")
    print(f"\n💡 提示: 查看汇总报告了解整体稳定性")

if __name__ == "__main__":
    main()
