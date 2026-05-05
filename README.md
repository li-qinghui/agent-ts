# Agent 文档记录项目

## 项目概述

本项目是一个基于 Obsidian 的 Agent 探索文档记录系统，采用渐进式目录结构设计，支持双向链接，便于知识管理和 Agent 相关技术的探索与追踪。

## 核心原则

- **渐进式设计**: 目录结构层次清晰，便于逐步扩展
- **双向链接**: 使用 Obsidian 语法建立文档间的关联关系
- **索引驱动**: 每个目录包含 `index.md` 文件，概述该目录内容
- **MD 格式**: 所有文档采用 Markdown 格式编写

## 目录结构

```
├── README.md           # 项目根说明
├── CONVENTIONS.md      # 通用约定规范
├── .obsidian/          # Obsidian 配置
│   └── settings.json   # 双向链接配置
├── exploration/        # Agent 探索方向
│   └── index.md
├── progress/           # 当前进度追踪
│   └── index.md
└── archive/            # 历史文档归档
    └── index.md
```

## 主要目录说明

### 1. exploration/

记录 Agent 技术探索的各个方向，包括研究笔记、技术分析、架构设计等。

### 2. progress/

追踪当前 Agent 项目的开发进度、任务状态、里程碑等。

### 3. archive/

归档历史文档、旧版本记录、已完成项目的总结等。

## 链接约定

所有文档间的引用使用 Obsidian 双向链接语法：

- 链接到目录索引: `[[exploration/index|探索方向]]`
- 链接到具体文件: `[[exploration/agent-design|Agent 设计文档]]`
- 链接到锚点: `[[progress/index#当前任务|当前任务]]`

## 快速开始

1. 使用 Obsidian 打开本目录
2. 配置 Obsidian 启用双向链接功能
3. 从 `[[exploration/index]]` 或 `[[progress/index]]` 开始浏览

---

*本项目遵循 [[CONVENTIONS]] 约定规范*