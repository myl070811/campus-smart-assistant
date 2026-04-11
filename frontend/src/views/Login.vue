<template>
  <div class="login">
    <el-card shadow="never" class="login__card">
      <h2 class="login__title">{{ t('loginTitle') }}</h2>
      <p class="login__subtitle">{{ t('loginSubtitle') }}</p>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('loginUsername')">
          <el-input v-model="form.username" :placeholder="t('loginUsernamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('loginPassword')">
          <el-input v-model="form.password" type="password" show-password :placeholder="t('loginPasswordPlaceholder')" />
        </el-form-item>
        <el-button type="primary" :loading="submitting" style="width: 100%" @click="onSubmit">{{ t('loginSubmit') }}</el-button>
      </el-form>
      <div class="login__demo">
        <div class="login__demo-title">{{ t('loginDemoHeading') }}</div>
        <ul class="login__demo-list">
          <li><code>student01</code> / <code>123456</code> — {{ t('roleStudent') }}（陈思远）</li>
          <li><code>student02</code> / <code>123456</code> — {{ t('roleStudent') }}（李华，{{ t('loginDemoSecondStudentNote') }}）</li>
          <li><code>orgadmin01</code> / <code>123456</code> — {{ t('roleOrgAdmin') }}</li>
          <li><code>twadmin01</code> / <code>123456</code> — {{ t('roleTwAdmin') }}</li>
        </ul>
        <p class="login__demo-tip">{{ t('loginDemoFeatureTip') }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../stores/role'
import { t, td } from '../i18n'

const router = useRouter()
const route = useRoute()
const submitting = ref(false)
const form = reactive({
  username: 'student01',
  password: '123456',
})

async function onSubmit() {
  if (!form.username.trim() || !form.password) {
    ElMessage.warning(t('loginValidationRequired'))
    return
  }
  submitting.value = true
  try {
    await login(form.username.trim(), form.password)
    ElMessage.success(t('loginSuccess'))
    const next = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.replace(next)
  } catch (e) {
    ElMessage.error(td(e?.message || t('loginFailed')))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.login__card { width: 420px; border: 1px solid #ebeef5; }
.login__title { margin: 0 0 8px; color: #303133; }
.login__subtitle { margin: 0 0 16px; color: #909399; font-size: 13px; }
.login__demo { margin-top: 16px; color: #606266; font-size: 12px; line-height: 1.65; }
.login__demo-title { font-weight: 600; color: #303133; margin-bottom: 8px; }
.login__demo-list { margin: 0; padding-left: 18px; }
.login__demo-list li { margin: 4px 0; }
.login__demo-list code { font-size: 11px; background: #f4f4f5; padding: 1px 5px; border-radius: 3px; }
.login__demo-tip { margin: 10px 0 0; padding: 8px 10px; background: #ecf5ff; border-radius: 6px; color: #409eff; font-size: 12px; }
</style>

