from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import text

from .db import db


def _table_columns(table_name: str) -> set[str]:
    rows = db.session.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
    return {str(r["name"]) for r in rows}


def _add_column_if_missing(table_name: str, column_name: str, ddl_type: str, default_sql: str = "''") -> None:
    cols = _table_columns(table_name)
    if column_name in cols:
        return
    db.session.execute(
        text(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_type} NOT NULL DEFAULT {default_sql}"
        )
    )


def _parse_to_dt(raw: str) -> datetime | None:
    s = (raw or "").strip()
    if not s:
        return None
    # Compatible with old "YYYY-MM-DD" and "YYYY-MM-DDTHH:mm:ss"
    try:
        if len(s) == 10:
            return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize_datetime_column(table_name: str, col_name: str) -> None:
    # SQLite has no strict DATETIME type, so normalize stored text format.
    rows = db.session.execute(text(f"SELECT id, {col_name} FROM {table_name}")).mappings().all()
    for row in rows:
        raw = row.get(col_name)
        if raw is None:
            continue
        dt = _parse_to_dt(str(raw))
        if not dt:
            continue
        normalized = dt.astimezone(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
        db.session.execute(
            text(f"UPDATE {table_name} SET {col_name} = :val WHERE id = :id"),
            {"val": normalized, "id": row["id"]},
        )


def run_migrations() -> None:
    # organizations extensions
    _add_column_if_missing("organizations", "short_name", "VARCHAR(64)")
    _add_column_if_missing("organizations", "logo_url", "VARCHAR(255)")
    _add_column_if_missing("organizations", "parent_id", "VARCHAR(32)")
    _add_column_if_missing("organizations", "leader_student_id", "VARCHAR(32)")
    _add_column_if_missing("organizations", "leader_teacher_name", "VARCHAR(64)")

    # tasks extensions
    _add_column_if_missing("tasks", "assignment_type", "VARCHAR(32)", "'single_department'")
    _add_column_if_missing("tasks", "collaborating_org_ids_json", "TEXT", "'[]'")
    _add_column_if_missing("tasks", "parent_task_id", "VARCHAR(32)")
    _add_column_if_missing("tasks", "current_owner_id", "VARCHAR(32)")

    # 旧库：direct/self → single_department；assignment_type 列若曾为 direct 则升级
    db.session.execute(
        text("UPDATE tasks SET assignment_type = 'single_department' WHERE assignment_type IN ('direct', 'self')")
    )

    # datetime normalization for legacy text columns
    _normalize_datetime_column("tasks", "due_date")
    _normalize_datetime_column("schedule_events", "start_at")
    _normalize_datetime_column("schedule_events", "end_at")

    _add_column_if_missing("volunteer_records", "status", "VARCHAR(32)", "'pending_review'")
    # 演示种子：部分已认定；其余（含数据集成导入）保持待审核，不计入总时长直至认定
    db.session.execute(
        text("UPDATE volunteer_records SET status = 'recognized' WHERE id IN ('vr_1', 'vr_3')")
    )

    db.session.commit()

