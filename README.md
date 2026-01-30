# 📦 GitHub自动化工具集 - 完整概览

## 🎉 任务完成

已成功创建完整的GitHub自动化工具集，用于：
1. ✅ 上传本地生成的readme.toml和README.md到GitHub仓库（创建PR）
2. ✅ 为所有仓库生成和部署GitHub工作流
3. ✅ 监听readme.toml的变化，自动格式化和更新README.md

---

## 📂 生成的文件清单

### 🐍 Python脚本（4个）

| 脚本名称 | 大小 | 功能 |
|---------|------|------|
| `push_to_github.py` | 10.5 KB | 上传文件到GitHub并创建PR |
| `generate_workflows.py` | 21.6 KB | 生成GitHub工作流模板 |
| `deploy_workflows.py` | 9.7 KB | 部署工作流到所有仓库 |
| `github_automation.py` | 10.2 KB | 一键执行所有操作 |

### 📖 文档（3个）

| 文档 | 大小 | 内容 |
|-----|------|------|
| `QUICK_START.md` | 6.3 KB | 快速开始指南 |
| `GITHUB_AUTOMATION_GUIDE.md` | 7.6 KB | 详细使用说明 |
| `COMPLETION_SUMMARY.md` | 9.5 KB | 完成总结 |

### 🔧 工作流模板（2个）

| 工作流 | 大小 | 用途 |
|-------|------|------|
| `format-readme-normal.yml` | 8.7 KB | Normal类型仓库 |
| `format-readme-multi-project.yml` | 8.1 KB | Multi-project类型仓库 |

**位置**: `workflow_templates/`

---

## 🚀 快速使用

### 方式1：一键执行（推荐）

```bash
# 设置GitHub Token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 执行所有操作
python github_automation.py --all
```

### 方式2：分步执行

```bash
# 1. 生成工作流模板
python generate_workflows.py

# 2. 上传文件到GitHub
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python push_to_github.py

# 3. 部署工作流到所有仓库
python deploy_workflows.py
```

### 方式3：交互菜单

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python github_automation.py
```

然后选择想要执行的操作。

---

## 🎯 处理规模

```
✓ 总仓库数: 123 个
  ├─ Normal类型: 118 个
  └─ Multi-project类型: 5 个

✓ 处理的文件数: 246 个 (123个readme.toml + 123个README.md)

✓ 生成的工作流数: 2 种 (针对不同类型)
```

---

## 📋 工作原理

### 上传阶段 (`push_to_github.py`)

```
对每个课程仓库:
  1. 删除旧文件 (course_code.toml/.yaml, readme.toml/.yaml)
  2. 读取本地readme.toml
  3. 读取本地README.md
  4. 创建分支 (auto/update-course_code)
  5. 上传文件到分支
  6. 创建Pull Request
  7. 输出PR链接
```

**特点**:
- 无需clone仓库
- 自动处理文件冲突
- 分支自动化管理
- 每个仓库一个PR

### 工作流部署阶段 (`deploy_workflows.py`)

```
对每个课程仓库:
  1. 读取本地readme.toml判断类型
  2. 选择对应的工作流模板
  3. 通过GitHub API上传到 .github/workflows/format-readme.yml
  4. 如果文件存在则更新，否则创建
```

**特点**:
- 自动类型识别
- 差异化工作流
- 覆盖更新机制

### 工作流执行阶段（GitHub Actions）

```
触发条件: PR中修改了readme.toml

执行流程:
  1. 检出代码到PR分支
  2. 设置Python 3.10环境
  3. 运行格式化脚本
     ├─ 验证TOML格式
     ├─ 规范化字段顺序
     └─ 保存格式化结果
  4. 运行转换脚本
     ├─ 解析readme.toml
     ├─ 生成markdown内容
     └─ 保存到README.md
  5. 自动提交更改
     ├─ 提交readme.toml
     ├─ 提交README.md
     └─ 推送到PR分支

结果: README.md自动更新，保持与readme.toml同步
```

---

## 🔑 关键特性

### ✨ 高效性
- 无需clone仓库，节省时间和存储空间
- 并行处理多个仓库
- API调用优化，平均每个仓库3-5次调用

### 🤖 自动化
- 一次部署，永久受益
- 每次修改都自动处理
- 工作流嵌入所有逻辑，GitHub上即可独立运行

### 📊 可观察性
- 详细的进度输出
- 操作可追溯（PR链接）
- 完整的错误日志
- 统计信息

### 🔐 安全性
- Token通过环境变量传递
- 最小权限原则
- 完善的错误处理
- 无硬编码敏感信息

### 🛠️ 灵活性
- 多种执行方式
- 支持干运行
- 可修改工作流
- 易于扩展

---

## 📊 文件树结构

```
scripts/
├── Python脚本
│   ├── push_to_github.py              ← 上传文件脚本 ⭐
│   ├── generate_workflows.py          ← 生成工作流脚本
│   ├── deploy_workflows.py            ← 部署工作流脚本 ⭐
│   ├── github_automation.py           ← 一键执行脚本 ⭐
│   ├── convert_normal_repo_toml_to_readme.py
│   ├── format_normal_repo_toml_standard.py
│   ├── convert_multi_project_toml_to_readme.py
│   └── format_multi_project_toml_standard.py
│
├── 文档
│   ├── QUICK_START.md                 ← 快速开始 📖
│   ├── GITHUB_AUTOMATION_GUIDE.md     ← 详细指南
│   └── COMPLETION_SUMMARY.md          ← 完成总结
│
├── 工作流模板
│   └── workflow_templates/
│       ├── format-readme-normal.yml
│       └── format-readme-multi-project.yml
│
├── 输入/输出
│   ├── readme_output/                 ← 本地生成的文件
│   │   ├── AUTO1001/
│   │   ├── COMP2001/
│   │   ├── CrossSpecialty/
│   │   └── ...
│   │
│   ├── normal_repo/                   ← 源TOML文件
│   │   ├── AUTO1001.toml
│   │   └── ...
│   │
│   └── multi_project_repo/
│       ├── CrossSpecialty.toml
│       └── ...
│
└── __pycache__/                       ← Python缓存
```

**⭐ 表示最常用的脚本**  
**📖 表示推荐首先阅读的文档**

---

## 🔄 执行流程示意

### 完整自动化流程

```
┌─────────────────────────────────────────────────────────────┐
│                     本地文件生成阶段                        │
│  (convert_normal_repo_toml_to_readme.py等)                │
│  输出: readme_output/{course_code}/*                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 GitHub自动化工具（本集合）                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 第1步: push_to_github.py                           │   │
│  │  ✓ 删除旧文件                                      │   │
│  │  ✓ 上传新文件到分支                                │   │
│  │  ✓ 创建Pull Request                               │   │
│  │  输出: PR链接 (https://github.com/...)            │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │ 第2步: generate_workflows.py                       │   │
│  │  ✓ 生成两种工作流模板                              │   │
│  │  输出: workflow_templates/*.yml                   │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │ 第3步: deploy_workflows.py                         │   │
│  │  ✓ 自动检测仓库类型                                │   │
│  │  ✓ 部署对应的工作流                                │   │
│  │  ✓ 上传到 .github/workflows/format-readme.yml    │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │   GitHub Actions自动化阶段       │
        │  (在每个仓库中自动执行)         │
        │                                  │
        │ 触发条件: readme.toml被修改      │
        │ 执行内容:                       │
        │  1. 格式化readme.toml           │
        │  2. 生成README.md               │
        │  3. 自动提交更改                │
        └──────────────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────┐
        │    完成！数据和显示保持一致      │
        └──────────────────────────────────┘
```

---

## 💻 系统要求

### 必需
- Python 3.10+
- 网络连接（GitHub API访问）
- GitHub Personal Access Token

### 可选依赖
- requests（用于GitHub API）
- tomli（用于TOML解析）

### 推荐环境
- Windows 10+ / macOS / Linux
- 足够的网络带宽（上传文件）
- 对应仓库的push权限

---

## 🎓 使用流程

### 第1次使用（完整设置）

```bash
# 1. 获取GitHub Token
#    访问 https://github.com/settings/tokens
#    创建新token (classic)，授予 repo + workflow 权限

# 2. 设置环境变量
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 3. 运行自动化脚本
python github_automation.py --all

# 4. 在GitHub上审核和合并PR
#    链接会在输出中显示

# 5. 验证工作流已部署
#    访问 https://github.com/HITSZ-OpenAuto/{仓库名}/settings/actions
```

### 后续使用（维护更新）

```bash
# 当本地文件有更新时：

# 1. 重新生成本地文件
python format_normal_repo_toml_standard.py
python convert_normal_repo_toml_to_readme.py

# 2. 上传更新到GitHub
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
python push_to_github.py

# 3. 审核并合并PR
```

---

## 📞 支持和故障排除

### 常见问题

**Q: 脚本报错"Repository not found"**  
A: 检查仓库名称是否正确，确保有权限访问

**Q: 工作流显示"authentication required"**  
A: 检查GitHub Actions在仓库中是否已启用

**Q: 想修改工作流逻辑**  
A: 编辑workflow_templates/*.yml，重新运行deploy_workflows.py

**Q: 如何确认工作流已生效**  
A: 访问仓库 → Actions标签，查看"Format and Update README"工作流

---

## 📚 文档指南

### 按用途分类

| 场景 | 推荐文档 |
|------|---------|
| 快速上手 | `QUICK_START.md` |
| 详细说明 | `GITHUB_AUTOMATION_GUIDE.md` |
| 技术细节 | `COMPLETION_SUMMARY.md` |
| API接口 | 脚本代码注释 |

### 按角色分类

| 角色 | 推荐阅读 |
|------|---------|
| 使用者 | QUICK_START.md |
| 管理员 | GITHUB_AUTOMATION_GUIDE.md |
| 开发者 | COMPLETION_SUMMARY.md + 源代码 |
| 维护者 | 所有文档 |

---

## ✅ 验证清单

在使用前，请确保：

- [ ] Python 3.10+ 已安装
- [ ] 具有GitHub个人访问令牌
- [ ] Token已授予repo和workflow权限
- [ ] 网络连接正常
- [ ] readme_output目录中有文件
- [ ] 对所有目标仓库有push权限

---

## 🎯 预期结果

执行完整流程后，您将获得：

1. ✅ 所有本地文件已上传到GitHub（作为PR）
2. ✅ 所有仓库都配置了自动化工作流
3. ✅ 每个仓库的README.md会在readme.toml更新时自动更新
4. ✅ 保证数据一致性和展示质量

---

## 🚀 下一步

1. 阅读 `QUICK_START.md` 快速了解
2. 获取GitHub Token
3. 运行 `python github_automation.py --all`
4. 在GitHub上审核PR
5. 验证工作流已启用
6. 完成！🎉

---

## 📞 联系和支持

如遇到问题：
1. 查看详细文档：`GITHUB_AUTOMATION_GUIDE.md`
2. 检查脚本输出信息
3. 验证环境变量设置
4. 查看GitHub仓库的Actions日志

---

**版本**: 1.0  
**创建日期**: 2026年1月31日  
**项目**: HITSZ-OpenAuto 自动化工具

