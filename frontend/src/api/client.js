const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
export const TOKEN_KEY = 'access_token'

function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export async function request(path, options = {}) {
  const token = getToken()
  const headers = { ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new Error('Network error — check your connection and try again.')
  }

  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY)
    window.location.href = '/login'
    throw new Error('Session expired — please log in again.')
  }

  if (res.status === 204) return null

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }

  return res.json().catch(() => {
    throw new Error(`Server returned non-JSON response (status ${res.status})`)
  })
}

export const api = {
  login: (email, password) =>
    request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }),

  signup: (email, password) =>
    request('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }),

  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    return request('/api/auth/logout', { method: 'POST' }).catch(() => {})
  },

  parseReceipt: (files) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    return request('/api/receipts/parse', { method: 'POST', body: formData })
  },

  confirmReceipt: (body) =>
    request('/api/receipts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }),

  listReceipts: (page = 1) => {
    const params = new URLSearchParams({ page })
    return request(`/api/receipts?${params}`)
  },

  getReceipt: (id) =>
    request(`/api/receipts/${encodeURIComponent(id)}`),

  deleteReceipt: (id) =>
    request(`/api/receipts/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
