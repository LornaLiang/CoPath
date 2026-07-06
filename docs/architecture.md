# CoPath 系统架构设计（Architecture Specification）

## 1. 文档目的

本文档用于描述 CoPath 系统的整体架构设计，包括系统模块划分、技术架构、双数据库架构、模块间调用关系、数据流以及部署方式，为系统开发、维护和后续扩展提供统一规范。

本文档是 CoPath 的顶层设计文档。

---

# 2. 系统概述

CoPath（Collaborative Personalized Path Learning）是一个面向智慧教育的个性化学习路径规划系统。

系统以课程知识图谱为基础，以学生学习行为和 AI 对话分析为驱动，根据学生实时学习状态动态调整学习路径，并通过 AI 学习助手提供个性化学习支持。

系统目标包括：

- 个性化学习目标制定
- 多路径学习规划
- 学习画像构建
- AI 学习助手
- 动态学习路径调整
- 学习过程可视化

---

# 3. 总体架构

系统采用前后端分离架构，并使用 SQLite + Neo4j 双数据库设计。

```text
                        ┌──────────────────────────────┐
                        │          React 前端          │
                        └──────────────┬───────────────┘
                                       │
                                  REST API
                                       │
                        ┌──────────────▼───────────────┐
                        │         FastAPI 后端         │
                        └──────────────┬───────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
          ▼                            ▼                            ▼
   SQLite Database              Neo4j Database              OpenAI API
   (业务数据)                   (知识图谱)                   (LLM)
          │                            │                            │
          └──────────────┬─────────────┴──────────────┬─────────────┘
                         ▼                            ▼
                  Profile Service              Graph Service
                         │                            │
                         └──────────────┬─────────────┘
                                        ▼
                               Adaptation Service
                                        │
                                        ▼
                                 Path Planner
                                        │
                                        ▼
                                学习路径动态调整
```

---

# 4. 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + Vite |
| UI组件 | Ant Design |
| 图表 | ECharts |
| HTTP通信 | Axios |
| 后端 | FastAPI |
| ORM | SQLAlchemy |
| 业务数据库 | SQLite |
| 图数据库 | Neo4j |
| 图计算 | Cypher + Neo4j Traversal |
| AI | OpenAI API |
| 部署 | Docker（后续） |

---

# 5. 系统模块

整个系统由七个核心模块组成。

## 5.1 前端模块

负责：

- 页面展示
- 用户交互
- 图表可视化
- 学习路径展示
- 知识图谱展示

主要页面包括：

- 学习目标
- 学习路径
- 我的学习
- 知识图谱
- 学习画像
- 学习记录
- 设置

---

## 5.2 后端模块

负责：

- API
- 权限控制（后续）
- 数据处理
- AI调用
- 图谱查询
- 路径规划

后端仅提供 REST API。

前端不直接访问数据库。

---

## 5.3 SQLite 模块

SQLite 存储业务数据。

包括：

- 学生信息
- 学习目标
- 学习事件
- 学习画像
- AI聊天记录
- 学习资源
- 学习路径记录
- 路径切换记录
- 系统设置

SQLite 不负责知识图谱查询。

---

## 5.4 Neo4j 模块

Neo4j 专门负责课程知识图谱。

存储：

- KnowledgeNode
- Prerequisite
- LearningGoal
- LearningResource（可选关联）

主要作用：

- 查询知识依赖
- 查询前置知识
- 查询后继知识
- 查询学习路径
- 支撑路径规划

Neo4j 不保存学生业务数据。

---

## 5.5 AI Assistant

AI 学习助手负责：

- 与学生自然语言交互
- 分析学习状态
- 提取学习信号
- 生成学习建议

AI 不直接修改数据库。

AI 输出结构化学习状态。

例如：

```json
{
  "knowledge_gap": "call_stack",
  "confusion_level": 0.82,
  "learning_preference": "example",
  "suggested_action": "insert_prerequisite"
}
```

---

## 5.6 Learning Profile

负责：

维护学生画像。

包括：

- 学习速度
- 学习偏好
- 知识掌握度
- 学习信心
- 当前目标

学习画像持续更新。

---

## 5.7 Path Planner

Path Planner 是系统核心。

负责：

- 根据学习目标生成候选路径
- 推荐最佳路径
- 插入补救节点
- 跳过已掌握节点
- 切换学习路径

Path Planner 不依赖 LLM。

路径规划逻辑由系统完成。

---

# 6. 双数据库架构

系统采用业务数据库与图数据库分离设计。

## SQLite

负责：

```text
Student
Goal
Profile
LearningEvent
Dialogue
PathHistory
Settings
```

特点：

- 事务支持
- 结构化业务数据
- 更新频繁

---

## Neo4j

负责：

```text
KnowledgeNode
Prerequisite
LearningPath
```

特点：

- 图结构存储
- 图查询效率高
- 支持 Cypher
- 支持复杂路径查询

---

数据库职责划分如下：

| 数据类型 | SQLite | Neo4j |
|-----------|---------|--------|
| 学生信息 | ✓ | |
| 学习画像 | ✓ | |
| 学习事件 | ✓ | |
| AI聊天 | ✓ | |
| 路径历史 | ✓ | |
| 系统设置 | ✓ | |
| 知识点 | | ✓ |
| 知识依赖 | | ✓ |
| 图遍历 | | ✓ |
| 路径搜索 | | ✓ |

---

# 7. 核心服务

## Graph Service

负责：

- Neo4j 查询
- 图遍历
- 前驱节点
- 后继节点
- 路径搜索

Graph Service 不处理业务数据。

---

## Profile Service

负责：

维护学生画像。

输入：

学习事件

AI聊天

输出：

更新后的画像。

---

## Adaptation Service

负责：

分析：

- AI结果
- 学习画像
- 学习记录

决定：

是否需要调整路径。

---

## AI Service

负责：

Prompt

LLM调用

JSON解析

学习状态提取

不负责路径规划。

---

# 8. 模块调用关系

系统调用流程如下：

```text
React

↓

FastAPI

↓

Profile Service

↓

AI Service

↓

Graph Service

↓

Path Planner

↓

SQLite / Neo4j

↓

返回前端
```

---

# 9. 数据流

学生学习过程中：

```text
学生

↓

AI聊天

↓

AI分析学习状态

↓

更新学习画像(SQLite)

↓

查询知识图谱(Neo4j)

↓

Path Planner

↓

更新学习路径(SQLite)

↓

页面刷新
```

---

# 10. API 调用流程

```text
React

↓

Axios

↓

FastAPI

↓

Service

↓

SQLite

Neo4j

OpenAI
```

所有数据库访问均通过 Service 层完成。

---

# 11. 部署架构

开发环境：

```text
React

FastAPI

SQLite

Neo4j Desktop
```

生产环境（可扩展）：

```text
Nginx

↓

FastAPI

↓

SQLite

Neo4j Server

↓

OpenAI API
```

---

# 12. 系统特点

本系统具有以下特点：

1. 前后端分离架构。
2. 双数据库架构。
3. 图数据与业务数据分离。
4. AI 与路径规划解耦。
5. 学习画像持续更新。
6. 路径规划可解释。
7. 支持动态学习路径调整。
8. 易于扩展新的课程知识图谱。

---

# 13. 设计原则

CoPath 遵循以下设计原则：

### 单一职责原则

每个模块仅负责一项核心职责。

---

### 数据与算法分离

SQLite 与 Neo4j 负责数据存储。

Path Planner 负责算法。

LLM 负责学习状态分析。

---

### 可扩展原则

课程知识图谱可独立扩展。

支持新增课程。

支持新增路径规划策略。

---

### 松耦合原则

React、FastAPI、SQLite、Neo4j、OpenAI 相互独立。

模块之间仅通过 API 或 Service 调用。

便于维护与替换。

---

# 14. 后续扩展

后续版本可进一步支持：

- 多课程知识图谱
- 多智能体协同学习
- RAG 检索增强
- 学习资源自动推荐
- 多模态学习分析
- 知识图谱自动构建
- 多模型 AI 调度

---

# 15. 文档关系

本文档为系统总体架构设计文档。

相关文档：

- AGENTS.md
- system_spec.md
- database_spec.md
- knowledge_graph_spec.md
- demo_data_spec.md
- api_spec.md
- data_flow.md
- ui_spec.md
- development_plan.md

所有后续开发应遵循本文档规定的系统架构。