<template>
  <div class="task-center">
    <el-card shadow="never" class="task-center__card">
      <template #header>
        <div class="task-center__header">
          <div>
            <h1 class="task-center__title">{{ t('taskCenterTitle') }}</h1>
            <p class="task-center__subtitle">{{ t('taskCenterSubtitle') }}</p>
          </div>
          <el-button type="primary" :icon="Plus" @click="onAddTask">{{ t('addTask') }}</el-button>
        </div>
      </template>

      <div class="task-center__ai">
        <el-input
          v-model="aiPrompt"
          class="task-center__ai-input"
          :placeholder="t('taskInputPlaceholder')"
          clearable
          :disabled="aiGenerating"
          @keyup.enter="onAiGenerate"
        />
        <el-button
          type="success"
          :icon="MagicStick"
          :loading="aiGenerating"
          @click="onAiGenerate"
        >
          {{ t('aiGenerate') }}
        </el-button>
      </div>

      <el-table
        :data="taskList"
        stripe
        border
        class="task-center__table"
        :empty-text="t('taskCenterNoTasks')"
        :row-class-name="rowClassName"
        :row-key="(row) => row._rowId"
        highlight-current-row
        @row-click="onRowClick"
      >
        <el-table-column prop="title" :label="t('taskTitle')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ td(row.title) }}</template>
        </el-table-column>
        <el-table-column prop="source" :label="t('source')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="sourceTagType(row.source)" effect="plain" size="small">
              {{ t(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" :label="t('type')" width="120" align="center">
          <template #default="{ row }">
            {{ t(row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="owner" :label="t('owner')" width="100" align="center">
          <template #default="{ row }">
            {{ row.owner === 'ownerSelf' ? t('ownerSelf') : td(row.owner) }}
          </template>
        </el-table-column>
        <el-table-column prop="deadline" :label="t('deadline')" width="120" align="center" />
        <el-table-column prop="priority" :label="t('priority')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" size="small">
              {{ t(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ t(statusDisplayKey(row.status)) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      :title="t('taskDetail')"
      width="520px"
      align-center
      destroy-on-close
      class="task-center__detail-dialog"
      @closed="onDetailClosed"
    >
      <template v-if="detailTask">
        <el-descriptions :column="1" border size="default" class="task-center__descriptions">
          <el-descriptions-item :label="t('taskTitle')" label-class-name="task-center__desc-label">
            {{ td(detailTask.title) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('source')" label-class-name="task-center__desc-label">
            <el-tag :type="sourceTagType(detailTask.source)" effect="plain" size="small">
              {{ t(detailTask.source) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('type')" label-class-name="task-center__desc-label">
            {{ t(detailTask.type) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('owner')" label-class-name="task-center__desc-label">
            {{ detailTask.owner === 'ownerSelf' ? t('ownerSelf') : td(detailTask.owner) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('deadline')" label-class-name="task-center__desc-label">
            {{ detailTask.deadline }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('priority')" label-class-name="task-center__desc-label">
            <el-tag :type="priorityTagType(detailTask.priority)" size="small">
              {{ t(detailTask.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('status')" label-class-name="task-center__desc-label">
            <el-tag :type="statusTagType(detailTask.status)" size="small">
              {{ t(statusDisplayKey(detailTask.status)) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="task-center__detail-block">
          <div class="task-center__detail-block-title">{{ t('taskDescriptionSection') }}</div>
          <p class="task-center__detail-block-text">{{ detailMockDescription }}</p>
        </div>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('btnClose') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createVisible" :title="t('addTask')" width="560px" destroy-on-close @closed="resetCreateForm">
      <el-form label-position="top">
        <el-form-item :label="t('taskTitle')">
          <el-input v-model="createForm.title" maxlength="80" />
        </el-form-item>
        <el-form-item :label="t('description')">
          <el-input v-model="createForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('type')">
              <el-select v-model="createForm.task_type" style="width: 100%">
                <el-option :label="t('taskTypePlanning')" value="planning" />
                <el-option :label="t('taskTypeExecute')" value="execute" />
                <el-option :label="t('taskTypeResearch')" value="research" />
                <el-option :label="t('taskTypeRetrospective')" value="retrospective" />
                <el-option :label="t('taskTypeAffairs')" value="affairs" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('priority')">
              <el-select v-model="createForm.priority" style="width: 100%">
                <el-option :label="t('priorityHigh')" value="high" />
                <el-option :label="t('priorityMedium')" value="medium" />
                <el-option :label="t('priorityLow')" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('deadline')">
          <el-date-picker v-model="createForm.deadline" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="submitCreateTask">{{ t('scheduleSave') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createTask, getTasks } from '../api/task'
import { t, td } from '../i18n'
import { roleState } from '../stores/role'

const router = useRouter()

const FLOW_STATUS_I18N = {
  pending: 'taskFlowPending',
  viewed: 'taskFlowViewed',
  in_progress: 'taskFlowInProgress',
  done: 'taskFlowDone',
}

function statusDisplayKey(status) {
  return FLOW_STATUS_I18N[status] || status
}

let rowIdSeq = 0
function nextRowId() {
  return `row_${Date.now()}_${++rowIdSeq}`
}

function deadlineAfter(days) {
  const d = new Date('2026-03-29')
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

/** 后端工作流状态 → pending | viewed | in_progress | done */
function normalizeWorkflowStatus(v) {
  if (v == null || v === '') return 'pending'
  const s = String(v).trim()
  if (['pending', 'viewed', 'in_progress', 'done'].includes(s)) return s
  if (['statusTodo', 'statusRead', 'statusDoing', 'statusDone'].includes(s)) {
    return {
      statusTodo: 'pending',
      statusRead: 'viewed',
      statusDoing: 'in_progress',
      statusDone: 'done',
    }[s]
  }
  const lower = s.toLowerCase().replace(/\s+/g, '_')
  if (lower === 'todo' || lower === 'pending' || s === '待办' || s === '待查看') return 'pending'
  if (lower === 'read' || lower === 'viewed' || s === '已读' || s === '已查看') return 'viewed'
  if (lower === 'doing' || lower === 'in_progress' || s === '进行中') return 'in_progress'
  if (lower === 'done' || lower === 'completed' || s === '已完成' || s === '完成') return 'done'
  return 'pending'
}

/**
 * 将领域任务（API 已映射为 camelCase）转为表格行
 */
function mapDomainTaskToRow(t) {
  if (!t || typeof t !== 'object' || !t.title) return null
  const id = t.id != null ? String(t.id) : ''
  return {
    title: t.title,
    source: t.sourceI18n,
    type: t.typeI18n,
    owner: t.ownerIsSelf ? 'ownerSelf' : t.ownerName || '—',
    deadline: t.dueDate ?? '',
    priority: t.priorityI18n,
    status: normalizeWorkflowStatus(t.status),
    taskId: id || undefined,
    _rowId: id ? `srv_${id}` : nextRowId(),
    _isNew: false,
  }
}

const taskList = ref([])

async function loadTasks() {
  try {
    const list = await getTasks()
    const rows = (Array.isArray(list) ? list : []).map(mapDomainTaskToRow).filter(Boolean)
    taskList.value = rows
  } catch (err) {
    console.error('[TaskCenter] loadTasks failed', err)
    const msg = td(err?.message || t('taskLoadFailed'))
    ElMessage.error(msg)
    taskList.value = []
  }
}

onMounted(() => {
  loadTasks()
})

const aiPrompt = ref('')
const aiGenerating = ref(false)

const detailVisible = ref(false)
const detailTask = ref(null)
const createVisible = ref(false)
const createSubmitting = ref(false)
const createForm = ref({
  title: '',
  description: '',
  task_type: 'planning',
  priority: 'medium',
  deadline: '',
})

const detailMockDescription = computed(() => {
  const row = detailTask.value
  if (!row) return ''
  const ownerLabel = row.owner === 'ownerSelf' ? t('ownerSelf') : td(row.owner)
  return t('taskDetailMockBody')
    .replace('{deadline}', row.deadline)
    .replace('{title}', td(row.title))
    .replace('{source}', t(row.source))
    .replace('{type}', t(row.type))
    .replace('{owner}', ownerLabel)
    .replace('{priority}', t(row.priority))
    .replace('{status}', t(statusDisplayKey(row.status)))
})

function onRowClick(row) {
  if (row.taskId) {
    router.push(`/tasks/${row.taskId}`)
    return
  }
  detailTask.value = row
  detailVisible.value = true
}

function onDetailClosed() {
  detailTask.value = null
}

/** 前端根据输入文案生成本地建议任务（非接口数据），供「AI 生成」演示 */
function generateTasksFromAiPrompt(description) {
  const snippet = description.trim().slice(0, 24) || t('taskDemoSnippetFallback')
  const count = 4
  const templates = [
    {
      key: 'taskAiTemplatePlan',
      source: 'sourcePersonal',
      type: 'taskTypePlanning',
      owner: 'ownerSelf',
      priority: 'priorityHigh',
    },
    {
      key: 'taskAiTemplateResearch',
      source: 'sourcePersonal',
      type: 'taskTypeResearch',
      owner: 'ownerSelf',
      priority: 'priorityMedium',
    },
    {
      key: 'taskAiTemplateExecute',
      source: 'sourcePersonal',
      type: 'taskTypeExecute',
      owner: 'ownerSelf',
      priority: 'priorityHigh',
    },
    {
      key: 'taskAiTemplateReview',
      source: 'sourcePersonal',
      type: 'taskTypeRetrospective',
      owner: 'ownerSelf',
      priority: 'priorityLow',
    },
  ]

  return templates.slice(0, count).map((row, i) => ({
    ...row,
    title: t(row.key).replace('{topic}', snippet),
    deadline: deadlineAfter(2 + i * 2),
    status: 'pending',
  }))
}

async function onAiGenerate() {
  const text = aiPrompt.value.trim()
  if (!text) {
    ElMessage.warning(t('taskAiWarnEmpty'))
    return
  }
  aiGenerating.value = true
  try {
    await new Promise((r) => setTimeout(r, 900 + Math.floor(Math.random() * 700)))
    const generated = generateTasksFromAiPrompt(text)
    const addedIds = []
    const added = generated.map((row) => {
      const _rowId = nextRowId()
      addedIds.push(_rowId)
      return { ...row, _rowId, _isNew: true }
    })
    taskList.value = [...added, ...taskList.value]
    ElMessage.success(t('taskAiGeneratedSuccess').replace('{count}', String(added.length)))
    setTimeout(() => {
      taskList.value = taskList.value.map((row) =>
        addedIds.includes(row._rowId) ? { ...row, _isNew: false } : row,
      )
    }, 4500)
  } finally {
    aiGenerating.value = false
  }
}

function rowClassName({ row }) {
  return row._isNew ? 'task-center__row--new' : ''
}

function sourceTagType(source) {
  const map = { sourceCourse: 'primary', sourceOrganization: 'success', sourcePersonal: 'info' }
  return map[source] ?? 'info'
}

function priorityTagType(priority) {
  const map = { priorityHigh: 'danger', priorityMedium: 'warning', priorityLow: 'info' }
  return map[priority] ?? 'info'
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

function onAddTask() {
  createVisible.value = true
}

function resetCreateForm() {
  createForm.value = {
    title: '',
    description: '',
    task_type: 'planning',
    priority: 'medium',
    deadline: '',
  }
}

async function submitCreateTask() {
  const title = createForm.value.title.trim()
  if (!title) {
    ElMessage.warning(t('scheduleWarnTitle'))
    return
  }
  if (!createForm.value.deadline) {
    ElMessage.warning(t('scheduleWarnDate'))
    return
  }
  createSubmitting.value = true
  try {
    const actorName = roleState.displayName || roleState.username || t('ownerSelf')
    const ret = await createTask({
      title,
      description: createForm.value.description || '',
      task_type: createForm.value.task_type,
      current_org_id: 'personal',
      current_owner_name: actorName,
      deadline: createForm.value.deadline,
      priority: createForm.value.priority,
      status: 'pending',
    })
    const row = mapDomainTaskToRow(ret?.task)
    if (row) taskList.value = [row, ...taskList.value]
    createVisible.value = false
    ElMessage.success(t('scheduleSavedPersonal'))
  } catch (err) {
    ElMessage.error(td(err?.message || t('taskLoadFailed')))
  } finally {
    createSubmitting.value = false
  }
}
</script>

<style scoped>
.task-center {
  max-width: 1200px;
  margin: 0 auto;
}

.task-center__card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.task-center__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.task-center__title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.02em;
}

.task-center__subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.task-center__ai {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px 18px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.task-center__ai-input {
  flex: 1;
  min-width: 220px;
}

.task-center__table {
  width: 100%;
}

.task-center__table :deep(.el-table__body tr) {
  cursor: pointer;
}

.task-center__table :deep(.el-table__header th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

.task-center__table :deep(tr.task-center__row--new > td.el-table__cell) {
  background-color: #ecf5ff !important;
  animation: task-center-row-new 4.2s ease-out forwards;
}

@keyframes task-center-row-new {
  0% {
    background-color: #d9ecff;
  }
  35% {
    background-color: #ecf5ff;
  }
  100% {
    background-color: transparent;
  }
}

.task-center__detail-block {
  margin-top: 16px;
}

.task-center__detail-block-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.task-center__detail-block-text {
  margin: 0;
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.65;
  color: #303133;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}
</style>

<style>
/* Dialog 挂载到 body，与页面风格统一 */
.task-center__detail-dialog .el-dialog__header {
  padding-bottom: 12px;
  margin-right: 0;
  border-bottom: 1px solid #ebeef5;
}

.task-center__detail-dialog .el-dialog__title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}

.task-center__detail-dialog .el-dialog__body {
  padding: 16px 20px 8px;
}

.task-center__detail-dialog .el-dialog__footer {
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.task-center__detail-dialog .task-center__desc-label {
  width: 96px !important;
  font-weight: 600 !important;
  color: #606266 !important;
  background: #fafafa !important;
}
</style>
