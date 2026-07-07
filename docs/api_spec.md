

# CoPath API 设计说明

## 1. API 总体原则

CoPath 后端使用 FastAPI 提供 RESTful API。

所有 API 必须返回 JSON。

前端只通过 API 与后端通信，不直接访问数据库。

---

## 2. 通用返回格式

### 成功返回

```json
{
  "success": true,
  "data": {},
  "message": "ok"
}
```

### 失败返回

```json
{
  "success": false,
  "data": null,
  "message": "错误信息"
}
```

------

## 3. 健康检查

### GET `/api/health`

用于检测后端服务状态。

返回：

```json
{
  "success": true,
  "data": {
    "status": "running",
    "database": "connected",
    "ai": "available"
  },
  "message": "ok"
}
```

------

# 4. 学生相关 API

## 4.1 获取当前学生

### GET `/api/students/current`

返回当前 Demo 学生信息。

```json
{
  "student_id": "S001",
  "name": "Tom",
  "avatar": "/assets/avatar/tom.png",
  "current_goal_id": "G001"
}
```

------

## 4.2 获取学生列表

### GET `/api/students`

用于设置页面切换 Demo 学生。

```json
[
  {
    "student_id": "S001",
    "name": "Tom",
    "learning_speed": "medium",
    "learning_preference": "basic"
  }
]
```

------

## 4.3 切换当前学生

### POST `/api/settings/student`

请求：

```json
{
  "student_id": "S002"
}
```

返回：

```json
{
  "current_student_id": "S002"
}
```

------

# 5. 学习目标 API

## 5.1 获取学习目标列表

### GET `/api/goals`

返回可选学习目标。

```json
[
  {
    "goal_id": "G001",
    "title": "掌握递归",
    "target_node_id": "recursion",
    "description": "理解递归思想并能编写简单递归程序",
    "recommended_level": "intermediate"
  }
]
```

------

## 5.2 选择学习目标

### POST `/api/goals/select`

请求：

```json
{
  "student_id": "S001",
  "goal_id": "G001"
}
```

处理逻辑：

1. 更新学生当前目标。
2. 读取知识图谱。
3. 生成三条候选路径。
4. 根据学生画像推荐当前路径。
5. 写入 `learning_paths`。

返回：

```json
{
  "goal_id": "G001",
  "target_node_id": "recursion",
  "candidate_paths": [],
  "current_path": {}
}
```

------

# 6. 学习路径 API

## 6.1 获取当前路径

### GET `/api/paths/current?student_id=S001`

返回当前学习路径。

```json
{
  "path_id": "P001",
  "path_name": "基础补全路径",
  "path_type": "basic",
  "goal_id": "G001",
  "current_node_id": "call_stack",
  "status": "active",
  "reason": "学生调用栈掌握较弱，建议先补充前置知识。",
  "nodes": [
    {
      "node_id": "function",
      "name": "函数",
      "status": "completed"
    },
    {
      "node_id": "call_stack",
      "name": "调用栈",
      "status": "learning"
    },
    {
      "node_id": "recursion",
      "name": "递归",
      "status": "pending"
    }
  ]
}
```

------

## 6.2 获取候选路径

### GET `/api/paths/candidates?student_id=S001&goal_id=G001`

返回至少三条路径。

```json
[
  {
    "path_id": "P001",
    "path_type": "basic",
    "path_name": "基础补全路径",
    "is_current": true,
    "nodes": []
  },
  {
    "path_id": "P002",
    "path_type": "example",
    "path_name": "案例驱动路径",
    "is_current": false,
    "nodes": []
  },
  {
    "path_id": "P003",
    "path_type": "fast",
    "path_name": "快速提升路径",
    "is_current": false,
    "nodes": []
  }
]
```

------

## 6.3 手动切换路径

### POST `/api/paths/switch`

该接口只执行真实切换。前端手动选择路径时应先调用
`POST /api/path/evaluate-switch`，根据评估结果由用户确认后再执行切换或覆盖。

请求：

```json
{
  "student_id": "S001",
  "new_path_id": "P002",
  "reason": "学生希望通过案例方式学习。"
}
```

处理逻辑：

1. 将旧路径 `is_current` 设置为 0。
2. 将新路径 `is_current` 设置为 1。
3. 写入 `path_switch_logs`。

返回：

```json
{
  "old_path_id": "P001",
  "new_path_id": "P002",
  "reason": "学生希望通过案例方式学习。"
}
```

------

## 6.4 获取路径切换记录

### GET `/api/paths/switch-logs?student_id=S001`

返回：

```json
[
  {
    "switch_id": 1,
    "old_path_name": "案例驱动路径",
    "new_path_name": "基础补全路径",
    "trigger_type": "dialogue",
    "reason": "AI 识别学生对调用栈存在明显困惑。",
    "created_at": "2026-07-05 20:00:00"
  }
]
```

------

## 6.5 生成路径调整建议

### POST `/api/path/suggest-adjustment`

只生成待确认建议，不切换当前路径，不写入 `path_switch_logs`。

请求：

```json
{
  "student_id": "S001",
  "goal_id": "G001",
  "trigger_type": "dialogue",
  "trigger_signal": {
    "knowledge_gap": "call_stack",
    "confusion_level": 0.82
  }
}
```

返回：

```json
{
  "suggestion_id": 1,
  "student_id": "S001",
  "current_path_id": "P003",
  "suggested_path_type": "basic",
  "suggested_path_name": "基础补全路径",
  "reason": "call_stack mastery 较低，建议切换到基础补全路径。",
  "risk_level": "medium",
  "status": "pending"
}
```

------

## 6.6 确认路径调整建议

### POST `/api/path/confirm-adjustment`

用户点击“接受切换”后调用。该接口才会执行 PathPlanner 调整，并在真实切换时写入
`path_switch_logs`。

请求：

```json
{
  "student_id": "S001",
  "suggestion_id": 1
}
```

返回：

```json
{
  "suggestion": {
    "suggestion_id": 1,
    "status": "applied"
  },
  "path_adjusted": true,
  "adjustment": {}
}
```

------

## 6.7 拒绝路径调整建议

### POST `/api/path/reject-adjustment`

用户点击“暂不切换”后调用。该接口只记录 `rejected` 状态，不修改当前路径。

请求：

```json
{
  "student_id": "S001",
  "suggestion_id": 1
}
```

------

## 6.8 手动切换前评估

### POST `/api/path/evaluate-switch`

用户手动选择其他路径时先调用该接口。`force=false` 时只评估不切换；
`force=true` 表示用户在风险提示后仍然切换，系统记录 `overridden` 状态。

请求：

```json
{
  "student_id": "S001",
  "new_path_id": "P003",
  "force": false
}
```

返回：

```json
{
  "recommended": false,
  "recommended_path_type": "basic",
  "risk_level": "high",
  "not_recommended_reason": "当前画像更匹配基础补全路径",
  "alternative_action": "先按基础补全路径学习",
  "requires_confirmation": true,
  "switched": false
}
```

------

# 7. 我的学习 API

## 7.1 获取当前学习内容

### GET `/api/learning/current?student_id=S001`

返回当前学习节点、内容和路径进度。

```json
{
  "current_node": {
    "node_id": "call_stack",
    "name": "调用栈",
    "description": "调用栈用于记录函数调用过程。"
  },
  "path_progress": {
    "completed": 2,
    "total": 5,
    "percent": 40
  },
  "resources": []
}
```

------

## 7.2 提交学习事件

### POST `/api/learning/event`

请求：

```json
{
  "student_id": "S001",
  "node_id": "call_stack",
  "event_type": "quiz",
  "result": "wrong",
  "score": 0.4,
  "time_spent": 180
}
```

返回：

```json
{
  "event_saved": true,
  "profile_updated": true,
  "path_adjusted": false,
  "new_path": null,
  "adjustment_suggestion": {
    "status": "pending",
    "suggested_path_type": "basic"
  }
}
```

------

## 7.3 提交学习反馈

### POST `/api/learning/feedback`

请求：

```json
{
  "student_id": "S001",
  "node_id": "call_stack",
  "feedback_type": "still_confused"
}
```

反馈类型：

- understood
- still_confused
- need_example
- lower_difficulty
- next_node

返回：

```json
{
  "feedback_saved": true,
  "suggested_action": "insert_prerequisite",
  "message": "建议补充函数返回值知识点。"
}
```

------

## 7.4 获取学习事件列表

### GET `/api/learning/events?student_id=S001`

返回：

```json
[
  {
    "event_id": 1,
    "node_name": "调用栈",
    "event_type": "quiz",
    "result": "wrong",
    "score": 0.4,
    "time_spent": 180,
    "created_at": "2026-07-05 20:00:00"
  }
]
```

------

## 7.5 获取学习总结

### GET `/api/learning/summary?student_id=S001`

返回：

```json
{
  "summary": "该学生当前主要薄弱点是调用栈和返回值，建议继续采用基础补全路径。",
  "weak_points": ["调用栈", "返回值"],
  "next_suggestion": "先完成调用栈补救练习，再进入递归。"
}
```

------

# 8. AI 对话 API

## 8.1 获取对话记录

### GET `/api/dialogues?student_id=S001`

返回：

```json
[
  {
    "dialogue_id": 1,
    "node_id": "call_stack",
    "user_message": "为什么函数返回后还能继续执行？",
    "ai_response": "因为调用栈会保存函数调用前的位置...",
    "extracted_signal": {
      "knowledge_gap": "call_stack",
      "confusion_level": 0.8
    },
    "created_at": "2026-07-05 20:00:00"
  }
]
```

------

## 8.2 发送消息给 AI

### POST `/api/chat`

请求：

```json
{
  "student_id": "S001",
  "node_id": "call_stack",
  "message": "为什么函数返回后还能继续执行？"
}
```

处理逻辑：

1. 读取学生画像。
2. 读取当前学习路径。
3. 读取当前知识节点。
4. 调用 LLM。
5. 提取结构化学习状态。
6. 写入 `dialogue_logs`。
7. 更新学习画像。
8. 判断是否需要生成路径调整建议。
9. 如需调整，写入 `path_adjustment_suggestions`，状态为 `pending`。

返回：

```json
{
  "reply": "因为调用栈会保存每次函数调用的位置...",
  "signal": {
    "knowledge_gap": "call_stack",
    "confusion_level": 0.8,
    "learning_preference": "example",
    "suggested_action": "insert_prerequisite"
  },
  "profile_updated": true,
  "path_adjusted": false,
  "adjustment": null,
  "adjustment_suggestion": {
    "suggestion_id": 1,
    "suggested_path_type": "basic",
    "suggested_path_name": "基础补全路径",
    "reason": "检测到学生对调用栈理解不足，建议切换到基础补全路径。",
    "risk_level": "medium",
    "status": "pending"
  }
}
```

------

# 9. 知识图谱 API

## 9.1 获取知识图谱

### GET `/api/graph?student_id=S001`

返回：

```json
{
  "nodes": [
    {
      "id": "function",
      "name": "函数",
      "difficulty": 3,
      "status": "completed"
    }
  ],
  "edges": [
    {
      "source": "function",
      "target": "call_stack",
      "relation": "prerequisite"
    }
  ],
  "current_path_nodes": ["function", "call_stack", "recursion"],
  "current_node": "call_stack"
}
```

------

## 9.2 获取知识点详情

### GET `/api/graph/node/{node_id}`

返回：

```json
{
  "node_id": "call_stack",
  "name": "调用栈",
  "description": "调用栈用于管理函数调用关系。",
  "difficulty": 4,
  "chapter": "函数与递归",
  "prerequisites": [],
  "next_nodes": [],
  "resources": []
}
```

------

# 10. 学习画像 API

## 10.1 获取学习画像

### GET `/api/profile?student_id=S001`

返回：

```json
{
  "student_id": "S001",
  "learning_speed": "medium",
  "learning_preference": "basic",
  "confidence": 0.62,
  "current_goal": "掌握递归",
  "current_path": "基础补全路径",
  "weak_points": ["调用栈", "返回值"],
  "recent_state": "confused"
}
```

------

## 10.2 获取知识掌握度

### GET `/api/profile/mastery?student_id=S001`

返回：

```json
[
  {
    "node_id": "function",
    "name": "函数",
    "mastery": 0.75
  },
  {
    "node_id": "call_stack",
    "name": "调用栈",
    "mastery": 0.30
  }
]
```

------

# 11. 学习资源 API

## 11.1 获取当前节点资源

### GET `/api/resources/current?student_id=S001`

返回：

```json
[
  {
    "resource_id": "R001",
    "title": "调用栈可视化讲解",
    "resource_type": "text",
    "url": "",
    "content": "调用栈用于记录函数调用顺序。",
    "difficulty": 3
  }
]
```

------

# 12. 设置 API

## 12.1 获取系统设置

### GET `/api/settings`

返回：

```json
{
  "theme": "light",
  "llm_provider": "openai",
  "model_name": "gpt-4.1-mini"
}
```

------

## 12.2 重置 Demo 数据

### POST `/api/settings/reset-demo`

处理逻辑：

1. 清空数据库。
2. 执行 `schema.sql`。
3. 执行 `seed_data.sql`。
4. 恢复默认学生。

返回：

```json
{
  "reset": true,
  "message": "Demo 数据已重置。"
}
```

------

# 13. API 实现要求

1. 所有接口路径以 `/api` 开头。
2. 所有接口返回统一 JSON 结构。
3. API 层不得直接访问数据库。
4. API 层调用 Service 层。
5. Service 层调用 Planner / Graph / AI / Database 模块。
6. 所有请求参数使用 Pydantic Model 校验。
7. 所有异常必须返回清晰错误信息。
8. Demo 阶段可以不做登录认证。
9. 当前学生可以通过 `student_id` 参数传递。
10. 后续扩展时再加入 JWT 登录认证。
