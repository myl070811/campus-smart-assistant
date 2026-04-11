/**
 * 将 API 枚举值映射到 `i18n.js` 里已有 key（避免一次性重命名所有翻译条目）。
 */

export const taskSourceTypeToI18n = Object.freeze({
  course: 'sourceCourse',
  organization: 'sourceOrganization',
  personal: 'sourcePersonal',
  league: 'taskSourceLeague',
  parent_unit: 'taskSourceParent',
})

export const taskTypeToI18n = Object.freeze({
  homework: 'taskTypeHomework',
  affairs: 'taskTypeAffairs',
  review_study: 'taskTypeReviewStudy',
  approval: 'orgTaskApproval',
  material: 'orgTaskMaterial',
  coordinate: 'orgTaskCoordinate',
  planning: 'taskTypePlanning',
})

export const taskPriorityToI18n = Object.freeze({
  high: 'priorityHigh',
  medium: 'priorityMedium',
  low: 'priorityLow',
})

export const organizationTypeToI18n = Object.freeze({
  youth_league: 'orgTypeYouthLeague',
  student_union: 'orgTypeStudentOrg',
  club: 'orgTypeClub',
  academic: 'orgTypeClub',
})

export const leaderRoleToI18n = Object.freeze({
  teacher: 'roleTeacher',
  student: 'roleStudent',
  advisor: 'roleTeacher',
})

export const volunteerStatusToI18n = Object.freeze({
  recognized: 'volunteerRecognized',
  pending_review: 'pendingReview',
  reviewing: 'reviewing',
  rejected: 'reviewRejected',
})

export const awardLevelToI18n = Object.freeze({
  national: 'awardLevelNational',
  provincial: 'awardLevelProvincial',
  municipal: 'awardLevelSocial',
  school: 'awardLevelSchool',
  other: 'awardLevelSchool',
})

export const awardAuditToI18n = Object.freeze({
  approved: 'approved',
  pending_review: 'pendingReview',
  rejected: 'reviewRejected',
})

/** @param {Record<string, string>} map @param {string} v @param {string} fallback */
export function mapEnumToI18n(map, v, fallback) {
  if (v == null || v === '') return fallback
  const s = String(v)
  return map[s] ?? fallback
}
