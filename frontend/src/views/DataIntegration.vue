<template>
  <div class="integration">
    <el-card shadow="never" class="integration__hero">
      <h1 class="integration__title">{{ t('integrationTitle') }}</h1>
      <p class="integration__subtitle">{{ t('integrationSubtitle') }}</p>
    </el-card>

    <el-row :gutter="12">
      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>{{ t('integrationUploadEntry') }}</template>
          <el-form v-if="canImportData" label-position="top">
            <el-form-item :label="t('integrationImportType')">
              <el-select v-model="importType" style="width: 100%">
                <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('integrationFileField')">
              <input type="file" accept=".json,.csv,application/json,text/csv" @change="onFileChange" />
              <div class="integration__hint">{{ t('integrationUploadHint') }}</div>
            </el-form-item>
            <el-button type="primary" :disabled="!selectedFile" :loading="submitting" @click="submitImport">
              {{ t('integrationStartImport') }}
            </el-button>
          </el-form>
          <el-alert
            v-else
            type="info"
            :title="t('commonNoPermission')"
            :description="t('reviewTipAdminOnly')"
            :closable="false"
            show-icon
          />

          <el-alert
            v-if="resultText"
            class="integration__result"
            type="success"
            :closable="false"
            show-icon
            :title="resultText"
          />
          <el-alert
            v-if="errorText"
            class="integration__result"
            type="error"
            :closable="false"
            show-icon
            :title="errorText"
          />
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="never">
          <template #header>{{ t('integrationTemplateTitle') }}</template>
          <div class="integration__template">
            <el-alert
              type="warning"
              :closable="false"
              show-icon
              :title="t('integrationNoWordExcel')"
              class="integration__warning"
            />
            <h4>{{ t('integrationTypeCourse') }} (course)</h4>
            <p>{{ t('integrationTemplateCourse') }}</p>

            <h4>{{ t('integrationTypeVolunteer') }} (volunteer)</h4>
            <p>{{ t('integrationTemplateVolunteer') }}</p>

            <h4>{{ t('integrationTypeWorkstudy') }} (workstudy)</h4>
            <p>{{ t('integrationTemplateWorkstudy') }}</p>

            <h4>{{ t('integrationTypeProjectNode') }} (project_node)</h4>
            <p>{{ t('integrationTemplateProjectNode') }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="integration__logs">
      <template #header>
        <div class="integration__logs-head">
          <span>{{ t('integrationLogs') }}</span>
          <el-button link type="primary" @click="loadLogs">{{ t('integrationRefresh') }}</el-button>
        </div>
      </template>
      <el-table :data="logs" size="small">
        <el-table-column prop="import_type" :label="t('integrationImportType')" width="130">
          <template #default="{ row }">{{ logTypeLabel(row.import_type) }}</template>
        </el-table-column>
        <el-table-column prop="file_name" :label="t('integrationFileName')" min-width="160" />
        <el-table-column prop="success_count" :label="t('integrationSuccessCount')" width="80" />
        <el-table-column prop="failed_count" :label="t('integrationFailedCount')" width="80" />
        <el-table-column prop="created_at" :label="t('integrationTime')" min-width="180" />
        <el-table-column prop="error_summary" :label="t('integrationErrorSummary')" min-width="220">
          <template #default="{ row }">{{ td(row.error_summary || '—') }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getIntegrationLogs, importIntegrationData } from '../api/integrations'
import { t, td } from '../i18n'
import { roleState } from '../stores/role'

const typeOptions = computed(() => [
  { value: 'course', label: t('integrationTypeCourse') },
  { value: 'volunteer', label: t('integrationTypeVolunteer') },
  { value: 'workstudy', label: t('integrationTypeWorkstudy') },
  { value: 'project_node', label: t('integrationTypeProjectNode') },
])

const importType = ref('course')
const selectedFile = ref(null)
const submitting = ref(false)
const resultText = ref('')
const errorText = ref('')
const logs = ref([])
const canImportData = computed(() => roleState.roleCode === 'org_admin' || roleState.roleCode === 'tw_admin')

function logTypeLabel(v) {
  const map = {
    course: t('integrationTypeCourse'),
    volunteer: t('integrationTypeVolunteer'),
    workstudy: t('integrationTypeWorkstudy'),
    project_node: t('integrationTypeProjectNode'),
  }
  return map[v] || td(v)
}

function onFileChange(e) {
  const files = e.target?.files
  const file = files && files.length ? files[0] : null
  if (!file) {
    selectedFile.value = null
    return
  }
  const lower = (file.name || '').toLowerCase()
  if (!lower.endsWith('.json') && !lower.endsWith('.csv')) {
    selectedFile.value = null
    errorText.value = t('integrationInvalidFileType')
    ElMessage.error(td(errorText.value))
    return
  }
  selectedFile.value = file
  errorText.value = ''
}

async function submitImport() {
  if (!canImportData.value) {
    ElMessage.warning(t('commonNoPermission'))
    return
  }
  if (!selectedFile.value) return
  submitting.value = true
  resultText.value = ''
  errorText.value = ''
  try {
    const ret = await importIntegrationData(importType.value, selectedFile.value)
    const success = ret?.success_count ?? 0
    const failed = ret?.failed_count ?? 0
    resultText.value = t('integrationImportResult').replace('{success}', success).replace('{failed}', failed)
    ElMessage.success(t('integrationImportSuccess'))
    await loadLogs()
  } catch (err) {
    errorText.value = td(err?.message || t('integrationImportFailed'))
    ElMessage.error(td(errorText.value))
  } finally {
    submitting.value = false
  }
}

async function loadLogs() {
  try {
    logs.value = await getIntegrationLogs(50)
  } catch (err) {
    ElMessage.error(td(err?.message || t('integrationLogLoadFailed')))
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.integration { max-width: 1100px; margin: 0 auto; }
.integration__hero { margin-bottom: 12px; border: 1px solid #ebeef5; }
.integration__title { margin: 0 0 8px; font-size: 24px; color: #303133; }
.integration__subtitle { margin: 0; color: #606266; }
.integration__result { margin-top: 12px; }
.integration__template h4 { margin: 8px 0 4px; color: #303133; }
.integration__template p { margin: 0 0 8px; color: #606266; line-height: 1.6; }
.integration__hint { margin-top: 6px; color: #909399; font-size: 12px; }
.integration__warning { margin-bottom: 10px; }
.integration__logs { margin-top: 12px; border: 1px solid #ebeef5; }
.integration__logs-head { display: flex; justify-content: space-between; align-items: center; }
</style>

