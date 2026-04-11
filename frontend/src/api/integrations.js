import { API_BASE } from './baseUrl'

export async function importIntegrationData(importType, file) {
  const form = new FormData()
  form.append('import_type', importType)
  form.append('file', file)
  const res = await fetch(`${API_BASE}/api/integrations/import`, {
    method: 'POST',
    credentials: 'include',
    body: form,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.message || `import failed: HTTP ${res.status}`)
  return body.data
}

export async function getIntegrationLogs(limit = 50) {
  const res = await fetch(`${API_BASE}/api/integrations/logs?limit=${encodeURIComponent(String(limit))}`, {
    credentials: 'include',
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(body.message || `get logs failed: HTTP ${res.status}`)
  return Array.isArray(body.data) ? body.data : []
}

