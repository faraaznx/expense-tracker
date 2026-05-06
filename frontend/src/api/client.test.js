import { request, api } from './client'

const FAKE_TOKEN = 'test-jwt-token'

beforeEach(() => {
  localStorage.clear()
  vi.stubGlobal('fetch', vi.fn())
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('request()', () => {
  it('attaches Authorization header when token is in localStorage', async () => {
    localStorage.setItem('access_token', FAKE_TOKEN)
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: '1' }),
    })

    await request('/api/test')

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/test'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: `Bearer ${FAKE_TOKEN}`,
        }),
      })
    )
  })

  it('does not attach Authorization header when no token', async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    })

    await request('/api/test')

    const calledWith = fetch.mock.calls[0][1]
    expect(calledWith.headers?.Authorization).toBeUndefined()
  })

  it('returns null for 204 responses', async () => {
    fetch.mockResolvedValue({ ok: true, status: 204 })

    const result = await request('/api/test', { method: 'DELETE' })

    expect(result).toBeNull()
  })

  it('throws with detail message on non-ok response', async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'Validation error' }),
    })

    await expect(request('/api/test')).rejects.toThrow('Validation error')
  })

  it('clears localStorage on 401', async () => {
    localStorage.setItem('access_token', FAKE_TOKEN)
    delete window.location
    window.location = { href: '' }

    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    })

    await request('/api/test')

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(window.location.href).toBe('/login')
  })
})
