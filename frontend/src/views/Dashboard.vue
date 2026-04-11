<template>
  <div v-loading="loading" class="dashboard">
    <div class="dashboard__intro">
      <h1 class="dashboard__title">{{ t('dashboardTitle') }}</h1>
      <p class="dashboard__subtitle">{{ t('dashboardSubtitle') }}</p>
    </div>

    <el-alert type="info" :closable="false" show-icon class="dashboard__demo-hint">
      <template #title>{{ t('dashboardDemoHintTitle') }}</template>
      <div class="dashboard__demo-hint-body">{{ t('dashboardDemoHintBody') }}</div>
    </el-alert>

    <el-alert
      v-if="error"
      type="error"
      :title="error"
      :closable="false"
      show-icon
      class="dashboard__alert"
    />

    <el-row :gutter="16" class="dashboard__stats">
      <el-col v-for="item in statItems" :key="item.key" :xs="24" :sm="12" :lg="6">
        <el-card shadow="never" class="dashboard__stat-card">
          <div class="dashboard__stat-inner">
            <div class="dashboard__stat-icon" :class="`dashboard__stat-icon--${item.tone}`">
              <el-icon :size="22"><component :is="item.icon" /></el-icon>
            </div>
            <div class="dashboard__stat-body">
              <div class="dashboard__stat-value">{{ item.value }}</div>
              <div class="dashboard__stat-label">{{ item.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="dashboard__main">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="dashboard__panel">
          <template #header>
            <div class="dashboard__panel-head">
              <span class="dashboard__panel-title">{{ t('todaySchedule') }}</span>
              <span class="dashboard__panel-hint">{{ scheduleHint }}</span>
            </div>
          </template>
          <el-empty v-if="!todaySchedule.length" :description="t('dashboardEmptySchedule')" :image-size="72" />
          <ul v-else class="dashboard__schedule">
            <li v-for="(row, i) in todaySchedule" :key="i" class="dashboard__schedule-row">
              <span class="dashboard__schedule-time">{{ row.time }}</span>
              <span class="dashboard__schedule-name">{{ td(row.name) }}</span>
            </li>
          </ul>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="dashboard__panel">
          <template #header>
            <div class="dashboard__panel-head">
              <span class="dashboard__panel-title">{{ t('myTasks') }}</span>
              <router-link to="/tasks" class="dashboard__panel-link">{{ t('menuTasks') }}</router-link>
            </div>
          </template>
          <ul class="dashboard__task-list">
            <li v-for="(row, i) in topTasks" :key="i" class="dashboard__task-row">
              <span class="dashboard__task-title" :title="td(row.title)">{{ td(row.title) }}</span>
              <el-tag :type="statusTagType(row.status)" size="small">{{
                t(taskStatusLabelKey(row.status))
              }}</el-tag>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="dashboard__panel">
          <template #header>
            <div class="dashboard__panel-head">
              <span class="dashboard__panel-title">{{ t('dashboardLinkedMetrics') }}</span>
              <router-link to="/profile" class="dashboard__panel-link">{{ t('menuProfile') }}</router-link>
            </div>
          </template>
          <div class="dashboard__linked-grid">
            <div class="dashboard__linked-item">
              <div class="dashboard__linked-label">{{ t('dashboardVolunteerContribution') }}</div>
              <div class="dashboard__linked-value">{{ volunteerContribution }} {{ t('hoursUnit') }}</div>
            </div>
            <div class="dashboard__linked-item">
              <div class="dashboard__linked-label">{{ t('dashboardCompletedTasks') }}</div>
              <div class="dashboard__linked-value">{{ completedTaskCount }}</div>
            </div>
            <div class="dashboard__linked-item">
              <div class="dashboard__linked-label">{{ t('dashboardApprovedAwards') }}</div>
              <div class="dashboard__linked-value">{{ approvedAwardCount }}</div>
            </div>
            <div class="dashboard__linked-item">
              <div class="dashboard__linked-label">{{ t('dashboardCurrentRoleView') }}</div>
              <div class="dashboard__linked-value">{{ roleViewLabel }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="dashboard__panel">
          <template #header>
            <div class="dashboard__panel-head">
              <span class="dashboard__panel-title">{{ t('dashboardQuickActions') }}</span>
            </div>
          </template>
          <div class="dashboard__actions">
            <router-link class="dashboard__action-link" to="/tasks">{{ t('dashboardGoTasks') }}</router-link>
            <router-link class="dashboard__action-link" to="/profile">{{ t('dashboardGoProfile') }}</router-link>
            <router-link class="dashboard__action-link" to="/schedule">{{ t('dashboardGoSchedule') }}</router-link>
            <router-link v-if="roleState.roleCode !== 'student'" class="dashboard__action-link" to="/organization">{{ t('dashboardGoOrganization') }}</router-link>
            <router-link v-if="roleState.roleCode === 'tw_admin'" class="dashboard__action-link" to="/quality-review">{{ t('dashboardGoReview') }}</router-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Calendar, List, Loading, Clock, Trophy, Tickets, OfficeBuilding } from '@element-plus/icons-vue'
import { getDashboard } from '../api/dashboard'
import { getTasks } from '../api/task'
import { getProfile } from '../api/profile'
import { getAdminAwards } from '../api/adminAwards'
import { roleState } from '../stores/role'
import { langState, t, td } from '../i18n'

const loading = ref(true)
const error = ref('')
const dashboardPayload = ref(null)
const taskRows = ref([])
const profileSnapshot = ref(null)
const pendingAwards = ref(0)

const todaySchedule = computed(() => {
  const p = dashboardPayload.value
  const rows = p?.todaySchedule ?? p?.today_schedule
  return Array.isArray(rows) ? rows : []
})

const myTasksAll = computed(() => {
  const p = dashboardPayload.value
  const rows = p?.myTasksPreview ?? p?.taskPreviews ?? p?.my_tasks_preview
  return Array.isArray(rows) ? rows : []
})

const scheduleHint = computed(() => {
  void langState.current
  const p = dashboardPayload.value
  const label = p?.dateLabel ?? p?.date_label
  if (label != null && String(label).trim() !== '') return td(String(label).trim())
  return t('dashboardScheduleHint')
})

const topTasks = computed(() => myTasksAll.value.slice(0, 5))
const completedTaskCount = computed(() =>
  taskRows.value.filter((x) => x.status === 'done').length,
)
const approvedAwardCount = computed(() =>
  (profileSnapshot.value?.submissions || []).filter((x) => x.status === 'approved').length,
)
const volunteerContribution = computed(() => {
  const records = profileSnapshot.value?.volunteerRecords || []
  return records
    .filter((x) => x.status === 'recognized')
    .reduce((sum, x) => sum + Number(x.hours || 0), 0)
    .toFixed(1)
})
const roleViewLabel = computed(() => {
  if (roleState.roleCode === 'tw_admin') return t('roleTwAdmin')
  if (roleState.roleCode === 'org_admin') return t('roleOrgAdmin')
  return t('roleStudent')
})

const pendingTodoCount = computed(() => {
  const stats = dashboardPayload.value?.stats
  if (stats && typeof stats.pendingTasks === 'number') return stats.pendingTasks
  if (stats && typeof stats.pending_task_count === 'number') return stats.pending_task_count
  if (stats && typeof stats.pending_tasks === 'number') return stats.pending_tasks
  return myTasksAll.value.filter(
    (task) => task.status !== 'done' && task.status !== 'statusDone',
  ).length
})

const inProgressCount = computed(() => {
  const stats = dashboardPayload.value?.stats
  if (stats && typeof stats.ongoingTasks === 'number') return stats.ongoingTasks
  if (stats && typeof stats.ongoing_task_count === 'number') return stats.ongoing_task_count
  if (stats && typeof stats.ongoing_tasks === 'number') return stats.ongoing_tasks
  return myTasksAll.value.filter(
    (task) => task.status === 'in_progress' || task.status === 'statusDoing',
  ).length
})

const statItems = computed(() => {
  void langState.current
  const stats = dashboardPayload.value?.stats
  const courseCount =
    stats && typeof stats.todayCourses === 'number'
      ? stats.todayCourses
      : stats && typeof stats.today_course_count === 'number'
        ? stats.today_course_count
        : stats && typeof stats.today_courses === 'number'
          ? stats.today_courses
          : todaySchedule.value.length
  const volunteerVal =
    stats && typeof stats.volunteerHoursTotal === 'number'
      ? stats.volunteerHoursTotal
      : stats && typeof stats.volunteer_hours_total === 'number'
        ? stats.volunteer_hours_total
        : stats && typeof stats.volunteer_hours === 'number'
          ? stats.volunteer_hours
          : 0
  const base = [
    {
      key: 'courses',
      label: t('todayCourses'),
      value: courseCount,
      icon: Calendar,
      tone: 'blue',
    },
    {
      key: 'pending',
      label: t('pendingTasks'),
      value: pendingTodoCount.value,
      icon: List,
      tone: 'orange',
    },
    {
      key: 'doing',
      label: t('ongoingTasks'),
      value: inProgressCount.value,
      icon: Loading,
      tone: 'green',
    },
    {
      key: 'volunteer',
      label: t('volunteerHours'),
      value: `${volunteerVal} ${t('hoursUnit')}`,
      icon: Clock,
      tone: 'purple',
    },
  ]
  if (roleState.roleCode === 'student') {
    base.push(
      {
        key: 'completedTasks',
        label: t('dashboardCompletedTasks'),
        value: completedTaskCount.value,
        icon: Tickets,
        tone: 'green',
      },
      {
        key: 'approvedAwards',
        label: t('dashboardApprovedAwards'),
        value: approvedAwardCount.value,
        icon: Trophy,
        tone: 'blue',
      },
    )
  } else if (roleState.roleCode === 'org_admin') {
    const orgCount =
      stats && typeof stats.organization_count === 'number' ? stats.organization_count : 0
    base.push({
      key: 'orgCount',
      label: t('dashboardOrgCount'),
      value: orgCount,
      icon: OfficeBuilding,
      tone: 'blue',
    })
  } else if (roleState.roleCode === 'tw_admin') {
    base.push({
      key: 'pendingAwards',
      label: t('dashboardPendingReviews'),
      value: pendingAwards.value,
      icon: Trophy,
      tone: 'orange',
    })
  }
  return base
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const tasksPromise = getTasks().catch(() => [])
    const profilePromise = getProfile().catch(() => null)
    const adminAwardsPromise = roleState.roleCode === 'tw_admin'
      ? getAdminAwards('pending').catch(() => [])
      : Promise.resolve([])
    const [data, tasksData, profileData, pendingAwardsData] = await Promise.all([
      getDashboard(),
      tasksPromise,
      profilePromise,
      adminAwardsPromise,
    ])
    dashboardPayload.value = data && typeof data === 'object' ? data : null
    taskRows.value = Array.isArray(tasksData) ? tasksData : []
    profileSnapshot.value = profileData
    pendingAwards.value = Array.isArray(pendingAwardsData) ? pendingAwardsData.length : 0
  } catch (e) {
    dashboardPayload.value = null
    taskRows.value = []
    profileSnapshot.value = null
    pendingAwards.value = 0
    error.value = td(e?.message || t('scheduleLoadFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})

const FLOW_STATUS_LABEL = {
  pending: 'taskFlowPending',
  viewed: 'taskFlowViewed',
  in_progress: 'taskFlowInProgress',
  done: 'taskFlowDone',
}

function taskStatusLabelKey(status) {
  if (status && FLOW_STATUS_LABEL[status]) return FLOW_STATUS_LABEL[status]
  return status || 'taskFlowPending'
}

function statusTagType(status) {
  const flow = {
    pending: 'info',
    viewed: '',
    in_progress: 'warning',
    done: 'success',
  }
  if (flow[status] !== undefined) return flow[status]
  const legacy = {
    statusTodo: 'info',
    statusRead: '',
    statusDoing: 'warning',
    statusDone: 'success',
  }
  return legacy[status] ?? 'info'
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard__demo-hint {
  margin-bottom: 16px;
}

.dashboard__demo-hint-body {
  font-size: 13px;
  line-height: 1.65;
  color: #606266;
  margin-top: 6px;
  white-space: pre-line;
}

.dashboard__intro {
  margin-bottom: 20px;
}

.dashboard__title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.02em;
}

.dashboard__subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.dashboard__alert {
  margin-bottom: 16px;
}

.dashboard__stats {
  margin-bottom: 16px;
}

.dashboard__stat-card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.dashboard__stat-card :deep(.el-card__body) {
  padding: 18px 20px;
}

.dashboard__stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dashboard__stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dashboard__stat-icon--blue {
  background: #ecf5ff;
  color: #409eff;
}

.dashboard__stat-icon--orange {
  background: #fdf6ec;
  color: #e6a23c;
}

.dashboard__stat-icon--green {
  background: #f0f9ff;
  color: #67c23a;
}

.dashboard__stat-icon--purple {
  background: #f4f0ff;
  color: #8b5cf6;
}

.dashboard__stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.dashboard__stat-label {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

.dashboard__main {
  align-items: stretch;
}

.dashboard__panel {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  height: 100%;
  margin-bottom: 16px;
}

.dashboard__panel :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.dashboard__panel :deep(.el-card__body) {
  padding: 16px 20px 20px;
}

.dashboard__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.dashboard__panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.dashboard__panel-hint {
  font-size: 12px;
  color: #909399;
}

.dashboard__panel-link {
  font-size: 13px;
  color: #409eff;
  text-decoration: none;
}

.dashboard__panel-link:hover {
  color: #66b1ff;
}

.dashboard__schedule {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dashboard__schedule-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.dashboard__schedule-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.dashboard__schedule-row:first-child {
  padding-top: 0;
}

.dashboard__schedule-time {
  flex: 0 0 132px;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  color: #606266;
}

.dashboard__schedule-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.dashboard__task-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.dashboard__task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.dashboard__task-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.dashboard__task-row:first-child {
  padding-top: 0;
}

.dashboard__task-title {
  font-size: 14px;
  color: #303133;
  line-height: 1.45;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  flex: 1;
  min-width: 0;
}

.dashboard__linked-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(180px, 1fr));
  gap: 10px;
}

.dashboard__linked-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background: #fafafa;
}

.dashboard__linked-label {
  font-size: 12px;
  color: #909399;
}

.dashboard__linked-value {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}

.dashboard__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dashboard__action-link {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 10px 12px;
  color: #303133;
  text-decoration: none;
  font-size: 14px;
}

.dashboard__action-link:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>
