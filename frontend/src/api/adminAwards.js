import { API_BASE } from './baseUrl'

async function readJson(res) {
  try {
    return await res.json()
  } catch {
    return {}
  }
}

export async function getAdminAwards(status = '') {
  const q = status ? `?status=${encodeURIComponent(status)}` : ''
  const res = await fetch(`${API_BASE}/api/admin/awards${q}`, {
    credentials: 'include',
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `getAdminAwards: HTTP ${res.status}`)
  }
  return Array.isArray(body.data) ? body.data : []
}

export async function reviewAward(awardId, payload) {
  const res = await fetch(`${API_BASE}/api/admin/awards/${encodeURIComponent(awardId)}/review`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload || {}),
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `reviewAward: HTTP ${res.status}`)
  }
  return body.data
}
