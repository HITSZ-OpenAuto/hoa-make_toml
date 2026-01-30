# GitHub 自动化工具使用指南

## 概述

此工具集用于自动化管理HITSZ-OpenAuto组织下的所有课程仓库，包括：
1. **上传本地生成的文件到GitHub** - 使用PR方式
2. **为仓库生成自动化工作流** - 在readme.toml更新时自动格式化和更新README.md

## 工具清单

### 1. `push_to_github.py` - GitHub API上传工具

**功能**：将本地生成的readme.toml和README.md上传到对应的GitHub仓库

**工作流程**：
1. 删除仓库中的旧文件：`{课程代码}.toml`, `{课程代码}.yaml`, `readme.toml`, `readme.yaml`
2. 上传本地的新文件到自动创建的分支
3. 创建Pull Request以供审核

**使用方法**：

```bash
# 设置GitHub令牌
export GITHUB_TOKEN="your_github_token_here"

# 运行上传脚本
python push_to_github.py
```

**输出示例**：
```
处理仓库: AUTO1001
  [1/4] 删除旧文件...
      尝试删除: AUTO1001.toml... (不存在或无需删除)
      尝试删除: AUTO1001.yaml... (不存在或无需删除)
      尝试删除: readme.toml... ✓
      尝试删除: readme.yaml... (不存在或无需删除)
  [2/4] 读取本地文件...
      ✓ TOML文件: 2345 字节
      ✓ README文件: 15234 字节
  [3/4] 上传文件到分支: auto/update-auto1001...
      ✓ readme.toml 已上传
      ✓ README.md 已上传
  [4/4] 创建Pull Request...
      ✓ PR已创建: #42
      链接: https://github.com/HITSZ-OpenAuto/AUTO1001/pull/42
```

**必要条件**：
- GitHub Personal Access Token (需要 repo 权限)
- 对所有目标仓库的push权限

---

### 2. `generate_workflows.py` - 工作流生成工具

**功能**：生成GitHub工作流模板文件

**输出文件**：
- `workflow_templates/format-readme-normal.yml` - Normal类型仓库工作流
- `workflow_templates/format-readme-multi-project.yml` - Multi-project类型仓库工作流

**使用方法**：

```bash
python generate_workflows.py
```

**工作流说明**：

#### Normal类型仓库工作流 (`format-readme-normal.yml`)

触发条件：PR中修改了 `readme.toml`

执行步骤：
1. Checkout代码
2. 设置Python 3.10
3. 使用本地嵌入的脚本格式化 `readme.toml`
4. 使用本地嵌入的脚本将 `readme.toml` 转换为 `README.md`
5. 自动提交更改到PR分支

支持的课程字段（11个）：
- `description` - 课程描述
- `lecturers` - 讲师评价 (嵌套结构)
- `textbooks` - 教材
- `online_resources` - 线上资源
- `course` - 课程资源
- `homework` - 作业
- `exam` - 考试
- `lab` - 实验
- `advice` - 学习建议
- `schedule` - 课程日程
- `related_links` - 相关链接

#### Multi-project类型仓库工作流 (`format-readme-multi-project.yml`)

触发条件：PR中修改了 `readme.toml`

执行步骤：
1. Checkout代码
2. 设置Python 3.10
3. 格式化 `readme.toml`
4. 将 `readme.toml` 转换为 `README.md`（显示多个课程列表）
5. 自动提交更改到PR分支

---

### 3. `deploy_workflows.py` - 工作流部署工具

**功能**：使用GitHub API自动为所有仓库部署工作流文件

**使用方法**：

```bash
# 显示摘要（不实际部署）
python deploy_workflows.py --dry-run

# 显示工作流模板内容
python deploy_workflows.py --show-templates

# 实际部署工作流（需要GITHUB_TOKEN）
export GITHUB_TOKEN="your_github_token_here"
python deploy_workflows.py
```

**工作原理**：
- 自动检测每个仓库的类型（normal或multi-project）
- 选择对应的工作流模板
- 通过GitHub API上传到 `.github/workflows/format-readme.yml`
- 如果文件已存在，则更新现有文件

---

## 完整工作流程

### 第一步：生成本地文件

```bash
# 使用现有脚本生成readme.toml和README.md
python format_normal_repo_toml_standard.py
python convert_normal_repo_toml_to_readme.py

python format_multi_project_toml_standard.py
python convert_multi_project_toml_to_readme.py
```

### 第二步：上传到GitHub

```bash
# 设置令牌
export GITHUB_TOKEN="your_github_token_here"

# 生成工作流模板
python generate_workflows.py

# 上传文件并创建PR
python push_to_github.py
```

### 第三步：部署工作流到仓库（可选）

```bash
# 部署工作流文件
python deploy_workflows.py

# 或先查看摘要
python deploy_workflows.py --dry-run
```

### 第四步：手动合并PR（推荐）

1. 在GitHub上审查每个PR
2. 确保生成的README.md格式正确
3. 手动合并PR
4. 一旦readme.toml被更新，工作流将自动运行

---

## GitHub Token 获取方法

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置权限：
   - ✓ repo（完全访问私有和公有仓库）
   - ✓ workflow（GitHub Actions工作流权限）
   - ✓ user（用户信息）
4. 生成token并妥善保管

---

## 常见问题

### Q: 为什么PR创建失败？
A: 检查以下内容：
- GITHUB_TOKEN是否正确设置
- 令牌是否有 `repo` 权限
- 目标仓库是否存在
- 网络连接是否正常

### Q: 工作流文件多久会起作用？
A: 一旦提交到main分支，工作流就可以在对应事件触发时运行。首次运行可能需要GitHub同步配置（通常不超过1分钟）。

### Q: 如何修改工作流逻辑？
A: 修改 `format-readme-normal.yml` 或 `format-readme-multi-project.yml` 中的Python代码部分，然后重新运行 `deploy_workflows.py` 更新所有仓库。

### Q: 能否指定只处理特定仓库？
A: 目前脚本处理所有仓库。如需处理特定仓库，可以：
1. 手动修改 `readme_output` 目录，只保留需要的课程文件夹
2. 或修改脚本添加过滤逻辑

---

## 文件依赖关系

```
push_to_github.py
  ├─ 读取: readme_output/{course_code}/readme.toml
  ├─ 读取: readme_output/{course_code}/README.md
  └─ 上传到: https://github.com/HITSZ-OpenAuto/{course_code}/

generate_workflows.py
  ├─ 读取: readme_output/{course_code}/readme.toml (仅判断类型)
  └─ 生成: workflow_templates/format-readme-*.yml

deploy_workflows.py
  ├─ 读取: workflow_templates/format-readme-*.yml
  ├─ 读取: readme_output/{course_code}/readme.toml (仅判断类型)
  └─ 上传到: https://github.com/HITSZ-OpenAuto/{course_code}/.github/workflows/
```

---

## 脚本权限说明

### 必要的GitHub权限

| 权限 | push_to_github | deploy_workflows | 说明 |
|------|---|---|---|
| repo:read | ✓ | ✓ | 读取仓库信息 |
| repo:write | ✓ | ✓ | 创建/更新文件和PR |
| workflow | | ✓ | 部署GitHub Actions工作流 |

### 操作系统权限

- 读取：`readme_output/` 目录
- 写入：`workflow_templates/` 目录（自动创建）

---

## 日志和调试

所有脚本都提供详细的日志输出。如遇到问题：

1. 查看完整的输出日志
2. 检查GITHUB_TOKEN是否正确
3. 尝试 `--dry-run` 参数测试逻辑
4. 检查网络连接

---

## 安全建议

⚠️ **重要**：
1. 不要在代码中硬编码GITHUB_TOKEN
2. 使用环境变量或安全的密钥管理系统
3. 定期轮换token
4. 使用最小权限原则（只授予必要的权限）
5. 在CI/CD系统中使用专用的bot账户和token

---

## 版本信息

- Python: 3.10+
- 依赖库：requests, tomli
- GitHub API: v3

---

## 更新日志

### v1.0 (2024-01-31)
- 初始版本
- 支持normal和multi-project两种仓库类型
- 通过API上传文件和创建PR
- 自动生成和部署GitHub工作流
- 两种类型的工作流分别处理

