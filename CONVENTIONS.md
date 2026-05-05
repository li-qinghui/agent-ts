# 文档约定规范

本文件定义了 Agent 文档记录项目的通用约定和规范。

## 目录结构约定

### 根目录
- `README.md` - 项目根说明
- `CONVENTIONS.md` - 通用约定规范
- `.obsidian/` - Obsidian 配置目录
- `exploration/` - Agent 探索方向
- `progress/` - 当前进度追踪
- `archive/` - 历史文档归档

### 子目录规范
每个子目录必须包含 `index.md` 文件，用于概述该目录内容并提供导航链接。

## 文件命名规范

- 使用小写字母
- 单词之间用连字符 `-` 分隔
- 使用描述性文件名
- 统一使用 `.md` 扩展名

**正确示例:**
- `agent-architecture.md`
- `prompt-engineering.md`
- `memory-system.md`

**错误示例:**
- `AgentArchitecture.md`
- `prompt engineering.md`
- `MemorySystem.txt`

## 链接约定

### 双向链接
使用 Obsidian 双向链接语法：

```markdown
[[filename|显示文本]]
```

### 链接到目录索引
```markdown
[[exploration/index|探索方向]]
```

### 链接到锚点
```markdown
[[progress/index#当前任务|当前任务]]
```

### 相对路径
跨目录链接使用相对路径：
```markdown
[[../README|项目首页]]
[[../progress/index|开发进度]]
```

## Markdown 格式规范

### 标题层级
- `# 一级标题` - 文档标题
- `## 二级标题` - 主要章节
- `### 三级标题` - 子章节
- `#### 四级标题` - 小节

### 列表
- 使用 `-` 或 `*` 表示无序列表
- 使用数字加 `.` 表示有序列表
- 支持嵌套列表

### 表格
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容1 | 内容2 | 内容3 |
```

### 代码块
```markdown
```python
def hello():
    print("Hello")
```
```

### 强调
- `*斜体*` - 用于强调
- `**粗体**` - 用于重点
- `` `代码` `` - 用于行内代码

## 文档模板

### index.md 模板
```markdown
# 目录名称

本目录描述...

## 内容分类

### 类别1
- [[文件1|描述1]]
- [[文件2|描述2]]

## 状态/统计

| 项目 | 状态 |
|------|------|

## 快速导航

- 返回 [[../README|项目首页]]
- 查看 [[../other/index|其他目录]]
```

## 元数据约定

### 文档属性
每个文档可在顶部添加 YAML 元数据：

```yaml
---
title: 文档标题
date: 2026-05-05
status: draft/review/published
tags: [tag1, tag2]
---
```

## 版本控制

- 使用 Git 进行版本控制
- 每次提交附带清晰的提交信息
- 重要变更应更新相关文档

## 更新规范

- 文档更新后应同步更新相关链接
- 删除文档前应检查是否有其他文档引用
- 定期清理无效链接和废弃文档

---

*本约定遵循 [[README]] 项目概述*