// Vite proxies /api -> http://localhost:8000 in dev (see vite.config.js)
export async function analyze({ recruiter_message, job_description, resume }) {
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recruiter_message, job_description, resume }),
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    const message = detail.detail || `Request failed: ${res.status}`
    const error = new Error(message)
    // Attach the HTTP status so the UI can render rate-limit (429) and
    // server (5xx) errors differently.
    error.status = res.status
    throw error
  }
  return res.json()
}
