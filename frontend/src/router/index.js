import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Schedule from '../views/Schedule.vue'
import TaskCenter from '../views/TaskCenter.vue'
import TaskDetail from '../views/TaskDetail.vue'
import Organization from '../views/Organization.vue'
import Profile from '../views/Profile.vue'
import QualityReview from '../views/QualityReview.vue'
import Settings from '../views/Settings.vue'
import DataIntegration from '../views/DataIntegration.vue'
import Login from '../views/Login.vue'
import { initAuth, roleState } from '../stores/role'

const routes = [
  { path: '/login', component: Login, meta: { guestOnly: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/schedule', component: Schedule, meta: { requiresAuth: true } },
  { path: '/tasks', component: TaskCenter, meta: { requiresAuth: true } },
  { path: '/tasks/:id', component: TaskDetail, meta: { requiresAuth: true } },
  { path: '/organization', component: Organization, meta: { requiresAuth: true } },
  { path: '/integrations', component: DataIntegration, meta: { requiresAuth: true } },
  { path: '/profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/quality-review', component: QualityReview, meta: { requiresAuth: true, requiresTwAdmin: true } },
  { path: '/settings', component: Settings, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (!roleState.initialized) {
    await initAuth()
  }
  if (to.meta?.guestOnly && roleState.authenticated) {
    return '/dashboard'
  }
  if (to.meta?.requiresAuth && !roleState.authenticated) {
    return `/login?redirect=${encodeURIComponent(to.fullPath)}`
  }
  if (to.meta?.requiresTwAdmin && roleState.roleCode !== 'tw_admin') {
    return '/dashboard'
  }
  return true
})

export default router