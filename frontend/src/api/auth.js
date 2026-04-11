import { API_BASE } from './baseUrl'

async function parseJson(res) {
  return res.json().catch(() => ({}))
}

export async function login(payload) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload || {}),
  })
  const body = await parseJson(res)
  if (!res.ok) throw new Error(body.message || `login: HTTP ${res.status}`)
  return body.data?.user || null
}

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: 'include',
  })
  const body = await parseJson(res)
  if (!res.ok) throw new Error(body.message || `me: HTTP ${res.status}`)
  return body.data?.user || null
}

export async function logout() {
  const res = await fetch(`${API_BASE}/api/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  const body = await parseJson(res)
  if (!res.ok) throw new Error(body.message || `logout: HTTP ${res.status}`)
  return body.data?.success === true
}

