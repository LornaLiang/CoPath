# CoPath

CoPath 是一个基于知识图谱与 AI 协同的自适应学习路径规划系统。

当前仓库完成 **Milestone 10：系统优化与演示收敛**。React 七个页面继续通过 FastAPI
读取数据；学生、画像、路径和学习记录保存在 SQLite，课程知识图谱由 Neo4j 管理，
学习助手通过 OpenAI Compatible API 生成结构化信号，LearningProfileService 根据
AI 信号与学习事件累计更新画像，PathPlanner 再通过 GraphService 进行确定性的路径选择
与调整。本阶段统一了 API 信封和异常处理，补齐页面 loading / empty / error 状态，并
加入 Demo 学生快捷切换与关键链路日志；AI、图谱和路径规划规则保持不变。

## 环境要求

- Node.js 20.19+
- Python 3.10+
- Neo4j 5.x 或更高版本

## 本地配置

先创建本地配置，并填写实际的 Neo4j 密码和 AI API Key：

```bash
cp .env.example .env
```

AI 默认调用 `https://api.openai.com/v1`。使用其他 OpenAI Compatible 服务时，修改
`OPENAI_BASE_URL`；如果服务不支持严格 JSON Schema，可将
`OPENAI_RESPONSE_FORMAT` 设置为 `json_object`。模型名称由 SQLite 的
`system_settings.model_name` 配置，Demo 默认值为 `gpt-4.1-mini`。

## 启动后端

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/init_neo4j.py
uvicorn backend.main:app --reload
```

数据库初始化脚本每次都会删除旧数据库并重新导入完整 Demo 数据。数据库文件默认创建在
`database/demo.db`，该运行文件已被 `.gitignore` 排除。

Milestone 8 为 `student_profiles` 增加独立的 `mastery_json`。FastAPI 启动时会对旧版
Demo 数据库执行幂等迁移，并从原有 `profile_json.mastery` 补齐数据，不会删除画像或
其他业务记录。

Neo4j 初始化脚本只删除带有 CoPath Demo 标识的旧图谱，不会清空同一数据库中的其他
图数据。脚本会导入 15 个知识点、1 个学习目标、15 个学习资源及其关系。

后端默认运行在 `http://127.0.0.1:8000`，健康检查地址为：

```text
http://127.0.0.1:8000/api/health
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

所有 API 均以 `/api` 开头，并统一返回 `code`、`data` 和 `message` 字段。成功请求的
`code` 为 `200`；失败请求同时使用对应 HTTP 状态码和相同数值的 `code`，`data` 为
`null`。参数校验、业务异常、404 和未处理异常均经过 FastAPI 全局异常处理器。
知识图谱接口保持为 `GET /api/graph` 和 `GET /api/graph/node/{node_id}`，内部通过
GraphService 查询 Neo4j；Neo4j 未配置或不可连接时会返回明确的 503 错误，后端本身仍
可启动并提供 SQLite 相关接口。
`POST /api/chat` 会读取学生画像、当前节点、当前路径和最近五轮对话，调用模型后将回复
与结构化学习信号写入 `dialogue_logs`，再依次更新画像和学习路径。AI 只提供信号，路径
选择、补救节点插入、跳过和重排均由规则驱动的 PathPlanner 完成。

学习画像接口：

- `GET /api/profile/{student_id}`：读取完整画像和掌握度
- `POST /api/profile/update`：应用 AI 学习状态信号
- `POST /api/profile/event`：记录 correct / wrong 事件并更新画像

原有 `GET /api/profile?student_id=...` 和 `GET /api/profile/mastery` 保持兼容。所有
掌握度与信心值都会限制在 `0.0～1.0`。

动态路径接口：

- `POST /api/path/generate`：生成推荐路径，不写数据库
- `POST /api/path/update`：应用推荐路径并写入路径切换历史
- `GET /api/path/{student_id}`：读取当前路径与最新推荐决策

PathPlanner 支持 basic、example、fast 三种策略，并综合画像掌握度、信心、学习速度、
AI 信号及学习事件决定补救节点插入、已掌握节点跳过和依赖顺序重排。所有 Neo4j 查询均
经过 GraphService，路径变化记录复用 `path_switch_logs`。

## 启动前端

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`。开发服务器会将 `/api` 请求代理到
`http://127.0.0.1:8000`。

## Demo Mode

`frontend/.env` 中设置 `VITE_DEMO_MODE=true` 后，页面顶部会显示 Tom、Alice、Bob
快捷切换器；这是默认配置。切换学生会调用现有 `POST /api/settings/student`，随后重新
读取目标、路径、画像和页面数据。设置为 `false` 并重启 Vite 即可隐藏快捷入口。

推荐完整演示流程：

1. 在顶部选择 Tom，进入“学习目标”确认“掌握递归”。
2. 打开“学习路径”，展示三种候选策略、当前路径和可解释推荐原因。
3. 进入“我的学习”，提交一次练习或向 AI 询问调用栈问题。
4. 返回“学习路径”查看补救节点、路径调整原因与切换记录。
5. 打开“学习画像”查看掌握度、信心和学习状态更新。
6. 打开“知识图谱”查看当前节点与路径高亮，再到“学习记录”核对事件、AI 信号和路径日志。
7. 用顶部入口切换 Alice / Bob，对比快速型与案例型偏好；需要复原时在“设置”中重置 Demo 数据。

后端运行日志会记录 AI 结构化信号摘要、画像更新、学习事件和路径变化，不记录 API Key
或完整用户对话内容。

前端页面路由：

- `/goals`：学习目标
- `/paths`：学习路径
- `/learning`：我的学习
- `/graph`：知识图谱
- `/profile`：学习画像
- `/records`：学习记录
- `/settings`：设置

图表统一使用 ECharts，表格使用 Ant Design Table。React 只负责展示与触发 API；
画像更新、AI 分析和路径规划不会在前端执行。学习画像与路径页面只展示后端返回的数据
和可解释决策原因。

## 项目结构

```text
CoPath/
├── backend/       # FastAPI 后端
├── database/      # SQLite schema、Demo 数据和本地数据库文件
├── docs/          # 设计文档
├── frontend/      # React + Vite 前端
├── scripts/       # SQLite 与 Neo4j 初始化脚本
└── tests/         # 测试
```
