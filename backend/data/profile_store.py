from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from . import enums as E
from .db import db
from .models import Award, AwardReview, SkillModule, Student, VolunteerRecord


UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "awards"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _next_award_id() -> str:
    max_num = 100
    row = Award.query.all()
    for x in row:
        sid = str(x.id or "")
        if sid.startswith("aw_") and sid.split("_", 1)[1].isdigit():
            max_num = max(max_num, int(sid.split("_", 1)[1]))
    return f"aw_{max_num + 1}"


def _student_to_dict(s: Student) -> Dict[str, Any]:
    return {
        "student_id": s.student_id,
        "display_name": s.display_name,
        "phone": s.phone,
        "wechat": s.wechat,
        "email": s.email,
        "github": s.github,
        "weibo": s.weibo,
        "ethnicity": s.ethnicity,
        "id_card_no": s.id_card_no,
        "volunteer_ref_id": s.volunteer_ref_id,
        "grade": s.grade,
        "college": s.college,
        "major": s.major,
        "class_name": s.class_name,
    }


def _award_to_dict(a: Award) -> Dict[str, Any]:
    return {
        "id": a.id,
        "student_id": a.student_id,
        "award_name": a.award_name,
        "award_time": a.award_time,
        "proof_file_name": a.proof_file_name,
        "proof_file_url": a.proof_file_url,
        "status": a.status,
        "review_comment": a.review_comment,
        "submitted_at": a.submitted_at,
        "reviewed_at": a.reviewed_at,
        "reviewed_by": a.reviewed_by,
    }


def _empty_profile() -> Dict[str, Any]:
    return {
        "student": None,
        "skill_modules": [],
        "volunteer_records": [],
        "volunteer_total_hours": 0.0,
        "awards_public": [],
        "awards_submissions": [],
    }


def get_profile(student_id: Optional[str]) -> Dict[str, Any]:
    sid = (student_id or "").strip()
    if not sid:
        return _empty_profile()
    student = Student.query.filter_by(student_id=sid).first()
    if not student:
        return _empty_profile()
    volunteer_id = student.volunteer_ref_id
    vr_rows = VolunteerRecord.query.filter_by(volunteer_ref_id=volunteer_id).order_by(VolunteerRecord.service_date.desc()).all()
    vr = [
        {
            "id": x.id,
            "volunteer_ref_id": x.volunteer_ref_id,
            "activity_title": x.activity_title,
            "service_date": x.service_date,
            "hours": float(x.hours or 0),
            "status": getattr(x, "status", None) or E.VOLUNTEER_STATUS_PENDING_REVIEW,
        }
        for x in vr_rows
    ]
    total_hours = round(
        sum(float(x["hours"]) for x in vr if x.get("status") == E.VOLUNTEER_STATUS_RECOGNIZED),
        1,
    )
    modules = SkillModule.query.filter_by(student_id=student.student_id).order_by(SkillModule.id.asc()).all()
    skill_modules = []
    for x in modules:
        try:
            tags = json.loads(x.tags_json or "[]")
        except json.JSONDecodeError:
            tags = []
        skill_modules.append({"module": x.module, "tags": tags if isinstance(tags, list) else []})
    approved_awards = Award.query.filter_by(student_id=student.student_id, status="approved").order_by(Award.submitted_at.desc()).all()
    all_awards = Award.query.filter_by(student_id=student.student_id).order_by(Award.submitted_at.desc()).all()
    return {
        "student": _student_to_dict(student),
        "skill_modules": skill_modules,
        "volunteer_records": vr,
        "volunteer_total_hours": total_hours,
        "awards_public": [_award_to_dict(x) for x in approved_awards],
        "awards_submissions": [_award_to_dict(x) for x in all_awards],
    }


def update_student_profile(
    student_id: str, payload: Dict[str, Any]
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    sid = (student_id or "").strip()
    if not sid:
        return False, "profile not linked to student account", {}
    s = Student.query.filter_by(student_id=sid).first()
    if not s:
        return False, "student not found", {}
    editable = {
        "display_name",
        "phone",
        "wechat",
        "email",
        "github",
        "weibo",
        "ethnicity",
        "id_card_no",
        "grade",
        "college",
        "major",
        "class_name",
    }
    for key in editable:
        if key in payload:
            setattr(s, key, str(payload.get(key) or "").strip())
    db.session.commit()
    return True, None, _student_to_dict(s)


def submit_award(
    student_id: str,
    award_name: str,
    award_time: str,
    proof_file: Optional[FileStorage],
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    sid = (student_id or "").strip()
    if not sid:
        return False, "student_id is required", None
    if not Student.query.filter_by(student_id=sid).first():
        return False, "student not found", None
    if not award_name.strip():
        return False, "award_name is required", None
    if not award_time.strip():
        return False, "award_time is required", None

    award_id = _next_award_id()
    saved_name = ""
    saved_url = ""
    if proof_file and proof_file.filename:
        original = secure_filename(proof_file.filename)
        if not original:
            return False, "invalid proof file name", None
        saved_name = f"{award_id}_{original}"
        target = UPLOAD_DIR / saved_name
        proof_file.save(target)
        saved_url = f"/api/files/awards/{saved_name}"

    award = Award(
        id=award_id,
        student_id=sid,
        award_name=award_name.strip(),
        award_time=award_time.strip(),
        proof_file_name=saved_name,
        proof_file_url=saved_url,
        status="pending",
        review_comment="",
        submitted_at=_now_iso(),
        reviewed_at="",
        reviewed_by="",
    )
    db.session.add(award)
    db.session.commit()
    return True, None, _award_to_dict(award)


def list_awards_for_admin(status: Optional[str] = None) -> List[Dict[str, Any]]:
    q = Award.query
    if status and status in {"pending", "approved", "rejected"}:
        q = q.filter_by(status=status)
    rows = q.order_by(Award.submitted_at.desc()).all()
    result = []
    for x in rows:
        row = _award_to_dict(x)
        stu = Student.query.filter_by(student_id=x.student_id).first()
        row["student_name"] = stu.display_name if stu else x.student_id
        result.append(row)
    return result


def review_award(
    award_id: str,
    status: str,
    review_comment: str,
    reviewer: str,
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    if status not in {"approved", "rejected"}:
        return False, "status must be approved or rejected", None
    target = Award.query.filter_by(id=award_id).first()
    if not target:
        return False, "award not found", None
    if status == "rejected" and not (review_comment or "").strip():
        return False, "reject_reason_required", None
    target.status = status
    target.review_comment = (review_comment or "").strip()
    target.reviewed_at = _now_iso()
    target.reviewed_by = reviewer or "admin"
    db.session.add(
        AwardReview(
            award_id=award_id,
            status=target.status,
            review_comment=target.review_comment,
            reviewed_at=target.reviewed_at,
            reviewed_by=target.reviewed_by,
        )
    )
    db.session.commit()
    return True, None, _award_to_dict(target)
