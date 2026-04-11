# Demo Guide (5 Minutes)

本指南用于比赛现场快速演示“校园综合智慧管理系统”核心能力。

## Demo Preconditions

- 已执行 `docker compose up -d --build`
- 浏览器可访问 `http://localhost/`
- 可用测试账号（见 `README.md`）

## Suggested Flow

### 1) Student View (约 90 秒)

- 使用 `student01 / 123456` 登录。
- 进入 `Dashboard`，展示今日课程、待办、志愿时长联动指标。
- 进入 `Schedule`，展示周/月/日视图和个人计划新增。
- 进入 `Task Center`，新增一条个人任务并点击进入详情页。

讲解点：

- 学生端统一时间与任务管理；
- 任务状态按流程推进（pending -> viewed -> in_progress -> done）。

### 2) Organization OA Flow (约 90 秒)

- 退出并登录 `orgadmin01 / 123456`。
- 进入 `Organization`，展示组织列表、组织详情、任务看板。
- 在组织任务中执行“分配任务/转交任务”。
- 观察任务日志记录（操作可追踪）。

讲解点：

- 组织 OA 管理统一入口；
- 任务流转链路可追踪、可回看。

### 3) Data Integration (约 45 秒)

- 在 `Data Integration` 选择导入类型（course/volunteer/workstudy/project_node）。
- 上传 `init-data/` 或 `samples/` 示例文件并提交。
- 展示导入日志中的成功/失败统计与错误摘要。

讲解点：

- 支持模拟 API 数据接入；
- 导入后可驱动日程与看板联动。

### 4) Profile + Review Loop (约 75 秒)

- 切回 `student01`，在 `Profile` 提交奖项材料。
- 切换 `twadmin01 / 123456`，进入 `Quality Review` 完成审核。
- 回到学生档案页，展示审核后结果更新。

讲解点：

- 学生档案中心与审核模块闭环；
- 奖项申报、审核、回写全链路。

### 5) Tri-lingual (约 30 秒)

- 在 `Settings` 中切换 `中文 / English / Русский`。
- 快速切换 `Dashboard` 与 `Task Center` 验证核心文案翻译。

## Common Q&A

- Q: 如果评委机器没有 Python/Node 环境怎么办？  
  A: 使用 Docker Compose 一键部署，不依赖本机运行时。

- Q: 数据导入失败如何排查？  
  A: 查看导入日志错误摘要，确认文件为 UTF-8 编码 JSON/CSV。

- Q: 权限边界如何保证？  
  A: 关键接口在后端执行角色与归属校验，未授权返回 403。
