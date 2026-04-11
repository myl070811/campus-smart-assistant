/**
 * 个人档案（Flask）
 * GET /api/profile → { data }
 */
import { API_BASE } from './baseUrl'
import { mapProfileFromApi } from '../domain/mapFromApi'

export async function getProfile() {
  const res = await fetch(`${API_BASE}/api/profile`, {
    credentials: 'include',
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.message || `getProfile: HTTP ${res.status}`)
  }
  return mapProfileFromApi(body.data)
}

export async function updateProfile(payload) {
  const res = await fetch(`${API_BASE}/api/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload || {}),
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.message || `updateProfile: HTTP ${res.status}`)
  }
  return body.data
}

export async function submitAward(formPayload) {
  const form = new FormData()
  form.set('student_id', formPayload?.student_id ?? '')
  form.set('award_name', formPayload?.award_name ?? '')
  form.set('award_time', formPayload?.award_time ?? '')
  if (formPayload?.proof_file) {
    form.set('proof_file', formPayload.proof_file)
  }
  const res = await fetch(`${API_BASE}/api/profile/awards`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.message || `submitAward: HTTP ${res.status}`)
  }
  return body.data
}
