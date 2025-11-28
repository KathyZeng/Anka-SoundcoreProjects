# 版本快速回退指南 ⚡

## 🔍 查看版本历史
```bash
git log --oneline -10
```

## ⏮️ 快速回退到上一版本

### 方案1：保留修改（推荐）
```bash
git reset --soft HEAD^
git push origin main --force
```

### 方案2：完全回退（危险）
```bash
git reset --hard HEAD^
git push origin main --force
```

### 方案3：安全回退（最安全）
```bash
git revert HEAD
git push origin main
```

## 📋 当前版本列表

| 版本 | 提交ID | 说明 | 日期 |
|------|--------|------|------|
| v2.0.1 | d146819 | 移除文件名特殊符号，优化布局 | 2025-11-26 |
| v2.0.0 | 71c5316 | 初始发布版本 | 2025-11-24 |

## 🎯 回退到指定版本

```bash
# 回退到 v2.0.0（初始版本）
git reset --soft 71c5316
git push origin main --force

# 回退到 v2.0.1（当前版本）
git reset --soft d146819
git push origin main --force
```

## 💡 一键命令

### 回退到初始版本
```bash
git reset --soft 71c5316 && git push origin main --force
```

### 恢复到最新版本
```bash
git reset --soft d146819 && git push origin main --force
```

## 📖 详细文档

查看完整的版本管理文档：[VERSION_CONTROL.md](VERSION_CONTROL.md)
