/**
 * API（snake_case）→ 前端视图模型（camelCase）。
 * 新业务优先只使用 camelCase 字段访问。
 */

import { OrganizationType } from './enums'
import {
  awardAuditToI18n,
  awardLevelToI18n,
  leaderRoleToI18n,
  mapEnumToI18n,
  organizationTypeToI18n,
  taskFlowToI18n,
  taskPriorityToI18n,
  taskSourceTypeToI18n,
  taskTypeToI18n,
  volunteerStatusToI18n,
} from './i18nBridge'

function pickStudent(raw) {
  if (!raw || typeof raw !== 'object') return {}
  return {
    studentId: raw.student_id ?? '',
    displayName: raw.display_name ?? '',
    phone: raw.phone ?? '',
    email: raw.email ?? '',
    wechat: raw.wechat ?? '',
    college: raw.college ?? '',
    major: raw.major ?? '',
    className: raw.class_name ?? '',
    volunteerRefId: raw.volunteer_ref_id ?? '',
    avatarUrl: raw.avatar_url ?? '',
    gradeYear: raw.grade_year != null ? Number(raw.grade_year) : null,
  }
}

/** 与 Profile 页模板字段对齐的 basicInfo 块 */
export function mapProfileFromApi(body) {
  if (!body || typeof body !== 'object') {
    return {
      basicInfo: {
        name: '',
        studentId: '',
        phone: '',
        wechat: '',
        email: '',
        college: '',
        major: '',
        className: '',
        volunteerId: '',
      },
      skillTags: [],
      volunteerRecords: [],
      honors: [],
    }
  }

  const rawStudent = body.student ?? body.basic_info
  const student =
    rawStudent != null && typeof rawStudent === 'object' ? rawStudent : {}
  const s = pickStudent(student)
  const basicInfo = {
    name: s.displayName || student.name || '',
    studentId: s.studentId,
    phone: s.phone,
    wechat: s.wechat,
    email: s.email,
    github: student.github ?? '',
    weibo: student.weibo ?? '',
    ethnicity: student.ethnicity ?? '',
    idCardNo: student.id_card_no ?? '',
    college: s.college,
    major: s.major,
    grade: student.grade ?? '',
    className: s.className,
    volunteerId: s.volunteerRefId || student.volunteer_id || '',
  }

  const tags = body.skill_tags ?? body.skillTags
  const skillTags = Array.isArray(tags) ? tags.filter((x) => typeof x === 'string') : []

  const vr = body.volunteer_records ?? body.volunteerRecords
  const volunteerRecords = Array.isArray(vr)
    ? vr.map((row) => ({
        id: row?.id ?? '',
        activityTitle: row?.activity_title ?? row?.activity ?? '',
        serviceDate: row?.service_date ?? row?.date ?? '',
        hours: Number(row?.hours) || 0,
        status: row?.status ?? 'pending_review',
      }))
    : []

  const awards = body.awards_public ?? body.awards ?? body.honors
  const honors = Array.isArray(awards)
    ? awards.map((row) => ({
        id: row?.id ?? '',
        awardName: row?.award_name ?? '',
        awardTime: row?.award_time ?? '',
        status: row?.status ?? 'pending',
        proofFileUrl: row?.proof_file_url ?? '',
        reviewComment: row?.review_comment ?? '',
        submittedAt: row?.submitted_at ?? '',
        reviewedAt: row?.reviewed_at ?? '',
        reviewedBy: row?.reviewed_by ?? '',
      }))
    : []

  const submissions = Array.isArray(body.awards_submissions)
    ? body.awards_submissions.map((row) => ({
        id: row?.id ?? '',
        awardName: row?.award_name ?? '',
        awardTime: row?.award_time ?? '',
        status: row?.status ?? 'pending',
        reviewComment: row?.review_comment ?? '',
        proofFileUrl: row?.proof_file_url ?? '',
        submittedAt: row?.submitted_at ?? '',
        reviewedAt: row?.reviewed_at ?? '',
        reviewedBy: row?.reviewed_by ?? '',
      }))
    : []

  const skillModules = Array.isArray(body.skill_modules)
    ? body.skill_modules.map((m) => ({
        module: m?.module ?? '',
        tags: Array.isArray(m?.tags) ? m.tags : [],
      }))
    : []

  return { basicInfo, skillTags, volunteerRecords, honors, submissions, skillModules }
}

/** 技能标签 id（skill_programming）→ i18n key（skillProgramming） */
export function skillTagIdToI18nKey(tagId) {
  if (!tagId || typeof tagId !== 'string') return ''
  return tagId.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}

function mapStats(raw) {
  if (!raw || typeof raw !== 'object') {
    return {
      todayCourses: 0,
      pendingTasks: 0,
      ongoingTasks: 0,
      volunteerHoursTotal: 0,
    }
  }
  return {
    todayCourses: Number(raw.today_course_count ?? raw.today_courses ?? 0) || 0,
    pendingTasks: Number(raw.pending_task_count ?? raw.pending_tasks ?? 0) || 0,
    ongoingTasks: Number(raw.ongoing_task_count ?? raw.ongoing_tasks ?? 0) || 0,
    volunteerHoursTotal: Number(raw.volunteer_hours_total ?? raw.volunteer_hours ?? 0) || 0,
  }
}

export function mapScheduleEventsFromApi(list) {
  if (!Array.isArray(list)) return []
  return list.map((ev) => ({
    id: ev?.id ?? '',
    title: ev?.title ?? '',
    eventType: ev?.event_type ?? ev?.event_kind ?? 'class',
    source: ev?.source ?? 'unknown',
    startAt: ev?.start_at ?? '',
    endAt: ev?.end_at ?? '',
    location: ev?.location ?? '',
    description: ev?.description ?? '',
    isEditable: Boolean(ev?.is_editable ?? false),
    eventDate: (ev?.start_at ?? '').slice(0, 10) || ev?.event_date || '',
    startTime: (ev?.start_at ?? '').slice(11, 16) || ev?.start_time || '',
    endTime: (ev?.end_at ?? '').slice(11, 16) || ev?.end_time || '',
    timeLabel: (ev?.start_at && ev?.end_at)
      ? `${String(ev.start_at).slice(11, 16)} — ${String(ev.end_at).slice(11, 16)}`
      : ev?.time ?? '',
  }))
}

export function mapDashboardFromApi(raw) {
  if (!raw || typeof raw !== 'object') {
    return {
      stats: mapStats(null),
      dateLabel: '',
      scheduleEvents: [],
      taskPreviews: [],
      weekSchedule: [],
      myTasksPreview: [],
      todaySchedule: [],
    }
  }

  const stats = mapStats(raw.stats)
  const dateLabel = raw.date_label ?? raw.dateLabel ?? ''
  const scheduleEvents = mapScheduleEventsFromApi(raw.schedule_events ?? raw.scheduleEvents)

  const previews = raw.task_previews ?? raw.my_tasks_preview ?? raw.myTasksPreview
  const taskPreviews = Array.isArray(previews)
    ? previews.map((p) => ({
        title: p?.title ?? '',
        status: p?.status ?? 'pending',
      }))
    : []

  const weekSchedule = Array.isArray(raw.week_schedule) ? raw.week_schedule : []

  const anchorMatch = String(dateLabel).match(/(\d{4}-\d{2}-\d{2})/)
  const anchorDate = anchorMatch ? anchorMatch[1] : ''
  const todaySchedule = anchorDate
    ? scheduleEvents
        .filter((e) => e.eventDate === anchorDate)
        .map((e) => ({
          name: e.title,
          time: e.timeLabel || `${e.startTime} — ${e.endTime}`,
        }))
    : []

  return {
    stats,
    dateLabel,
    scheduleEvents,
    taskPreviews,
    weekSchedule,
    myTasksPreview: taskPreviews,
    todaySchedule,
  }
}

export function mapOrganizationFromApi(raw) {
  if (!raw || typeof raw !== 'object') return null
  const id = raw.id != null ? String(raw.id) : ''
  if (!id) return null

  const orgType = raw.organization_type ?? raw.org_type ?? raw.orgType ?? OrganizationType.CLUB
  const leaderRole = raw.leader_role ?? raw.leaderRole ?? 'student'

  const tasksRaw = raw.tasks
  const tasks = Array.isArray(tasksRaw)
    ? tasksRaw
        .map((t) => {
          if (!t || typeof t !== 'object') return null
          const st = t.source_type ?? t.source ?? 'organization'
          const tt = t.task_type ?? t.type ?? 'affairs'
          return {
            id: String(t.id ?? ''),
            title: t.title ?? '',
            sourceType: st,
            taskType: tt,
            ownerName: t.owner_name ?? t.owner ?? '',
            status: t.status ?? 'pending',
            sourceKey: mapEnumToI18n(taskSourceTypeToI18n, st, 'sourceOrganization'),
            typeKey: mapEnumToI18n(taskTypeToI18n, tt, 'taskTypeAffairs'),
          }
        })
        .filter(Boolean)
    : []

  return {
    id,
    name: raw.name ?? '',
    shortName: raw.short_name ?? '',
    logoUrl: raw.logo_url ?? '',
    parentId: raw.parent_id ?? '',
    leaderStudentId: raw.leader_student_id ?? '',
    leaderTeacherName: raw.leader_teacher_name ?? '',
    organizationType: orgType,
    orgType: mapEnumToI18n(organizationTypeToI18n, orgType, 'orgTypeClub'),
    leaderName: raw.leader_name ?? raw.leaderName ?? '',
    leaderRole: mapEnumToI18n(leaderRoleToI18n, leaderRole, 'roleStudent'),
    memberCount: Number(raw.member_count ?? raw.memberCount ?? 0) || 0,
    description: raw.description ?? '',
    tasks,
  }
}

export function mapOrganizationListFromApi(list) {
  if (!Array.isArray(list)) return []
  return list.map(mapOrganizationFromApi).filter(Boolean)
}

/** 任务详情 / 列表项（camelCase） */
export function mapTaskFromApi(raw) {
  if (!raw || typeof raw !== 'object') return null
  const id = raw.id != null ? String(raw.id) : ''
  if (!id) return null

  const sourceType =
    raw.source_type ?? raw.source ?? 'personal'
  const taskType = raw.task_type ?? raw.type ?? 'affairs'
  const priority = raw.priority ?? 'medium'
  const ownerIsSelf = Boolean(raw.owner_is_self ?? raw.ownerIsSelf)
  let ownerName = raw.current_owner_name ?? raw.owner_name ?? raw.owner ?? ''
  if (ownerIsSelf && !ownerName) ownerName = ''

  const flowRaw = raw.assignment_type ?? raw.task_flow ?? 'single_department'
  const assignmentType = String(flowRaw || 'single_department')
  const collabRaw = raw.collaborating_org_ids
  const collaboratingOrgIds = Array.isArray(collabRaw)
    ? collabRaw.map((x) => String(x))
    : []

  return {
    id,
    title: raw.title ?? '',
    description: raw.description ?? '',
    taskType,
    sourceType,
    sourceOrgId: raw.source_org_id ?? '',
    currentOrgId: raw.current_org_id ?? '',
    ownerName,
    ownerIsSelf,
    dueDate: raw.due_date ?? raw.deadline ?? '',
    priority,
    status: raw.status ?? 'pending',
    assignmentType,
    collaboratingOrgIds,
    sourceI18n: mapEnumToI18n(taskSourceTypeToI18n, sourceType, 'sourcePersonal'),
    typeI18n: mapEnumToI18n(taskTypeToI18n, taskType, 'taskTypeAffairs'),
    priorityI18n: mapEnumToI18n(taskPriorityToI18n, priority, 'priorityMedium'),
    taskFlowI18n: mapEnumToI18n(taskFlowToI18n, assignmentType, 'taskFlowSingleDepartment'),
  }
}

export function mapTaskLogFromApi(log) {
  if (!log || typeof log !== 'object') return null
  return {
    id: log.id ?? '',
    action: log.action ?? '',
    actor: log.actor ?? '',
    createdAt: log.created_at ?? '',
    note: log.note ?? '',
    fromStatus: log.from_status ?? null,
    toStatus: log.to_status ?? null,
    fromOwner: log.from_owner ?? '',
    toOwner: log.to_owner ?? '',
  }
}
