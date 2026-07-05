# CoPath

CoPath 是一个基于知识图谱与 AI 协同的自适应学习路径规划系统。

当前仓库完成 **Milestone 4：React 页面**，包含完整 FastAPI API、SQLite Demo 数据，
以及学习目标、学习路径、我的学习、知识图谱、学习画像、学习记录、设置七个 React 页面。
前端页面当前使用与 API 结构一致的 Mock 数据；真实接口联调将在 Milestone 5 完成。

## 环境要求

- Node.js 20.19+
- Python 3.10+

## 启动后端

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.init_db
uvicorn backend.main:app --reload
```

数据库初始化脚本可重复执行，不会重复插入 Demo 数据。数据库文件默认创建在
`database/copath.db`。

后端默认运行在 `http://127.0.0.1:8000`，健康检查地址为：

```text
http://127.0.0.1:8000/api/health
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

所有 API 均以 `/api` 开头，并统一返回 `success`、`data` 和 `message` 字段。
`POST /api/chat` 当前仅返回占位响应，真实 AI 能力将在 Milestone 7 实现。

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`。开发服务器会将 `/api` 请求代理到
`http://127.0.0.1:8000`。

前端页面路由：

- `/goals`：学习目标
- `/paths`：学习路径
- `/learning`：我的学习
- `/graph`：知识图谱
- `/profile`：学习画像
- `/records`：学习记录
- `/settings`：设置

图表统一使用 ECharts，表格使用 Ant Design Table。当前按钮操作提供 Mock 反馈，
不会在 React 中执行画像更新、AI 分析或路径规划。

## 项目结构

```text
CoPath/
├── backend/       # FastAPI 后端
├── database/      # SQLite schema、Demo 数据和本地数据库文件
├── docs/          # 设计文档
├── frontend/      # React + Vite 前端
├── scripts/       # 项目脚本
└── tests/         # 测试
```
