from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .db import db
from .models import Organization, Task

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "org-logos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _task_summary(t: Task) -> Dict:
    return {
        "id": t.id,
        "title": t.title,
        "source_type": t.source_type,
        "task_type": t.task_type,
        "owner_name": t.current_owner_name,
        "status": t.status,
    }


def _org_with_tasks(org: Organization) -> Dict:
    tasks = Task.query.filter_by(current_org_id=org.id).order_by(Task.id.asc()).all()
    return {
        "id": org.id,
        "name": org.name,
        "short_name": org.short_name or "",
        "logo_url": org.logo_url or "",
        "parent_id": org.parent_id or "",
        "leader_student_id": org.leader_student_id or "",
        "leader_teacher_name": org.leader_teacher_name or "",
        "organization_type": org.organization_type,
        "leader_name": org.leader_name,
        "leader_role": org.leader_role,
        "member_count": org.member_count,
        "description": org.description or "",
        "tasks": [_task_summary(t) for t in tasks],
    }


def list_organizations() -> List[Dict]:
    orgs = Organization.query.order_by(Organization.id.asc()).all()
    return [_org_with_tasks(o) for o in orgs]


def get_organization(org_id: str) -> Optional[Dict]:
    org = Organization.query.filter_by(id=org_id).first()
    if not org:
        return None
    return _org_with_tasks(org)


def _new_org_id() -> str:
    rows = Organization.query.all()
    max_num = 0
    for row in rows:
        v = str(row.id or "")
        if v.startswith("org_") and v.split("_", 1)[1].isdigit():
            max_num = max(max_num, int(v.split("_", 1)[1]))
    return f"org_{max_num + 1:03d}"


def _save_logo(org_id: str, logo_file: Optional[FileStorage]) -> str:
    if not logo_file or not logo_file.filename:
        return ""
    original = secure_filename(logo_file.filename)
    if not original:
        raise ValueError("invalid logo file name")
    filename = f"{org_id}_{original}"
    target = UPLOAD_DIR / filename
    logo_file.save(target)
    return f"/api/files/org-logos/{filename}"


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": str(payload.get("name", "")).strip(),
        "short_name": str(payload.get("short_name", "")).strip(),
        "organization_type": str(payload.get("organization_type", "club")).strip() or "club",
        "parent_id": str(payload.get("parent_id", "")).strip(),
        "leader_student_id": str(payload.get("leader_student_id", "")).strip(),
        "leader_teacher_name": str(payload.get("leader_teacher_name", "")).strip(),
        "leader_name": str(payload.get("leader_name", "")).strip(),
        "leader_role": str(payload.get("leader_role", "student")).strip() or "student",
        "member_count": int(payload.get("member_count", 0) or 0),
        "description": str(payload.get("description", "")).strip(),
    }


def create_organization(payload: Dict[str, Any], logo_file: Optional[FileStorage]) -> Tuple[bool, Optional[str], Optional[Dict]]:
    body = _normalize_payload(payload)
    if not body["name"]:
        return False, "name is required", None

    org_id = str(payload.get("id", "")).strip() or _new_org_id()
    if Organization.query.filter_by(id=org_id).first():
        return False, "organization id already exists", None
    if body["parent_id"] and not Organization.query.filter_by(id=body["parent_id"]).first():
        return False, "parent organization not found", None
    try:
        logo_url = _save_logo(org_id, logo_file)
    except ValueError as exc:
        return False, str(exc), None

    org = Organization(
        id=org_id,
        name=body["name"],
        short_name=body["short_name"] or body["name"][:16],
        logo_url=logo_url,
        parent_id=body["parent_id"],
        leader_student_id=body["leader_student_id"],
        leader_teacher_name=body["leader_teacher_name"],
        organization_type=body["organization_type"],
        leader_name=body["leader_name"],
        leader_role=body["leader_role"],
        member_count=max(0, body["member_count"]),
        description=body["description"],
    )
    db.session.add(org)
    db.session.commit()
    return True, None, _org_with_tasks(org)


def update_organization(org_id: str, payload: Dict[str, Any], logo_file: Optional[FileStorage]) -> Tuple[bool, Optional[str], Optional[Dict]]:
    org = Organization.query.filter_by(id=org_id).first()
    if not org:
        return False, "organization not found", None
    body = _normalize_payload(payload)

    if body["name"]:
        org.name = body["name"]
    if body["short_name"]:
        org.short_name = body["short_name"]
    if body["organization_type"]:
        org.organization_type = body["organization_type"]
    if body["leader_student_id"] or "leader_student_id" in payload:
        org.leader_student_id = body["leader_student_id"]
    if body["leader_teacher_name"] or "leader_teacher_name" in payload:
        org.leader_teacher_name = body["leader_teacher_name"]
    if body["leader_name"] or "leader_name" in payload:
        org.leader_name = body["leader_name"]
    if body["leader_role"]:
        org.leader_role = body["leader_role"]
    if "member_count" in payload:
        org.member_count = max(0, body["member_count"])
    if "description" in payload:
        org.description = body["description"]

    if "parent_id" in payload:
        if body["parent_id"] == org_id:
            return False, "parent_id cannot be self", None
        if body["parent_id"] and not Organization.query.filter_by(id=body["parent_id"]).first():
            return False, "parent organization not found", None
        org.parent_id = body["parent_id"]
    try:
        logo_url = _save_logo(org_id, logo_file)
    except ValueError as exc:
        return False, str(exc), None
    if logo_url:
        org.logo_url = logo_url
    db.session.commit()
    return True, None, _org_with_tasks(org)


def delete_organization(org_id: str) -> Tuple[bool, Optional[str]]:
    org = Organization.query.filter_by(id=org_id).first()
    if not org:
        return False, "organization not found"
    if Organization.query.filter_by(parent_id=org_id).first():
        return False, "organization has child organizations"
    if Task.query.filter((Task.current_org_id == org_id) | (Task.source_org_id == org_id)).first():
        return False, "organization has related tasks"
    db.session.delete(org)
    db.session.commit()
    return True, None

