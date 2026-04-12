from __future__ import annotations

import json
from datetime import datetime, timezone

from . import enums as E
from .db import db
from .models import (
    Award,
    AwardReview,
    Organization,
    ScheduleEvent,
    SkillModule,
    Student,
    Task,
    TaskLog,
    VolunteerRecord,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_dt(raw: str) -> datetime:
    if len(raw) == 10:
        return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def seed_if_empty() -> None:
    if Student.query.first():
        return

    student = Student(
        student_id="2023XXXX0218",
        display_name="陈思远",
        phone="13800006280",
        wechat="campus_csy",
        email="chen.siyuan@stu.university.edu.cn",
        github="https://github.com/campus-csy",
        weibo="@校园思远",
        ethnicity="汉族",
        id_card_no="320102200401011234",
        volunteer_ref_id="VOL-2024-00816",
        grade="2023级",
        college="计算机科学与技术学院",
        major="软件工程",
        class_name="软工 2023-2 班",
    )
    db.session.add(student)

    student_b = Student(
        student_id="2023XXXX0219",
        display_name="李华",
        phone="13800003190",
        wechat="lihua_lab",
        email="li.hua@stu.university.edu.cn",
        github="",
        weibo="",
        ethnicity="汉族",
        id_card_no="440301200402022468",
        volunteer_ref_id="VOL-2024-0319",
        grade="2023级",
        college="计算机科学与技术学院",
        major="信息安全",
        class_name="信安 2023-1 班",
    )
    db.session.add(student_b)

    modules = [
        {"module": "编程", "tags": ["Python", "Vue", "Flask"]},
        {"module": "策划", "tags": ["活动统筹", "流程设计"]},
        {"module": "文案", "tags": ["新闻稿", "新媒体文案"]},
        {"module": "管理", "tags": ["任务分解", "团队协作"]},
        {"module": "运动", "tags": ["羽毛球", "长跑"]},
        {"module": "语言", "tags": ["英语 CET-6"]},
    ]
    db.session.add_all(
        [
            SkillModule(student_id=student.student_id, module=m["module"], tags_json=json.dumps(m["tags"], ensure_ascii=False))
            for m in modules
        ]
    )
    db.session.add(
        SkillModule(
            student_id=student_b.student_id,
            module="编程",
            tags_json=json.dumps(["C++", "网络安全基础"], ensure_ascii=False),
        )
    )

    db.session.add_all(
        [
            VolunteerRecord(
                id="vr_1",
                volunteer_ref_id="VOL-2024-00816",
                activity_title="迎新志愿服务（报到引导）",
                service_date="2025-09-06",
                hours=6.0,
                status=E.VOLUNTEER_STATUS_RECOGNIZED,
            ),
            VolunteerRecord(
                id="vr_2",
                volunteer_ref_id="VOL-2024-00816",
                activity_title="校园马拉松后勤保障",
                service_date="2026-03-15",
                hours=5.5,
                status=E.VOLUNTEER_STATUS_PENDING_REVIEW,
            ),
            VolunteerRecord(
                id="vr_3",
                volunteer_ref_id="VOL-2024-0319",
                activity_title="图书馆志愿整架",
                service_date="2026-03-10",
                hours=3.0,
                status=E.VOLUNTEER_STATUS_RECOGNIZED,
            ),
        ]
    )

    db.session.add_all(
        [
            Award(
                id="aw_101",
                student_id=student.student_id,
                award_name="全国大学生软件创新大赛 华东赛区 二等奖",
                award_time="2025-11",
                proof_file_name="",
                proof_file_url="",
                status="approved",
                review_comment="材料完整",
                submitted_at="2025-11-20T10:00:00Z",
                reviewed_at="2025-11-22T14:20:00Z",
                reviewed_by="admin",
            ),
            Award(
                id="aw_102",
                student_id=student.student_id,
                award_name="“互联网+”校赛铜奖",
                award_time="2026-03",
                proof_file_name="",
                proof_file_url="",
                status="pending",
                review_comment="",
                submitted_at="2026-03-30T09:00:00Z",
                reviewed_at="",
                reviewed_by="",
            ),
        ]
    )
    db.session.add(
        AwardReview(
            award_id="aw_101",
            status="approved",
            review_comment="材料完整",
            reviewed_at="2025-11-22T14:20:00Z",
            reviewed_by="admin",
        )
    )

    db.session.add_all(
        [
            Organization(
                id="tw",
                name="校团委",
                short_name="团委",
                logo_url="",
                parent_id="",
                leader_student_id="",
                leader_teacher_name="李静",
                organization_type=E.ORG_TYPE_YOUTH_LEAGUE,
                leader_name="李静",
                leader_role=E.LEADER_ROLE_TEACHER,
                member_count=45,
                description="",
            ),
            Organization(
                id="xsh",
                name="学生会",
                short_name="学生会",
                logo_url="",
                parent_id="tw",
                leader_student_id="2023XXXX0311",
                leader_teacher_name="",
                organization_type=E.ORG_TYPE_STUDENT_UNION,
                leader_name="周子墨",
                leader_role=E.LEADER_ROLE_STUDENT,
                member_count=128,
                description="",
            ),
        ]
    )

    tasks = [
        Task(
            id="t1",
            title="完成《数据结构》第三章课后习题",
            description="整理第三章栈与队列的课后习题解答，标注思考过程与参考教材页码。",
            source_type=E.TASK_SOURCE_COURSE,
            assignment_type=E.TASK_FLOW_SINGLE_DEPARTMENT,
            collaborating_org_ids_json=json.dumps(["tw"], ensure_ascii=False),
            parent_task_id="",
            source_org_id="",
            current_org_id="tw",
            current_owner_id="2022XXXX0011",
            task_type=E.TASK_TYPE_HOMEWORK,
            current_owner_name="张明",
            owner_is_self=False,
            due_date=_parse_dt("2026-04-02"),
            priority=E.TASK_PRIORITY_HIGH,
            status=E.TASK_STATUS_IN_PROGRESS,
        ),
        Task(
            id="t2",
            title="学生会宣传部本周推文素材整理",
            description="汇总本周活动照片与文案要点，按发布时间线归档，交予审核。",
            source_type=E.TASK_SOURCE_ORGANIZATION,
            assignment_type=E.TASK_FLOW_SINGLE_DEPARTMENT,
            collaborating_org_ids_json=json.dumps(["xsh"], ensure_ascii=False),
            parent_task_id="",
            source_org_id="xsh",
            current_org_id="xsh",
            current_owner_id="2023XXXX0312",
            task_type=E.TASK_TYPE_AFFAIRS,
            current_owner_name="李雪",
            owner_is_self=False,
            due_date=_parse_dt("2026-03-30"),
            priority=E.TASK_PRIORITY_MEDIUM,
            status=E.TASK_STATUS_VIEWED,
        ),
        Task(
            id="t3",
            title="准备英语四级模拟卷复盘",
            description="完成一套全真模拟后，登记错题类型与对应生词本条目。",
            source_type=E.TASK_SOURCE_PERSONAL,
            assignment_type=E.TASK_FLOW_SINGLE_DEPARTMENT,
            collaborating_org_ids_json="[]",
            parent_task_id="",
            source_org_id="",
            current_org_id="tw",
            current_owner_id=student.student_id,
            task_type=E.TASK_TYPE_REVIEW_STUDY,
            current_owner_name="",
            owner_is_self=True,
            creator_student_id=student.student_id,
            due_date=_parse_dt("2026-04-05"),
            priority=E.TASK_PRIORITY_MEDIUM,
            status=E.TASK_STATUS_PENDING,
        ),
        Task(
            id="t4",
            title="迎新晚会联合筹备（团委×学生会）",
            description="统筹场地审批与宣传物料联动，双方组织对齐时间节点与责任人。",
            source_type=E.TASK_SOURCE_ORGANIZATION,
            assignment_type=E.TASK_FLOW_CROSS_DEPARTMENT,
            collaborating_org_ids_json=json.dumps(["tw", "xsh"], ensure_ascii=False),
            parent_task_id="",
            source_org_id="tw",
            current_org_id="xsh",
            current_owner_id="2023XXXX0312",
            task_type=E.TASK_TYPE_COORDINATE,
            current_owner_name="李雪",
            owner_is_self=False,
            due_date=_parse_dt("2026-04-08"),
            priority=E.TASK_PRIORITY_HIGH,
            status=E.TASK_STATUS_PENDING,
        ),
    ]
    db.session.add_all(tasks)
    db.session.flush()

    for task in tasks:
        db.session.add(
            TaskLog(
                task_id=task.id,
                action=E.TASK_LOG_CREATE,
                actor="system",
                created_at=datetime.now(timezone.utc).replace(microsecond=0),
                note="",
            )
        )

    schedule_events = [
        ("cls_20260401_01", "高等数学 A", "class", "academic_system", "2026-04-01T08:00:00", "2026-04-01T09:40:00", "教学楼 A-201", "第六章积分应用", False, False, ""),
        ("cls_20260402_01", "数据结构与算法", "class", "academic_system", "2026-04-02T14:00:00", "2026-04-02T15:40:00", "实验楼 C-305", "图与最短路径", False, False, ""),
        ("org_20260402_01", "学生会推文终审", "org_task", "org_task_center", "2026-04-02T20:00:00", "2026-04-02T21:00:00", "线上协作", "发布前终审内容和配图。", False, False, ""),
        ("vol_20260404_01", "社区义诊志愿服务", "volunteer", "volunteer_platform", "2026-04-04T09:00:00", "2026-04-04T12:00:00", "南门社区服务站", "签到与现场秩序维护。", False, False, ""),
        ("ws_20260403_01", "图书馆勤工值班", "work_study", "work_study_system", "2026-04-03T15:00:00", "2026-04-03T18:00:00", "图书馆一层服务台", "借还书引导与书架整理。", False, False, ""),
        ("ip_20260405_01", "大创中期检查材料提交", "innovation_project", "innovation_platform", "2026-04-05T10:00:00", "2026-04-05T11:00:00", "科研管理系统", "上传报告与经费使用说明。", False, False, ""),
        ("plan_1001", "机器学习比赛 baseline 复盘", "personal_plan", "manual_input", "2026-04-03T19:00:00", "2026-04-03T20:30:00", "图书馆四层", "对比提交记录并写下一轮优化计划。", True, True, student.student_id),
        ("se_2026_04_02_1", "高等数学 A", "class", "academic_system", "2026-04-02T08:00:00", "2026-04-02T09:40:00", "教学楼 A-201", "", False, False, ""),
        ("se_2026_04_02_2", "大学英语（三）", "class", "academic_system", "2026-04-02T10:00:00", "2026-04-02T11:40:00", "教学楼 B-103", "", False, False, ""),
        ("se_2026_04_02_3", "数据结构与算法", "class", "academic_system", "2026-04-02T14:00:00", "2026-04-02T15:40:00", "实验楼 C-305", "", False, False, ""),
        ("se_2026_04_02_4", "体育与健康", "class", "academic_system", "2026-04-02T16:00:00", "2026-04-02T17:40:00", "运动场", "", False, False, ""),
        ("se_2026_04_01_1", "形势与政策", "class", "academic_system", "2026-04-01T19:00:00", "2026-04-01T20:40:00", "报告厅", "", False, False, ""),
    ]
    db.session.add_all(
        [
            ScheduleEvent(
                id=i,
                title=title,
                event_type=et,
                source=source,
                start_at=_parse_dt(start_at),
                end_at=_parse_dt(end_at),
                location=location,
                description=desc,
                is_editable=is_editable,
                is_personal_plan=is_plan,
                owner_student_id=owner_sid or "",
            )
            for (i, title, et, source, start_at, end_at, location, desc, is_editable, is_plan, owner_sid) in schedule_events
        ]
    )

    db.session.commit()


def ensure_demo_extensions() -> None:
    """
    在「已有旧种子库」上幂等补全：第二名学生、其技能/志愿记录、跨部门示例任务 t4。
    解决仅执行过早期 seed_if_empty 的环境看不到 student02 数据的问题。
    """
    sid_b = "2023XXXX0219"
    if not Student.query.filter_by(student_id=sid_b).first():
        db.session.add(
            Student(
                student_id=sid_b,
                display_name="李华",
                phone="13800003190",
                wechat="lihua_lab",
                email="li.hua@stu.university.edu.cn",
                github="",
                weibo="",
                ethnicity="汉族",
                id_card_no="440301200402022468",
                volunteer_ref_id="VOL-2024-0319",
                grade="2023级",
                college="计算机科学与技术学院",
                major="信息安全",
                class_name="信安 2023-1 班",
            )
        )

    if not SkillModule.query.filter_by(student_id=sid_b).first():
        db.session.add(
            SkillModule(
                student_id=sid_b,
                module="编程",
                tags_json=json.dumps(["C++", "网络安全基础"], ensure_ascii=False),
            )
        )

    if not VolunteerRecord.query.filter_by(id="vr_3").first():
        db.session.add(
            VolunteerRecord(
                id="vr_3",
                volunteer_ref_id="VOL-2024-0319",
                activity_title="图书馆志愿整架",
                service_date="2026-03-10",
                hours=3.0,
                status=E.VOLUNTEER_STATUS_RECOGNIZED,
            )
        )

    if not Task.query.filter_by(id="t4").first():
        t4 = Task(
            id="t4",
            title="迎新晚会联合筹备（团委×学生会）",
            description="统筹场地审批与宣传物料联动，双方组织对齐时间节点与责任人。",
            source_type=E.TASK_SOURCE_ORGANIZATION,
            assignment_type=E.TASK_FLOW_CROSS_DEPARTMENT,
            collaborating_org_ids_json=json.dumps(["tw", "xsh"], ensure_ascii=False),
            parent_task_id="",
            source_org_id="tw",
            current_org_id="xsh",
            current_owner_id="2023XXXX0312",
            task_type=E.TASK_TYPE_COORDINATE,
            current_owner_name="李雪",
            owner_is_self=False,
            due_date=_parse_dt("2026-04-08"),
            priority=E.TASK_PRIORITY_HIGH,
            status=E.TASK_STATUS_PENDING,
        )
        db.session.add(t4)
        db.session.flush()
        db.session.add(
            TaskLog(
                task_id="t4",
                action=E.TASK_LOG_CREATE,
                actor="system",
                created_at=datetime.now(timezone.utc).replace(microsecond=0),
                note="",
            )
        )

    db.session.commit()


if __name__ == "__main__":
    # Script mode will be handled by backend/scripts/seed_db.py
    print(_now_iso())

