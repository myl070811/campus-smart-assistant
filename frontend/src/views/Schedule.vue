<template>
  <div v-loading="loading" class="schedule">
    <el-card shadow="never" class="schedule__hero">
      <div class="schedule__hero-head">
        <div>
          <h1 class="schedule__title">{{ t('scheduleCenterTitle') }}</h1>
          <p class="schedule__subtitle">
            {{ t('scheduleCenterSubtitle') }}
          </p>
        </div>
        <el-button type="primary" @click="openCreatePlan">{{ t('scheduleAddPersonal') }}</el-button>
      </div>

      <div class="schedule__toolbar">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="week">{{ t('scheduleViewWeek') }}</el-radio-button>
          <el-radio-button label="day">{{ t('scheduleViewDay') }}</el-radio-button>
          <el-radio-button label="month">{{ t('scheduleViewMonth') }}</el-radio-button>
        </el-radio-group>
        <el-date-picker v-model="selectedDate" type="date" value-format="YYYY-MM-DD" />
      </div>

      <div class="schedule__filters">
        <el-checkbox-group v-model="selectedTypes">
          <el-checkbox v-for="item in typeOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </el-card>

    <el-alert v-if="error" type="error" :title="error" :closable="false" show-icon class="schedule__alert" />

    <el-row :gutter="12" class="schedule__stats">
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="schedule__stat-card">
          <div class="schedule__stat-value">{{ statCards.weekClassCount }}</div>
          <div class="schedule__stat-label">{{ t('scheduleStatWeekClasses') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="schedule__stat-card">
          <div class="schedule__stat-value">{{ statCards.pendingTaskCount }}</div>
          <div class="schedule__stat-label">{{ t('scheduleStatPendingTasks') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="schedule__stat-card">
          <div class="schedule__stat-value">{{ statCards.volunteerHours }}</div>
          <div class="schedule__stat-label">{{ t('scheduleStatVolunteerHours') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="schedule__stat-card">
          <div class="schedule__stat-value">{{ statCards.weekPlanCount }}</div>
          <div class="schedule__stat-label">{{ t('scheduleStatWeekPlans') }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="schedule__panel">
      <template #header>
        <div class="schedule__panel-head">
          <span>{{ t('scheduleTodayTimeline').replace('{date}', selectedDate) }}</span>
          <span class="schedule__muted">{{ t('scheduleCountItems').replace('{count}', dayEvents.length) }}</span>
        </div>
      </template>
      <el-empty v-if="!dayEvents.length" :description="t('scheduleTodayNoEvents')" :image-size="60" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="ev in dayEvents"
          :key="`today-${ev.id}`"
          :timestamp="`${ev.startTime} - ${ev.endTime}`"
          placement="top"
        >
          <div class="schedule__event-row" @click="openDetail(ev)">
            <span class="schedule__event-title">{{ td(ev.title) }}</span>
            <el-tag size="small" :type="typeTagType(ev.eventType)">{{ typeLabel(ev.eventType) }}</el-tag>
          </div>
          <div class="schedule__event-meta">{{ td(ev.location || '—') }} · {{ sourceLabel(ev.source) }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-card v-if="viewMode === 'day'" shadow="never" class="schedule__panel">
      <template #header>
        <div class="schedule__panel-head">
          <span>{{ t('scheduleDayEvents').replace('{date}', selectedDate) }}</span>
          <span class="schedule__muted">{{ t('scheduleCountItems').replace('{count}', dayEvents.length) }}</span>
        </div>
      </template>
      <el-empty v-if="!dayEvents.length" :description="t('scheduleNoEvents')" :image-size="72" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="ev in dayEvents"
          :key="ev.id"
          :timestamp="`${ev.startTime} - ${ev.endTime}`"
          placement="top"
        >
          <div class="schedule__event-row" @click="openDetail(ev)">
            <span class="schedule__event-title">{{ td(ev.title) }}</span>
            <el-tag size="small" :type="typeTagType(ev.eventType)">{{ typeLabel(ev.eventType) }}</el-tag>
          </div>
          <div class="schedule__event-meta">{{ td(ev.location || '—') }} · {{ sourceLabel(ev.source) }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-card v-else-if="viewMode === 'month'" shadow="never" class="schedule__panel">
      <template #header>
        <div class="schedule__panel-head">
          <span>{{ monthTitle }}</span>
          <span class="schedule__muted">{{ t('scheduleJumpToDayHint') }}</span>
        </div>
      </template>
      <div class="schedule__month-weekdays">
        <div v-for="wd in monthWeekdayHeaders" :key="wd" class="schedule__month-weekday">{{ wd }}</div>
      </div>
      <div class="schedule__month-grid">
        <button
          v-for="cell in monthCells"
          :key="cell.date"
          type="button"
          class="schedule__month-cell"
          :class="{
            'is-current-month': cell.inCurrentMonth,
            'is-selected': cell.date === selectedDate,
            'has-events': cell.events.length > 0,
          }"
          @click="openDayFromMonth(cell.date)"
        >
          <div class="schedule__month-cell-head">
            <span class="schedule__month-day">{{ cell.day }}</span>
            <span v-if="cell.events.length" class="schedule__month-count">{{ cell.events.length }}</span>
          </div>
          <ul v-if="cell.events.length" class="schedule__month-events">
            <li v-for="ev in cell.events.slice(0, 3)" :key="`${cell.date}-${ev.id}`" class="schedule__month-event">
              <span class="schedule__month-dot" :class="`dot-${ev.eventType}`"></span>
              <span class="schedule__month-event-title">{{ td(ev.title) }}</span>
            </li>
            <li v-if="cell.events.length > 3" class="schedule__month-more">
              +{{ cell.events.length - 3 }} {{ t('scheduleMoreEvents') }}
            </li>
          </ul>
          <div v-else class="schedule__month-empty">{{ t('scheduleNoEvents') }}</div>
        </button>
      </div>
    </el-card>

    <div v-else class="schedule__week-grid">
      <el-card v-for="day in weekDays" :key="day.date" shadow="never" class="schedule__day-card">
        <template #header>
          <div class="schedule__day-head">
            <span>{{ day.label }}</span>
            <span class="schedule__muted">{{ day.date }}</span>
          </div>
        </template>
        <ul v-if="day.events.length" class="schedule__list">
          <li v-for="ev in day.events" :key="ev.id" class="schedule__item" @click="openDetail(ev)">
            <div class="schedule__item-title">{{ td(ev.title) }}</div>
            <div class="schedule__item-meta">{{ ev.startTime }}-{{ ev.endTime }}</div>
            <el-tag size="small" :type="typeTagType(ev.eventType)">{{ typeLabel(ev.eventType) }}</el-tag>
          </li>
        </ul>
        <el-empty v-else :description="t('scheduleNoEvents')" :image-size="48" />
      </el-card>
    </div>

    <el-dialog v-model="detailVisible" :title="t('scheduleEventDetail')" width="520px">
      <template v-if="currentEvent">
        <el-descriptions border :column="1">
          <el-descriptions-item :label="t('scheduleFieldTitle')">{{ td(currentEvent.title) }}</el-descriptions-item>
          <el-descriptions-item :label="t('scheduleFieldType')">{{ typeLabel(currentEvent.eventType) }}</el-descriptions-item>
          <el-descriptions-item :label="t('scheduleFieldTimeRange')">{{ currentEvent.startAt }} ~ {{ currentEvent.endAt }}</el-descriptions-item>
          <el-descriptions-item :label="t('scheduleFieldLocation')">{{ td(currentEvent.location || '—') }}</el-descriptions-item>
          <el-descriptions-item :label="t('scheduleFieldSource')">{{ sourceLabel(currentEvent.source) }}</el-descriptions-item>
          <el-descriptions-item :label="t('scheduleFieldNote')">{{ td(currentEvent.description || '—') }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">{{ t('btnClose') }}</el-button>
        <el-button v-if="currentEvent?.isEditable" type="primary" @click="openEditPlan(currentEvent)">{{ t('scheduleEditPlan') }}</el-button>
        <el-popconfirm
          v-if="currentEvent?.isEditable"
          :title="t('scheduleDeletePlanConfirm')"
          @confirm="onDeletePlan(currentEvent.id)"
        >
          <template #reference>
            <el-button type="danger">{{ t('scheduleDeletePlan') }}</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-dialog>

    <el-dialog v-model="planVisible" :title="editingPlanId ? t('scheduleEditPlanTitle') : t('scheduleCreatePlanTitle')" width="560px">
      <el-form label-position="top">
        <el-form-item :label="t('scheduleFieldTitle')">
          <el-input v-model="planForm.title" maxlength="60" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('scheduleFieldStartTime')">
              <el-date-picker v-model="planForm.startAt" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('scheduleFieldEndTime')">
              <el-date-picker v-model="planForm.endAt" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('scheduleFieldLocation')">
          <el-input v-model="planForm.location" />
        </el-form-item>
        <el-form-item :label="t('scheduleFieldNoteText')">
          <el-input v-model="planForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="onSubmitPlan">{{ t('scheduleSave') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createSchedulePlan,
  deleteSchedulePlan,
  getScheduleEvents,
  updateSchedulePlan,
} from '../api/schedule'
import { t, td } from '../i18n'

const typeOptions = computed(() => [
  { value: 'class', label: t('scheduleSectionCourses') },
  { value: 'personal_plan', label: t('scheduleSectionPersonal') },
  { value: 'org_task', label: t('sourceOrganization') },
  { value: 'volunteer', label: t('volunteerRecords') },
  { value: 'work_study', label: t('orgTaskAffairs') },
  { value: 'innovation_project', label: t('taskTypePlanning') },
])

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const events = ref([])
const selectedTypes = ref(['class', 'personal_plan', 'org_task', 'volunteer', 'work_study', 'innovation_project'])
const selectedDate = ref('2026-04-02')
const viewMode = ref('week')

const detailVisible = ref(false)
const currentEvent = ref(null)

const planVisible = ref(false)
const editingPlanId = ref('')
const planForm = ref({
  title: '',
  startAt: '',
  endAt: '',
  location: '',
  description: '',
})

function typeLabel(type) {
  return typeOptions.value.find((x) => x.value === type)?.label || type
}

function typeTagType(type) {
  const map = {
    class: 'primary',
    personal_plan: 'success',
    org_task: 'warning',
    volunteer: 'danger',
    work_study: 'info',
    innovation_project: '',
  }
  return map[type] ?? 'info'
}

function sourceLabel(source) {
  const map = {
    academic_system: t('scheduleSourceAcademic'),
    org_task_center: t('scheduleSourceOrgTask'),
    volunteer_platform: t('scheduleSourceVolunteer'),
    work_study_system: t('scheduleSourceWorkStudy'),
    innovation_platform: t('scheduleSourceInnovation'),
    manual_input: t('scheduleSourceManual'),
  }
  return map[source] ?? t('scheduleSourceExternal').replace('{source}', source || 'unknown')
}

const filteredEvents = computed(() => {
  const allow = new Set(selectedTypes.value)
  return events.value.filter((e) => allow.has(e.eventType))
})

const dayEvents = computed(() =>
  filteredEvents.value
    .filter((e) => e.eventDate === selectedDate.value)
    .sort((a, b) => `${a.startAt}`.localeCompare(`${b.startAt}`)),
)

function weekdayLabel(d) {
  const names = [
    t('scheduleWeekdaySun'),
    t('scheduleWeekdayMon'),
    t('scheduleWeekdayTue'),
    t('scheduleWeekdayWed'),
    t('scheduleWeekdayThu'),
    t('scheduleWeekdayFri'),
    t('scheduleWeekdaySat'),
  ]
  return names[d.getDay()]
}

function startOfWeek(isoDate) {
  const d = new Date(`${isoDate}T00:00:00`)
  const diff = d.getDay() === 0 ? -6 : 1 - d.getDay()
  d.setDate(d.getDate() + diff)
  return d
}

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const weekDays = computed(() => {
  const base = startOfWeek(selectedDate.value)
  const rows = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(base)
    d.setDate(base.getDate() + i)
    const date = formatDate(d)
    rows.push({
      date,
      label: weekdayLabel(d),
      events: filteredEvents.value
        .filter((e) => e.eventDate === date)
        .sort((a, b) => `${a.startAt}`.localeCompare(`${b.startAt}`)),
    })
  }
  return rows
})

const monthTitle = computed(() => {
  const d = new Date(`${selectedDate.value}T00:00:00`)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${y}-${m}`
})

const monthWeekdayHeaders = computed(() => [
  t('scheduleWeekdayMon'),
  t('scheduleWeekdayTue'),
  t('scheduleWeekdayWed'),
  t('scheduleWeekdayThu'),
  t('scheduleWeekdayFri'),
  t('scheduleWeekdaySat'),
  t('scheduleWeekdaySun'),
])

function monthMatrixStart(isoDate) {
  const d = new Date(`${isoDate}T00:00:00`)
  d.setDate(1)
  const day = d.getDay() || 7 // Monday=1 ... Sunday=7
  d.setDate(d.getDate() - (day - 1))
  return d
}

const monthCells = computed(() => {
  const selected = new Date(`${selectedDate.value}T00:00:00`)
  const month = selected.getMonth()
  const start = monthMatrixStart(selectedDate.value)
  const rows = []
  for (let i = 0; i < 42; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const date = formatDate(d)
    const eventsOfDay = filteredEvents.value
      .filter((e) => e.eventDate === date)
      .sort((a, b) => `${a.startAt}`.localeCompare(`${b.startAt}`))
    rows.push({
      date,
      day: d.getDate(),
      inCurrentMonth: d.getMonth() === month,
      events: eventsOfDay,
    })
  }
  return rows
})

const weekRange = computed(() => {
  const base = startOfWeek(selectedDate.value)
  const start = formatDate(base)
  const endDate = new Date(base)
  endDate.setDate(base.getDate() + 6)
  const end = formatDate(endDate)
  return { start, end }
})

function inCurrentWeek(dateStr) {
  return dateStr >= weekRange.value.start && dateStr <= weekRange.value.end
}

function durationHours(ev) {
  const s = new Date(ev.startAt).getTime()
  const e = new Date(ev.endAt).getTime()
  if (!Number.isFinite(s) || !Number.isFinite(e) || e <= s) return 0
  return (e - s) / 3600000
}

const statCards = computed(() => {
  const weekEvents = events.value.filter((e) => inCurrentWeek(e.eventDate))
  const weekClassCount = weekEvents.filter((e) => e.eventType === 'class').length
  const pendingTaskCount = weekEvents.filter((e) =>
    ['org_task', 'work_study', 'innovation_project', 'personal_plan'].includes(e.eventType),
  ).length
  const volunteerHours = weekEvents
    .filter((e) => e.eventType === 'volunteer')
    .reduce((sum, ev) => sum + durationHours(ev), 0)
    .toFixed(1)
  const weekPlanCount = weekEvents.filter((e) => e.eventType === 'personal_plan').length
  return { weekClassCount, pendingTaskCount, volunteerHours, weekPlanCount }
})

async function loadEvents() {
  loading.value = true
  error.value = ''
  try {
    events.value = await getScheduleEvents()
  } catch (e) {
    error.value = td(e?.message || t('scheduleLoadError'))
  } finally {
    loading.value = false
  }
}

function openDetail(ev) {
  currentEvent.value = ev
  detailVisible.value = true
}

function openDayFromMonth(date) {
  selectedDate.value = date
  viewMode.value = 'day'
}

function openCreatePlan() {
  editingPlanId.value = ''
  planForm.value = { title: '', startAt: '', endAt: '', location: '', description: '' }
  planVisible.value = true
}

function openEditPlan(ev) {
  detailVisible.value = false
  editingPlanId.value = ev.id
  planForm.value = {
    title: ev.title || '',
    startAt: ev.startAt || '',
    endAt: ev.endAt || '',
    location: ev.location || '',
    description: ev.description || '',
  }
  planVisible.value = true
}

async function onSubmitPlan() {
  saving.value = true
  try {
    const payload = {
      title: planForm.value.title,
      start_at: planForm.value.startAt,
      end_at: planForm.value.endAt,
      location: planForm.value.location,
      description: planForm.value.description,
    }
    if (editingPlanId.value) {
      await updateSchedulePlan(editingPlanId.value, payload)
      ElMessage.success(t('schedulePlanUpdated'))
    } else {
      await createSchedulePlan(payload)
      ElMessage.success(t('schedulePlanCreated'))
    }
    planVisible.value = false
    await loadEvents()
  } catch (e) {
    ElMessage.error(td(e?.message || t('schedulePlanSavedError')))
  } finally {
    saving.value = false
  }
}

async function onDeletePlan(id) {
  try {
    await deleteSchedulePlan(id)
    detailVisible.value = false
    ElMessage.success(t('schedulePlanDeleted'))
    await loadEvents()
  } catch (e) {
    ElMessage.error(td(e?.message || t('schedulePlanDeleteError')))
  }
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.schedule { max-width: 1200px; margin: 0 auto; }
.schedule__hero { margin-bottom: 16px; border: 1px solid #ebeef5; }
.schedule__hero-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.schedule__title { margin: 0 0 6px; font-size: 24px; font-weight: 700; color: #303133; }
.schedule__subtitle { margin: 0; color: #606266; line-height: 1.6; }
.schedule__toolbar { margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.schedule__filters { margin-top: 12px; padding-top: 10px; border-top: 1px dashed #ebeef5; }
.schedule__alert { margin-bottom: 12px; }
.schedule__stats { margin-bottom: 12px; }
.schedule__stat-card { border: 1px solid #ebeef5; }
.schedule__stat-value { font-size: 24px; font-weight: 700; color: #303133; line-height: 1.2; }
.schedule__stat-label { margin-top: 6px; color: #909399; font-size: 12px; }
.schedule__panel { border: 1px solid #ebeef5; }
.schedule__panel-head { display: flex; justify-content: space-between; align-items: center; }
.schedule__muted { color: #909399; font-size: 12px; }
.schedule__event-row { display: flex; justify-content: space-between; align-items: center; gap: 10px; cursor: pointer; }
.schedule__event-title { font-weight: 600; color: #303133; }
.schedule__event-meta { margin-top: 4px; color: #909399; font-size: 12px; }
.schedule__week-grid { display: grid; grid-template-columns: repeat(7, minmax(120px, 1fr)); gap: 10px; }
.schedule__day-card { border: 1px solid #ebeef5; }
.schedule__day-head { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.schedule__list { list-style: none; margin: 0; padding: 0; }
.schedule__item { padding: 8px 0; border-bottom: 1px solid #f2f4f8; cursor: pointer; }
.schedule__item:last-child { border-bottom: none; }
.schedule__item-title { font-size: 13px; color: #303133; }
.schedule__item-meta { font-size: 12px; color: #909399; margin: 3px 0 6px; }
.schedule__month-weekdays { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-bottom: 8px; }
.schedule__month-weekday { text-align: center; font-size: 12px; color: #909399; font-weight: 600; }
.schedule__month-grid { display: grid; grid-template-columns: repeat(7, minmax(110px, 1fr)); gap: 8px; }
.schedule__month-cell { border: 1px solid #ebeef5; border-radius: 8px; background: #fff; min-height: 118px; padding: 8px; text-align: left; cursor: pointer; }
.schedule__month-cell.is-selected { border-color: #409eff; box-shadow: 0 0 0 1px rgba(64, 158, 255, .2); }
.schedule__month-cell:not(.is-current-month) { opacity: 0.55; }
.schedule__month-cell.has-events { background: #fafcff; }
.schedule__month-cell-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.schedule__month-day { font-size: 13px; font-weight: 700; color: #303133; }
.schedule__month-count { font-size: 11px; color: #606266; background: #f2f4f8; border-radius: 10px; padding: 1px 6px; }
.schedule__month-events { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 3px; }
.schedule__month-event { display: flex; align-items: center; gap: 5px; }
.schedule__month-dot { width: 6px; height: 6px; border-radius: 50%; background: #909399; flex-shrink: 0; }
.schedule__month-dot.dot-class { background: #409eff; }
.schedule__month-dot.dot-personal_plan { background: #67c23a; }
.schedule__month-dot.dot-org_task { background: #e6a23c; }
.schedule__month-dot.dot-volunteer { background: #f56c6c; }
.schedule__month-dot.dot-work_study { background: #909399; }
.schedule__month-dot.dot-innovation_project { background: #8b5cf6; }
.schedule__month-event-title { font-size: 11px; color: #606266; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.schedule__month-more { font-size: 11px; color: #909399; }
.schedule__month-empty { font-size: 11px; color: #c0c4cc; }
@media (max-width: 1100px) { .schedule__week-grid { grid-template-columns: repeat(3, minmax(120px, 1fr)); } }
@media (max-width: 1100px) { .schedule__month-grid { grid-template-columns: repeat(3, minmax(120px, 1fr)); } }
</style>
