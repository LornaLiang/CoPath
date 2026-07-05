# CoPath 数据库设计说明

## 1. 数据库选择

CoPath 原型系统使用 SQLite 作为后端数据库。

原因：

- 部署简单
- 无需额外数据库服务
- 适合课程 Demo 和原型系统
- 后续可迁移至 PostgreSQL / MySQL / Neo4j

---

## 2. 数据库职责

数据库用于存储：

- 学生信息
- 学习画像
- 知识图谱
- 学习路径
- 学习事件
- AI 对话记录
- 路径调整记录
- 学习资源
- 系统设置

---

## 3. 核心数据表

### 3.1 students：学生表

存储学生基础信息。

| 字段            | 类型             | 说明         |
| --------------- | ---------------- | ------------ |
| student_id      | TEXT PRIMARY KEY | 学生ID       |
| name            | TEXT             | 学生姓名     |
| avatar          | TEXT             | 头像地址     |
| current_goal_id | TEXT             | 当前学习目标 |
| created_at      | TEXT             | 创建时间     |

---

### 3.2 student_profiles：学生画像表

存储学生动态学习画像。

| 字段                | 类型                              | 说明                             |
| ------------------- | --------------------------------- | -------------------------------- |
| profile_id          | INTEGER PRIMARY KEY AUTOINCREMENT | 画像ID                           |
| student_id          | TEXT                              | 学生ID                           |
| learning_speed      | TEXT                              | 学习速度：slow / medium / fast   |
| learning_preference | TEXT                              | 学习偏好：basic / example / fast |
| confidence          | REAL                              | 学习信心，0-1                    |
| profile_json        | TEXT                              | 扩展画像 JSON                    |
| updated_at          | TEXT                              | 更新时间                         |

示例 `profile_json`：

```json
{
  "mastery": {
    "function": 0.75,
    "return_value": 0.55,
    "call_stack": 0.30,
    "recursion": 0.10
  },
  "weak_points": ["call_stack", "return_value"],
  "recent_state": "confused"
}
```

### 3.3 knowledge_nodes：知识点表



存储课程知识点。

| 字段        | 类型             | 说明       |
| ----------- | ---------------- | ---------- |
| node_id     | TEXT PRIMARY KEY | 知识点ID   |
| name        | TEXT             | 知识点名称 |
| description | TEXT             | 知识点说明 |
| difficulty  | INTEGER          | 难度等级   |
| chapter     | TEXT             | 所属章节   |

------

### 3.4 knowledge_edges：知识依赖表

存储知识点之间的依赖关系。

| 字段      | 类型                              | 说明                        |
| --------- | --------------------------------- | --------------------------- |
| edge_id   | INTEGER PRIMARY KEY AUTOINCREMENT | 关系ID                      |
| source_id | TEXT                              | 前置知识点                  |
| target_id | TEXT                              | 后继知识点                  |
| relation  | TEXT                              | 关系类型，默认 prerequisite |

例如：

```text
函数调用栈 → 递归
```

表示学习递归前需要掌握函数调用栈。

------

### 3.5 learning_goals：学习目标表

存储可选择的学习目标。

| 字段              | 类型             | 说明         |
| ----------------- | ---------------- | ------------ |
| goal_id           | TEXT PRIMARY KEY | 目标ID       |
| target_node_id    | TEXT             | 对应知识点   |
| title             | TEXT             | 目标名称     |
| description       | TEXT             | 目标说明     |
| recommended_level | TEXT             | 推荐学习阶段 |

------

### 3.6 learning_paths：学习路径表

存储候选路径和当前路径。

| 字段       | 类型             | 说明                                    |
| ---------- | ---------------- | --------------------------------------- |
| path_id    | TEXT PRIMARY KEY | 路径ID                                  |
| student_id | TEXT             | 学生ID                                  |
| goal_id    | TEXT             | 学习目标ID                              |
| path_type  | TEXT             | basic / example / fast                  |
| path_name  | TEXT             | 路径名称                                |
| nodes_json | TEXT             | 路径知识点列表                          |
| is_current | INTEGER          | 是否当前路径，1 是，0 否                |
| status     | TEXT             | planned / active / completed / switched |
| reason     | TEXT             | 推荐原因                                |
| created_at | TEXT             | 创建时间                                |

示例 `nodes_json`：

```json
["function", "parameter", "return_value", "call_stack", "recursion"]
```

------

### 3.7 learning_events：学习事件表

记录学生学习行为。

| 字段       | 类型                              | 说明                          |
| ---------- | --------------------------------- | ----------------------------- |
| event_id   | INTEGER PRIMARY KEY AUTOINCREMENT | 事件ID                        |
| student_id | TEXT                              | 学生ID                        |
| node_id    | TEXT                              | 知识点ID                      |
| event_type | TEXT                              | learn / quiz / finish / pause |
| result     | TEXT                              | correct / wrong / completed   |
| score      | REAL                              | 得分                          |
| time_spent | INTEGER                           | 学习时长，单位秒              |
| created_at | TEXT                              | 创建时间                      |

------

### 3.8 dialogue_logs：AI 对话记录表

记录学生与 AI 助手的交流。

| 字段                  | 类型                              | 说明              |
| --------------------- | --------------------------------- | ----------------- |
| dialogue_id           | INTEGER PRIMARY KEY AUTOINCREMENT | 对话ID            |
| student_id            | TEXT                              | 学生ID            |
| node_id               | TEXT                              | 当前知识点        |
| user_message          | TEXT                              | 学生输入          |
| ai_response           | TEXT                              | AI 回复           |
| extracted_signal_json | TEXT                              | AI 提取的学习状态 |
| created_at            | TEXT                              | 创建时间          |

示例 `extracted_signal_json`：

```json
{
  "knowledge_gap": "call_stack",
  "confusion_level": 0.8,
  "learning_preference": "example",
  "suggested_action": "insert_prerequisite"
}
```

------

### 3.9 path_switch_logs：路径切换记录表

记录系统动态调整路径的过程。

| 字段                | 类型                              | 说明                            |
| ------------------- | --------------------------------- | ------------------------------- |
| switch_id           | INTEGER PRIMARY KEY AUTOINCREMENT | 切换ID                          |
| student_id          | TEXT                              | 学生ID                          |
| old_path_id         | TEXT                              | 原路径ID                        |
| new_path_id         | TEXT                              | 新路径ID                        |
| trigger_type        | TEXT                              | dialogue / quiz / time / manual |
| trigger_signal_json | TEXT                              | 触发信号                        |
| reason              | TEXT                              | 切换原因                        |
| created_at          | TEXT                              | 创建时间                        |

------

### 3.10 learning_resources：学习资源表

存储知识点对应的学习资源。

| 字段          | 类型             | 说明                           |
| ------------- | ---------------- | ------------------------------ |
| resource_id   | TEXT PRIMARY KEY | 资源ID                         |
| node_id       | TEXT             | 关联知识点                     |
| title         | TEXT             | 资源标题                       |
| resource_type | TEXT             | video / text / exercise / code |
| url           | TEXT             | 资源地址                       |
| content       | TEXT             | 文本内容或说明                 |
| difficulty    | INTEGER          | 资源难度                       |

------

### 3.11 system_settings：系统设置表

存储系统配置。

| 字段          | 类型             | 说明   |
| ------------- | ---------------- | ------ |
| setting_key   | TEXT PRIMARY KEY | 设置项 |
| setting_value | TEXT             | 设置值 |

例如：

```text
theme = light
llm_provider = openai
model_name = gpt-4.1-mini
```

------

## 4. 表关系说明

核心关系：

```text
students
  ├── student_profiles
  ├── learning_paths
  ├── learning_events
  ├── dialogue_logs
  └── path_switch_logs

knowledge_nodes
  ├── knowledge_edges
  ├── learning_goals
  ├── learning_resources
  └── learning_events

learning_goals
  └── learning_paths
```

------

## 5. Demo 数据设计

第一版 Demo 建议预置 3 个学生。

### Tom

特点：

- 基础薄弱
- 学习速度中等
- 调用栈掌握较差
- 推荐基础补全路径

### Alice

特点：

- 基础较好
- 学习速度快
- 推荐快速提升路径

### Bob

特点：

- 喜欢案例
- 理论理解较弱
- 推荐案例驱动路径

------

## 6. Demo 课程

第一版课程建议使用：

```text
Python 基础：递归学习
```

核心知识点：

```text
变量
表达式
条件语句
循环
函数
参数传递
返回值
调用栈
递归
树形递归
DFS
回溯
```

------

## 7. 最小可运行数据

系统启动时至少需要：

- 3 个学生
- 12 个知识点
- 15 条知识依赖关系
- 1 个学习目标：掌握递归
- 3 条候选学习路径
- 若干学习事件
- 若干 AI 对话记录
- 至少 1 条路径切换记录

------

## 8. 设计原则

1. 数据库只负责存储，不负责路径规划。
2. 路径规划逻辑放在后端 Planner 模块。
3. AI 只生成学习状态信号，不直接修改数据库。
4. 所有 JSON 字段必须保持结构稳定。
5. Demo 数据必须能支撑前端所有页面展示。
6. 后续可将知识图谱迁移至 Neo4j。
7. 后续可将学习资源与对话记忆接入向量数据库。

