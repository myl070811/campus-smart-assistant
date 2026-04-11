<template>
  <div v-loading="loading" class="profile">
    <div class="profile__intro">
      <h1 class="profile__title">{{ t('profileCenterTitle') }}</h1>
      <p class="profile__subtitle">{{ t('profileCenterSubtitle') }}</p>
      <p class="profile__role-tip">
        {{ t('profileRoleTip').replace('{role}', roleLabel) }}
      </p>
    </div>

    <el-alert v-if="error" type="error" :title="error" :closable="false" show-icon class="profile__alert" />

    <el-row :gutter="12" class="profile__stats">
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="profile__stat-card">
          <div class="profile__stat-value">{{ totalVolunteerHours }}</div>
          <div class="profile__stat-label">{{ t('profileStatVolunteerHours') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="profile__stat-card">
          <div class="profile__stat-value">{{ approvedAwardsCount }}</div>
          <div class="profile__stat-label">{{ t('profileStatApprovedAwards') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="profile__stat-card">
          <div class="profile__stat-value">{{ skillTagCount }}</div>
          <div class="profile__stat-label">{{ t('profileStatSkillCoverage') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="profile__stat-card">
          <div class="profile__stat-value">{{ pendingReviewCount }}</div>
          <div class="profile__stat-label">{{ t('profileStatPendingReviews') }}</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="never" class="profile__stat-card">
          <div class="profile__stat-value">{{ completedTasksCount }}</div>
          <div class="profile__stat-label">{{ t('profileStatCompletedTasks') }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <div class="profile__card-head">
          <span class="profile__card-title">{{ t('profileTaskParticipation') }}</span>
          <router-link to="/tasks" class="profile__link">{{ t('menuTasks') }}</router-link>
        </div>
      </template>
      <el-table :data="recentCompletedTasks" stripe border class="profile__table" :empty-text="t('profileNoTaskRecords')">
        <el-table-column prop="title" :label="t('taskTitle')" min-width="220">
          <template #default="{ row }">{{ td(row.title) }}</template>
        </el-table-column>
        <el-table-column prop="typeI18n" :label="t('type')" width="140" align="center">
          <template #default="{ row }">{{ t(row.typeI18n) }}</template>
        </el-table-column>
        <el-table-column prop="sourceI18n" :label="t('source')" width="120" align="center">
          <template #default="{ row }">{{ t(row.sourceI18n) }}</template>
        </el-table-column>
        <el-table-column prop="dueDate" :label="t('deadline')" width="130" align="center" />
        <el-table-column :label="t('status')" width="100" align="center">
          <template #default>
            <el-tag type="success" size="small">{{ t('taskFlowDone') }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <div class="profile__card-head">
          <span class="profile__card-title">{{ t('profileSectionBasicDocs') }}</span>
          <el-button type="primary" size="small" @click="openEditProfile">{{ t('profileEditProfile') }}</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border class="profile__descriptions">
        <el-descriptions-item :label="t('name')">{{ displayValue(td(basicInfo.name)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('studentId')">{{ displayValue(basicInfo.studentId) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileGrade')">{{ displayValue(td(basicInfo.grade)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('className')">{{ displayValue(td(basicInfo.className)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('college')">{{ displayValue(td(basicInfo.college)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('major')">{{ displayValue(td(basicInfo.major)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('phone')">{{ displayValue(basicInfo.phone) }}</el-descriptions-item>
        <el-descriptions-item :label="t('wechat')">{{ displayValue(basicInfo.wechat) }}</el-descriptions-item>
        <el-descriptions-item :label="t('email')">{{ displayValue(basicInfo.email) }}</el-descriptions-item>
        <el-descriptions-item :label="t('volunteerId')">{{ displayValue(basicInfo.volunteerId) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileGithub')">{{ displayValue(basicInfo.github) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileWeibo')">{{ displayValue(basicInfo.weibo) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileEthnicity')">{{ displayValue(td(basicInfo.ethnicity)) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileIdCardNo')">{{ displayValue(maskedIdCard) }}</el-descriptions-item>
        <el-descriptions-item :label="t('profileDevelopmentDirection')" :span="2">
          {{ profileDirection }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('description')" :span="2">
          {{ profileBio }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <span class="profile__card-title">{{ t('profileSectionSkillModules') }}</span>
      </template>
      <el-row :gutter="12">
        <el-col v-for="group in groupedSkillModules" :key="group.key" :xs="24" :md="12">
          <div class="profile__skill-module">
            <div class="profile__skill-title">{{ t(group.labelKey) }}</div>
            <div class="profile__skill-tags">
              <el-tag
                v-for="(tag, idx) in group.tags"
                :key="`${group.key}-${idx}`"
                effect="plain"
                class="profile__tag"
              >
                {{ td(tag) }}
              </el-tag>
              <span v-if="!group.tags.length" class="profile__empty-text">{{ t('profileNoData') }}</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <div class="profile__card-head">
          <span class="profile__card-title">{{ t('profileSectionVolunteerById').replace('{id}', basicInfo.volunteerId || '-') }}</span>
          <span class="profile__card-stat">{{ t('profileTotalHoursFmt').replace('{hours}', totalVolunteerHours) }}</span>
        </div>
      </template>
      <el-table :data="volunteerRecords" stripe border class="profile__table" :empty-text="t('profileVolunteerEmpty')">
        <el-table-column prop="activityTitle" :label="t('profileVolunteerActivity')" min-width="220">
          <template #default="{ row }">{{ td(row.activityTitle) }}</template>
        </el-table-column>
        <el-table-column prop="serviceDate" :label="t('profileVolunteerDate')" width="140" align="center" />
        <el-table-column prop="hours" :label="t('profileVolunteerHours')" width="120" align="center" />
        <el-table-column prop="status" :label="t('profileStatus')" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="submissionTagType(row.status)" size="small">{{ volunteerStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <div class="profile__card-head">
          <span class="profile__card-title">{{ t('profileSectionAwardsApproved') }}</span>
          <div class="profile__header-actions">
            <el-button size="small" @click="loadProfile">{{ t('profileRefresh') }}</el-button>
            <el-button
              v-if="roleState.roleCode === 'student'"
              type="primary"
              size="small"
              @click="awardDialogVisible = true"
            >
              {{ t('profileAddAward') }}
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="honors" stripe border class="profile__table" :empty-text="t('profileAwardsApprovedEmpty')">
        <el-table-column prop="awardName" :label="t('profileAwardTitle')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ td(row.awardName) }}</template>
        </el-table-column>
        <el-table-column prop="awardTime" :label="t('profileAwardTime')" width="120" align="center" />
        <el-table-column prop="status" :label="t('profileStatus')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="submissionTagType(row.status)" size="small">{{ submissionStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewedAt" :label="t('profileReviewedAt')" width="180" align="center" />
        <el-table-column :label="t('profileProof')" width="140" align="center">
          <template #default="{ row }">
            <a v-if="row.proofFileUrl" :href="fileUrl(row.proofFileUrl)" target="_blank" rel="noreferrer">{{ t('profileViewProof') }}</a>
            <span v-else>{{ t('profileNoData') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reviewComment" :label="t('profileReviewComment')" min-width="180">
          <template #default="{ row }">{{ displayValue(td(row.reviewComment)) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="profile__card">
      <template #header>
        <span class="profile__card-title">{{ t('profileMySubmissions') }}</span>
      </template>
      <el-table :data="submissions" stripe border class="profile__table" :empty-text="t('profileSubmissionsEmpty')">
        <el-table-column prop="awardName" :label="t('profileAwardTitle')" min-width="220">
          <template #default="{ row }">{{ td(row.awardName) }}</template>
        </el-table-column>
        <el-table-column prop="awardTime" :label="t('profileSubmissionAwardTime')" width="130" align="center" />
        <el-table-column prop="submittedAt" :label="t('profileSubmittedAt')" width="180" align="center" />
        <el-table-column prop="reviewedAt" :label="t('profileReviewedAt')" width="180" align="center" />
        <el-table-column :label="t('profileProof')" width="140" align="center">
          <template #default="{ row }">
            <a v-if="row.proofFileUrl" :href="fileUrl(row.proofFileUrl)" target="_blank" rel="noreferrer">{{ t('profileViewProof') }}</a>
            <span v-else>{{ t('profileNoData') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('profileStatus')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="submissionTagType(row.status)" size="small">{{ submissionStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewComment" :label="t('profileReviewComment')" min-width="180">
          <template #default="{ row }">{{ displayValue(td(row.reviewComment)) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editDialogVisible" :title="t('profileEditDialogTitle')" width="620px">
      <el-form label-position="top">
        <el-row :gutter="10">
          <el-col :span="12"><el-form-item :label="t('name')"><el-input v-model="editForm.display_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="t('phone')"><el-input v-model="editForm.phone" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12"><el-form-item :label="t('wechat')"><el-input v-model="editForm.wechat" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="t('email')"><el-input v-model="editForm.email" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12"><el-form-item :label="t('profileGithub')"><el-input v-model="editForm.github" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item :label="t('profileWeibo')"><el-input v-model="editForm.weibo" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="profileSaving" @click="submitProfileEdit">{{ t('scheduleSave') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="awardDialogVisible" :title="t('profileUploadDialogTitle')" width="620px">
      <el-form label-position="top">
        <el-form-item :label="t('profileAwardTitle')"><el-input v-model="awardForm.award_name" /></el-form-item>
        <el-form-item :label="t('profileAwardTime')"><el-input v-model="awardForm.award_time" :placeholder="t('profileAwardTimePlaceholder')" /></el-form-item>
        <el-form-item :label="t('profileProofFile')">
          <input type="file" @change="onProofFileChange" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="awardDialogVisible = false">{{ t('reviewCancel') }}</el-button>
        <el-button type="primary" :loading="awardSubmitting" @click="submitAwardRecord">{{ t('profileSubmitReview') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getProfile, submitAward, updateProfile } from '../api/profile'
import { getTasks } from '../api/task'
import { API_BASE } from '../api/baseUrl'
import { roleState } from '../stores/role'
import { t, td } from '../i18n'

const loading = ref(true)
const error = ref('')
const basicInfo = ref({
  name: '',
  studentId: '',
  phone: '',
  wechat: '',
  email: '',
  github: '',
  weibo: '',
  ethnicity: '',
  idCardNo: '',
  volunteerId: '',
  grade: '',
  college: '',
  major: '',
  className: '',
})
const skillModules = ref([])
const volunteerRecords = ref([])
const honors = ref([])
const submissions = ref([])
const tasks = ref([])
const roleLabel = computed(() => {
  if (roleState.roleCode === 'tw_admin') return t('roleTwAdmin')
  if (roleState.roleCode === 'org_admin') return t('roleOrgAdmin')
  return t('roleStudent')
})

const editDialogVisible = ref(false)
const profileSaving = ref(false)
const editForm = ref({
  display_name: '',
  phone: '',
  wechat: '',
  email: '',
  github: '',
  weibo: '',
})

const awardDialogVisible = ref(false)
const awardSubmitting = ref(false)
const awardForm = ref({
  award_name: '',
  award_time: '',
  proof_file: null,
})

const totalVolunteerHours = computed(() =>
  volunteerRecords.value.reduce((sum, r) => sum + Number(r.hours || 0), 0).toFixed(1),
)

const approvedAwardsCount = computed(() =>
  submissions.value.filter((x) => x.status === 'approved').length,
)
const pendingReviewCount = computed(() =>
  submissions.value.filter((x) => x.status === 'pending' || x.status === 'reviewing').length,
)
const completedTasksCount = computed(() =>
  tasks.value.filter((x) => x.status === 'done').length,
)
const skillTagCount = computed(() =>
  skillModules.value.reduce((sum, m) => sum + (Array.isArray(m.tags) ? m.tags.length : 0), 0),
)
const recentCompletedTasks = computed(() =>
  tasks.value
    .filter((x) => x.status === 'done')
    .sort((a, b) => String(b.dueDate || '').localeCompare(String(a.dueDate || '')))
    .slice(0, 5),
)

const profileDirection = computed(() => {
  const major = td(basicInfo.value.major || '')
  const grade = td(basicInfo.value.grade || '')
  if (!major && !grade) return t('profileNoData')
  return t('profileDirectionTemplate').replace('{major}', major || t('profileNoData')).replace('{grade}', grade || t('profileNoData'))
})

const profileBio = computed(() => {
  const topSkills = (skillModules.value || [])
    .flatMap((m) => (Array.isArray(m.tags) ? m.tags : []))
    .slice(0, 3)
    .map((x) => td(x))
    .join(' / ')
  if (!topSkills) return t('profileBioFallback')
  return t('profileBioTemplate').replace('{skills}', topSkills)
})

const groupedSkillModules = computed(() => {
  const groups = {
    academic: { key: 'academic', labelKey: 'profileSkillAcademic', tags: [] },
    management: { key: 'management', labelKey: 'profileSkillManagement', tags: [] },
    volunteer: { key: 'volunteer', labelKey: 'profileSkillVolunteer', tags: [] },
    practice: { key: 'practice', labelKey: 'profileSkillPractice', tags: [] },
    quality: { key: 'quality', labelKey: 'profileSkillQuality', tags: [] },
  }
  const moduleToGroup = {
    编程: 'academic',
    策划: 'management',
    文案: 'practice',
    管理: 'management',
    运动: 'quality',
    语言: 'academic',
  }
  for (const m of skillModules.value) {
    const g = moduleToGroup[m.module] || 'quality'
    groups[g].tags.push(...(Array.isArray(m.tags) ? m.tags : []))
  }
  return Object.values(groups)
})

const maskedIdCard = computed(() => {
  const s = String(basicInfo.value.idCardNo || '')
  if (s.length < 8) return s || '—'
  return `${s.slice(0, 4)}********${s.slice(-4)}`
})

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const [mapped, taskRows] = await Promise.all([getProfile(), getTasks()])
    basicInfo.value = mapped.basicInfo
    skillModules.value = mapped.skillModules || []
    volunteerRecords.value = mapped.volunteerRecords || []
    honors.value = mapped.honors || []
    submissions.value = mapped.submissions || []
    tasks.value = Array.isArray(taskRows) ? taskRows : []
  } catch (e) {
    error.value = td(e?.message || t('profileLoadError'))
  } finally {
    loading.value = false
  }
}

function openEditProfile() {
  editForm.value = {
    display_name: basicInfo.value.name,
    phone: basicInfo.value.phone,
    wechat: basicInfo.value.wechat,
    email: basicInfo.value.email,
    github: basicInfo.value.github,
    weibo: basicInfo.value.weibo,
  }
  editDialogVisible.value = true
}

async function submitProfileEdit() {
  profileSaving.value = true
  try {
    await updateProfile(editForm.value)
    editDialogVisible.value = false
    ElMessage.success(t('profileUpdateSuccess'))
    await loadProfile()
  } catch (e) {
    ElMessage.error(td(e?.message || t('profileUpdateError')))
  } finally {
    profileSaving.value = false
  }
}

function onProofFileChange(event) {
  const f = event?.target?.files?.[0]
  awardForm.value.proof_file = f || null
}

async function submitAwardRecord() {
  awardSubmitting.value = true
  try {
    await submitAward({
      student_id: basicInfo.value.studentId,
      award_name: awardForm.value.award_name,
      award_time: awardForm.value.award_time,
      proof_file: awardForm.value.proof_file,
    })
    awardDialogVisible.value = false
    awardForm.value = { award_name: '', award_time: '', proof_file: null }
    ElMessage.success(t('profileAwardSubmitSuccess'))
    await loadProfile()
  } catch (e) {
    ElMessage.error(td(e?.message || t('profileAwardSubmitError')))
  } finally {
    awardSubmitting.value = false
  }
}

function fileUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

function submissionTagType(status) {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

function submissionStatusText(status) {
  if (status === 'approved') return t('reviewApproved')
  if (status === 'rejected') return t('reviewRejected')
  return t('reviewPending')
}

function volunteerStatusText(status) {
  if (status === 'recognized') return t('volunteerRecognized')
  if (status === 'reviewing') return t('reviewing')
  if (status === 'rejected') return t('reviewRejected')
  return t('pendingReview')
}

function displayValue(v) {
  const s = String(v ?? '').trim()
  return s ? s : t('profileNoData')
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile {
  max-width: 1200px;
  margin: 0 auto;
}

.profile__intro {
  margin-bottom: 20px;
}

.profile__title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.02em;
}

.profile__subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.profile__role-tip {
  margin: 8px 0 0;
  font-size: 12px;
  color: #606266;
}

.profile__alert {
  margin-bottom: 16px;
}

.profile__stats {
  margin-bottom: 12px;
}

.profile__stat-card {
  border: 1px solid #ebeef5;
}

.profile__stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.profile__stat-label {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.profile__card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.profile__card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.profile__card :deep(.el-card__body) {
  padding: 20px;
}

.profile__card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.profile__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.profile__link {
  font-size: 13px;
  color: #409eff;
  text-decoration: none;
}

.profile__header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.profile__card-stat {
  font-size: 13px;
  color: #909399;
}

.profile__hours {
  margin: 0 4px;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.profile__descriptions :deep(.el-descriptions__label) {
  width: 100px;
  font-weight: 600;
  color: #606266;
  background: #fafafa !important;
}

.profile__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.profile__skill-module {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.profile__skill-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.profile__skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile__empty-text {
  font-size: 12px;
  color: #909399;
}

.profile__tag {
  border-radius: 4px;
}

.profile__volunteer-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.profile__volunteer-row {
  padding: 14px 0;
  border-bottom: 1px solid #ebeef5;
}

.profile__volunteer-row:first-child {
  padding-top: 0;
}

.profile__volunteer-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.profile__volunteer-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.profile__volunteer-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  line-height: 1.45;
}

.profile__volunteer-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.profile__volunteer-duration {
  font-variant-numeric: tabular-nums;
  color: #606266;
}

.profile__table {
  width: 100%;
}

.profile__table :deep(.el-table__header th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}
</style>
