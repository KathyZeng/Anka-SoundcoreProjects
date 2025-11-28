# 版本管理文档

工作负载饱和度分析系统的版本管理和回退操作指南

## 📋 版本历史

### v2.0.1 - 2025-11-26 (当前版本)
**提交ID**: `d146819`

**更新内容**:
- 移除所有页面文件名中的表情符号，使用纯文本命名
- 更新所有代码中的文件引用链接
- 优化数据预览页面布局：将"本周统计"板块提前到数据筛选之前
- 提升用户体验，先展示整体统计再进行详细筛选

**文件变更**:
```
app.py                      (文件引用更新)
pages/1_数据上传.py         (重命名 + 链接更新)
pages/2_数据预览.py         (重命名 + 布局优化)
pages/3_负载分析.py         (重命名 + 链接更新)
pages/4_趋势对比.py         (重命名 + 链接更新)
pages/5_配置管理.py         (重命名)
```

---

### v2.0.0 - Initial Release
**提交ID**: `71c5316`

**功能特性**:
- 完整的工作负载分析系统
- 数据上传和处理
- 三周工作负载对比
- 历史趋势分析
- 可视化图表展示
- 配置管理功能

---

## 🔍 查看版本信息

### 查看所有版本历史
```bash
# 查看完整提交历史
git log

# 查看简洁的提交历史（推荐）
git log --oneline

# 查看最近 5 个版本
git log --oneline -5

# 查看每个版本的详细改动
git log --stat
```

### 查看具体版本的详细信息
```bash
# 查看某个版本的详细信息
git show d146819

# 查看某个版本修改了哪些文件
git show --stat d146819

# 查看某个版本的具体代码改动
git diff 71c5316 d146819
```

### 查看当前版本
```bash
# 查看当前所在的版本
git log -1 --oneline

# 查看当前分支和版本状态
git status
```

---

## ⏮️ 版本回退操作

### 方式一：软回退（保留修改，推荐）
```bash
# 回退到指定版本，保留工作区的修改
git reset --soft 71c5316

# 查看状态（修改会变成待提交状态）
git status

# 如果确认回退，推送到 GitHub
git push origin main --force
```

**使用场景**: 想回退版本但保留当前的代码修改

---

### 方式二：混合回退（默认方式）
```bash
# 回退到指定版本，保留工作区修改但取消暂存
git reset --mixed 71c5316
# 或简写为
git reset 71c5316

# 查看状态
git status

# 推送到 GitHub
git push origin main --force
```

**使用场景**: 回退版本并重新组织提交

---

### 方式三：硬回退（完全回退，危险）
```bash
# 完全回退到指定版本，丢弃所有修改
git reset --hard 71c5316

# 推送到 GitHub
git push origin main --force
```

**使用场景**: 完全放弃当前修改，恢复到之前的干净状态

⚠️ **警告**: 此操作会永久删除未提交的修改，请谨慎使用！

---

### 方式四：创建回退提交（安全推荐）
```bash
# 创建一个新的提交来撤销某个版本的修改
git revert d146819

# 或者撤销最近的提交
git revert HEAD

# 推送到 GitHub（不需要 --force）
git push origin main
```

**使用场景**: 最安全的回退方式，保留完整的历史记录

---

## 🚀 快速回退命令表

### 回退到上一个版本
```bash
# 方案1：软回退（保留修改）
git reset --soft HEAD^
git push origin main --force

# 方案2：硬回退（删除修改）
git reset --hard HEAD^
git push origin main --force

# 方案3：安全回退（创建新提交）
git revert HEAD
git push origin main
```

### 回退到指定版本
```bash
# 使用版本号回退（推荐）
git reset --soft 71c5316    # 回退到 v2.0.0
git push origin main --force

# 使用相对位置回退
git reset --soft HEAD~2      # 回退 2 个版本
git push origin main --force
```

### 查看可回退的版本列表
```bash
# 快速查看版本列表（带序号）
git log --oneline --reverse | cat -n
```

---

## 📌 常用版本管理命令

### 1. 版本对比
```bash
# 对比两个版本的差异
git diff 71c5316 d146819

# 对比当前版本和某个历史版本
git diff 71c5316

# 只看修改了哪些文件
git diff --stat 71c5316 d146819
```

### 2. 分支管理
```bash
# 查看所有分支
git branch -a

# 基于某个版本创建新分支（用于实验）
git checkout -b experiment-branch 71c5316

# 切换回主分支
git checkout main
```

### 3. 标签管理
```bash
# 为当前版本打标签
git tag v2.0.1

# 为指定版本打标签
git tag v2.0.0 71c5316

# 推送标签到 GitHub
git push origin --tags

# 查看所有标签
git tag -l

# 回退到某个标签
git checkout v2.0.0
```

### 4. 临时保存修改
```bash
# 保存当前修改（用于临时切换版本）
git stash save "临时保存的修改说明"

# 回退到某个版本进行查看
git checkout 71c5316

# 恢复之前保存的修改
git checkout main
git stash pop
```

---

## 🎯 推荐的版本管理工作流

### 日常开发流程
```bash
# 1. 开始新功能开发前，确保在最新版本
git pull origin main

# 2. 进行开发和测试
# ... 修改代码 ...

# 3. 查看修改
git status
git diff

# 4. 提交修改
git add .
git commit -m "功能描述"

# 5. 推送到 GitHub
git push origin main
```

### 发现问题需要回退
```bash
# 1. 先保存当前修改（如果需要）
git stash save "当前进度"

# 2. 查看历史版本
git log --oneline

# 3. 回退到稳定版本
git reset --hard 71c5316

# 4. 推送回退
git push origin main --force

# 5. 如果需要恢复之前的修改
git stash pop
```

---

## 📝 版本号命名规范

本项目采用语义化版本号: `v主版本号.次版本号.修订号`

- **主版本号**: 重大功能更新或架构变更
- **次版本号**: 新增功能或较大改进
- **修订号**: Bug 修复或小改进

示例:
- `v2.0.0` - 初始发布版本
- `v2.0.1` - 界面优化和文件重命名
- `v2.1.0` - 新增导出功能（假设）
- `v3.0.0` - 架构重构（假设）

---

## 🔐 安全建议

1. **推送前确认**: 使用 `--force` 推送前务必确认操作
2. **备份重要修改**: 重要修改先保存到其他地方
3. **使用标签**: 为稳定版本打标签方便快速回退
4. **定期提交**: 小步提交，方便精确回退
5. **测试分支**: 重大修改先在新分支测试

---

## 🆘 常见问题

### Q1: 如何撤销刚才的提交？
```bash
# 撤销最后一次提交，保留修改
git reset --soft HEAD^

# 重新提交
git add .
git commit -m "新的提交信息"
```

### Q2: 如何查看某个文件的修改历史？
```bash
git log --oneline -- pages/2_数据预览.py
```

### Q3: 如何恢复被删除的文件？
```bash
# 恢复到最后一次提交的状态
git checkout HEAD -- 文件路径
```

### Q4: 推送被拒绝怎么办？
```bash
# 先拉取远程更新
git pull origin main

# 如果确定要覆盖远程版本
git push origin main --force
```

### Q5: 如何查看两个版本之间改了什么？
```bash
# 详细对比
git diff 71c5316..d146819

# 只看文件列表
git diff --name-status 71c5316..d146819
```

---

## 📚 相关文档

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 使用指南](https://docs.github.com)
- 项目 README: `README.md`
- 部署文档: `DEPLOYMENT.md`

---

**文档更新日期**: 2025-11-26
**维护者**: Workload Analysis System Team
