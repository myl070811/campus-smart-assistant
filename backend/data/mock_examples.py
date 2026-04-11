"""
各实体最小 mock 示例（文档与单测参考；字段与生产 mock 数据保持一致）。
"""

from . import enums as E

EXAMPLE_STUDENT = {
    "student_id": "20230010218",
    "display_name": "Example Student",
    "phone": "13800000000",
    "email": "stu@university.edu.cn",
    "wechat": "wx_example",
    "college": "计算机学院",
    "major": "软件工程",
    "class_name": "软工 2023-2 班",
    "volunteer_ref_id": "VOL-2024-00001",
    "avatar_url": "",
    "grade_year": 2023,
}

EXAMPLE_ORGANIZATION = {
    "id": "org_demo",
    "name": "示例社团",
    "organization_type": E.ORG_TYPE_CLUB,
    "leader_name": "张三",
    "leader_role": E.LEADER_ROLE_STUDENT,
    "member_count": 42,
    "description": "示例说明",
    "tasks": [
        {
            "id": "ot_demo",
            "title": "示例任务",
            "task_type": E.TASK_TYPE_AFFAIRS,
            "source_type": E.TASK_SOURCE_ORGANIZATION,
            "owner_name": "李四",
            "status": E.TASK_STATUS_PENDING,
        }
    ],
}

EXAMPLE_TASK = {
    "id": "task_demo",
    "title": "示例学习任务",
    "description": "完成第三章作业。",
    "task_type": E.TASK_TYPE_HOMEWORK,
    "source_type": E.TASK_SOURCE_COURSE,
    "owner_name": "王五",
    "owner_is_self": False,
    "due_date": "2026-04-10",
    "priority": E.TASK_PRIORITY_MEDIUM,
    "status": E.TASK_STATUS_PENDING,
    "logs": [],
}

EXAMPLE_SCHEDULE_EVENT = {
    "id": "se_demo",
    "title": "高等数学 A",
    "event_type": E.SCHEDULE_EVENT_TYPE_CLASS,
    "source": "academic_system",
    "start_at": "2026-04-02T08:00:00",
    "end_at": "2026-04-02T09:40:00",
    "location": "教学楼 A301",
    "description": "微分方程章节",
    "is_editable": False,
}

EXAMPLE_VOLUNTEER_RECORD = {
    "id": "vr_demo",
    "activity_title": "迎新志愿服务",
    "service_date": "2025-09-06",
    "hours": 6.0,
    "status": E.VOLUNTEER_STATUS_RECOGNIZED,
}

EXAMPLE_AWARD = {
    "id": "aw_demo",
    "title": "校级奖学金 三等奖",
    "awarded_at": "2025-12",
    "award_level": E.AWARD_LEVEL_SCHOOL,
    "audit_status": E.AWARD_AUDIT_APPROVED,
}
