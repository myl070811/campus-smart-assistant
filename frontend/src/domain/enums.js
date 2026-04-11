/**
 * 与后端 `data/enums.py` 一致的一组常量（值均为 snake_case）。
 * 页面展示文案通过 `domain/i18nBridge.js` 映射到现有 i18n key。
 */

export const TaskStatus = Object.freeze({
  PENDING: 'pending',
  VIEWED: 'viewed',
  IN_PROGRESS: 'in_progress',
  DONE: 'done',
})

export const TaskPriority = Object.freeze({
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
})

export const TaskSourceType = Object.freeze({
  COURSE: 'course',
  ORGANIZATION: 'organization',
  PERSONAL: 'personal',
  LEAGUE: 'league',
  PARENT_UNIT: 'parent_unit',
})

export const TaskType = Object.freeze({
  HOMEWORK: 'homework',
  AFFAIRS: 'affairs',
  REVIEW_STUDY: 'review_study',
  APPROVAL: 'approval',
  MATERIAL: 'material',
  COORDINATE: 'coordinate',
  PLANNING: 'planning',
})

export const OrganizationType = Object.freeze({
  YOUTH_LEAGUE: 'youth_league',
  STUDENT_UNION: 'student_union',
  CLUB: 'club',
  ACADEMIC: 'academic',
})

export const LeaderRole = Object.freeze({
  TEACHER: 'teacher',
  STUDENT: 'student',
  ADVISOR: 'advisor',
})

export const ScheduleEventType = Object.freeze({
  CLASS: 'class',
  PERSONAL_PLAN: 'personal_plan',
  ORG_TASK: 'org_task',
  VOLUNTEER: 'volunteer',
  WORK_STUDY: 'work_study',
  INNOVATION_PROJECT: 'innovation_project',
})

export const VolunteerStatus = Object.freeze({
  RECOGNIZED: 'recognized',
  PENDING_REVIEW: 'pending_review',
  REVIEWING: 'reviewing',
  REJECTED: 'rejected',
})

export const AwardLevel = Object.freeze({
  NATIONAL: 'national',
  PROVINCIAL: 'provincial',
  MUNICIPAL: 'municipal',
  SCHOOL: 'school',
  OTHER: 'other',
})

export const AwardAuditStatus = Object.freeze({
  APPROVED: 'approved',
  PENDING_REVIEW: 'pending_review',
  REJECTED: 'rejected',
})

export const TaskLogAction = Object.freeze({
  CREATE: 'create',
  VIEW: 'view',
  STATUS_CHANGE: 'status_change',
  TRANSFER: 'transfer',
})
