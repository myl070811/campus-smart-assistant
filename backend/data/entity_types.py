"""
基础实体形状说明（TypedDict，供类型检查与文档；运行时可为普通 dict）。

与 `enums.py` 中的枚举值配合使用。字段一律 snake_case。
"""

from __future__ import annotations

from typing import List, TypedDict

class Student(TypedDict, total=False):
    """在读学生基本档案（控制台登录用户主体）。"""

    student_id: str
    display_name: str
    phone: str
    email: str
    wechat: str
    college: str
    major: str
    class_name: str
    volunteer_ref_id: str
    avatar_url: str
    grade_year: int


class TaskLogEntry(TypedDict, total=False):
    id: str
    action: str
    actor: str
    created_at: str
    note: str
    from_status: str
    to_status: str
    from_owner: str
    to_owner: str


class Task(TypedDict, total=False):
    id: str
    title: str
    description: str
    task_type: str
    source_type: str
    owner_name: str
    owner_is_self: bool
    due_date: str
    priority: str
    status: str
    logs: List[TaskLogEntry]


class OrganizationTaskSummary(TypedDict, total=False):
    """组织详情下列出的任务摘要。"""

    id: str
    title: str
    task_type: str
    source_type: str
    owner_name: str
    status: str


class Organization(TypedDict, total=False):
    id: str
    name: str
    organization_type: str
    leader_name: str
    leader_role: str
    member_count: int
    description: str
    tasks: List[OrganizationTaskSummary]


class ScheduleEvent(TypedDict, total=False):
    id: str
    title: str
    event_type: str
    source: str
    start_at: str
    end_at: str
    location: str
    description: str
    is_editable: bool


class VolunteerRecord(TypedDict, total=False):
    id: str
    activity_title: str
    service_date: str
    hours: float
    status: str


class Award(TypedDict, total=False):
    id: str
    title: str
    awarded_at: str
    award_level: str
    audit_status: str


class DashboardStats(TypedDict, total=False):
    """仪表盘顶部统计。"""

    today_course_count: int
    pending_task_count: int
    ongoing_task_count: int
    volunteer_hours_total: float


class TaskPreview(TypedDict, total=False):
    title: str
    status: str


class DashboardPayload(TypedDict, total=False):
    stats: DashboardStats
    schedule_events: List[ScheduleEvent]
    task_previews: List[TaskPreview]
    date_label: str
    # 兼容旧前端：按周聚合的课表（可选，由 mock 或 DB 填充）
    week_schedule: List[dict]
