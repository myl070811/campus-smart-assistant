/**
 * 仪表盘 / 课表概览（Flask）
 * GET /api/dashboard → { data }
 */
import { API_BASE } from './baseUrl'
import { mapDashboardFromApi } from '../domain/mapFromApi'

export async function getDashboard() {
  const res = await fetch(`${API_BASE}/api/dashboard`, {
    credentials: 'include',
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.message || `getDashboard: HTTP ${res.status}`)
  }
  return mapDashboardFromApi(body.data)
}
