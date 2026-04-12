from __future__ import annotations

from datetime import datetime, timezone

from .db import db


def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0)


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.String(32), primary_key=True)
    display_name = db.Column(db.String(64), nullable=False, default="")
    phone = db.Column(db.String(32), nullable=False, default="")
    wechat = db.Column(db.String(64), nullable=False, default="")
    email = db.Column(db.String(128), nullable=False, default="")
    github = db.Column(db.String(255), nullable=False, default="")
    weibo = db.Column(db.String(255), nullable=False, default="")
    ethnicity = db.Column(db.String(32), nullable=False, default="")
    id_card_no = db.Column(db.String(32), nullable=False, default="")
    volunteer_ref_id = db.Column(db.String(64), nullable=False, default="")
    grade = db.Column(db.String(32), nullable=False, default="")
    college = db.Column(db.String(128), nullable=False, default="")
    major = db.Column(db.String(128), nullable=False, default="")
    class_name = db.Column(db.String(64), nullable=False, default="")


class SkillModule(db.Model):
    __tablename__ = "skill_modules"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(32), db.ForeignKey("students.student_id"), nullable=False, index=True)
    module = db.Column(db.String(64), nullable=False, default="")
    tags_json = db.Column(db.Text, nullable=False, default="[]")


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(128), nullable=False, default="")
    short_name = db.Column(db.String(64), nullable=False, default="")
    logo_url = db.Column(db.String(255), nullable=False, default="")
    parent_id = db.Column(db.String(32), nullable=False, default="")
    leader_student_id = db.Column(db.String(32), nullable=False, default="")
    leader_teacher_name = db.Column(db.String(64), nullable=False, default="")
    organization_type = db.Column(db.String(32), nullable=False, default="club")
    leader_name = db.Column(db.String(64), nullable=False, default="")
    leader_role = db.Column(db.String(32), nullable=False, default="student")
    member_count = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False, default="")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(255), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    task_type = db.Column(db.String(32), nullable=False, default="affairs")
    source_type = db.Column(db.String(32), nullable=False, default="personal")
    assignment_type = db.Column(db.String(32), nullable=False, default="single_department")
    collaborating_org_ids_json = db.Column(db.Text, nullable=False, default="[]")
    parent_task_id = db.Column(db.String(32), nullable=False, default="")
    source_org_id = db.Column(db.String(32), nullable=False, default="")
    current_org_id = db.Column(db.String(32), nullable=False, default="")
    current_owner_id = db.Column(db.String(32), nullable=False, default="")
    current_owner_name = db.Column(db.String(64), nullable=False, default="")
    owner_is_self = db.Column(db.Boolean, nullable=False, default=False)
    creator_student_id = db.Column(db.String(32), nullable=False, default="")
    due_date = db.Column(db.DateTime(timezone=True), nullable=True)
    priority = db.Column(db.String(16), nullable=False, default="medium")
    status = db.Column(db.String(32), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)


class TaskLog(db.Model):
    __tablename__ = "task_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(32), db.ForeignKey("tasks.id"), nullable=False, index=True)
    action = db.Column(db.String(32), nullable=False, default="")
    actor = db.Column(db.String(64), nullable=False, default="user")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc, index=True)
    note = db.Column(db.Text, nullable=True)
    from_status = db.Column(db.String(32), nullable=True)
    to_status = db.Column(db.String(32), nullable=True)
    from_owner = db.Column(db.String(64), nullable=True)
    to_owner = db.Column(db.String(64), nullable=True)
    from_org_id = db.Column(db.String(32), nullable=True)
    to_org_id = db.Column(db.String(32), nullable=True)


class ScheduleEvent(db.Model):
    __tablename__ = "schedule_events"

    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(255), nullable=False, default="")
    event_type = db.Column(db.String(32), nullable=False, default="class", index=True)
    source = db.Column(db.String(32), nullable=False, default="unknown")
    start_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    end_at = db.Column(db.DateTime(timezone=True), nullable=True)
    location = db.Column(db.String(255), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    is_editable = db.Column(db.Boolean, nullable=False, default=False)
    is_personal_plan = db.Column(db.Boolean, nullable=False, default=False, index=True)
    owner_student_id = db.Column(db.String(32), nullable=False, default="")


class VolunteerRecord(db.Model):
    __tablename__ = "volunteer_records"

    id = db.Column(db.String(64), primary_key=True)
    volunteer_ref_id = db.Column(db.String(64), nullable=False, index=True)
    activity_title = db.Column(db.String(255), nullable=False, default="")
    service_date = db.Column(db.String(32), nullable=False, default="")
    hours = db.Column(db.Float, nullable=False, default=0.0)
    # recognized = 已认定，可计入志愿总时长；导入默认为 pending_review
    status = db.Column(db.String(32), nullable=False, default="pending_review", index=True)


class Award(db.Model):
    __tablename__ = "awards"

    id = db.Column(db.String(64), primary_key=True)
    student_id = db.Column(db.String(32), db.ForeignKey("students.student_id"), nullable=False, index=True)
    award_name = db.Column(db.String(255), nullable=False, default="")
    award_time = db.Column(db.String(32), nullable=False, default="")
    proof_file_name = db.Column(db.String(255), nullable=False, default="")
    proof_file_url = db.Column(db.String(255), nullable=False, default="")
    status = db.Column(db.String(32), nullable=False, default="pending", index=True)
    review_comment = db.Column(db.Text, nullable=False, default="")
    submitted_at = db.Column(db.String(64), nullable=False, default="")
    reviewed_at = db.Column(db.String(64), nullable=False, default="")
    reviewed_by = db.Column(db.String(64), nullable=False, default="")


class AwardReview(db.Model):
    __tablename__ = "award_reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    award_id = db.Column(db.String(64), db.ForeignKey("awards.id"), nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="")
    review_comment = db.Column(db.Text, nullable=False, default="")
    reviewed_at = db.Column(db.String(64), nullable=False, default="")
    reviewed_by = db.Column(db.String(64), nullable=False, default="")


class IntegrationImportLog(db.Model):
    __tablename__ = "integration_import_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    import_type = db.Column(db.String(32), nullable=False, default="", index=True)
    file_name = db.Column(db.String(255), nullable=False, default="")
    success_count = db.Column(db.Integer, nullable=False, default=0)
    failed_count = db.Column(db.Integer, nullable=False, default=0)
    error_summary = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc, index=True)

