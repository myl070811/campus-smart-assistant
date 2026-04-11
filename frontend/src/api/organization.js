/**
 * 组织列表（Flask）
 * GET /api/organizations → { data }
 */
import { API_BASE } from './baseUrl'
import { mapOrganizationListFromApi } from '../domain/mapFromApi'

export async function getOrganizations() {
  const res = await fetch(`${API_BASE}/api/organizations`, {
    credentials: 'include',
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.message || `getOrganizations: HTTP ${res.status}`)
  }
  const raw = body.data
  return mapOrganizationListFromApi(Array.isArray(raw) ? raw : [])
}

export async function createOrganization(payload) {
  const form = new FormData()
  Object.entries(payload || {}).forEach(([k, v]) => {
    if (v == null || v === '') return
    if (k === 'logo' && v instanceof File) form.append('logo', v)
    else form.append(k, String(v))
  })
  const res = await fetch(`${API_BASE}/api/organizations`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.message || `createOrganization: HTTP ${res.status}`)
  return body.data
}

export async function updateOrganization(orgId, payload) {
  const form = new FormData()
  Object.entries(payload || {}).forEach(([k, v]) => {
    if (v == null || v === '') return
    if (k === 'logo' && v instanceof File) form.append('logo', v)
    else form.append(k, String(v))
  })
  const res = await fetch(`${API_BASE}/api/organizations/${encodeURIComponent(orgId)}`, {
    method: 'PATCH',
    credentials: 'include',
    body: form,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.message || `updateOrganization: HTTP ${res.status}`)
  return body.data
}

export async function deleteOrganization(orgId) {
  const res = await fetch(`${API_BASE}/api/organizations/${encodeURIComponent(orgId)}`, {
    method: 'DELETE',
    credentials: 'include',
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.message || `deleteOrganization: HTTP ${res.status}`)
  return body.success === true
}
