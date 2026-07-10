# CoPath

CoPath 是一个基于知识图谱与 AI 协同的自适应学习路径规划系统。系统由 React 前端、FastAPI 后端、SQLite 业务库和 Neo4j 知识图谱组成

## Docker 启动

### 1. 环境要求

- Docker Engine / Docker Desktop
- Docker Compose v2
- 可选：OpenAI 或 OpenAI Compatible API Key

如果只是离线复现演示流程，可以使用默认 `AI_MODE=mock`，不需要真实 API Key。

### 2. 准备配置

在项目根目录创建 `.env`：

```bash
cp .env.example .env
```

根据 Docker Compose 中 Neo4j 服务的名称调整连接地址。容器内通常不要使用
`localhost` 连接 Neo4j，而应使用 compose service 名称，例如：

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_with_your_password
NEO4J_DATABASE=neo4j

AI_MODE=mock
OPENAI_API_KEY=replace_with_your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_RESPONSE_FORMAT=json_schema
```

如需调用真实模型，将 `AI_MODE` 改为 `openai`，并填写可用的 `OPENAI_API_KEY`。如果兼容
服务不支持严格 JSON Schema，可将 `OPENAI_RESPONSE_FORMAT` 设置为 `json_object`。

前端默认通过 `/api` 访问后端；Docker 交付包中如已由反向代理统一转发，一般不需要额外
修改 `frontend/.env`。

### 3. 构建并启动

如果交付包包含 `docker-compose.yml`，在项目根目录执行：

```bash
docker compose up -d --build
```

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

### 4. 初始化 Demo 数据

首次启动后初始化 SQLite 和 Neo4j 数据：

```bash
docker compose exec backend python scripts/init_db.py
docker compose exec backend python scripts/init_neo4j.py
```

如果你的 Docker 镜像入口已经自动执行初始化脚本，可以跳过这一步。重复执行
`scripts/init_db.py` 会重建 `database/demo.db` 并恢复 Demo 数据；Neo4j 初始化脚本只清理
带有 CoPath Demo 标识的图谱数据，不会清空同一 Neo4j 数据库里的其他图数据。

### 5. 访问系统

常用访问地址以 `docker-compose.yml` 的端口映射为准，推荐映射如下：

- 前端页面：`http://localhost:5173`
- 后端健康检查：`http://localhost:8000/api/health`
- 后端 API 文档：`http://localhost:8000/docs`
- Neo4j Browser：`http://localhost:7474`

所有后端 API 均以 `/api` 开头，并统一返回 `code`、`data` 和 `message` 字段。

### 6. 停止与重启

停止容器：

```bash
docker compose down
```

保留数据并重启：

```bash
docker compose up -d
```

如果需要完全恢复演示数据，可以在前端“设置”页面点击“重置 Demo 数据”，或重新执行：

```bash
docker compose exec backend python scripts/init_db.py
```

## 数据说明

当前系统运行时使用的 SQLite 数据库是：

```text
database/demo.db
```

前端聊天、练习提交、目标选择、路径切换等操作会写入 `database/demo.db`。该文件是运行期
数据文件，已被 `.gitignore` 排除。

`database/copath.db` 是早期测试运行产生的历史 SQLite 数据库快照，仅用于测试数据留存与
对比；当前后端不会读取或写入 `copath.db`。打包交付时如果保留该文件，请在交付说明中
标注它是测试数据。

Neo4j 用于保存课程知识图谱。图谱接口包括：

- `GET /api/graph`
- `GET /api/graph/node/{node_id}`

Neo4j 未配置或不可连接时，图谱接口会返回明确的 503 错误，后端本身仍可启动并提供
SQLite 相关接口。

## 演示流程

`frontend/.env` 中设置 `VITE_DEMO_MODE=true` 后，页面顶部会显示 Tom、Alice、Bob 快捷
切换器；这是默认演示配置。

推荐演示路径：

1. 在顶部选择 Tom，进入“学习目标”确认“掌握递归”。
2. 打开“学习路径”，查看三种候选策略、当前路径和推荐原因。
3. 进入“我的学习”，提交一次练习或向 AI 学习助手提问。
4. 返回“学习路径”，查看路径调整建议与切换记录。
5. 打开“学习画像”，查看掌握度、信心和学习状态变化。
6. 打开“知识图谱”和“学习记录”，核对当前节点、路径高亮、事件和对话日志。
7. 切换 Alice / Bob，对比不同学习偏好下的路径策略。

后端日志会记录 AI 结构化信号摘要、画像更新、学习事件和路径变化，不记录 API Key 或完整
用户对话内容。

## 本地开发补充

本地开发适合调试代码；面向他人复现时优先使用 Docker 流程。

### 后端

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python scripts/init_neo4j.py
uvicorn backend.main:app --reload
```

本地后端默认运行在：

```text
http://127.0.0.1:8000
```

### 前端

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

本地前端默认运行在：

```text
http://127.0.0.1:5173
```

Vite 开发服务器会将 `/api` 请求代理到 `http://127.0.0.1:8000`。

## 页面路由

- `/goals`：学习目标
- `/paths`：学习路径
- `/learning`：我的学习
- `/graph`：知识图谱
- `/profile`：学习画像
- `/records`：学习记录
- `/settings`：设置

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
