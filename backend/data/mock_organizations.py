from .models import Organization, Task


def list_organizations() -> list[dict]:
    orgs = Organization.query.order_by(Organization.id.asc()).all()
    result = []
    for org in orgs:
        tasks = Task.query.filter_by(current_org_id=org.id).order_by(Task.id.asc()).all()
        result.append(
            {
                "id": org.id,
                "name": org.name,
                "organization_type": org.organization_type,
                "leader_name": org.leader_name,
                "leader_role": org.leader_role,
                "member_count": org.member_count,
                "description": org.description or "",
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "source_type": t.source_type,
                        "task_type": t.task_type,
                        "owner_name": t.current_owner_name,
                        "status": t.status,
                    }
                    for t in tasks
                ],
            }
        )
    return result
