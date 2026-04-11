# Permissions Matrix

本文档用于说明系统角色权限边界，供评审和答辩时快速核对。

## Roles

- `student`：学生
- `org_admin`：组织负责人
- `tw_admin`：团委管理员

## Page-Level Permissions

| 页面 | student | org_admin | tw_admin |
|---|---|---|---|
| Dashboard | 可访问 | 可访问 | 可访问 |
| Schedule | 可访问 | 可访问 | 可访问 |
| Task Center | 可访问（仅个人任务主视角） | 可访问 | 可访问 |
| Task Detail | 可访问（仅可操作本人任务） | 可访问 | 可访问 |
| Organization | 可访问（负责人视角） | 可访问（负责人+管理员视角） | 可访问（负责人+管理员视角） |
| Data Integration | 只读（不可导入） | 可导入 | 可导入 |
| Profile | 可访问 | 可访问 | 可访问 |
| Quality Review | 不可访问 | 不可访问 | 可访问 |
| Settings | 可访问 | 可访问 | 可访问 |

## API-Level Permissions

### Auth

- `POST /api/auth/login`：公开
- `GET /api/auth/me`：需登录
- `POST /api/auth/logout`：需登录

### Tasks

- `GET /api/tasks`：需登录
  - `student`：仅返回本人相关任务（`owner_is_self` 或负责人匹配当前用户）
  - `org_admin` / `tw_admin`：可返回全量任务
- `POST /api/tasks`：需登录
  - `student`：仅允许创建个人任务，不允许组织来源任务
  - `org_admin` / `tw_admin`：可创建组织任务
- `GET /api/tasks/:id`：需登录
- `PATCH /api/tasks/:id/status`：需登录并具备任务操作权限
- `POST /api/tasks/:id/transfer`：需登录并具备任务操作权限

### Organizations

- `GET /api/organizations`：需登录
- `GET /api/organizations/:id`：需登录
- `POST /api/organizations`：`org_admin` / `tw_admin`
- `PATCH /api/organizations/:id`：`org_admin` / `tw_admin`
- `DELETE /api/organizations/:id`：`org_admin` / `tw_admin`

### Schedule

- `GET /api/schedule/events`：需登录
- `POST /api/schedule/plans`：需登录
- `PUT /api/schedule/plans/:plan_id`：需登录
- `DELETE /api/schedule/plans/:plan_id`：需登录

### Profile & Awards

- `GET /api/profile`：需登录
- `PUT /api/profile`：需登录
- `POST /api/profile/awards`：需登录

### Award Review (Admin)

- `GET /api/admin/awards`：`tw_admin`
- `PATCH /api/admin/awards/:award_id/review`：`tw_admin`

### Integrations

- `POST /api/integrations/import`：`org_admin` / `tw_admin`
- `GET /api/integrations/logs`：需登录

## Notes

- 所有受保护接口基于 Session 鉴权。
- 无权限操作会返回 `403 forbidden`。
- 未登录会返回 `401 unauthorized`。
