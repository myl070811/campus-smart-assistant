"""个人档案 API mock：`student` + `skill_tags` + `volunteer_records` + `awards`。"""

from . import enums as E

MOCK_PROFILE = {
    "student": {
        "student_id": "2023XXXX0218",
        "display_name": "陈思远",
        "phone": "138****6280",
        "wechat": "campus_csy",
        "email": "chen.siyuan@stu.university.edu.cn",
        "college": "计算机科学与技术学院",
        "major": "软件工程",
        "class_name": "软工 2023-2 班",
        "volunteer_ref_id": "VOL-2024-00816",
        "avatar_url": "",
        "grade_year": 2023,
    },
    "skill_tags": [
        E.SKILL_PROGRAMMING,
        E.SKILL_PLANNING,
        E.SKILL_WRITING,
        E.SKILL_DESIGN,
        E.SKILL_COORDINATION,
        E.SKILL_DATA_ANALYSIS,
    ],
    "volunteer_records": [
        {
            "id": "vr_1",
            "activity_title": "迎新志愿服务（报到引导）",
            "service_date": "2025-09-06",
            "hours": 6.0,
            "status": E.VOLUNTEER_STATUS_RECOGNIZED,
        },
        {
            "id": "vr_2",
            "activity_title": "校园马拉松后勤保障",
            "service_date": "2026-03-15",
            "hours": 5.5,
            "status": E.VOLUNTEER_STATUS_PENDING_REVIEW,
        },
    ],
    "awards": [
        {
            "id": "aw_1",
            "title": "全国大学生软件创新大赛 华东赛区 二等奖",
            "awarded_at": "2025-11",
            "award_level": E.AWARD_LEVEL_PROVINCIAL,
            "audit_status": E.AWARD_AUDIT_APPROVED,
        },
        {
            "id": "aw_2",
            "title": "「互联网+」校赛铜奖",
            "awarded_at": "2026-03",
            "award_level": E.AWARD_LEVEL_SCHOOL,
            "audit_status": E.AWARD_AUDIT_PENDING_REVIEW,
        },
    ],
}
