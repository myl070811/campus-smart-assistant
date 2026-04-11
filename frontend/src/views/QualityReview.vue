<template>
  <div v-loading="loading" class="review">
    <div class="review__intro">
      <h1 class="review__title">{{ t('reviewCenterTitle') }}</h1>
      <p class="review__subtitle">{{ t('reviewCenterSubtitle') }}</p>
      <p class="review__tip">{{ t('reviewTipAdminOnly') }}</p>
    </div>

    <el-card shadow="never" class="review__card">
      <div class="review__toolbar">
        <el-radio-group v-model="statusFilter" @change="loadRows">
          <el-radio-button label="">{{ t('reviewAll') }}</el-radio-button>
          <el-radio-button label="pending">{{ t('reviewPending') }}</el-radio-button>
          <el-radio-button label="approved">{{ t('reviewApproved') }}</el-radio-button>
          <el-radio-button label="rejected">{{ t('reviewRejected') }}</el-radio-button>
        </el-radio-group>
      </div>
      <el-table :data="rows" stripe border :empty-text="t('reviewEmpty')" class="review__table">
        <el-table-column prop="student_name" :label="t('reviewStudent')" width="120" align="center">
          <template #default="{ row }">{{ td(row.student_name) }}</template>
        </el-table-column>
        <el-table-column prop="award_name" :label="t('reviewAwardName')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ td(row.award_name) }}</template>
        </el-table-column>
        <el-table-column prop="submitted_at" :label="t('reviewSubmittedAt')" width="180" align="center" />
        <el-table-column :label="t('reviewProof')" width="120" align="center">
          <template #default="{ row }">
            <a v-if="row.proof_file_url" :href="fileUrl(row.proof_file_url)" target="_blank" rel="noreferrer">{{ t('profileViewProof') }}</a>
            <span v-else>{{ t('reviewNone') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('reviewStatus')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="review_comment" :label="t('reviewOpinion')" min-width="180">
          <template #default="{ row }">{{ td(row.review_comment || '—') }}</template>
        </el-table-column>
        <el-table-column :label="t('reviewAction')" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="success" link @click="openReview(row, 'approved')">
              {{ t('reviewPass') }}
            </el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="openReview(row, 'rejected')">
              {{ t('reviewReject') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="reviewVisible" :title="t('reviewDialogTitle')" width="520px">
      <el-form label-position="top">
        <el-form-item :label="t('reviewResult')">
          <el-tag :type="reviewAction === 'approved' ? 'success' : 'danger'">
            {{ statusText(reviewAction) }}
          </el-tag>
        </el-form-item>
        <el-form-item :label="t('reviewOpinion')">
          <el-input v-model="reviewComment" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">{{ t('reviewCancel') }}</el-button>
        <el-button type="primary" :loading="reviewSubmitting" @click="submitReview">{{ t('reviewSubmit') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminAwards, reviewAward } from '../api/adminAwards'
import { API_BASE } from '../api/baseUrl'
import { t, td } from '../i18n'

const loading = ref(true)
const rows = ref([])
const statusFilter = ref('')

const reviewVisible = ref(false)
const reviewSubmitting = ref(false)
const reviewTarget = ref(null)
const reviewAction = ref('approved')
const reviewComment = ref('')

async function loadRows() {
  loading.value = true
  try {
    rows.value = await getAdminAwards(statusFilter.value)
  } catch (e) {
    ElMessage.error(td(e?.message || t('reviewLoadError')))
  } finally {
    loading.value = false
  }
}

function openReview(row, action) {
  reviewTarget.value = row
  reviewAction.value = action
  reviewComment.value = ''
  reviewVisible.value = true
}

async function submitReview() {
  if (!reviewTarget.value?.id) return
  reviewSubmitting.value = true
  try {
    await reviewAward(reviewTarget.value.id, {
      status: reviewAction.value,
      review_comment: reviewComment.value,
      reviewed_by: 'admin',
    })
    reviewVisible.value = false
    ElMessage.success(t('reviewSuccess'))
    await loadRows()
  } catch (e) {
    ElMessage.error(td(e?.message || t('reviewError')))
  } finally {
    reviewSubmitting.value = false
  }
}

function statusTag(status) {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function statusText(status) {
  if (status === 'approved') return t('reviewApproved')
  if (status === 'rejected') return t('reviewRejected')
  return t('reviewPending')
}

function fileUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

onMounted(() => {
  loadRows()
})
</script>

<style scoped>
.review { max-width: 1200px; margin: 0 auto; }
.review__intro { margin-bottom: 20px; }
.review__title { margin: 0 0 6px; font-size: 20px; font-weight: 600; color: #303133; }
.review__subtitle { margin: 0; font-size: 13px; color: #909399; }
.review__tip { margin: 8px 0 0; font-size: 12px; color: #606266; }
.review__card { border-radius: 8px; border: 1px solid #ebeef5; }
.review__toolbar { margin-bottom: 12px; }
</style>
