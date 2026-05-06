const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('access_token')
}

export async function request(path, options = {}) {
  const token = getToken()
  const headers = { ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('access_token')
    window.location.href = '/login'
    return
  }

  if (res.status === 204) return null

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }

  return res.json()
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

  logout: () =>
    request('/api/auth/logout', { method: 'POST' }),

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

  listReceipts: (page = 1) =>
    request(`/api/receipts?page=${page}`),

  getReceipt: (id) =>
    request(`/api/receipts/${id}`),

  deleteReceipt: (id) =>
    request(`/api/receipts/${id}`, { method: 'DELETE' }),
}
