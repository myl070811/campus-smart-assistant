<template>
  <div class="settings">
    <div class="settings__intro">
      <h1 class="settings__title">{{ t('settingsTitle') }}</h1>
      <p class="settings__subtitle">{{ t('settingsSubtitle') }}</p>
    </div>

    <el-card shadow="never" class="settings__card">
      <template #header>
        <span class="settings__card-title">{{ t('languageSettings') }}</span>
      </template>
      <div class="settings__current-lang">
        <span class="settings__current-label">{{ t('currentLanguage') }}</span>
        <el-tag type="primary" effect="dark" size="large" round class="settings__current-tag">
          {{ currentLanguageLabel }}
        </el-tag>
      </div>
      <p class="settings__hint">{{ t('selectLanguage') }}</p>
      <el-radio-group v-model="currentLanguage" size="large" class="settings__lang-group">
        <el-radio-button label="zh">{{ t('chinese') }}</el-radio-button>
        <el-radio-button label="en">{{ t('english') }}</el-radio-button>
        <el-radio-button label="ru">{{ t('russian') }}</el-radio-button>
      </el-radio-group>
    </el-card>

    <el-card shadow="never" class="settings__card">
      <template #header>
        <span class="settings__card-title">{{ t('systemSettings') }}</span>
      </template>
      <div class="settings__form">
        <div class="settings__row">
          <div class="settings__row-main">
            <div class="settings__row-title">{{ t('notification') }}</div>
            <div class="settings__row-desc">{{ t('settingsNotificationDesc') }}</div>
          </div>
          <el-switch
            v-model="notifyEnabled"
            :active-text="t('switchOn')"
            :inactive-text="t('switchOff')"
            inline-prompt
          />
        </div>

        <el-divider class="settings__divider" />

        <div class="settings__row settings__row--top">
          <div class="settings__row-main">
            <div class="settings__row-title">{{ t('defaultHome') }}</div>
            <div class="settings__row-desc">{{ t('settingsDefaultHomeDesc') }}</div>
          </div>
          <el-select
            v-model="defaultHome"
            :placeholder="t('pleaseSelect')"
            class="settings__select"
            size="default"
          >
            <el-option
              v-for="opt in homeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </div>

        <el-divider class="settings__divider" />

        <div class="settings__row">
          <div class="settings__row-main">
            <div class="settings__row-title">{{ t('syncStatus') }}</div>
            <div class="settings__row-desc">{{ t('settingsSyncDesc') }}</div>
          </div>
          <div class="settings__sync">
            <el-tag :type="syncDisplay.type" effect="plain" size="large" class="settings__sync-tag">
              <el-icon class="settings__sync-icon"><CircleCheck /></el-icon>
              {{ syncDisplay.text }}
            </el-tag>
            <span class="settings__sync-time">{{ syncDisplay.time }}</span>
          </div>
        </div>

        <el-divider class="settings__divider" />

        <div class="settings__row settings__row--top">
          <div class="settings__row-main">
            <div class="settings__row-title">{{ t('themeMode') }}</div>
            <div class="settings__row-desc">{{ t('settingsThemeDesc') }}</div>
          </div>
          <el-radio-group v-model="themeMode" class="settings__theme-group">
            <el-radio-button value="light">{{ t('lightMode') }}</el-radio-button>
            <el-radio-button value="dark" disabled>{{ t('darkMode') }}</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <div class="settings__footer">
        <el-button type="primary" @click="onSaveMock">{{ t('saveSettingsDemo') }}</el-button>
        <el-button @click="onResetMock">{{ t('resetSettingsDemo') }}</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { CircleCheck } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { t, langState, setLanguage } from '../i18n'

const currentLanguage = computed({
  get: () => langState.current,
  set: (value) => setLanguage(value),
})

/** 界面语言的本族名称（不随 t() 语言包变化，便于识别当前所用语种） */
const NATIVE_LANGUAGE_LABEL = {
  zh: '中文',
  en: 'English',
  ru: 'Русский',
}

const currentLanguageLabel = computed(() => {
  const code = langState.current
  return NATIVE_LANGUAGE_LABEL[code] ?? NATIVE_LANGUAGE_LABEL.zh
})

const notifyEnabled = ref(true)
const defaultHome = ref('/dashboard')
const themeMode = ref('light')

const homeOptions = computed(() => [
  { label: t('homeDashboard'), value: '/dashboard' },
  { label: t('homeTasks'), value: '/tasks' },
  { label: t('homeProfile'), value: '/profile' },
])

const syncDisplay = computed(() => ({
  type: 'success',
  text: t('synced'),
  time: t('lastSyncedAt'),
}))

const defaults = {
  notifyEnabled: true,
  defaultHome: '/dashboard',
  themeMode: 'light',
  language: 'zh',
}

function onSaveMock() {
  ElMessage.success(t('saveSettingsToast'))
}

function onResetMock() {
  setLanguage(defaults.language)
  notifyEnabled.value = defaults.notifyEnabled
  defaultHome.value = defaults.defaultHome
  themeMode.value = defaults.themeMode
  ElMessage.info(t('resetSettingsToast'))
}
</script>

<style scoped>
.settings {
  max-width: 1200px;
  margin: 0 auto;
}

.settings__intro {
  margin-bottom: 20px;
}

.settings__title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  letter-spacing: 0.02em;
}

.settings__subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.settings__card {
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.settings__card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
}

.settings__card :deep(.el-card__body) {
  padding: 20px;
}

.settings__card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.settings__current-lang {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.settings__current-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.settings__current-tag {
  font-size: 14px;
  padding: 6px 16px;
  font-weight: 600;
}

.settings__hint {
  margin: 0 0 16px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.settings__lang-group {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}

.settings__lang-group :deep(.el-radio-button) {
  flex: 1;
  min-width: 0;
}

.settings__lang-group :deep(.el-radio-button__inner) {
  width: 100%;
  padding: 12px 16px;
  font-weight: 500;
}

.settings__form {
  max-width: 720px;
}

.settings__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.settings__row--top {
  align-items: flex-start;
}

.settings__row-main {
  flex: 1;
  min-width: 200px;
}

.settings__row-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.settings__row-desc {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.settings__select {
  width: 220px;
}

.settings__divider {
  margin: 18px 0;
}

.settings__sync {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.settings__sync-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.settings__sync-icon {
  font-size: 16px;
}

.settings__sync-time {
  font-size: 12px;
  color: #909399;
}

.settings__theme-group :deep(.el-radio-button__inner) {
  padding: 10px 20px;
  font-weight: 500;
}

.settings__footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
</style>
