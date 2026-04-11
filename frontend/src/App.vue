<template>
  <el-config-provider :locale="elementLocale">
    <router-view v-if="isLoginPage" />
    <el-container v-else class="app-layout" :key="langState.current">
      <el-aside width="220px" class="app-layout__aside">
        <h2 class="app-layout__brand">{{ t('appName') }}</h2>

        <el-menu
          :default-active="$route.path"
          router
          background-color="#2c3e50"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/dashboard">{{ t('menuDashboard') }}</el-menu-item>
          <el-menu-item index="/schedule">{{ t('menuSchedule') }}</el-menu-item>
          <el-menu-item index="/tasks">{{ t('menuTasks') }}</el-menu-item>
          <el-menu-item index="/organization">{{ t('menuOrganization') }}</el-menu-item>
          <el-menu-item index="/integrations">{{ t('menuIntegrations') }}</el-menu-item>
          <el-menu-item index="/profile">{{ t('menuProfile') }}</el-menu-item>
          <el-menu-item v-if="showQualityReview" index="/quality-review">{{ t('menuQualityReview') }}</el-menu-item>
          <el-menu-item index="/settings">{{ t('menuSettings') }}</el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="app-layout__header">
          <span class="app-layout__title">{{ t('systemTitle') }}</span>
          <div class="app-layout__role">
            <span class="app-layout__role-label">{{ t('roleCurrent') }}：{{ roleLabel }}</span>
            <span class="app-layout__role-label">{{ td(roleState.displayName || roleState.username) }}</span>
            <el-button size="small" @click="onLogout">{{ t('logout') }}</el-button>
          </div>
        </el-header>

        <el-main class="app-layout__main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import ru from 'element-plus/es/locale/lang/ru'
import { langState, t, td } from './i18n'
import { logout, roleState } from './stores/role'

const elementLocales = {
  zh: zhCn,
  en,
  ru,
}

const elementLocale = computed(() => elementLocales[langState.current] ?? zhCn)
const route = useRoute()
const router = useRouter()
const isLoginPage = computed(() => route.path === '/login')
const roleLabel = computed(() => {
  const map = {
    student: t('roleStudent'),
    org_admin: t('roleOrgAdmin'),
    tw_admin: t('roleTwAdmin'),
  }
  return map[roleState.roleCode] || t('roleStudent')
})
const showQualityReview = computed(() => roleState.roleCode === 'tw_admin')

async function onLogout() {
  await logout()
  router.replace('/login')
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
}

.app-layout__aside {
  background: #2c3e50;
  color: white;
}

.app-layout__brand {
  padding: 20px;
  color: white;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.app-layout__header {
  background: #fff;
  border-bottom: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.app-layout__title {
  font-size: 24px;
  font-weight: bold;
}

.app-layout__role {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-layout__role-label {
  font-size: 13px;
  color: #606266;
}

.app-layout__main {
  background: #f5f7fa;
}
</style>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>
