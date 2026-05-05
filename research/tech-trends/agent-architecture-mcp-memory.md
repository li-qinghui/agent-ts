# Agent 技术架构：记忆、工具与 MCP

**日期：** 2026 年 5 月 5 日
**状态：** 进行中
**标签：** #agent, #architecture, #mcp, #skills, #memory

---

## 概述

本文档深入分析当前 Agent 技术的核心组件架构，特别是：
- 记忆管理（Memory Management）
- 工具调用和 Skills
- MCP (Model Context Protocol)
- OpenCloud 和 HoneyS 等新概念（调研中）

---

## 1. MCP (Model Context Protocol) 架构详解

### 1.1 MCP 是什么？

MCP 是连接 LLM 与外部系统的开放标准，由 Anthropic 2024 年 11 月首次提出，2025 年 12 月捐赠给 Linux 基金会（Agentic AI Foundation）。

**核心理念：**
- 类比为 Agent 的 USB-C，统一工具连接方式
- 替代传统的 Function Calling 模型
- 提供标准化的资源、工具、提示的访问机制

### 1.2 MCP 核心组件

MCP 有三个基础原语（Primitives）：

```
MCP Server
  ├── 1. Tools (工具)
  ├── 2. Resources (资源)
  └── 3. Prompts (提示)
```

#### Tools（工具）
- 定义为可被 Agent 调用的操作
- 提供参数 Schema 和结果返回
- 示例：read_file、search_database、send_email

#### Resources（资源）
- 可被读取或订阅的数据来源
- 可以是静态的或动态的（流）
- 示例：文件系统目录、数据库表、API 端点

#### Prompts（提示）
- 预定义的提示模板
- 提供参数化的提示重用
- 示例：代码审查提示、数据清理提示

### 1.3 MCP Server 架构

```
┌─────────────────────────────────────┐
│         Agent Host                  │
│  (Claude Code, OpenAI, Codex...)    │
└───────────────┬─────────────────────┘
                │ JSON-RPC
                ▼
┌─────────────────────────────────────┐
│         MCP Server                  │
│  (Processes MCP requests)           │
└───────────────┬─────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌───────┐  ┌─────────┐  ┌───────┐
│ Tools │  │Resources│  │Prompts│
└───────┘  └─────────┘  └───────┘
    │            │            │
    └───────┬────┴────────────┘
            ▼
    ┌─────────────┐
    │External APIs│
    │ / Filesystem│
    │ / Databases │
    └─────────────┘
```

### 1.4 主流 MCP Servers（2026）

#### 官方 MCP Servers（Anthropic）
- `@modelcontextprotocol/server-filesystem` - 文件系统操作
- `@modelcontextprotocol/server-git` - Git 操作
- `@modelcontextprotocol/server-web` - 网页访问和搜索
- `@modelcontextprotocol/server-database` - 数据库查询

#### 社区 MCP Servers（热门）
- `mcp-agents-memory` - Agent 共享记忆（见下文）
- `@modelcontextprotocol/server-slack` - Slack 集成
- `@modelcontextprotocol/server-jira` - Jira 集成
- `@modelcontextprotocol/server-bash` - Bash 命令执行
- 各种业务定制 MCP Servers（几百个生态）

### 1.5 MCP 与 Function Calling 对比

| 特性 | Function Calling | MCP |
|------|-----------------|------|
| **发现方式** | 静态注册 | 运行时可发现 |
| **复用性** | 单 Agent | 多 Agent / 工具生态 |
| **资源访问** | 无 | Resources 原生支持 |
| **提示复用** | 无 | Prompts 组件 |
| **发现流程** | 静态 | 运行时 negotiate |
| **生态规模** | 自定义 | 标准化，大生态 |

---

## 2. Agent Skills 架构

### 2.1 Skills 是什么？

Skills 是一种 Agent 的模块化能力单元，由 Anthropic 在 Claude Code 中提出（2025-10），后作为开放标准发布（2025-12-18）。

**设计思想：**
- 类比为新员工入职指南
- 不需要为每个用例构建定制化单体 Agent
- 而是通过可组合的 Skills 赋予 Agent 专业知识

### 2.2 Skills 的类型和位置

OpenClaw 定义了两类 Skills：

```
~/.openclaw/
├── skills/             ← 轻型 Skills
│   ├── filesystem/     ← 教 Agent 用 Filesystem MCP
│   │   ├── skill.json  ← Skill 元数据
│   │   └── prompt.md   ← 使用说明
│   └── wechat/
│       ├── skill.json
│       ├── prompt.md
│       └── scripts/    ← 工具脚本
└── workspace/skills/   ← 重型 Skills（业务流水线）
    └── auto-twitter-campaign/
        ├── SKILL.md
        └── scripts/
            ├── campaign.py    ← 编排器
            └── batch_compare.py
```

#### 轻型 Skills
- 位置：`~/.openclaw/skills/`
- 用途：教 Agent 如何使用 MCP Servers
- 组成：`skill.json` + `prompt.md`

#### 重型 Skills
- 位置：`~/.openclaw/workspace/skills/`
- 用途：业务流水线（自动化工作流）
- 组成：`SKILL.md` + 脚本 + 测试

### 2.3 Skills 结构示例

**skill.json（元数据）：**
```json
{
  "name": "Filesystem Operations",
  "version": "1.0.0",
  "description": "Teach agent how to work with filesystem MCP",
  "usesMcp": ["filesystem"],
  "capabilities": ["read", "write", "list", "search"],
  "promptTemplate": "prompt.md"
}
```

**prompt.md（使用说明）：**
```markdown
# Filesystem Skill - How to Use

## When to use this skill
When you need to interact with the user's filesystem.

## How to use it
1. Use `list_directory` to explore
2. Use `read_file` to load content
3. Use `edit_file` to modify (with confirmation!)

## Best practices
- Always confirm before writing
- Don't read too many files at once
- Use search_files for faster lookup
```

### 2.4 MCP 与 Skills 的关系

这是 2026 年的核心设计：
```
┌─────────────────────────────────────┐
│         Skills (知识层)              │
│  "How to do X with these tools?"    │
└────────────────┬────────────────────┘
                 │
┌─────────────────────────────────────┐
│         MCP (工具层)                 │
│  "Connecting to external systems"   │
└────────────────┬────────────────────┘
                 │
┌─────────────────────────────────────┐
│         LLM (推理层)                 │
└─────────────────────────────────────┘
```

- **MCP = 工具层**：解决如何连接外部系统
- **Skills = 知识层**：解决如何使用这些工具做具体任务

---

## 3. Agent 记忆管理架构

### 3.1 主流记忆分层模型

现代 Agent 记忆架构遵循三层结构：

```
┌─────────────────────────────────────┐
│      Episodic Memory (短期)         │
│      - Last 2-3 days                │
│      - Raw conversations            │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│      Semantic Memory (长期)         │
│      - Tag-based summarized         │
│      - Semantic embedding retrieval │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│      Procedural Memory (技能)       │
│      - Skills                       │
│      - Best practices               │
└─────────────────────────────────────┘
```

### 3.2 MemPalace/Agent-Memory 实现细节

根据 GitHub `mcp-ai-wpoos` 项目的 `AGENT-MEMORY-COMPLETE-GUIDE.md`：

#### 层次化范围（Wings & Rooms）

```
Agent Memory
├── Wing (项目/人/领域)
│   ├── "client-acme"
│   ├── "personal"
│   └── "team-alpha"
│
└── Room (子领域)
    ├── "auth-flows"
    ├── "billing"
    └── "onboarding"
```

**检索流程：**
1. 先用 Wing 预筛选候选池
2. 再在 Room 内语义排序
3. 大幅提升共享记忆池中的检索准确率

#### 核心功能

| 功能 | 描述 |
|------|------|
| Full CRUD | 创建、读取、更新、删除单条记忆 |
| Batch Operations | 批量操作 |
| Versioning | 版本历史追踪 |
| Audit Trail | 完整变更追踪（合规用） |
| Tag Management | 标签组织 |
| Health Monitoring | 记忆使用模式跟踪 |

#### API 示例

**`store_agent_context`（存储记忆）：**
```json
{
  "agent_id": 123,
  "context_type": "learning",
  "context_data": {
    "title": "Machine Learning Best Practices",
    "content": "Key insights about ML optimization...",
    "importance": "high",
    "tags": ["ml", "optimization"],
    "metadata": {
      "source": "research",
      "confidence": 0.95
    }
  },
  "wing": "client-acme",
  "room": "training-pipeline",
  "verbatim": false,
  "ttl": 2592000
}
```

### 3.3 mcp-agents-memory 设计（人的记忆模型）

韩国项目 `mcp-agents-memory`（2026-05）采用人类记忆模型：

#### 核心设计

1. **时间顺序如人：** 所有对话按时间顺序 raw 存储
2. **自动模型分离：** 按 `agent_platform` / `agent_model` 自动分离
3. **双轨异步：** Hot Path（立即存储）↔ Cold Path（后台标记+嵌入）
4. **标签中心回忆：** 短期用最近 2-3 天 raw，长期用标签摘要

#### 双轨异步架构

```
┌─────────────────┐
│     Agent       │
│ (Claude Code,   │──▶ Hot Path (立即存储)
│  Codex, ...)    │──▶ memory 表
└─────────────────┘       (raw + role + platform/model)
       │
       │ p_tag/d_tag/embedding 空值累计
       ▼
┌─────────────────────────────────┐
│ Cold Path (1分钟 / 5消息)     │
│ ├─ Tagger (gemini-2.5-flash) │──▶ p_tag, d_tag
│ └─ Embedder (3-large)        │──▶ embedding
└─────────────────────────────────┘
       │ 更新空值
       ▼
┌─────────────────────────────────┐
│ Librarian (memory → user)    │──▶ user 表
│ 核心用户信息提升            │ (core_profile / sub_profile)
└─────────────────────────────────┘
```

#### 数据模型

**`memory` 表**（时间顺序 raw 对话存储）：

| 列 | 说明 |
|----|------|
| `user_id` | 用户标识 |
| `agent_platform` | claude-code / codex / chatgpt / hermes-agent / openclaw |
| `agent_model` | opus-4-7 / gemini-3-pro / gpt-5.5 |
| `subagent` | yes / no |
| `role` | user / assistant |
| `message` | raw 正文 |
| `p_tag` | predefined 标签 |
| `d_tag` | dynamic 上下文标签 |
| `embedding` | vector(3072) |
| `is_pinned` | 强制记忆的行（archive 豁免） |
| `created_at` / `updated_at` | 时间戳 |

**`user` 表**（Librarian 自动提升）：

| 列 | 说明 |
|----|------|
| `core_profile` | 非常重要的用户核心信息 |
| `sub_profile` | 其他需要记住的用户信息 |

**`project_tags` 表**（项目标签动态积累）。

---

## 4. OpenClaw 完整架构（记忆+技能+MCP）

### 4.1 整体架构图

```
┌─────────────────────────────────────────────────┐
│               Agent Host                        │
│    (Claude Code / OpenClaw / Codex)            │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌─────────────┐ ┌──────────┐ ┌───────────┐
│    Skills   │ │  Memory  │ │    MCP    │
│  (知识层)  │ │  (记忆)  │ │ (工具层) │
└──────┬──────┘ └─────┬────┘ └─────┬─────┘
       │              │             │
       └──────────────┼─────────────┘
                      ▼
           ┌─────────────────┐
           │   LLM (Opus)   │
           └─────────────────┘
```

### 4.2 2026-04 "Dreaming" 更新亮点

OpenClaw 在 2026-04-09 的 "Dreaming" 更新引入：
- **记忆整合（Memory Consolidation）**：类似睡眠时的记忆整理
- **能力自推荐**：Agent 可以推荐自己的新功能
- **上下文压缩**：保留信息密度同时减少 Token 消耗

---

## 5. 企业级 Agent 架构要点

### 5.1 必须组件

根据 2026 年企业实践，生产 Agent 需要：

1. **MCP 连接层** - 标准化工具接入
2. **Skills 组织层** - 能力模块化
3. **记忆管理层** - 三层记忆 + 版本/审计
4. **编排层** - LangGraph / Workflow 等
5. **监控/可观测层** - LangSmith / OpenTelemetry
6. **安全/隔离层** - 沙箱、权限、审计

### 5.2 架构演进建议

```
阶段 1: 基础 Agent（单 Agent + 简单工具）
阶段 2: 引入 MCP（标准化工具连接）
阶段 3: Skills 模块化（能力可组合）
阶段 4: 记忆系统（上下文保留）
阶段 5: 多 Agent 协作（复杂工作流）
阶段 6: 企业级治理（安全、审计、成本）
```

---

## 6. OpenCloud / HoneyS 工程（调研中）

*注：这部分信息需要进一步调研确认...*

根据初步搜索，目前了解到：

**OpenCloud / HoneyS 可能涉及：**
- 自主 Agent 的云基础设施
- Agent 集群管理和编排
- 可能与 Google / Anthropic 的合作有关
- 开源社区的自主 Agent 运行环境

*后续会补充详细调研内容。*

---

## 参考资源

- MCP 完全入门：https://qiita.com/agdexai/items/6ba08896963f7e4911f
- mcp-agents-memory：https://www.npmjs.com/package/mcp-agents-memory
- Agent Memory Complete Guide：https://github.com/nvdigitalsolutions/mcp-ai-wpoos/blob/main/docs/AGENT-MEMORY-COMPLETE-GUIDE.md
- Skills 学习笔记：https://developer.aliyun.com/article/1721315
