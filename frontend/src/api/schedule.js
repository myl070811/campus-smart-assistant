import { API_BASE } from './baseUrl'
import { mapScheduleEventsFromApi } from '../domain/mapFromApi'

async function readJson(res) {
  try {
    return await res.json()
  } catch {
    return {}
  }
}

export async function getScheduleEvents(eventTypes = []) {
  const q = Array.isArray(eventTypes) && eventTypes.length
    ? `?event_types=${encodeURIComponent(eventTypes.join(','))}`
    : ''
  const res = await fetch(`${API_BASE}/api/schedule/events${q}`, {
    credentials: 'include',
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `getScheduleEvents: HTTP ${res.status}`)
  }
  return mapScheduleEventsFromApi(Array.isArray(body.data) ? body.data : [])
}

export async function createSchedulePlan(payload) {
  const res = await fetch(`${API_BASE}/api/schedule/plans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `createSchedulePlan: HTTP ${res.status}`)
  }
  return mapScheduleEventsFromApi([body.data])[0] ?? null
}

export async function updateSchedulePlan(planId, payload) {
  const res = await fetch(`${API_BASE}/api/schedule/plans/${encodeURIComponent(planId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload),
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `updateSchedulePlan: HTTP ${res.status}`)
  }
  return mapScheduleEventsFromApi([body.data])[0] ?? null
}

export async function deleteSchedulePlan(planId) {
  const res = await fetch(`${API_BASE}/api/schedule/plans/${encodeURIComponent(planId)}`, {
    method: 'DELETE',
    credentials: 'include',
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `deleteSchedulePlan: HTTP ${res.status}`)
  }
  return body.success === true
}
