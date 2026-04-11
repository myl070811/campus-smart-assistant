<template>
  <div v-loading="loading" class="organization">
    <div class="organization__intro">
      <h1 class="organization__title">{{ t('organizationTitle') }}</h1>
      <p class="organization__subtitle">{{ t('organizationSubtitle') }}</p>
      <div class="organization__role-switch">
        <span class="organization__role-label">{{ t('orgCurrentView') }}</span>
        <el-radio-group v-model="currentRole" size="small">
          <el-radio-button v-if="canUseAdminView" label="admin">{{ t('orgViewAdmin') }}</el-radio-button>
          <el-radio-button label="owner">{{ t('orgViewOwner') }}</el-radio-button>
        </el-radio-group>
        <el-button v-if="canManageOrganizations" type="primary" size="small" @click="openCreateOrganization">
          {{ t('orgCreateOrg') }}
        </el-button>
      </div>
      <p class="organization__role-hint">{{ currentRoleHint }}</p>
    </div>

    <el-alert
      v-if="error"
      type="error"
      :title="error"
      :closable="false"
      show-icon
      class="organization__alert"
    />

    <el-card shadow="never" class="organization__card organization__board-card">
      <template #header>
        <div class="organization__task-head">
          <span class="organization__card-title">{{ t('orgBoardTitle') }}</span>
          <span class="organization__board-hint">{{ t('orgBoardSubtitle') }}</span>
        </div>
      </template>

      <el-row :gutter="12" class="organization__stats">
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.pendingHandlingCount }}</div>
            <div class="organization__stat-label">{{ t('orgStatPendingHandling') }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.inProgressCount }}</div>
            <div class="organization__stat-label">{{ t('orgStatInProgress') }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.doneCount }}</div>
            <div class="organization__stat-label">{{ t('orgStatDone') }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.totalOrganizations }}</div>
            <div class="organization__stat-label">{{ t('orgStatOrganizations') }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.activeTasks }}</div>
            <div class="organization__stat-label">{{ t('orgStatActiveTasks') }}</div>
          </div>
        </el-col>
        <el-col :xs="12" :md="8" :lg="4">
          <div class="organization__stat">
            <div class="organization__stat-num">{{ boardStats.crossOrgTasks }}</div>
            <div class="organization__stat-label">{{ t('orgStatCrossOrgTasks') }}</div>
          </div>
        </el-col>
      </el-row>

      <el-card shadow="never" class="organization__todo-card">
        <template #header>
          <div class="organization__task-head">
            <span class="organization__card-title">{{ t('orgTodoTitle') }}</span>
            <span class="organization__board-hint">{{ t('orgTodoSubtitle') }}</span>
          </div>
        </template>
        <el-table :data="todoTasks" size="small" border :empty-text="t('orgTodoEmpty')">
          <el-table-column prop="title" :label="t('orgColTaskTitle')" min-width="200" show-overflow-tooltip>
            <template #default="{ row }">{{ td(row.title) }}</template>
          </el-table-column>
          <el-table-column prop="orgName" :label="t('orgColOrganization')" width="120" align="center">
            <template #default="{ row }">{{ td(row.orgName) }}</template>
          </el-table-column>
          <el-table-column prop="priorityI18n" :label="t('priority')" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="priorityTagType(row.priorityI18n)" size="small">{{ t(row.priorityI18n) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="dueDate" :label="t('deadline')" width="120" align="center" />
          <el-table-column prop="status" :label="t('status')" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="taskStatusTagType(row.status)" size="small">{{ t(orgTaskStatusLabelKey(row.status)) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <div class="organization__filters">
        <el-select v-model="boardFilters.orgId" clearable :placeholder="t('orgFilterByOrg')" class="organization__filter-item">
          <el-option :label="t('orgAllOrganizations')" value="" />
          <el-option v-for="org in organizations" :key="`org-filter-${org.id}`" :label="td(org.name)" :value="org.id" />
        </el-select>
        <el-select v-model="boardFilters.status" clearable :placeholder="t('orgFilterByStatus')" class="organization__filter-item">
          <el-option :label="t('orgAllStatuses')" value="" />
          <el-option :label="t('orgStatusPending')" value="pending" />
          <el-option :label="t('orgStatusInProgress')" value="in_progress" />
          <el-option :label="t('orgStatusDone')" value="done" />
          <el-option :label="t('orgStatusViewed')" value="viewed" />
        </el-select>
        <el-select v-model="boardFilters.typeKey" clearable :placeholder="t('orgFilterByType')" class="organization__filter-item">
          <el-option :label="t('orgAllTypes')" value="" />
          <el-option v-for="type in boardTypeOptions" :key="type.value" :label="type.label" :value="type.value" />
        </el-select>
      </div>

      <el-table
        :data="filteredBoardTasks"
        stripe
        border
        class="organization__table"
        :empty-text="boardEmptyText"
        :row-key="(row) => `${row.orgId}-${row.id}`"
      >
        <el-table-column prop="title" :label="t('orgColTaskTitle')" min-width="210" show-overflow-tooltip>
          <template #default="{ row }">{{ td(row.title) }}</template>
        </el-table-column>
        <el-table-column prop="orgName" :label="t('orgColOrganization')" width="120" align="center">
          <template #default="{ row }">{{ td(row.orgName) }}</template>
        </el-table-column>
        <el-table-column prop="typeKey" :label="t('orgColTaskType')" width="120" align="center">
          <template #default="{ row }">{{ t(row.typeKey) }}</template>
        </el-table-column>
        <el-table-column prop="ownerName" :label="t('currentTaskOwner')" width="130" align="center">
          <template #default="{ row }">{{ td(row.ownerName || '—') }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="taskStatusTagType(row.status)" size="small">
              {{ t(orgTaskStatusLabelKey(row.status)) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('orgColProgress')" width="140" align="center">
          <template #default="{ row }">
            <el-progress :percentage="progressPercent(row.status)" :stroke-width="10" :show-text="false" />
          </template>
        </el-table-column>
        <el-table-column :label="t('orgColFlow')" min-width="220">
          <template #default="{ row }">
            <div class="organization__flow-line">{{ taskFlowSummary(row) }}</div>
          </template>
        </el-table-column>
        <el-table-column :label="t('orgColOperation')" width="130" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openBoardTaskDetail(row)">
              {{ t('orgViewDetail') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16" class="organization__layout">
      <el-col :xs="24" :md="7" :lg="6">
        <el-card shadow="never" class="organization__card organization__list-card">
          <template #header>
            <span class="organization__card-title">{{ t('organizationList') }}</span>
          </template>
          <div class="organization__list">
            <button
              v-for="org in organizations"
              :key="org.id"
              type="button"
              class="organization__list-item"
              :class="{ 'is-active': activeOrgId === org.id }"
              @click="activeOrgId = org.id"
            >
              <span class="organization__list-name">{{ td(org.name) }}</span>
              <el-tag :type="orgTypeTag(org.orgType)" effect="plain" size="small" class="organization__list-tag">
                {{ t(org.orgType) }}
              </el-tag>
            </button>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="17" :lg="18">
        <template v-if="activeOrg">
          <el-card shadow="never" class="organization__card organization__detail-card">
            <template #header>
              <span class="organization__card-title">{{ t('organizationInfo') }}</span>
            </template>
            <el-descriptions :column="2" border class="organization__descriptions">
              <el-descriptions-item :label="t('organizationName')">{{ td(activeOrg.name) }}</el-descriptions-item>
              <el-descriptions-item :label="t('orgShortName')">{{ td(activeOrg.shortName || '—') }}</el-descriptions-item>
              <el-descriptions-item :label="t('organizationType')">
                <el-tag :type="orgTypeTag(activeOrg.orgType)" effect="plain" size="small">
                  {{ t(activeOrg.orgType) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('orgStatus')">
                <el-tag :type="orgStatusTagType(activeOrgStatus)" size="small">{{ t(activeOrgStatus) }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('orgLogo')">
                <img v-if="activeOrg.logoUrl" :src="fileUrl(activeOrg.logoUrl)" class="organization__logo-preview" alt="logo" />
                <span v-else>—</span>
              </el-descriptions-item>
              <el-descriptions-item :label="t('organizationLeader')">
                {{ td(activeOrg.leaderName) }}
                <el-tag size="small" class="organization__leader-role" effect="light">
                  {{ t(activeOrg.leaderRole) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('orgParentOrg')">{{ td(parentOrgName(activeOrg.parentId)) }}</el-descriptions-item>
              <el-descriptions-item :label="t('memberCount')">
                <span class="organization__member-count">{{ activeOrg.memberCount }}</span>
                {{ t('personsUnit') }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('orgTeacherLeader')">{{ td(activeOrg.leaderTeacherName || '—') }}</el-descriptions-item>
              <el-descriptions-item :label="t('orgStudentLeaderId')">{{ activeOrg.leaderStudentId || '—' }}</el-descriptions-item>
              <el-descriptions-item :label="t('description')">{{ td(activeOrg.description || t('orgDescriptionEmpty')) }}</el-descriptions-item>
            </el-descriptions>
            <div class="organization__meta-tags">
              <el-tag size="small" effect="light">{{ t(activeOrg.orgType) }}</el-tag>
              <el-tag size="small" effect="light">{{ t(activeOrgStatus) }}</el-tag>
            </div>
            <div v-if="canManageOrganizations" class="organization__org-actions">
              <el-button size="small" @click="openEditOrganization(activeOrg)">{{ t('orgEditOrg') }}</el-button>
              <el-popconfirm :title="t('orgDeleteConfirm')" @confirm="onDeleteOrganization(activeOrg)">
                <template #reference>
                  <el-button type="danger" size="small">{{ t('orgDeleteOrg') }}</el-button>
                </template>
              </el-popconfirm>
            </div>
          </el-card>

          <el-card shadow="never" class="organization__card organization__task-card">
            <template #header>
              <div class="organization__task-head">
                <span class="organization__card-title">{{ t('taskFlow') }}</span>
                <el-button
                  v-if="currentRole === 'admin'"
                  type="primary"
                  size="small"
                  :icon="UserFilled"
                  @click="onAssignTask"
                >
                  {{ t('assignTask') }}
                </el-button>
              </div>
            </template>
            <el-table
              :data="activeOrgTasks"
              stripe
              border
              class="organization__table"
              :empty-text="activeOrgTaskEmptyText"
              :row-key="(row) => row.id"
            >
              <el-table-column prop="title" :label="t('taskTitle')" min-width="168" show-overflow-tooltip>
                <template #default="{ row }">{{ td(row.title) }}</template>
              </el-table-column>
              <el-table-column prop="sourceKey" :label="t('source')" width="110" align="center">
                <template #default="{ row }">
                  <el-tag :type="taskSourceTagType(row.sourceKey)" effect="plain" size="small">
                    {{ t(row.sourceKey) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="typeKey" :label="t('type')" width="100" align="center">
                <template #default="{ row }">
                  {{ t(row.typeKey) }}
                </template>
              </el-table-column>
              <el-table-column prop="ownerName" :label="t('currentTaskOwner')" width="100" align="center">
                <template #default="{ row }">{{ td(row.ownerName) }}</template>
              </el-table-column>
              <el-table-column prop="status" :label="t('status')" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="taskStatusTagType(row.status)" size="small">{{
                  t(orgTaskStatusLabelKey(row.status))
                }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('action')" width="168" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="openTaskDetail(row)">{{ t('orgViewDetail') }}</el-button>
                  <el-button type="primary" link size="small" @click="onHandover(row)">
                    {{ t('transferTask') }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </template>
      </el-col>
    </el-row>

    <el-dialog v-model="boardTaskDetailVisible" :title="t('orgTaskDetailTitle')" width="520px" destroy-on-close>
      <template v-if="selectedBoardTask">
        <el-descriptions border :column="1">
          <el-descriptions-item :label="t('orgFieldTaskTitle')">{{ td(selectedBoardTask.title) }}</el-descriptions-item>
          <el-descriptions-item :label="t('orgFieldOrganization')">{{ td(selectedBoardTask.orgName) }}</el-descriptions-item>
          <el-descriptions-item :label="t('orgFieldTaskType')">{{ t(selectedBoardTask.typeKey) }}</el-descriptions-item>
          <el-descriptions-item :label="t('taskFlowCategory')">{{ t(selectedBoardTask.taskFlowI18n || 'taskFlowSingleDepartment') }}</el-descriptions-item>
          <el-descriptions-item :label="t('taskCollaboratingOrgs')">{{ collabOrgDisplay(selectedBoardTask) }}</el-descriptions-item>
          <el-descriptions-item :label="t('orgFieldAssignee')">{{ td(selectedBoardTask.ownerName || '—') }}</el-descriptions-item>
          <el-descriptions-item :label="t('orgFieldTaskSource')">{{ t(selectedBoardTask.sourceKey) }}</el-descriptions-item>
          <el-descriptions-item :label="t('orgFieldTaskStatus')">
            <el-tag :type="taskStatusTagType(selectedBoardTask.status)" size="small">
              {{ t(orgTaskStatusLabelKey(selectedBoardTask.status)) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('orgColFlow')">
            {{ taskFlowSummary(selectedBoardTask) }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="organization__log-block">
          <div class="organization__log-title">{{ t('orgRecentUpdates') }}</div>
          <el-timeline v-if="selectedBoardTaskLogs.length" class="organization__timeline">
            <el-timeline-item
              v-for="log in selectedBoardTaskLogs"
              :key="`board-log-${log.id}`"
              :timestamp="log.createdAt"
            >
              {{ formatBoardLog(log) }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else :description="t('taskHistoryEmpty')" :image-size="56" />
        </div>
      </template>
      <template #footer>
        <el-button @click="boardTaskDetailVisible = false">{{ t('btnClose') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignVisible" :title="t('orgAssignDialogTitle')" width="560px">
      <el-form label-position="top">
        <el-form-item :label="t('orgFieldTaskTitle')">
          <el-input v-model="assignForm.title" />
        </el-form-item>
        <el-form-item :label="t('orgFieldTaskDesc')">
          <el-input v-model="assignForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgFieldTaskType')">
              <el-select v-model="assignForm.task_type">
                <el-option :label="t('orgTaskTypeAffairs')" value="affairs" />
                <el-option :label="t('orgTaskTypeApproval')" value="approval" />
                <el-option :label="t('orgTaskTypeMaterial')" value="material" />
                <el-option :label="t('orgTaskTypeCoordinate')" value="coordinate" />
                <el-option :label="t('orgTaskTypePlanning')" value="planning" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('deadline')">
              <el-date-picker v-model="assignForm.deadline" value-format="YYYY-MM-DD" type="date" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('taskFlowCategory')">
          <el-select v-model="assignForm.assignment_type" style="width: 100%" @change="onAssignFlowChange">
            <el-option :label="t('taskFlowSingleDepartment')" value="single_department" />
            <el-option :label="t('taskFlowCrossDepartment')" value="cross_department" />
            <el-option :label="t('taskFlowTopDown')" value="top_down" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="assignForm.assignment_type === 'cross_department'" :label="t('taskCollaboratingOrgs')">
          <el-select
            v-model="assignForm.collaborating_org_ids"
            multiple
            filterable
            style="width: 100%"
            :placeholder="t('taskCollaboratingOrgsPlaceholder')"
          >
            <el-option
              v-for="org in organizations"
              :key="`collab-${org.id}`"
              :label="td(org.name)"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgFieldAssignOrg')">
              <el-select v-model="assignForm.current_org_id">
                <el-option
                  v-for="org in organizations"
                  :key="`assign-org-${org.id}`"
                  :label="td(org.name)"
                  :value="org.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('orgFieldAssignee')">
              <el-input v-model="assignForm.current_owner_name" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="assignSubmitting" @click="submitAssignTask">{{ t('orgSubmitAssign') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="transferVisible" :title="t('orgTransferDialogTitle')" width="520px">
      <el-form label-position="top">
        <el-form-item :label="t('orgFieldAssignOrg')">
          <el-select v-model="transferForm.to_org_id">
            <el-option
              v-for="org in organizations"
              :key="`transfer-org-${org.id}`"
              :label="td(org.name)"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('orgFieldAssigneeNew')">
          <el-input v-model="transferForm.to_owner" />
        </el-form-item>
        <el-form-item :label="t('orgFieldComment')">
          <el-input v-model="transferForm.note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="transferSubmitting" @click="submitTransferTask">{{ t('orgSubmitTransfer') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="orgDialogVisible" :title="orgEditingId ? t('orgEditOrg') : t('orgCreateOrg')" width="640px">
      <el-form label-position="top">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgFullName')">
              <el-input v-model="orgForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('orgShortName')">
              <el-input v-model="orgForm.short_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgNature')">
              <el-select v-model="orgForm.organization_type">
                <el-option :label="t('orgTypeYouthLeague')" value="youth_league" />
                <el-option :label="t('orgTypeStudentOrg')" value="student_union" />
                <el-option :label="t('orgTypeClub')" value="club" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('orgParentOrg')">
              <el-select v-model="orgForm.parent_id" clearable>
                <el-option :label="t('orgNoParent')" value="" />
                <el-option
                  v-for="org in organizations.filter((o) => o.id !== orgEditingId)"
                  :key="`parent-${org.id}`"
                  :label="td(org.name)"
                  :value="org.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgLeaderRole')">
              <el-select v-model="orgForm.leader_role">
                <el-option :label="t('roleTeacher')" value="teacher" />
                <el-option :label="t('roleStudent')" value="student" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('organizationLeader')">
              <el-input v-model="orgForm.leader_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('orgTeacherLeader')">
              <el-input v-model="orgForm.leader_teacher_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('orgStudentLeaderId')">
              <el-input v-model="orgForm.leader_student_id" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item :label="t('memberCount')">
              <el-input-number v-model="orgForm.member_count" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('orgLogo')">
              <input type="file" accept="image/*" @change="onLogoChange" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="orgDialogVisible = false">{{ t('scheduleCancel') }}</el-button>
        <el-button type="primary" :loading="orgSubmitting" @click="submitOrganization">{{ t('scheduleSave') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { API_BASE } from '../api/baseUrl'
import { createOrganization, deleteOrganization, getOrganizations, updateOrganization } from '../api/organization'
import { createTask, getTaskDetail, getTasks, transferTask } from '../api/task'
import { t, td } from '../i18n'
import { roleState } from '../stores/role'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const organizations = ref([])
const tasks = ref([])
const activeOrgId = ref('')
const currentRole = ref('owner')
const boardTaskDetailVisible = ref(false)
const selectedBoardTask = ref(null)
const selectedBoardTaskLogs = ref([])
const assignVisible = ref(false)
const assignSubmitting = ref(false)
const transferVisible = ref(false)
const transferSubmitting = ref(false)
const handoverTask = ref(null)
const orgDialogVisible = ref(false)
const orgSubmitting = ref(false)
const orgEditingId = ref('')
const orgForm = ref({
  name: '',
  short_name: '',
  organization_type: 'club',
  parent_id: '',
  leader_role: 'student',
  leader_name: '',
  leader_student_id: '',
  leader_teacher_name: '',
  member_count: 0,
  logo: null,
})
const boardFilters = ref({
  orgId: '',
  status: '',
  typeKey: '',
})
const assignForm = ref({
  title: '',
  description: '',
  task_type: 'affairs',
  assignment_type: 'single_department',
  collaborating_org_ids: [],
  current_org_id: '',
  current_owner_name: '',
  deadline: '',
})
const transferForm = ref({
  to_org_id: '',
  to_owner: '',
  note: '',
})

const activeOrg = computed(() => organizations.value.find((o) => o.id === activeOrgId.value) ?? null)
const canUseAdminView = computed(() => roleState.roleCode === 'org_admin' || roleState.roleCode === 'tw_admin')
const canManageOrganizations = computed(() => canUseAdminView.value && currentRole.value === 'admin')
const twOrgId = computed(() => {
  const tw = organizations.value.find((o) => o.id === 'tw')
  return tw?.id || organizations.value[0]?.id || ''
})

const boardTasks = computed(() => {
  const orgMap = new Map(organizations.value.map((o) => [o.id, o.name]))
  return (Array.isArray(tasks.value) ? tasks.value : []).map((task) => ({
    ...task,
    orgId: task.currentOrgId || '',
    orgName: orgMap.get(task.currentOrgId) || t('commonUnassigned'),
    sourceOrgName: orgMap.get(task.sourceOrgId) || t('commonUnassigned'),
    typeKey: task.typeI18n || 'taskTypeAffairs',
    sourceKey: task.sourceI18n || 'sourceOrganization',
  }))
})

const activeOrgTasks = computed(() =>
  boardTasks.value.filter((row) => row.orgId === activeOrgId.value),
)

const boardTypeOptions = computed(() => {
  const seen = new Set()
  const rows = []
  for (const task of boardTasks.value) {
    if (!task?.typeKey || seen.has(task.typeKey)) continue
    seen.add(task.typeKey)
    rows.push({ value: task.typeKey, label: t(task.typeKey) })
  }
  return rows
})

const filteredBoardTasks = computed(() => {
  const { orgId, status, typeKey } = boardFilters.value
  return boardTasks.value.filter((row) => {
    if (orgId && row.orgId !== orgId) return false
    if (status && row.status !== status) return false
    if (typeKey && row.typeKey !== typeKey) return false
    return true
  })
})

const boardStats = computed(() => {
  const rows = boardTasks.value
  return {
    pendingHandlingCount: rows.filter((x) => x.status === 'pending' || x.status === 'viewed').length,
    inProgressCount: rows.filter((x) => x.status === 'in_progress').length,
    doneCount: rows.filter((x) => x.status === 'done').length,
    totalOrganizations: organizations.value.length,
    activeTasks: rows.filter((x) => x.status === 'in_progress' || x.status === 'viewed').length,
    crossOrgTasks: rows.filter(
      (x) =>
        x.assignmentType === 'cross_department' ||
        (Array.isArray(x.collaboratingOrgIds) && x.collaboratingOrgIds.length > 1),
    ).length,
  }
})

const activeOrgStatus = computed(() => {
  if (!activeOrg.value) return 'orgStatusPreparing'
  const rows = boardTasks.value.filter((x) => x.orgId === activeOrg.value.id)
  if (Number(activeOrg.value.memberCount || 0) <= 0) return 'orgStatusPreparing'
  if (rows.some((x) => x.status === 'in_progress' || x.status === 'viewed')) return 'orgStatusActive'
  if (rows.length === 0) return 'orgStatusPaused'
  return 'orgStatusActive'
})

const todoTasks = computed(() => {
  const rank = { priorityHigh: 0, priorityMedium: 1, priorityLow: 2 }
  return boardTasks.value
    .filter((x) => x.status === 'pending' || x.status === 'viewed' || x.status === 'in_progress')
    .sort((a, b) => {
      const pa = rank[a.priorityI18n] ?? 9
      const pb = rank[b.priorityI18n] ?? 9
      if (pa !== pb) return pa - pb
      return String(a.dueDate || '').localeCompare(String(b.dueDate || ''))
    })
    .slice(0, 8)
})

const currentRoleHint = computed(() =>
  currentRole.value === 'admin'
    ? t('orgRoleHintAdmin')
    : t('orgRoleHintOwner'),
)

const boardEmptyText = computed(() => {
  if (!boardTasks.value.length) return t('orgNoTaskData')
  return t('orgNoTaskByFilter')
})

const activeOrgTaskEmptyText = computed(() => {
  if (!activeOrg.value) return t('orgSelectOrgFirst')
  if (currentRole.value === 'owner') return t('orgOwnerNoTasks')
  return t('orgAdminNoTasks')
})

function orgTypeTag(orgType) {
  const map = {
    orgTypeYouthLeague: 'danger',
    orgTypeStudentOrg: 'primary',
    orgTypeClub: 'success',
  }
  return map[orgType] ?? 'info'
}

function taskSourceTagType(sourceKey) {
  const map = {
    taskSourceLeague: 'primary',
    taskSourceParent: 'warning',
    sourceCourse: 'primary',
    sourceOrganization: 'success',
    sourcePersonal: 'info',
  }
  return map[sourceKey] ?? 'info'
}

function priorityTagType(priorityI18n) {
  const map = {
    priorityHigh: 'danger',
    priorityMedium: 'warning',
    priorityLow: 'info',
  }
  return map[priorityI18n] ?? 'info'
}

const ORG_FLOW_LABEL = {
  pending: 'taskFlowPending',
  viewed: 'taskFlowViewed',
  in_progress: 'taskFlowInProgress',
  done: 'taskFlowDone',
}

function orgTaskStatusLabelKey(status) {
  if (status && ORG_FLOW_LABEL[status]) return ORG_FLOW_LABEL[status]
  return status || 'taskFlowPending'
}

function taskStatusTagType(status) {
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

function orgStatusTagType(statusKey) {
  const map = {
    orgStatusActive: 'success',
    orgStatusPreparing: 'warning',
    orgStatusPaused: 'info',
  }
  return map[statusKey] ?? 'info'
}

function taskFlowSummary(row) {
  const sourceOrg = row.sourceOrgName || t('commonUnassigned')
  const currentOrg = row.orgName || t('commonUnassigned')
  const owner = row.ownerName ? td(row.ownerName) : t('commonUnassigned')
  return `${td(sourceOrg)} -> ${td(currentOrg)} -> ${owner}`
}

function onAssignFlowChange() {
  if (assignForm.value.assignment_type !== 'cross_department') {
    assignForm.value.collaborating_org_ids = []
  }
}

function onAssignTask() {
  const oid = activeOrgId.value || organizations.value[0]?.id || ''
  assignForm.value = {
    title: '',
    description: '',
    task_type: 'affairs',
    assignment_type: 'single_department',
    collaborating_org_ids: [],
    current_org_id: oid,
    current_owner_name: '',
    deadline: '',
  }
  assignVisible.value = true
}

function collabOrgDisplay(row) {
  const ids = row?.collaboratingOrgIds
  if (!Array.isArray(ids) || !ids.length) return '—'
  const map = new Map(organizations.value.map((o) => [o.id, o.name]))
  return ids.map((id) => td(map.get(id) || id)).join(' / ')
}

function emptyOrgForm() {
  return {
    name: '',
    short_name: '',
    organization_type: 'club',
    parent_id: '',
    leader_role: 'student',
    leader_name: '',
    leader_student_id: '',
    leader_teacher_name: '',
    member_count: 0,
    logo: null,
  }
}

function openCreateOrganization() {
  orgEditingId.value = ''
  orgForm.value = emptyOrgForm()
  orgDialogVisible.value = true
}

function openEditOrganization(org) {
  orgEditingId.value = org.id
  orgForm.value = {
    name: org.name || '',
    short_name: org.shortName || '',
    organization_type: org.organizationType || 'club',
    parent_id: org.parentId || '',
    leader_role: org.leaderRole === 'roleTeacher' ? 'teacher' : 'student',
    leader_name: org.leaderName || '',
    leader_student_id: org.leaderStudentId || '',
    leader_teacher_name: org.leaderTeacherName || '',
    member_count: Number(org.memberCount || 0),
    logo: null,
  }
  orgDialogVisible.value = true
}

function onLogoChange(event) {
  const f = event?.target?.files?.[0]
  orgForm.value.logo = f || null
}

function fileUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

function parentOrgName(parentId) {
  if (!parentId) return '—'
  return organizations.value.find((x) => x.id === parentId)?.name || parentId
}

async function submitOrganization() {
  if (!canManageOrganizations.value) return
  if (!orgForm.value.name.trim()) {
    ElMessage.warning(t('orgFullNameRequired'))
    return
  }
  orgSubmitting.value = true
  try {
    const payload = { ...orgForm.value }
    if (orgEditingId.value) {
      await updateOrganization(orgEditingId.value, payload)
      ElMessage.success(t('orgUpdated'))
    } else {
      await createOrganization(payload)
      ElMessage.success(t('orgCreated'))
    }
    orgDialogVisible.value = false
    await loadOrganizations()
  } catch (e) {
    ElMessage.error(td(e?.message || t('orgSaveFailed')))
  } finally {
    orgSubmitting.value = false
  }
}

async function onDeleteOrganization(org) {
  if (!canManageOrganizations.value) return
  try {
    await deleteOrganization(org.id)
    ElMessage.success(t('orgDeleted'))
    await loadOrganizations()
  } catch (e) {
    ElMessage.error(td(e?.message || t('orgDeleteFailed')))
  }
}

function onHandover(row) {
  handoverTask.value = row
  transferForm.value = {
    to_org_id: row.orgId || activeOrgId.value || '',
    to_owner: '',
    note: '',
  }
  transferVisible.value = true
}

function progressPercent(status) {
  const map = {
    pending: 20,
    viewed: 40,
    in_progress: 70,
    done: 100,
  }
  return map[status] ?? 20
}

async function openBoardTaskDetail(row) {
  selectedBoardTask.value = row
  selectedBoardTaskLogs.value = []
  if (row?.id) {
    try {
      const detail = await getTaskDetail(row.id)
      selectedBoardTaskLogs.value = Array.isArray(detail?.logs) ? detail.logs.slice(-5).reverse() : []
    } catch (_) {
      selectedBoardTaskLogs.value = []
    }
  }
  boardTaskDetailVisible.value = true
}

function formatBoardLog(log) {
  if (!log) return ''
  if (log.action === 'create') return t('taskLogCreate')
  if (log.action === 'view') return t('taskLogView')
  if (log.action === 'status_change') {
    const from = t(orgTaskStatusLabelKey(log.fromStatus || 'pending'))
    const to = t(orgTaskStatusLabelKey(log.toStatus || 'pending'))
    return t('taskLogStatusChange').replace('{from}', from).replace('{to}', to)
  }
  if (log.action === 'transfer') {
    return t('taskLogTransfer')
      .replace('{from}', td(log.fromOwner || t('commonUnassigned')))
      .replace('{to}', td(log.toOwner || t('commonUnassigned')))
  }
  if (log.action === 'priority_change') {
    return t('taskLogPriorityChange').replace('{detail}', td(String(log.note || '—')))
  }
  return td(log.action || '')
}

function openTaskDetail(row) {
  router.push(`/tasks/${row.id}`)
}

async function loadOrganizations() {
  const data = await getOrganizations()
  const list = Array.isArray(data) ? data.filter(Boolean) : []
  organizations.value = list
  if (!list.length) {
    activeOrgId.value = ''
    return
  }
  if (!list.some((o) => o.id === activeOrgId.value)) {
    activeOrgId.value = list[0].id
  }
}

async function loadTaskData() {
  const filters = {}
  if (currentRole.value === 'owner' && activeOrgId.value) {
    filters.currentOrgId = activeOrgId.value
  }
  const list = await getTasks(filters)
  tasks.value = Array.isArray(list) ? list : []
}

async function initializePageData() {
  loading.value = true
  error.value = ''
  try {
    await loadOrganizations()
    await loadTaskData()
  } catch (e) {
    organizations.value = []
    tasks.value = []
    activeOrgId.value = ''
    error.value = td(e?.message || t('orgTaskRefreshError'))
  } finally {
    loading.value = false
  }
}

watch(
  () => [activeOrgId.value, currentRole.value],
  async () => {
    if (!organizations.value.length) return
    try {
      await loadTaskData()
    } catch (e) {
      ElMessage.error(td(e?.message || t('orgTaskRefreshError')))
    }
  },
)

watch(
  () => roleState.roleCode,
  () => {
    if (!canUseAdminView.value && currentRole.value !== 'owner') {
      currentRole.value = 'owner'
    } else if (canUseAdminView.value && currentRole.value === 'owner' && !activeOrgId.value) {
      currentRole.value = 'admin'
    } else if (canUseAdminView.value && currentRole.value !== 'admin' && currentRole.value !== 'owner') {
      currentRole.value = 'admin'
    }
  },
  { immediate: true },
)

async function submitAssignTask() {
  if (assignForm.value.assignment_type === 'cross_department') {
    const ids = assignForm.value.collaborating_org_ids || []
    if (ids.length < 2) {
      ElMessage.warning(t('taskFlowCrossOrgsMinTwo'))
      return
    }
    if (!ids.includes(assignForm.value.current_org_id)) {
      ElMessage.warning(t('taskFlowCrossMustIncludeCurrentOrg'))
      return
    }
  }
  assignSubmitting.value = true
  try {
    let source_org_id = twOrgId.value
    if (assignForm.value.assignment_type === 'single_department') {
      source_org_id = assignForm.value.current_org_id || twOrgId.value
    }
    const payload = {
      title: assignForm.value.title,
      description: assignForm.value.description,
      task_type: assignForm.value.task_type,
      assignment_type: assignForm.value.assignment_type,
      source_org_id,
      current_org_id: assignForm.value.current_org_id,
      current_owner_name: assignForm.value.current_owner_name,
      deadline: assignForm.value.deadline,
      status: 'pending',
    }
    if (assignForm.value.assignment_type === 'cross_department') {
      payload.collaborating_org_ids = [...assignForm.value.collaborating_org_ids]
    }
    await createTask(payload)
    assignVisible.value = false
    ElMessage.success(t('orgAssignSuccess').replace('{title}', payload.title))
    await loadTaskData()
  } catch (e) {
    ElMessage.error(td(e?.message || t('orgAssignError')))
  } finally {
    assignSubmitting.value = false
  }
}

async function submitTransferTask() {
  const row = handoverTask.value
  if (!row?.id) return
  transferSubmitting.value = true
  try {
    await transferTask(row.id, {
      to_owner: transferForm.value.to_owner,
      to_org_id: transferForm.value.to_org_id,
      note: transferForm.value.note,
    })
    transferVisible.value = false
    ElMessage.success(
      t('orgTransferSuccess').replace('{title}', row.title).replace('{owner}', transferForm.value.to_owner),
    )
    await loadTaskData()
  } catch (e) {
    ElMessage.error(td(e?.message || t('orgTransferError')))
  } finally {
    transferSubmitting.value = false
  }
}

onMounted(() => {
  initializePageData()
})
</script>

<style scoped>
.organization {
  max-width: 1200px;
  margin: 0 auto;
}

.organization__intro {
  margin-bottom: 20px;
}

.organization__title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.02em;
}

.organization__subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.organization__role-switch {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.organization__role-label {
  font-size: 12px;
  color: #909399;
}

.organization__role-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #606266;
}

.organization__alert {
  margin-bottom: 16px;
}

.organization__layout {
  align-items: flex-start;
}

.organization__board-card :deep(.el-card__body) {
  padding-top: 12px;
}

.organization__board-hint {
  font-size: 12px;
  color: #909399;
}

.organization__todo-card {
  margin-bottom: 12px;
  border: 1px solid #ebeef5;
}

.organization__stats {
  margin-bottom: 12px;
}

.organization__stat {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
  padding: 12px;
}

.organization__stat-num {
  font-size: 22px;
  line-height: 1.2;
  font-weight: 700;
  color: #303133;
}

.organization__stat-label {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.organization__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}

.organization__filter-item {
  width: 220px;
  max-width: 100%;
}

.organization__card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.organization__card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.organization__card :deep(.el-card__body) {
  padding: 16px 20px 20px;
}

.organization__list-card :deep(.el-card__body) {
  padding: 8px 12px 12px;
}

.organization__card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.organization__list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.organization__list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  padding: 12px 12px;
  text-align: left;
  font: inherit;
  color: #303133;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}

.organization__list-item:hover {
  background: #f0f9ff;
  border-color: #c6e2ff;
}

.organization__list-item.is-active {
  background: #ecf5ff;
  border-color: #409eff;
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.2);
}

.organization__list-name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
}

.organization__list-tag {
  flex-shrink: 0;
}

.organization__descriptions :deep(.el-descriptions__label) {
  width: 100px;
  font-weight: 600;
  color: #606266;
  background: #fafafa !important;
}

.organization__leader-role {
  margin-left: 8px;
  vertical-align: middle;
}

.organization__member-count {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: #409eff;
  margin-right: 2px;
}

.organization__task-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.organization__task-card :deep(.el-card__body) {
  padding-top: 12px;
}

.organization__table {
  width: 100%;
}

.organization__flow-line {
  font-size: 12px;
  color: #606266;
}

.organization__table :deep(.el-table__header th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

.organization__org-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.organization__meta-tags {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.organization__log-block {
  margin-top: 14px;
}

.organization__log-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.organization__timeline {
  margin-top: 4px;
}

.organization__logo-preview {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}
</style>
