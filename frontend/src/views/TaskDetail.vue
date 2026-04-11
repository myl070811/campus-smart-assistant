<template>
  <div v-loading="loading" class="task-detail">
    <el-page-header class="task-detail__header" @back="goBack">
      <template #content>
        <span class="task-detail__title">{{ td(task?.title) || t('taskDetail') }}</span>
      </template>
    </el-page-header>

    <div v-if="loadError && !task" class="task-detail__error">
      <el-alert type="error" :title="loadError" :closable="false" show-icon />
      <div class="task-detail__error-actions">
        <el-button @click="goBack">{{ t('taskCenterTitle') }}</el-button>
        <el-button
          type="primary"
          :icon="Refresh"
          :loading="loading"
          circle
          :title="t('commonReload')"
          @click="load"
        />
      </div>
    </div>

    <el-card v-else-if="task" shadow="never" class="task-detail__card">
      <el-descriptions :column="1" border size="default" class="task-detail__desc">
        <el-descriptions-item :label="t('taskTitle')">{{ td(task.title) }}</el-descriptions-item>
        <el-descriptions-item :label="t('description')">
          <span class="task-detail__desc-text">{{ td(task.description) || t('taskDetailNoDescription') }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('source')">
          <el-tag :type="sourceTagType(task.sourceI18n)" effect="plain" size="small">
            {{ t(task.sourceI18n) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('type')">{{ t(task.typeI18n) }}</el-descriptions-item>
        <el-descriptions-item :label="t('owner')">{{ ownerLabel(task.ownerName, task.ownerIsSelf) }}</el-descriptions-item>
        <el-descriptions-item :label="t('deadline')">{{ task.dueDate }}</el-descriptions-item>
        <el-descriptions-item :label="t('priority')">
          <el-tag :type="priorityTagType(task.priorityI18n)" size="small">{{ t(task.priorityI18n) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item :label="t('status')">
          <el-tag :type="statusTagType(task.status)" size="small">{{ t(flowI18nKey(task.status)) }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div class="task-detail__section">
        <div class="task-detail__section-title">{{ t('taskWorkflow') }}</div>
        <el-steps :active="stepActive" finish-status="success" align-center class="task-detail__steps">
          <el-step :title="t('taskFlowPending')" />
          <el-step :title="t('taskFlowViewed')" />
          <el-step :title="t('taskFlowInProgress')" />
          <el-step :title="t('taskFlowDone')" />
        </el-steps>
        <div class="task-detail__actions">
          <el-button
            v-if="nextStatus"
            type="primary"
            :loading="statusSubmitting"
            @click="onAdvanceStatus"
          >
            {{ t('taskNextStepLabel').replace('{status}', t(flowI18nKey(nextStatus))) }}
          </el-button>
          <el-button :loading="transferSubmitting" @click="transferVisible = true">
            {{ t('taskTransfer') }}
          </el-button>
        </div>
      </div>

      <div class="task-detail__section">
        <div class="task-detail__section-title">{{ t('taskHistory') }}</div>
        <el-timeline v-if="history.length" class="task-detail__timeline">
          <el-timeline-item
            v-for="item in history"
            :key="item.id"
            :timestamp="item.createdAt"
            placement="top"
          >
            <div class="task-detail__log-line">{{ formatLogLine(item) }}</div>
            <div v-if="item.note" class="task-detail__log-note">{{ t('taskLogNotePrefix') }}{{ td(item.note) }}</div>
            <div class="task-detail__log-actor">{{ t('taskActor') }}：{{ td(item.actor || '—') }}</div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else :description="t('taskHistoryEmpty')" :image-size="72" />
      </div>
    </el-card>

    <el-dialog
      v-model="transferVisible"
      :title="t('taskTransferDialogTitle')"
      width="440px"
      destroy-on-close
      @closed="onTransferClosed"
    >
      <el-form label-position="top">
        <el-form-item :label="t('taskTransferToOwnerLabel')">
          <el-input v-model="transferTo" :placeholder="t('taskTransferToOwnerPlaceholder')" clearable />
        </el-form-item>
        <el-form-item :label="t('taskTransferNoteLabel')">
          <el-input
            v-model="transferNote"
            type="textarea"
            :rows="3"
            :placeholder="t('taskTransferNotePlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferVisible = false">{{ t('btnClose') }}</el-button>
        <el-button type="primary" :loading="transferSubmitting" @click="onTransferSubmit">
          {{ t('taskTransferSubmit') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getTaskDetail, transferTask, updateTaskStatus } from '../api/task'
import { t, td } from '../i18n'

const FLOW_ORDER = ['pending', 'viewed', 'in_progress', 'done']

const FLOW_I18N = {
  pending: 'taskFlowPending',
  viewed: 'taskFlowViewed',
  in_progress: 'taskFlowInProgress',
  done: 'taskFlowDone',
}

const NEXT_STATUS = {
  pending: 'viewed',
  viewed: 'in_progress',
  in_progress: 'done',
  done: null,
}

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const loadError = ref('')
const statusSubmitting = ref(false)
const transferSubmitting = ref(false)
const task = ref(null)
/** 接口字段为 logs，页面以时间线展示为 history（新在前） */
const history = ref([])
const transferVisible = ref(false)
const transferTo = ref('')
const transferNote = ref('')

const stepActive = computed(() => {
  const s = task.value?.status
  const i = FLOW_ORDER.indexOf(s)
  return i >= 0 ? i : 0
})

const nextStatus = computed(() => {
  const s = task.value?.status
  if (!s) return null
  return NEXT_STATUS[s] ?? null
})

function flowI18nKey(status) {
  return FLOW_I18N[status] || 'taskFlowPending'
}

function ownerLabel(ownerName, isSelf) {
  if (isSelf) return t('ownerSelf')
  const n = ownerName != null ? String(ownerName).trim() : ''
  return td(n) || '—'
}

function sourceTagType(sourceKey) {
  const map = {
    sourceCourse: 'primary',
    sourceOrganization: 'success',
    sourcePersonal: 'info',
    taskSourceLeague: 'primary',
    taskSourceParent: 'warning',
  }
  return map[sourceKey] ?? 'info'
}

function priorityTagType(priorityI18n) {
  const map = { priorityHigh: 'danger', priorityMedium: 'warning', priorityLow: 'info' }
  return map[priorityI18n] ?? 'info'
}

function statusTagType(status) {
  const map = {
    pending: 'info',
    viewed: '',
    in_progress: 'warning',
    done: 'success',
  }
  return map[status] ?? 'info'
}

function formatLogLine(log) {
  const action = log.action
  if (action === 'create') return t('taskLogCreate')
  if (action === 'view') return t('taskLogView')
  if (action === 'status_change') {
    const fromLabel =
      log.fromStatus != null ? t(flowI18nKey(log.fromStatus)) : '—'
    const toLabel = log.toStatus != null ? t(flowI18nKey(log.toStatus)) : '—'
    return t('taskLogStatusChange').replace('{from}', fromLabel).replace('{to}', toLabel)
  }
  if (action === 'transfer') {
    return t('taskLogTransfer')
      .replace('{from}', td(String(log.fromOwner ?? '—')))
      .replace('{to}', td(String(log.toOwner ?? '—')))
  }
  return action || '—'
}

async function load() {
  const id = route.params.id
  if (!id) {
    router.replace('/tasks')
    return
  }
  loading.value = true
  loadError.value = ''
  try {
    const data = await getTaskDetail(id)
    task.value = data.task
    history.value = Array.isArray(data.logs) ? [...data.logs].reverse() : []
  } catch (e) {
    const msg = td(e?.message || t('taskLoadFailed'))
    loadError.value = msg
    task.value = null
    history.value = []
    ElMessage.error(msg)
    if (e?.code === 'not_found') {
      router.replace('/tasks')
    }
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    load()
  },
  { immediate: true },
)

function goBack() {
  router.push('/tasks')
}

async function onAdvanceStatus() {
  const id = route.params.id
  const to = nextStatus.value
  if (!id || !to) return
  statusSubmitting.value = true
  try {
    const r = await updateTaskStatus(id, to)
    if (!r.success) {
      if (r.error === 'invalid_transition') {
        ElMessage.warning(t('taskInvalidTransition'))
      } else {
        ElMessage.error(td(r.message || t('taskLoadFailed')))
      }
      return
    }
    const payload = r.data || {}
    task.value = payload.task
    history.value = Array.isArray(payload.logs) ? [...payload.logs].reverse() : []
    ElMessage.success(t('taskStatusUpdated'))
  } catch (e) {
    ElMessage.error(td(e?.message || t('taskLoadFailed')))
  } finally {
    statusSubmitting.value = false
  }
}

function onTransferClosed() {
  transferTo.value = ''
  transferNote.value = ''
}

async function onTransferSubmit() {
  const id = route.params.id
  const to = transferTo.value.trim()
  if (!to) {
    ElMessage.warning(t('taskTransferOwnerRequired'))
    return
  }
  transferSubmitting.value = true
  try {
    const data = await transferTask(id, { to_owner: to, note: transferNote.value })
    task.value = data.task
    history.value = Array.isArray(data.logs) ? [...data.logs].reverse() : []
    transferVisible.value = false
    ElMessage.success(t('taskTransferSuccess'))
  } catch (e) {
    ElMessage.error(td(e?.message || t('taskLoadFailed')))
  } finally {
    transferSubmitting.value = false
  }
}
</script>

<style scoped>
.task-detail {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 32px;
}

.task-detail__error {
  margin-top: 12px;
}

.task-detail__error-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.task-detail__header {
  margin-bottom: 16px;
}

.task-detail__desc-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.task-detail__title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.task-detail__card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.task-detail__desc {
  margin-bottom: 8px;
}

.task-detail__section {
  margin-top: 24px;
}

.task-detail__section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.task-detail__steps {
  margin-bottom: 16px;
}

.task-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.task-detail__timeline {
  padding-left: 4px;
}

.task-detail__log-line {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
}

.task-detail__log-note {
  margin-top: 4px;
  font-size: 13px;
  color: #606266;
}

.task-detail__log-actor {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>
