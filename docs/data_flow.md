# CoPath 数据流设计说明

## 1. 数据流总览

CoPath 的核心数据流是：

```text
学生操作
  ↓
React 前端
  ↓
FastAPI API
  ↓
Service 层
  ↓
SQLite / NetworkX / AI Assistant
  ↓
状态更新
  ↓
返回 JSON
  ↓
前端刷新页面
```

前端只负责展示和触发操作，不负责路径规划、画像更新和 AI 分析。

------

## 2. 核心运行流程

```text
选择学习目标
  ↓
读取知识图谱
  ↓
生成三条候选路径
  ↓
根据学生画像推荐初始路径
  ↓
学生开始学习
  ↓
学生与 AI 对话 / 完成测验 / 提交反馈
  ↓
AI 提取学习状态信号
  ↓
更新学生画像
  ↓
判断是否需要路径调整
  ↓
如需要，生成待确认路径调整建议
  ↓
用户确认 / 拒绝 / 覆盖
  ↓
确认后才执行真实路径切换并记录切换原因
  ↓
前端展示最新路径、画像和学习记录
```

------

## 3. 学习目标选择数据流

### 触发

学生在“学习目标”页面选择目标。

### 数据流

```text
React
POST /api/goals/select
  ↓
GoalService
  ↓
更新 students.current_goal_id
  ↓
PathPlanner 读取 knowledge_nodes / knowledge_edges
  ↓
生成 basic / example / fast 三条路径
  ↓
写入 learning_paths
  ↓
返回当前目标与候选路径
```

### 写入表

- students
- learning_paths

### 前端刷新

- 学习目标页面
- 学习路径页面

------

## 4. 学习路径生成数据流

### 触发

选择学习目标后自动触发。

### 数据流

```text
PathPlanner
  ↓
读取 knowledge_edges
  ↓
使用 NetworkX 构建知识图谱
  ↓
根据目标节点生成候选路径
  ↓
结合 student_profiles 进行路径排序
  ↓
写入 learning_paths
```

### 输出

至少三条路径：

- 基础补全路径
- 案例驱动路径
- 快速提升路径

### 注意

LLM 不直接生成学习路径。

LLM 只参与解释和学习状态分析。

------

## 5. 我的学习页面数据流

### 触发

学生进入“我的学习”页面。

### 数据流

```text
React
GET /api/learning/current
  ↓
LearningService
  ↓
读取当前学生 current path
  ↓
读取当前学习节点
  ↓
读取 learning_resources
  ↓
返回学习内容、当前节点、路径进度
```

### 读取表

- students
- learning_paths
- knowledge_nodes
- learning_resources

------

## 6. AI 对话数据流

### 触发

学生向 AI 助手发送问题。

### 数据流

```text
React
POST /api/chat
  ↓
ChatService
  ↓
读取当前学生画像
  ↓
读取当前学习节点
  ↓
读取当前学习路径
  ↓
调用 LLM
  ↓
生成自然语言回复
  ↓
生成结构化学习状态信号
  ↓
写入 dialogue_logs
  ↓
调用 ProfileService 更新学生画像
  ↓
调用 PathCollaborationService 判断是否需要调整路径
  ↓
返回 AI 回复、学习状态信号、待确认路径建议
```

### 写入表

- dialogue_logs
- student_profiles
- path_adjustment_suggestions（仅当触发路径调整建议）
- path_switch_logs（仅当用户确认后真正执行切换）

### AI 输出结构

```json
{
  "reply": "你现在主要困惑的是函数返回后程序如何继续执行...",
  "signal": {
    "knowledge_gap": "call_stack",
    "confusion_level": 0.8,
    "learning_preference": "example",
    "suggested_action": "insert_prerequisite"
  }
}
```

------

## 7. 学习事件数据流

### 触发

学生完成学习、测验、反馈或进入下一节点。

### 数据流

```text
React
POST /api/learning/event
  ↓
LearningService
  ↓
写入 learning_events
  ↓
ProfileService 更新掌握度、速度、信心
  ↓
PathCollaborationService 判断是否需要生成路径调整建议
  ↓
返回最新画像、路径状态和待确认建议
```

### 写入表

- learning_events
- student_profiles
- path_adjustment_suggestions（如果触发路径调整建议）

------

## 8. 学习画像更新数据流

### 触发来源

- AI 对话信号
- 测验结果
- 学习反馈
- 学习时长

### 数据流

```text
ProfileService
  ↓
读取旧 profile_json
  ↓
合并新信号
  ↓
更新 mastery / weak_points / confidence / preference
  ↓
写回 student_profiles
```

### 示例

学生连续询问调用栈问题：

```json
{
  "knowledge_gap": "call_stack",
  "confusion_level": 0.8
}
```

更新后：

```json
{
  "mastery": {
    "call_stack": 0.25
  },
  "weak_points": ["call_stack"]
}
```

------

## 9. 动态路径调整数据流

### 触发条件

满足任意一种：

- 当前知识点连续答错
- AI 识别困惑程度较高
- 学生主动请求降低难度
- 学习速度明显慢于预期
- 当前路径与学习偏好不匹配

### 数据流

```text
PathCollaborationService
  ↓
读取 student_profiles
  ↓
读取 current learning_path
  ↓
读取 knowledge_graph
  ↓
判断是否需要切换路径 / 插入补救节点 / 跳过节点
  ↓
生成 pending 路径调整建议
  ↓
前端展示建议卡片和风险等级
  ↓
用户接受 / 拒绝 / 查看其他路径
  ↓
用户接受后调用 PathPlanner 执行调整
  ↓
真实切换时写入 path_switch_logs
```

### 路径调整类型

- switch_path：切换路径
- insert_node：插入补救知识点
- skip_node：跳过已掌握节点
- reorder_nodes：调整节点顺序

### 协同状态

- pending：系统只生成建议，等待用户确认。
- applied：用户接受建议后已执行路径调整。
- rejected：用户选择暂不切换。
- overridden：系统不建议切换，但用户仍然手动切换。

------

## 10. 知识图谱页面数据流

### 触发

进入“知识图谱”页面。

### 数据流

```text
React
GET /api/graph
  ↓
GraphService
  ↓
读取 knowledge_nodes
  ↓
读取 knowledge_edges
  ↓
读取 current path
  ↓
返回节点、边、当前路径高亮信息
```

### 返回结构

```json
{
  "nodes": [],
  "edges": [],
  "current_path_nodes": [],
  "current_node": "call_stack"
}
```

------

## 11. 学习记录页面数据流

### 触发

进入“学习记录”页面。

### 数据流

```text
React
GET /api/learning/events
GET /api/dialogues
GET /api/paths/switch-logs
  ↓
对应 Service
  ↓
读取学习事件、对话、路径切换记录
  ↓
返回表格数据
```

------

## 12. 设置页面数据流

### 学生切换

```text
React
POST /api/settings/student
  ↓
SettingsService
  ↓
更新当前演示学生
  ↓
前端重新请求所有当前学生数据
```

### Demo 数据重置

```text
React
POST /api/settings/reset-demo
  ↓
DatabaseService
  ↓
清空 demo.db
  ↓
重新执行 seed_data
  ↓
返回初始化结果
```

------

## 13. 数据一致性原则

1. 当前学生只允许有一条 `is_current = 1` 的学习路径。
2. 只有真正执行过的路径切换才写入 `path_switch_logs`。
3. AI 对话必须写入 `dialogue_logs`。
4. 学习行为必须写入 `learning_events`。
5. 学生画像更新必须写入 `student_profiles`。
6. 前端不能直接修改路径状态。
7. AI 和系统不能绕过用户确认直接切换学习路径。
7. 所有状态变化必须经过后端 Service 层。

------

## 14. Codex 实现要求

Codex 实现时必须遵循：

1. API 层只接收请求和返回结果。
2. Service 层处理业务逻辑。
3. Planner 层处理路径生成与最终执行调整。
4. AI 层只负责调用模型和解析输出。
5. 协同路径调整由 PathCollaborationService 生成建议并记录用户决策。
5. Database 层只负责数据库连接和持久化。
6. 前端通过 Axios 调用 API，不直接写业务逻辑。


