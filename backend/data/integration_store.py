from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from werkzeug.datastructures import FileStorage

from . import enums as E
from .db import db
from .models import IntegrationImportLog, ScheduleEvent, Student, VolunteerRecord

IMPORT_TYPES = {"course", "volunteer", "workstudy", "project_node"}
ALLOWED_EXTENSIONS = (".json", ".csv")
UNSUPPORTED_FILE_MSG = "仅支持 JSON 或 CSV 文件，请先导出为 CSV UTF-8 格式"
CSV_ENCODING_MSG = "CSV 编码错误：请使用 UTF-8（可尝试 Excel 另存为 CSV UTF-8）"


def _parse_dt(val: str) -> datetime:
    s = str(val or "").strip()
    if not s:
        raise ValueError("字段缺失：start_at / end_at")
    if len(s) == 10:
        return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"时间格式错误：{s}") from exc


def _validate_file_type(filename: str) -> None:
    name = (filename or "").lower().strip()
    if not name.endswith(ALLOWED_EXTENSIONS):
        raise ValueError(UNSUPPORTED_FILE_MSG)


def _decode_file(file: FileStorage) -> str:
    raw = file.read()
    file.stream.seek(0)
    name = (file.filename or "").lower().strip()
    if name.endswith(".json"):
        try:
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("JSON 编码错误：请使用 UTF-8 编码") from exc

    # CSV: utf-8 -> gbk -> gb2312
    for enc in ("utf-8-sig", "gbk", "gb2312"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(CSV_ENCODING_MSG)


def _read_rows(file: FileStorage) -> List[Dict[str, Any]]:
    name = (file.filename or "").lower()
    _validate_file_type(name)
    text = _decode_file(file)
    if name.endswith(".json"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"文件格式错误：JSON 解析失败（{exc.msg}）") from exc
        if isinstance(data, dict):
            data = data.get("data", data.get("rows", []))
        if not isinstance(data, list):
            raise ValueError("文件格式错误：JSON 顶层需为数组")
        return [x for x in data if isinstance(x, dict)]
    if name.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise ValueError("文件格式错误：CSV 缺少表头")
        return [dict(r) for r in reader]
    raise ValueError(UNSUPPORTED_FILE_MSG)


def _schedule_row(row: Dict[str, Any], event_type: str, source: str, title_key: str = "title") -> Dict[str, Any]:
    title = str(row.get(title_key) or "").strip()
    if not title:
        raise ValueError("字段缺失：title")
    start_raw = row.get("start_at") or row.get("startAt")
    end_raw = row.get("end_at") or row.get("endAt")
    if not start_raw or not end_raw:
        date = row.get("date")
        start_time = row.get("start_time") or row.get("startTime")
        end_time = row.get("end_time") or row.get("endTime")
        if date and start_time and end_time:
            start_raw = f"{str(date).strip()}T{str(start_time).strip()}"
            end_raw = f"{str(date).strip()}T{str(end_time).strip()}"
    start_at = _parse_dt(str(start_raw or ""))
    end_at = _parse_dt(str(end_raw or ""))
    if end_at <= start_at:
        raise ValueError("字段错误：end_at 必须晚于 start_at")
    return {
        "id": f"ext_{uuid4().hex[:12]}",
        "title": title,
        "event_type": event_type,
        "source": source,
        "start_at": start_at,
        "end_at": end_at,
        "location": str(row.get("location") or "").strip(),
        "description": str(row.get("description") or "").strip(),
        "is_editable": False,
        "is_personal_plan": False,
    }


def _default_volunteer_ref_id() -> str:
    s = Student.query.first()
    return s.volunteer_ref_id if s else "VOL-EXT-0001"


def import_data(import_type: str, file: FileStorage) -> Tuple[bool, str, Dict[str, Any]]:
    t = (import_type or "").strip().lower()
    if t not in IMPORT_TYPES:
        return False, "导入类型错误", {}
    if not file or not file.filename:
        return False, "请选择要导入的文件", {}

    try:
        rows = _read_rows(file)
    except Exception as exc:
        return False, str(exc), {}

    success = 0
    failed = 0
    errors: List[str] = []

    for idx, row in enumerate(rows, start=1):
        try:
            if t == "course":
                row2 = dict(row)
                row2["course_name"] = row.get("course_name") or row.get("title")
                payload = _schedule_row(row2, "class", "academic_system", title_key="course_name")
                db.session.add(ScheduleEvent(**payload))
            elif t == "workstudy":
                payload = _schedule_row(row, "work_study", "work_study_system", title_key="title")
                db.session.add(ScheduleEvent(**payload))
            elif t == "project_node":
                row2 = dict(row)
                row2["node_title"] = row.get("node_title") or row.get("title")
                payload = _schedule_row(row2, "innovation_project", "innovation_platform", title_key="node_title")
                db.session.add(ScheduleEvent(**payload))
            elif t == "volunteer":
                activity_title = str(row.get("activity_title") or row.get("title") or "").strip()
                service_date = str(row.get("service_date") or row.get("date") or "").strip()
                hours_raw = row.get("hours")
                if hours_raw in (None, ""):
                    hours_raw = row.get("duration_hours")
                if hours_raw in (None, ""):
                    raise ValueError("字段缺失：hours")
                hours = float(hours_raw)
                if not activity_title or not service_date:
                    raise ValueError("字段缺失：activity_title 或 service_date")
                raw_status = str(row.get("status") or "").strip().lower()
                if raw_status in E.VOLUNTEER_STATUSES:
                    vr_status = raw_status
                else:
                    vr_status = E.VOLUNTEER_STATUS_PENDING_REVIEW
                db.session.add(
                    VolunteerRecord(
                        id=f"vr_ext_{uuid4().hex[:10]}",
                        volunteer_ref_id=str(row.get("volunteer_ref_id") or _default_volunteer_ref_id()).strip(),
                        activity_title=activity_title,
                        service_date=service_date,
                        hours=hours,
                        status=vr_status,
                    )
                )
            success += 1
        except Exception as exc:
            failed += 1
            errors.append(f"第 {idx} 行：{exc}")

    error_summary = "; ".join(errors[:8])
    db.session.add(
        IntegrationImportLog(
            import_type=t,
            file_name=file.filename or "",
            success_count=success,
            failed_count=failed,
            error_summary=error_summary,
        )
    )
    db.session.commit()
    return True, "", {"success_count": success, "failed_count": failed, "errors": errors[:20]}


def list_logs(limit: int = 50) -> List[Dict[str, Any]]:
    rows = (
        IntegrationImportLog.query
        .order_by(IntegrationImportLog.created_at.desc(), IntegrationImportLog.id.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    result = []
    for x in rows:
        created = x.created_at.isoformat().replace("+00:00", "Z") if x.created_at else ""
        result.append(
            {
                "id": x.id,
                "import_type": x.import_type,
                "file_name": x.file_name,
                "success_count": x.success_count,
                "failed_count": x.failed_count,
                "error_summary": x.error_summary,
                "created_at": created,
            }
        )
    return result

