# CoPath 知识图谱设计说明

## 1. 文档目的

本文档定义 CoPath 系统中知识图谱部分的 Neo4j 存储与查询方式。

本次调整只涉及知识图谱模块：

- 知识点
- 知识依赖
- 学习资源关联
- 图查询

系统其他部分保持不变，仍以以下文档为准：

- system_spec.md
- database_spec.md
- api_spec.md
- data_flow.md
- demo_data_spec.md
- architecture.md

---

## 2. 存储职责划分

CoPath 采用 SQLite + Neo4j 双数据库架构。

### SQLite 负责

- 学生信息
- 学习画像
- 学习事件
- AI 对话记录
- 学习路径记录
- 路径切换记录
- 系统设置

### Neo4j 负责

- 课程知识点
- 知识点依赖关系
- 学习资源与知识点的关联
- 前置知识查询
- 后继知识查询
- 路径查询
- 补救节点查询

前端不得直接访问 Neo4j。

所有图谱查询必须经过 FastAPI 后端的 GraphService。

---

## 3. Neo4j 节点设计

### 3.1 KnowledgeNode

表示课程知识点。

标签：

```cypher
:KnowledgeNode
```

属性：

| 属性         | 类型    | 说明          |
| ------------ | ------- | ------------- |
| id           | string  | 知识点唯一 ID |
| name         | string  | 知识点名称    |
| english_name | string  | 英文名称      |
| description  | string  | 知识点说明    |
| difficulty   | integer | 难度等级      |
| chapter      | string  | 所属章节      |
| type         | string  | 节点类型      |

节点类型包括：

- foundation
- core
- remedial
- example
- target
- advanced

示例：

```cypher
(:KnowledgeNode {
  id: "call_stack",
  name: "调用栈",
  english_name: "Call Stack",
  description: "调用栈用于记录函数调用过程。",
  difficulty: 4,
  chapter: "函数与递归",
  type: "remedial"
})
```

------

### 3.2 LearningGoal

表示学习目标。

标签：

```cypher
:LearningGoal
```

属性：

| 属性        | 类型   | 说明     |
| ----------- | ------ | -------- |
| id          | string | 目标 ID  |
| title       | string | 目标名称 |
| description | string | 目标说明 |

示例：

```cypher
(:LearningGoal {
  id: "goal_recursion",
  title: "掌握递归",
  description: "理解递归思想、递归出口，并能编写基础递归程序。"
})
```

------

### 3.3 LearningResource

表示学习资源。

标签：

```cypher
:LearningResource
```

属性：

| 属性          | 类型    | 说明                           |
| ------------- | ------- | ------------------------------ |
| id            | string  | 资源 ID                        |
| title         | string  | 资源标题                       |
| resource_type | string  | text / video / exercise / code |
| content       | string  | 简要内容                       |
| url           | string  | 资源链接                       |
| difficulty    | integer | 资源难度                       |

------

## 4. Neo4j 关系设计

### 4.1 PREREQUISITE

表示知识点前置依赖。

方向：

```text
前置知识点 → 后续知识点
```

Cypher 形式：

```cypher
(:KnowledgeNode)-[:PREREQUISITE]->(:KnowledgeNode)
```

示例：

```cypher
(:KnowledgeNode {id: "call_stack"})
  -[:PREREQUISITE]->
(:KnowledgeNode {id: "recursion_thinking"})
```

------

### 4.2 TARGET_OF

表示学习目标对应的目标知识点。

方向：

```text
LearningGoal → KnowledgeNode
```

Cypher 形式：

```cypher
(:LearningGoal)-[:TARGET_OF]->(:KnowledgeNode)
```

示例：

```cypher
(:LearningGoal {id: "goal_recursion"})
  -[:TARGET_OF]->
(:KnowledgeNode {id: "basic_recursion"})
```

------

### 4.3 HAS_RESOURCE

表示知识点关联学习资源。

方向：

```text
KnowledgeNode → LearningResource
```

Cypher 形式：

```cypher
(:KnowledgeNode)-[:HAS_RESOURCE]->(:LearningResource)
```

------

### 4.4 EXAMPLE_SUPPORT

表示案例节点支持某个知识点理解。

方向：

```text
案例节点 → 被支持知识点
```

Cypher 形式：

```cypher
(:KnowledgeNode)-[:EXAMPLE_SUPPORT]->(:KnowledgeNode)
```

示例：

```cypher
(:KnowledgeNode {id: "hanoi"})
  -[:EXAMPLE_SUPPORT]->
(:KnowledgeNode {id: "recursion_thinking"})
```

------

## 5. Demo 知识点

第一版 Demo 图谱使用以下知识点。

| id                 | name       | difficulty | chapter    | type       |
| ------------------ | ---------- | ---------- | ---------- | ---------- |
| variable           | 变量       | 1          | Python基础 | foundation |
| expression         | 表达式     | 1          | Python基础 | foundation |
| condition          | 条件语句   | 2          | 控制结构   | foundation |
| loop               | 循环       | 2          | 控制结构   | foundation |
| function           | 函数       | 3          | 函数基础   | core       |
| parameter          | 参数传递   | 3          | 函数基础   | core       |
| return_value       | 返回值     | 3          | 函数基础   | remedial   |
| call_stack         | 调用栈     | 4          | 函数与递归 | remedial   |
| recursion_thinking | 递归思想   | 4          | 递归       | core       |
| base_case          | 递归出口   | 4          | 递归       | core       |
| basic_recursion    | 基础递归   | 5          | 递归       | target     |
| hanoi              | 汉诺塔案例 | 4          | 递归案例   | example    |
| tree_recursion     | 树形递归   | 5          | 递归进阶   | advanced   |
| dfs                | DFS        | 5          | 搜索算法   | advanced   |
| backtracking       | 回溯       | 6          | 搜索算法   | advanced   |

------

## 6. Demo 依赖关系

| source             | target             | relation        |
| ------------------ | ------------------ | --------------- |
| variable           | expression         | PREREQUISITE    |
| expression         | condition          | PREREQUISITE    |
| condition          | loop               | PREREQUISITE    |
| loop               | function           | PREREQUISITE    |
| function           | parameter          | PREREQUISITE    |
| function           | return_value       | PREREQUISITE    |
| parameter          | call_stack         | PREREQUISITE    |
| return_value       | call_stack         | PREREQUISITE    |
| call_stack         | recursion_thinking | PREREQUISITE    |
| recursion_thinking | base_case          | PREREQUISITE    |
| base_case          | basic_recursion    | PREREQUISITE    |
| basic_recursion    | tree_recursion     | PREREQUISITE    |
| basic_recursion    | dfs                | PREREQUISITE    |
| tree_recursion     | backtracking       | PREREQUISITE    |
| dfs                | backtracking       | PREREQUISITE    |
| hanoi              | recursion_thinking | EXAMPLE_SUPPORT |
| hanoi              | basic_recursion    | EXAMPLE_SUPPORT |

------

## 7. 三条候选学习路径

目标：

```text
掌握递归
```

目标节点：

```text
basic_recursion
```

### 7.1 基础补全路径

适合基础一般、前置知识薄弱的学生。

```text
function
→ parameter
→ return_value
→ call_stack
→ recursion_thinking
→ base_case
→ basic_recursion
```

### 7.2 案例驱动路径

适合喜欢案例学习的学生。

```text
hanoi
→ recursion_thinking
→ base_case
→ basic_recursion
→ dfs
```

### 7.3 快速提升路径

适合基础较好、学习速度快的学生。

```text
recursion_thinking
→ base_case
→ basic_recursion
→ dfs
→ backtracking
```

------

## 8. GraphService 需要支持的查询

GraphService 是后端访问 Neo4j 的唯一入口。

必须提供以下能力。

### 8.1 获取完整图谱

方法：

```python
get_full_graph()
```

返回：

```json
{
  "nodes": [],
  "edges": []
}
```

用于：

- 知识图谱页面
- ECharts 图谱展示

------

### 8.2 获取知识点详情

方法：

```python
get_node_detail(node_id)
```

返回：

- 知识点信息
- 前置知识
- 后继知识
- 关联资源

------

### 8.3 查询前置知识

方法：

```python
get_prerequisites(node_id)
```

Cypher 示例：

```cypher
MATCH (pre:KnowledgeNode)-[:PREREQUISITE]->(n:KnowledgeNode {id: $node_id})
RETURN pre
```

------

### 8.4 查询后继知识

方法：

```python
get_successors(node_id)
```

Cypher 示例：

```cypher
MATCH (n:KnowledgeNode {id: $node_id})-[:PREREQUISITE]->(next:KnowledgeNode)
RETURN next
```

------

### 8.5 查询学习资源

方法：

```python
get_resources(node_id)
```

Cypher 示例：

```cypher
MATCH (n:KnowledgeNode {id: $node_id})-[:HAS_RESOURCE]->(r:LearningResource)
RETURN r
```

------

### 8.6 查询目标节点

方法：

```python
get_goal_target(goal_id)
```

Cypher 示例：

```cypher
MATCH (g:LearningGoal {id: $goal_id})-[:TARGET_OF]->(n:KnowledgeNode)
RETURN n
```

------

### 8.7 查询候选路径

方法：

```python
get_candidate_paths(goal_id)
```

第一版可以直接返回本文档定义的三条路径。

后续可以扩展为基于 Neo4j 路径查询生成。

------

### 8.8 查询补救节点

方法：

```python
get_remedial_nodes(node_id)
```

用于当 AI 识别某个知识点存在困难时，查询其前置补救节点。

例如：

```text
call_stack
```

返回：

```text
parameter
return_value
```

------

## 9. Neo4j 初始化要求

需要新增初始化脚本，例如：

```text
scripts/init_neo4j.py
```

职责：

1. 连接 Neo4j。
2. 清空旧 Demo 图谱数据。
3. 创建约束。
4. 创建 KnowledgeNode。
5. 创建 LearningGoal。
6. 创建 LearningResource。
7. 创建 PREREQUISITE 关系。
8. 创建 TARGET_OF 关系。
9. 创建 HAS_RESOURCE 关系。
10. 创建 EXAMPLE_SUPPORT 关系。

脚本运行后应打印：

```text
Neo4j demo graph initialized successfully.
Inserted knowledge nodes: 15
Inserted learning goals: 1
Inserted resources: ...
Inserted relationships: ...
```

------

## 10. Neo4j 配置

Neo4j 配置必须放在 `.env` 中。

示例：

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

禁止硬编码 Neo4j 密码。

后端应通过配置模块读取环境变量。

------

## 11. FastAPI 接口影响

已有接口保持不变。

知识图谱相关接口的数据来源改为 Neo4j。

需要支持：

```text
GET /api/graph
GET /api/graph/node/{node_id}
```

如果已有接口存在，只修改内部数据来源，不修改接口路径和返回格式。

前端不需要知道底层从 SQLite 还是 Neo4j 查询。

------

## 12. 与 SQLite 的关系

SQLite 中可以保留：

```text
knowledge_nodes
knowledge_edges
learning_resources
```

作为 Demo 初始化来源或备用数据。

但在 Milestone 6 之后：

- 知识图谱页面优先从 Neo4j 查询。
- GraphService 优先使用 Neo4j。
- 路径规划模块后续应优先调用 GraphService。
- 不删除 SQLite 已有业务数据。

------

## 13. 与 AI 助手的关系

AI 不直接访问 Neo4j。

AI 输出学习状态信号，例如：

```json
{
  "knowledge_gap": "call_stack",
  "confusion_level": 0.82,
  "suggested_action": "insert_prerequisite"
}
```

后续由 AdaptationService / PathPlanner 使用 GraphService 查询 Neo4j，再决定是否插入补救节点或切换路径。

------

## 14. 知识图谱页面要求

知识图谱页面继续通过 FastAPI 获取数据。

页面需要展示：

- 所有 KnowledgeNode
- 所有 PREREQUISITE / EXAMPLE_SUPPORT 关系
- 当前学习路径节点高亮
- 当前学习节点高亮
- 点击节点查看详情

前端不得直接连接 Neo4j。

------

## 15. Codex 实现要求

Codex 实现 Milestone 6 时必须遵循以下要求：

1. 不修改系统总体架构。
2. 不删除 SQLite 已有表和数据。
3. 不修改前端页面布局。
4. 不修改已有 API 路径。
5. 只新增 Neo4j 图谱存储与查询能力。
6. 新增 Neo4j 配置必须放在 `.env`。
7. 新增 Neo4j 连接代码必须封装在后端模块中。
8. GraphService 是访问 Neo4j 的唯一业务入口。
9. 前端不得直接访问 Neo4j。
10. AI 不得直接访问 Neo4j。
11. 动态路径调整暂不在本阶段实现。
12. 如果 Neo4j 未连接，应返回清晰错误信息，而不是导致后端崩溃。

