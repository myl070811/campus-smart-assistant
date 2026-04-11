import { computed, reactive } from 'vue'
import { getCurrentUser, login as loginApi, logout as logoutApi } from '../api/auth'

const KEY = 'campus_role'
const USER_KEY = 'campus_user'
const allowed = new Set(['student', 'org_admin', 'tw_admin'])

function normalizeRole(raw) {
  const v = String(raw || '').trim().toLowerCase()
  return allowed.has(v) ? v : ''
}

const initialRoleCode =
  typeof localStorage !== 'undefined' ? normalizeRole(localStorage.getItem(KEY)) : ''
const initialUserName =
  typeof localStorage !== 'undefined' ? String(localStorage.getItem(USER_KEY) || '') : ''

export const roleState = reactive({
  current: initialRoleCode || 'student',
  roleCode: initialRoleCode || 'student',
  username: initialUserName,
  displayName: initialUserName,
  initialized: false,
  authenticated: Boolean(initialRoleCode),
})

if (typeof localStorage !== 'undefined') {
  if (initialRoleCode) {
    localStorage.setItem(KEY, initialRoleCode)
  } else {
    localStorage.removeItem(KEY)
  }
}

function applyUser(user) {
  const roleCode = normalizeRole(user?.role) || 'student'
  roleState.roleCode = roleCode
  roleState.current = roleCode
  roleState.username = String(user?.username || '')
  roleState.displayName = String(user?.display_name || user?.username || '')
  roleState.authenticated = true
  roleState.initialized = true
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(KEY, roleCode)
    localStorage.setItem(USER_KEY, roleState.username)
  }
}

function clearUserState() {
  roleState.current = 'student'
  roleState.roleCode = 'student'
  roleState.username = ''
  roleState.displayName = ''
  roleState.authenticated = false
  roleState.initialized = true
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(KEY)
    localStorage.removeItem(USER_KEY)
  }
}

export async function initAuth() {
  try {
    const user = await getCurrentUser()
    if (user) {
      applyUser(user)
      return true
    }
  } catch (_) {
    // ignore, handled as logged out
  }
  clearUserState()
  return false
}

export async function login(username, password) {
  const user = await loginApi({ username, password })
  applyUser(user)
  return user
}

export async function logout() {
  try {
    await logoutApi()
  } finally {
    clearUserState()
  }
}

export const isTwAdmin = computed(() => roleState.roleCode === 'tw_admin')
export const isOrgAdmin = computed(() => roleState.roleCode === 'org_admin')
export const isStudent = computed(() => roleState.roleCode === 'student')
