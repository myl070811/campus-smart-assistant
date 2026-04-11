# Campus Smart Assistant

校园智慧助手（比赛交付版），面向“可部署、可登录、可演示、可答辩”场景，采用前后端分离和 Docker 一键部署。

## 项目简介

本项目聚焦校园场景下的统一任务协作与学生成长档案管理，提供：

- 统一登录与会话鉴权（Flask Session + 前端凭据透传）
- 三语界面（中文 / English / Русский）
- 学生、组织负责人、团委管理员三角色边界
- 任务流转、日程聚合、组织管理、档案管理、奖项审核、数据导入

## 技术架构

- 前端：`Vue 3` + `Vite` + `Element Plus` + `vue-router`
- 后端：`Flask` + `Flask-SQLAlchemy` + `gunicorn`
- 数据库：`SQLite`（容器部署时持久化到宿主机）
- 部署：`Docker Compose`（`frontend` Nginx + `backend` Flask）

## 项目目录结构

```text
.
├─ backend/
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ Dockerfile
│  ├─ routes/                 # API 路由与权限装饰器
│  ├─ data/                   # 模型、种子数据、数据服务
│  ├─ scripts/                # 脚本
│  └─ uploads/                # 奖项与组织 Logo 上传目录
├─ frontend/
│  ├─ src/
│  │  ├─ views/
│  │  ├─ api/
│  │  ├─ router/
│  │  ├─ stores/
│  │  └─ i18n.js
│  ├─ Dockerfile
│  ├─ package.json
│  └─ .env.example
├─ deploy-data/               # Docker 持久化目录（sqlite/uploads/org-logos）
├─ init-data/                 # 导入示例文件
├─ samples/                   # 导入示例文件
├─ docker-compose.yml
├─ nginx.conf
├─ .env.example
├─ deploy.sh
└─ README.md
```

## 本地开发启动方式

### 1) 启动后端

```bash
cd backend
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

后端默认地址：`http://127.0.0.1:5000`

### 2) 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：`http://127.0.0.1:5173`

## Docker Compose 一键部署方式

在项目根目录执行：

```bash
cp .env.example .env
```

按需修改 `.env`（建议至少修改 `FLASK_SECRET_KEY`），然后执行：

```bash
docker compose up -d --build
```

或使用脚本：

```bash
chmod +x deploy.sh
./deploy.sh
```

启动后访问：

- 前端：`http://localhost:${FRONTEND_PORT}`（默认 `80`）
- 后端健康检查：`http://localhost:${BACKEND_PORT}/api/health`（默认 `5000`）

## 环境变量说明

### 根目录 `.env.example`

```env
FLASK_SECRET_KEY=change-me
SQLALCHEMY_DATABASE_URI=sqlite:////data/campus_assistant.db
FRONTEND_PORT=80
BACKEND_PORT=5000
```

- `FLASK_SECRET_KEY`：Flask 会话密钥（建议部署时修改）
- `SQLALCHEMY_DATABASE_URI`：数据库连接（Docker 默认使用挂载到 `/data` 的 SQLite）
- `FRONTEND_PORT`：Docker 对外暴露的前端端口（容器内固定 `80`）
- `BACKEND_PORT`：Docker 对外暴露的后端端口（容器内固定 `5000`）

### 前端 `frontend/.env.example`

```env
VITE_API_BASE_URL=
VITE_DEV_API_TARGET=http://127.0.0.1:5000
```

- `VITE_API_BASE_URL`：默认留空，前端统一走同源 `/api`（推荐，Docker/生产环境）
- `VITE_DEV_API_TARGET`：仅本地 `npm run dev` 代理目标（默认 Flask `127.0.0.1:5000`）

## 默认测试账号（登录系统）

| 用户名 | 密码 | 角色 | 用途 |
|---|---|---|---|
| `student01` | `123456` | `student` | 学生视角演示 |
| `orgadmin01` | `123456` | `org_admin` | 组织管理与导入 |
| `twadmin01` | `123456` | `tw_admin` | 团委审核与全量演示 |

## 角色权限矩阵

| 角色 | 页面权限 | 典型操作 |
|---|---|---|
| `student` | Dashboard / Schedule / Tasks / Organization(负责人视角) / Profile / Settings / Integrations(只读) | 管理个人任务与日程、提交奖项申请 |
| `org_admin` | 在 `student` 基础上增加 Organization 管理视图 | 组织增删改、任务分配/转交、数据导入 |
| `tw_admin` | 全部页面（含 Quality Review） | 奖项审核、组织管理、数据导入、全流程演示 |

> 详细接口级权限请见 `PERMISSIONS.md`。

## 核心功能模块简介

- `Dashboard`：汇总今日课程、任务状态、志愿时长等指标
- `Task Center / Task Detail`：任务创建、状态推进、转交、日志记录
- `Organization`：组织档案管理、组织任务流转、分配与转交
- `Schedule`：课表/任务/志愿/勤工/大创/个人计划统一时间视图
- `Profile`：学生基础信息、能力标签、志愿记录、奖项申请
- `Quality Review`：团委管理员审核奖项材料
- `Data Integration`：按模板导入课程/志愿/勤工/项目节点数据

## 三语支持说明

- 支持语言：中文（`zh`）、英文（`en`）、俄文（`ru`）
- 设置入口：`Settings`
- 三语覆盖范围：导航、页面文案、核心业务字段动态翻译

## 初始化数据与导入数据说明

- 后端首次启动会自动执行数据库建表、迁移和种子数据初始化
- 导入示例文件：
  - `init-data/`
  - `samples/`
- 导入类型：
  - `course`
  - `volunteer`
  - `workstudy`
  - `project_node`

## 访问地址与端口说明

### 本地开发

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:5000`
- 健康检查：`http://127.0.0.1:5000/api/health`

### Docker 部署

- 前端：`http://localhost:${FRONTEND_PORT}`（默认容器映射 `80:80`）
- 后端：`http://localhost:${BACKEND_PORT}`（默认容器映射 `5000:5000`）
- 健康检查：`http://localhost:${BACKEND_PORT}/api/health`

## 常见问题排查

### 1) 无法登录 / 接口返回 401

- 确认先访问登录页并成功登录
- 确认前端请求统一走同源 `/api`（默认配置）
- 本地分离开发时确认 `VITE_DEV_API_TARGET` 指向可访问后端
- 确认浏览器未禁用 Cookie

### 2) Docker 启动后前端可开、接口失败

- 检查 `backend` 容器状态：`docker compose ps`
- 查看后端日志：`docker compose logs backend`
- 访问健康检查确认后端可用

### 3) 上传文件或持久化数据丢失

- 确认宿主机目录存在并可写：
  - `deploy-data/sqlite`
  - `deploy-data/uploads`
  - `deploy-data/org-logos`

### 4) 修改代码后希望重建容器

```bash
docker compose down
docker compose up -d --build
```

## 答辩演示建议路径

建议流程（约 5 分钟）：

1. 使用 `student01` 登录，展示 Dashboard 总览
2. 进入 Schedule / Tasks，展示时间与任务联动
3. 切换 `orgadmin01`，展示 Organization 分配与转交、Data Integration 导入
4. 返回学生 Profile，展示奖项提交
5. 使用 `twadmin01` 进入 Quality Review，展示审核闭环
6. 在 Settings 演示三语切换

> 现场讲稿版请见 `DEMO_GUIDE.md`。
