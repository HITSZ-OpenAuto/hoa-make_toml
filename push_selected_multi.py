from pathlib import Path
import os
import sys

from push_to_github import GitHubAPIPusher

if __name__ == '__main__':
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print('请先设置 GITHUB_TOKEN 环境变量')
        sys.exit(1)

    pusher = GitHubAPIPusher(github_token)
    base = Path(__file__).parent / 'readme_output'
    targets = ['CrossSpecialty', 'EE30XX', 'GeneralKnowledge', 'MOOC', 'PE100X']

    for t in targets:
        toml = base / t / 'readme.toml'
        readme = base / t / 'README.md'
        print('----')
        print(f'处理 {t}')
        if not toml.exists() or not readme.exists():
            print('  本地文件不存在，跳过')
            continue
        ok = pusher.push_course(t, 'multi-project', str(toml), str(readme))
        print(f'  结果: {ok}')
