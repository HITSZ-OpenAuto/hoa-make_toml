#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用GitHub API将本地文件上传到对应的仓库，并创建PR
- 删除旧文件：仓库名.toml/.yaml, readme.toml/.yaml
- 上传新文件：对应的.toml和README.md
不需要clone仓库
"""

import os
import json
import base64
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests

class GitHubAPIPusher:
    def __init__(self, github_token: str, org: str = "HITSZ-OpenAuto"):
        """
        初始化GitHub API推送器
        
        Args:
            github_token: GitHub个人访问令牌
            org: GitHub组织名称
        """
        self.token = github_token
        self.org = org
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
    def _api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            timeout = 15
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            # 如果是 404/422，视为不存在/无法处理
            if response.status_code in [404, 422]:
                return None

            # 其他非 2xx 抛出异常
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.Timeout:
            print(f"API 请求超时: {method} {url}")
            return None
        except requests.exceptions.RequestException as e:
            # 其他错误才输出日志
            print(f"API请求失败: {e}")
            return None

    
    def _get_file_content(self, repo: str, path: str) -> Optional[Dict[str, Any]]:
        """获取仓库中的文件信息"""
        return self._get_file_content_owner(repo, path, owner=self.org)

    def _get_file_content_owner(self, repo: str, path: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        return self._api_request("GET", endpoint)
    
    def _delete_file(self, repo: str, path: str, commit_message: str) -> bool:
        """删除仓库中的文件"""
        file_info = self._get_file_content_owner(repo, path, owner=self.org)
        if not file_info:
            return False
        endpoint = f"/repos/{self.org}/{repo}/contents/{path}"
        data = {
            "message": commit_message,
            "sha": file_info.get("sha")
        }
        result = self._api_request("DELETE", endpoint, data)
        return result is not None

    def _delete_file_owner(self, repo: str, path: str, commit_message: str, owner: Optional[str] = None) -> bool:
        owner = owner or self.org
        file_info = self._get_file_content_owner(repo, path, owner=owner)
        if not file_info:
            return False
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        data = {
            "message": commit_message,
            "sha": file_info.get("sha")
        }
        result = self._api_request("DELETE", endpoint, data)
        return result is not None
    
    def _create_or_update_file(
        self, 
        repo: str, 
        path: str, 
        content: str, 
        commit_message: str,
        branch: str = "main",
        owner: Optional[str] = None
    ) -> bool:
        """创建或更新仓库中的文件"""
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"

        # 检查文件是否已存在（在指定分支上）
        file_info = self._get_file_content_owner(repo, path, owner=owner)
        sha = file_info.get("sha") if file_info else None
        
        # 编码内容为base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch
        }
        if sha:
            data["sha"] = sha  # 必须提供SHA来更新现有文件
        
        try:
            result = self._api_request("PUT", endpoint, data)
            return result is not None
        except Exception:
            return False
    
    def _get_repo_info(self, repo: str) -> Optional[Dict[str, Any]]:
        """获取仓库信息，包括默认分支"""
        return self._get_repo_info_owner(repo, owner=self.org)

    def _get_repo_info_owner(self, repo: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}"
        return self._api_request("GET", endpoint)
    
    def _get_default_branch(self, repo: str) -> str:
        """获取仓库的默认分支名"""
        repo_info = self._get_repo_info_owner(repo, owner=self.org)
        if repo_info and "default_branch" in repo_info:
            return repo_info["default_branch"]
        return "main"  # 默认fallback
    
    def _get_branch_ref(self, repo: str, branch: str = "main") -> Optional[Dict[str, Any]]:
        """获取分支的最新commit SHA"""
        return self._get_branch_ref_owner(repo, branch=branch, owner=self.org)

    def _get_branch_ref_owner(self, repo: str, branch: str = "main", owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}/git/refs/heads/{branch}"
        return self._api_request("GET", endpoint)
    
    def _create_branch(self, repo: str, new_branch: str, from_branch: Optional[str] = None) -> bool:
        """创建新分支"""
        # 如果没有指定源分支，获取默认分支
        if not from_branch:
            from_branch = self._get_default_branch(repo)
        
        # 获取源分支的最新commit SHA
        branch_ref = self._get_branch_ref_owner(repo, from_branch, owner=self.org)
        if not branch_ref or "object" not in branch_ref:
            return False
        
        sha = branch_ref["object"].get("sha")
        if not sha:
            return False
        
        # 创建新分支
        endpoint = f"/repos/{self.org}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{new_branch}",
            "sha": sha
        }
        result = self._api_request("POST", endpoint, data)
        return result is not None

    def _create_branch_owner(self, repo: str, new_branch: str, from_branch: Optional[str] = None, owner: Optional[str] = None) -> bool:
        owner = owner or self.org
        if not from_branch:
            # get default branch from upstream owner if necessary
            from_branch = self._get_repo_info_owner(repo, owner=self.org).get("default_branch", "main")

        # try to get ref sha from owner (may be upstream or fork)
        branch_ref = self._get_branch_ref_owner(repo, from_branch, owner=owner)
        if not branch_ref or "object" not in branch_ref:
            return False

        sha = branch_ref["object"].get("sha")
        if not sha:
            return False

        endpoint = f"/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{new_branch}",
            "sha": sha
        }
        result = self._api_request("POST", endpoint, data)
        return result is not None

    def _create_fork(self, repo: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}/forks"
        return self._api_request("POST", endpoint)

    def _get_authenticated_user(self) -> Optional[Dict[str, Any]]:
        endpoint = "/user"
        return self._api_request("GET", endpoint)
    
    def _create_pr(
        self,
        repo: str,
        head: str,
        base: str,
        title: str,
        description: str,
        owner: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """创建拉取请求

        head should be in form 'owner:branch' or just 'branch' when owner==upstream
        owner param indicates the upstream repo owner where PR is created
        """
        owner = owner or self.org
        endpoint = f"/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": description,
            "head": head,
            "base": base
        }
        return self._api_request("POST", endpoint, data)
    
    def push_course(
        self,
        course_code: str,
        repo_type: str,
        local_toml_path: str,
        local_readme_path: str
    ) -> bool:
        """
        推送课程文件到GitHub仓库
        
        Args:
            course_code: 课程代码（如AUTO1001）
            repo_type: 仓库类型（normal或multi-project）
            local_toml_path: 本地TOML文件路径
            local_readme_path: 本地README文件路径
        
        Returns:
            是否成功
        """
        print(f"\n处理仓库: {course_code}")
        
        repo = course_code
        branch_name = f"auto/update-{course_code.lower()}"
        
        try:
            # 第0步：验证仓库存在
            print(f"  [0/5] 验证仓库...")
            repo_info = self._get_repo_info(repo)
            if not repo_info:
                print(f"    [ERROR] 仓库不存在或无权限访问: {self.org}/{repo}")
                return False
            default_branch = repo_info.get("default_branch", "main")
            print(f"    [OK] 仓库验证成功 (默认分支: {default_branch})")
            
            # 第1步：在上游尝试创建分支；失败则尝试 Fork -> 在 Fork 创建分支
            print(f"  [1/5] 创建分支: {branch_name}...")
            upstream_owner = self.org
            upload_owner = upstream_owner
            created_branch = False

            if self._create_branch_owner(repo, branch_name, default_branch, owner=upstream_owner):
                print(f"    [OK] 分支已在上游创建")
                created_branch = True
                upload_owner = upstream_owner
            else:
                print(f"    [WARN] 在上游创建分支失败，尝试 Fork 并在 Fork 上创建分支...")
                # 尝试 Fork 仓库到当前用户
                fork = self._create_fork(repo, owner=upstream_owner)
                if not fork:
                    print(f"    [WARN] Fork 操作失败或不可用，将尝试直接在默认分支上提交（若无权限则失败）")
                    upload_owner = upstream_owner
                else:
                    # 获取当前认证用户
                    me = self._get_authenticated_user()
                    fork_owner = me.get("login") if me else None
                    if not fork_owner:
                        print(f"    [WARN] 无法获取当前用户信息，放弃 Fork 路径")
                        upload_owner = upstream_owner
                    else:
                        # 等待 fork 出现
                        for _ in range(10):
                            fork_info = self._get_repo_info_owner(repo, owner=fork_owner)
                            if fork_info:
                                break
                            time.sleep(1)

                        # 尝试在 fork 创建分支（基于上游默认分支的 sha）
                        upstream_ref = self._get_branch_ref_owner(repo, default_branch, owner=upstream_owner)
                        upstream_sha = None
                        if upstream_ref and "object" in upstream_ref:
                            upstream_sha = upstream_ref["object"].get("sha")

                        created_in_fork = False
                        if upstream_sha:
                            endpoint = f"/repos/{fork_owner}/{repo}/git/refs"
                            data = {"ref": f"refs/heads/{branch_name}", "sha": upstream_sha}
                            res = self._api_request("POST", endpoint, data)
                            if res:
                                created_in_fork = True

                        if created_in_fork:
                            print(f"    [OK] Fork 上的分支已创建: {fork_owner}/{branch_name}")
                            upload_owner = fork_owner
                            created_branch = True
                        else:
                            print(f"    [WARN] 在 Fork 上创建分支失败，之后会尝试在默认分支提交（或在 Fork 上直接修改默认分支）")
                            upload_owner = fork_owner
            
            # 第2步：删除旧文件（在 upload_owner 下操作）
            old_files = [
                f"{course_code}.toml",
                f"{course_code}.yaml",
                "readme.toml",
                "readme.yaml"
            ]

            print(f"  [2/5] 删除旧文件 (owner={upload_owner})...")
            for old_file in old_files:
                print(f"      尝试删除: {old_file}...", end="")
                try:
                    if self._delete_file_owner(repo, old_file, f"Remove {old_file}", owner=upload_owner):
                        print(" [OK]")
                    else:
                        print(" [SKIP]")
                except Exception:
                    print(" [SKIP]")
            
            # 第3步：读取本地文件
            print(f"  [3/5] 读取本地文件...")
            
            if not Path(local_toml_path).exists():
                print(f"    [ERROR] TOML文件不存在: {local_toml_path}")
                return False
            
            if not Path(local_readme_path).exists():
                print(f"    [ERROR] README文件不存在: {local_readme_path}")
                return False
            
            with open(local_toml_path, 'r', encoding='utf-8') as f:
                toml_content = f.read()
            
            with open(local_readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            print(f"    [OK] TOML文件: {len(toml_content)} 字节")
            print(f"    [OK] README文件: {len(readme_content)} 字节")
            
            # 第4步：上传文件到分支或main分支
            print(f"  [4/5] 上传文件 (owner={upload_owner})...")

            # 决定上传分支：若成功创建分支则上传到 branch_name，否则上传到默认分支
            if created_branch:
                upload_branch = branch_name
            else:
                upload_branch = default_branch

            if not self._create_or_update_file(repo, "readme.toml", toml_content,
                                               f"Update readme.toml for {course_code}", upload_branch,
                                               owner=upload_owner):
                if upload_branch != default_branch:
                    print(f"    [WARN] 上传到{upload_branch}失败，尝试上传到{default_branch}...")
                    upload_branch = default_branch
                    if not self._create_or_update_file(repo, "readme.toml", toml_content,
                                                       f"Update readme.toml for {course_code}", upload_branch,
                                                       owner=upload_owner):
                        print(f"    [ERROR] 上传TOML文件失败")
                        return False
                else:
                    print(f"    [ERROR] 上传TOML文件失败")
                    return False
            print(f"    [OK] readme.toml 已上传 ({upload_owner}:{upload_branch})")

            if not self._create_or_update_file(repo, "README.md", readme_content,
                                               f"Update README.md for {course_code}", upload_branch,
                                               owner=upload_owner):
                print(f"    [ERROR] 上传README文件失败")
                return False
            print(f"    [OK] README.md 已上传 ({upload_owner}:{upload_branch})")
            
            # 第5步：创建PR（如果是在分支上上传）
            print(f"  [5/5] 创建Pull Request...")
            
            # 第5步：创建PR（若在非默认分支/在 Fork 上创建）
            print(f"  [5/5] 创建Pull Request...")

            if upload_owner == upstream_owner and upload_branch == default_branch:
                print(f"    [INFO] 文件已上传到上游默认分支 {default_branch}，跳过PR创建")
                return True

            pr_title = f"docs: Update {course_code} resources"
            pr_body = f"""自动更新 {course_code} 课程资源

- 更新 readme.toml
- 更新 README.md

本PR由自动化工具生成。"""

            # 如果是 Fork 提交，则 head 需要写成 owner:branch
            if upload_owner != upstream_owner:
                head = f"{upload_owner}:{branch_name if created_branch else upload_branch}"
                pr = self._create_pr(repo, head, default_branch, pr_title, pr_body, owner=upstream_owner)
            else:
                # 上游仓库自身的分支
                head = branch_name if created_branch else upload_branch
                pr = self._create_pr(repo, head, default_branch, pr_title, pr_body, owner=upstream_owner)

            if pr:
                pr_url = pr.get("html_url", "")
                pr_number = pr.get("number", "")
                print(f"    [OK] PR已创建: #{pr_number}")
                print(f"      Link: {pr_url}")
                return True
            else:
                print(f"    [WARN] PR创建失败（可能分支已有待审PR或权限问题）")
                return True
                
        except Exception as e:
            print(f"    [ERROR] 处理失败: {e}")
            return False


def determine_repo_type(course_code: str, readme_output_path: Path) -> str:
    """根据readme.toml内容判断仓库类型"""
    readme_toml = readme_output_path / course_code / "readme.toml"
    
    if not readme_toml.exists():
        return "unknown"
    
    try:
        with open(readme_toml, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'repo_type = "normal"' in content:
                return "normal"
            elif 'repo_type = "multi-project"' in content:
                return "multi-project"
    except:
        pass
    
    return "unknown"


def main():
    """主函数"""
    # 获取配置
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ 错误: 请设置 GITHUB_TOKEN 环境变量")
        sys.exit(1)
    
    # 本地输出目录
    readme_output = Path(__file__).parent / "readme_output"
    
    if not readme_output.exists():
        print(f"❌ 错误: readme_output目录不存在: {readme_output}")
        sys.exit(1)
    
    # 初始化API推送器
    pusher = GitHubAPIPusher(github_token)
    
    # 收集所有课程
    courses = sorted([d.name for d in readme_output.iterdir() if d.is_dir()])
    
    print("=" * 60)
    print("GitHub API 上传工具")
    print("=" * 60)
    print(f"找到 {len(courses)} 个课程仓库")
    print()
    
    stats = {
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "normal": 0,
        "multi-project": 0,
        "unknown": 0
    }
    
    # 处理每个课程
    for course_code in courses:
        course_dir = readme_output / course_code
        repo_type = determine_repo_type(course_code, readme_output)
        
        if repo_type == "unknown":
            print(f"⚠️  {course_code}: 无法判断仓库类型，跳过")
            stats["skipped"] += 1
            continue
        
        toml_path = course_dir / "readme.toml"
        readme_path = course_dir / "README.md"
        
        if pusher.push_course(course_code, repo_type, str(toml_path), str(readme_path)):
            stats["success"] += 1
            stats[repo_type] += 1
        else:
            stats["failed"] += 1
    
    # 打印统计信息
    print()
    print("=" * 60)
    print("处理完成! 统计信息:")
    print("=" * 60)
    print(f"总课程数:     {len(courses)}")
    print(f"成功上传:     {stats['success']}")
    print(f"已跳过:       {stats['skipped']}")
    print(f"处理失败:     {stats['failed']}")
    print()
    print(f"  Normal类型:       {stats['normal']}")
    print(f"  Multi-project类型: {stats['multi-project']}")
    print()


if __name__ == "__main__":
    main()
