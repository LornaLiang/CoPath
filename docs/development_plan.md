# CoPath 开发计划（Development Plan）

## 一、项目概述

项目名称：

**CoPath**

项目定位：

基于知识图谱与 AI 协同的自适应学习路径规划系统。

开发方式：

采用前后端分离架构，按照里程碑（Milestone）逐步开发。

开发原则：

- 小步迭代
- 每个阶段可运行
- 每个阶段可演示
- 每个阶段完成后提交 Git
- 不跨阶段开发

---

# 二、开发流程

整个项目按照以下顺序开发：

```text
需求分析
    ↓
数据库设计
    ↓
API设计
    ↓
页面设计
    ↓
项目初始化
    ↓
数据库实现
    ↓
API实现
    ↓
前端实现
    ↓
前后端联调
    ↓
知识图谱
    ↓
AI助手
    ↓
动态路径规划
    ↓
测试
    ↓
部署
```

---

# 三、Milestone 规划

---

# Milestone 1：项目初始化

## 目标

完成整个项目基础工程。

## 内容

初始化：

React

FastAPI

SQLite

SQLAlchemy

Axios

React Router

建立项目目录：

frontend

backend

database

docs

scripts

tests

创建：

requirements.txt

package.json

README.md

配置：

.gitignore

## 验收标准

React 能运行。

FastAPI 能运行。

项目目录完整。

Git 初始化完成。

GitHub 成功同步。

## Git Commit

```
feat: initialize project
```

---

# Milestone 2：数据库

## 目标

完成数据库设计落地。

## 内容

根据：

database_spec.md

完成：

schema.sql

SQLAlchemy Models

数据库初始化脚本

Demo 数据

创建：

students

knowledge_nodes

knowledge_edges

learning_paths

learning_events

student_profiles

dialogue_logs

path_switch_logs

learning_resources

system_settings

## 验收标准

数据库能够成功创建。

能够导入 Demo 数据。

所有表正常查询。

## Git Commit

```
feat: implement database schema
```

---

# Milestone 3：API

## 目标

完成后端接口。

## 内容

根据：

api_spec.md

实现：

所有 Router

所有 Service

Pydantic Models

统一返回格式

统一异常处理

API 可以先返回 Mock 数据。

## 验收标准

Swagger 可访问。

所有接口存在。

接口返回格式统一。

## Git Commit

```
feat: implement backend api
```

---

# Milestone 4：React 页面

## 目标

完成所有页面。

## 内容

根据：

ui_spec.md

docs/ui/home.png

docs/ui/detail.png

实现：

左侧导航

顶部状态栏

学习目标

学习路径

我的学习

知识图谱

学习画像

学习记录

设置

页面数据可以先 Mock。

## 验收标准

页面布局完成。

路由正常。

页面风格符合设计图。

## Git Commit

```
feat: build frontend ui
```

---

# Milestone 5：前后端联调

## 目标

替换所有 Mock 数据。

## 内容

React

↓

Axios

↓

FastAPI

↓

SQLite

所有页面改为真实 API。

## 验收标准

页面能够读取数据库。

所有页面正常展示。

## Git Commit

```
feat: connect frontend and backend
```

---

# Milestone 6：引入 Neo4j 知识图谱

## 目标

在保留 SQLite 业务数据库的基础上，引入 Neo4j 作为知识图谱数据库，实现课程知识点、知识依赖关系和路径查询的图数据库管理。

## 内容

1. 安装并配置 Neo4j。
2. 在后端新增 Neo4j 连接配置。
3. 新增 GraphRepository / GraphService。
4. 将 Demo 知识点和知识依赖从 SQLite 或 seed 数据同步到 Neo4j。
5. 使用 Cypher 查询：
   - 全部知识点
   - 前置知识
   - 后继知识
   - 当前学习路径
   - 可达路径
   - 补救节点
6. 修改知识图谱相关 API，使其优先从 Neo4j 查询。
7. 保留 SQLite 中的 knowledge_nodes 和 knowledge_edges 作为初始化来源或备份。
8. 知识图谱页面继续通过现有 API 展示，不直接访问 Neo4j。

## 验收标准

- Neo4j 能成功启动。
- 后端能连接 Neo4j。
- Demo 知识图谱能导入 Neo4j。
- `/api/graph` 能返回 Neo4j 中的节点和边。
- 知识图谱页面能正常显示。
- SQLite 中原有学生、画像、学习记录、对话等数据不受影响。

## Git Commit

```text
feat: integrate neo4j knowledge graph
---


# Milestone 7：AI 学习助手

## 目标

实现 AI 助手。

## 内容

ChatService

Prompt

LLM

JSON Output

聊天窗口

历史记录

学习状态提取

AI 暂不负责路径规划。

## 验收标准

AI 能正常回复。

能够保存聊天记录。

能够输出学习状态。

## Git Commit

```
feat: implement ai assistant
```

---

# Milestone 8：学习画像

## 目标

实现学习画像动态更新。

## 内容

掌握度更新

学习速度

学习偏好

学习信心

学习状态

ProfileService

Profile API

Profile 页面

## 验收标准

学习画像能够动态变化。

图表正常刷新。

## Git Commit

```
feat: implement learning profile
```

---

# Milestone 9：动态路径规划（核心创新）

## 目标

实现论文核心功能。

## 内容

PathPlanner

AdaptationService

根据：

学习事件

AI 对话

学习画像

动态调整路径。

支持：

生成待确认路径调整建议

用户确认后切换路径

用户拒绝建议

用户手动切换前风险评估

用户覆盖系统建议

插入补救节点

跳过节点

重新排序

记录路径调整历史。

## 验收标准

系统能够生成 pending 路径调整建议。

用户确认后才真正调整路径。

用户拒绝后当前路径保持不变。

用户手动切换前会看到系统评估和风险提示。

路径调整具有解释。

学习路径页面实时刷新。

## Git Commit

```
feat: implement adaptive learning path
```

---

# Milestone 10：系统优化



# Milestone 11：测试

## 内容

数据库测试

API 测试

React 测试

路径规划测试

AI 测试

异常测试

## Git Commit

```
test: add system tests
```

---

# Milestone 12：论文 Demo

## 内容

准备：

Demo 数据

Demo 学生

系统截图

录屏

README

论文图片

系统流程图

ER 图

数据流图

部署说明

## Git Commit

```
docs: prepare demo and paper
```

---

# 四、开发规范

每个 Milestone 必须遵循：

开发

↓

Review

↓

测试

↓

Commit

↓

Push

↓

进入下一阶段

禁止跨阶段开发。

---

# 五、Codex 开发规则

每次仅完成一个 Milestone。

不得提前开发下一阶段内容。

不得修改系统架构。

不得新增系统模块。

若发现设计问题，应提出建议，而不是直接修改。

完成后停止，等待下一阶段任务。

---

# 六、当前开发状态

当前状态：

✅ 系统设计完成

✅ 数据库设计完成

✅ API 设计完成

✅ UI 设计完成

✅ 数据流设计完成

下一步：

**Milestone 1：项目初始化**

完成后进入：

**Milestone 2：数据库实现**
