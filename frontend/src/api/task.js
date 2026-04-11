/**
 * 任务相关 API（Flask 后端）— 返回值为领域 camelCase（经 mapFromApi）。
 */
import { API_BASE } from './baseUrl'
import { mapTaskFromApi, mapTaskLogFromApi } from '../domain/mapFromApi'

async function readJson(res) {
  try {
    return await res.json()
  } catch {
    return {}
  }
}

/**
 * GET /api/tasks — 每条为 camelCase 任务对象
 */
export async function getTasks(filters = {}) {
  const params = new URLSearchParams()
  if (filters?.currentOrgId) params.set('current_org_id', String(filters.currentOrgId))
  if (filters?.status) params.set('status', String(filters.status))
  const query = params.toString() ? `?${params.toString()}` : ''
  const res = await fetch(`${API_BASE}/api/tasks${query}`, {
    credentials: 'include',
  })
  if (!res.ok) {
    throw new Error(`getTasks: HTTP ${res.status}`)
  }
  const body = await readJson(res)
  const list = Array.isArray(body.data) ? body.data : []
  return list.map((raw) => mapTaskFromApi(raw)).filter(Boolean)
}

/**
 * POST /api/tasks
 * body: { title, description, task_type, source_org_id, current_org_id, current_owner_name, deadline, status? }
 */
export async function createTask(payload) {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload || {}),
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `createTask: HTTP ${res.status}`)
  }
  const data = body.data
  if (!data || typeof data !== 'object') {
    throw new Error('createTask: invalid response format')
  }
  const task = mapTaskFromApi(data.task)
  if (!task) {
    throw new Error('createTask: invalid task payload')
  }
  return {
    task,
    logs: Array.isArray(data.logs) ? data.logs.map((l) => mapTaskLogFromApi(l)).filter(Boolean) : [],
  }
}

/**
 * GET /api/tasks/:id
 */
export async function getTaskDetail(id) {
  const res = await fetch(`${API_BASE}/api/tasks/${encodeURIComponent(id)}`, {
    credentials: 'include',
  })
  const body = await readJson(res)
  if (res.status === 404) {
    const err = new Error(body.message || '任务不存在')
    err.code = 'not_found'
    throw err
  }
  if (!res.ok) {
    throw new Error(body.message || `getTaskDetail: HTTP ${res.status}`)
  }
  const data = body.data
  if (!data || typeof data !== 'object') {
    throw new Error('getTaskDetail: invalid response format')
  }
  const task = mapTaskFromApi(data.task)
  if (!task) {
    throw new Error('getTaskDetail: invalid task payload')
  }
  return {
    task,
    logs: Array.isArray(data.logs) ? data.logs.map((l) => mapTaskLogFromApi(l)).filter(Boolean) : [],
  }
}

/**
 * PATCH /api/tasks/:id/status
 */
export async function updateTaskStatus(id, status) {
  const res = await fetch(`${API_BASE}/api/tasks/${encodeURIComponent(id)}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ status }),
  })
  const body = await readJson(res)
  if (res.status === 404) {
    const err = new Error(body.message || '任务不存在')
    err.code = 'not_found'
    throw err
  }
  if (!res.ok && body.success !== false) {
    throw new Error(body.message || `updateTaskStatus: HTTP ${res.status}`)
  }
  if (body.success && body.data) {
    body.data = {
      task: mapTaskFromApi(body.data.task),
      logs: Array.isArray(body.data.logs)
        ? body.data.logs.map((l) => mapTaskLogFromApi(l)).filter(Boolean)
        : [],
    }
  }
  return body
}

/**
 * POST /api/tasks/:id/transfer
 */
export async function transferTask(id, payload) {
  const res = await fetch(`${API_BASE}/api/tasks/${encodeURIComponent(id)}/transfer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      to_owner: payload?.to_owner ?? '',
      to_org_id: payload?.to_org_id ?? '',
      note: payload?.note ?? '',
    }),
  })
  const body = await readJson(res)
  if (!res.ok) {
    throw new Error(body.message || `transferTask: HTTP ${res.status}`)
  }
  const data = body.data
  if (!data || typeof data !== 'object') {
    throw new Error('transferTask: invalid response format')
  }
  const task = mapTaskFromApi(data.task)
  if (!task) {
    throw new Error('transferTask: invalid task payload')
  }
  return {
    task,
    logs: Array.isArray(data.logs) ? data.logs.map((l) => mapTaskLogFromApi(l)).filter(Boolean) : [],
  }
}
