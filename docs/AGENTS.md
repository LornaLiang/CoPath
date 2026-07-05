# CoPath 开发规范（AGENTS）

## 项目简介

CoPath 是一个基于知识图谱和 AI 协同的自适应学习路径规划系统。

本项目的核心目标不是开发一个聊天机器人，而是构建一个能够根据学生学习过程动态调整学习路径的智慧教育系统。

AI 助手只是系统中的一个模块，而不是整个系统。

---

# 技术栈

前端

- React
- Vite
- Ant Design
- ECharts
- Axios

后端

- FastAPI
- SQLAlchemy
- SQLite
- NetworkX

AI

- OpenAI Compatible API
- Prompt Engineering
- JSON Structured Output

数据库

- SQLite

开发环境

- WSL2
- VS Code

---

# 开发原则

所有开发必须遵循以下原则。

## 1

前后端彻底分离。

React 只负责界面展示。

所有业务逻辑必须放在 FastAPI。

---

## 2

路径规划逻辑只能放在后端。

React 不允许参与路径规划。

---

## 3

所有接口统一返回 JSON。

---

## 4

模块化开发。

禁止出现超大文件。

每个模块职责单一。

---

## 5

数据库只能通过 Service 层访问。

API 不允许直接操作数据库。

---

## 6

所有密钥必须存放于 .env。

禁止硬编码 API Key。

---

# 项目目录

CoPath/

frontend/

backend/

database/

docs/

scripts/

tests/

---

# 后端目录

backend/

api/

services/

models/

planner/

graph/

ai/

database/

utils/

main.py

---

# 前端目录

frontend/src/

pages/

components/

hooks/

services/

layouts/

router/

assets/

---

# 系统模块

系统包含以下模块：

学习目标

知识图谱

路径规划

AI 学习助手

学习画像

动态路径调整

学习记录

---

# 路径规划原则

每个学习目标至少生成三条学习路径。

例如：

基础补全路径

案例驱动路径

快速学习路径

禁止仅生成唯一学习路径。

---

# AI 工作原则

AI 负责：

- 回答学生问题
- 分析学生对话
- 提取学习状态
- 给出调整建议
- 解释路径调整原因

AI 不负责：

- 决定学习路径
- 修改数据库
- 修改知识图谱

路径调整必须由系统规划模块完成。

---

# 学习画像

学习画像至少包含：

知识掌握程度

学习速度

学习偏好

学习信心

当前学习路径

最近学习状态

---

# 数据库

SQLite

核心数据表：

students

knowledge_nodes

knowledge_edges

learning_paths

student_profiles

learning_events

dialogue_logs

path_switch_logs

---

# 页面

学习目标

学习路径

知识图谱

学习画像

学习记录

AI助手

设置

---

# UI风格

现代

简洁

科技感

蓝白配色

支持响应式布局

图表统一使用 ECharts。

UI 使用 Ant Design。

---

# Commit规范

feat:

fix:

refactor:

docs:

style:

test:

例如：

feat: 完成学习路径规划模块

fix: 修复知识图谱查询错误

docs: 更新系统设计文档

---

# 重要要求

不得随意修改系统架构。

若认为架构需要调整，应先提出建议，再等待确认。

不得擅自增加系统模块。

不得擅自删除已有功能。