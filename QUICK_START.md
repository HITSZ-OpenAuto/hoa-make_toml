# 快速使用指南

## 一句话概括

将本地生成的课程资源文件上传到GitHub并自动部署工作流，使得每次readme.toml更新都能自动格式化和更新README.md。

## 三个核心脚本

### 1️⃣ `push_to_github.py` - 上传文件到GitHub

**功能**: 将本地的readme.toml和README.md作为PR上传到对应的GitHub仓库

**运行命令**:
```bash
export GITHUB_TOKEN="your_token_here"
python push_to_github.py
```

**做了什么**:
- 删除旧文件（course_code.toml/.yaml, readme.toml/.yaml）
- 上传新的readme.toml和README.md
- 创建PR供审核
- 输出PR链接

---

### 2️⃣ `generate_workflows.py` - 生成工作流模板

**功能**: 生成两种类型仓库的GitHub工作流模板文件

**运行命令**:
```bash
python generate_workflows.py
```

**生成文件**:
- `workflow_templates/format-readme-normal.yml` - Normal类型
- `workflow_templates/format-readme-multi-project.yml` - Multi-project类型

**工作流的作用**:
- 监听readme.toml的更新（在PR中）
- 自动运行格式化脚本
- 自动运行README生成脚本
- 自动提交结果到PR分支

---

### 3️⃣ `deploy_workflows.py` - 部署工作流到所有仓库

**功能**: 使用GitHub API将工作流文件自动上传到所有仓库

**运行命令**:
```bash
export GITHUB_TOKEN="your_token_here"
python deploy_workflows.py
```

**或者只查看摘要**:
```bash
python deploy_workflows.py --dry-run
```

**或者查看工作流内容**:
```bash
python deploy_workflows.py --show-templates
```

---

## 完整执行流程（推荐）

### 方式1：一键执行所有操作

```bash
export GITHUB_TOKEN="your_token_here"
python github_automation.py --all
```

### 方式2：分步执行

```bash
# 第1步：生成工作流模板
python generate_workflows.py

# 第2步：上传文件到GitHub（创建PR）
export GITHUB_TOKEN="your_token_here"
python push_to_github.py

# 第3步：部署工作流到所有仓库
python deploy_workflows.py
```

### 方式3：交互式菜单

```bash
export GITHUB_TOKEN="your_token_here"
python github_automation.py
```

然后选择要执行的操作。

---

## GitHub Token 获取（3分钟）

1. 打开 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 输入名称，例如：`OpenAuto-Script`
4. 勾选权限：
   - ✓ repo（访问仓库）
   - ✓ workflow（访问GitHub Actions）
5. 点击 "Generate token"
6. **复制token**（只显示一次！）
7. 设置环境变量：

```bash
# PowerShell
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# CMD
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Bash/Linux/Mac
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## 预期输出示例

### push_to_github.py
```
处理仓库: AUTO1001
  [1/4] 删除旧文件...
      尝试删除: readme.toml... ✓
  [2/4] 读取本地文件...
      ✓ TOML文件: 2345 字节
      ✓ README文件: 15234 字节
  [3/4] 上传文件到分支...
      ✓ readme.toml 已上传
      ✓ README.md 已上传
  [4/4] 创建Pull Request...
      ✓ PR已创建: #42
      链接: https://github.com/HITSZ-OpenAuto/AUTO1001/pull/42
```

### deploy_workflows.py
```
AUTO1001             (normal         )... ✓
AUTO2001             (normal         )... ✓
COMP2001             (normal         )... ✓
CrossSpecialty       (multi-project  )... ✓
```

---

## 常见问题

**Q: 脚本失败了，怎么办？**  
A: 检查：
1. GITHUB_TOKEN是否正确设置
2. Token是否有repo权限
3. 网络连接是否正常
4. readme_output目录中是否有文件

**Q: 工作流多久会起效？**  
A: 部署后通常立即生效，首次运行在下次readme.toml被修改时触发。

**Q: 可以修改工作流吗？**  
A: 可以。修改workflow_templates目录中的YAML文件，然后重新运行deploy_workflows.py。

**Q: 工作流是做什么的？**  
A: 监听readme.toml的变化，自动执行格式化和README生成，保证数据和显示一致。

**Q: 需要clone仓库吗？**  
A: 不需要！所有操作都通过GitHub API完成，不需要clone任何仓库。

---

## 目录结构

```
scripts/
├── push_to_github.py              # 上传文件脚本
├── generate_workflows.py          # 生成工作流脚本
├── deploy_workflows.py            # 部署工作流脚本
├── github_automation.py           # 一键执行脚本
├── GITHUB_AUTOMATION_GUIDE.md     # 详细指南
├── QUICK_START.md                 # 本文件
├── workflow_templates/            # 工作流模板目录
│   ├── format-readme-normal.yml
│   └── format-readme-multi-project.yml
├── readme_output/                 # 本地生成的文件
│   ├── AUTO1001/
│   │   ├── readme.toml
│   │   └── README.md
│   ├── COMP2001/
│   ├── CrossSpecialty/
│   └── ...
└── (其他脚本文件)
```

---

## 工作流原理（简化版）

当有人在GitHub上修改readme.toml并创建PR时：

```
修改readme.toml
       ↓
GitHub Actions工作流触发
       ↓
1. 格式化readme.toml
2. 从readme.toml生成README.md
3. 自动提交到PR分支
       ↓
开发者审核并合并PR
       ↓
完成！数据和显示保持一致
```

---

## 监控和验证

### 查看工作流执行情况
- GitHub仓库 → Actions标签 → "Format and Update README"

### 查看最近的PR
- GitHub仓库 → Pull requests标签 → 搜索"auto/update"前缀的分支

### 验证工作流文件
```bash
# 查看部署的工作流内容
python deploy_workflows.py --show-templates
```

---

## 注意事项

⚠️ **重要**：
1. 妥善保管GITHUB_TOKEN，不要上传到仓库
2. Token只显示一次，丢失需要重新生成
3. 确保有对所有目标仓库的push权限
4. 第一次部署可能需要一些时间（取决于仓库数量）

---

## 获取帮助

```bash
# 查看脚本帮助
python push_to_github.py --help
python deploy_workflows.py --help
python github_automation.py --help

# 查看详细文档
cat GITHUB_AUTOMATION_GUIDE.md
```

---

祝你使用愉快！ 🎉

