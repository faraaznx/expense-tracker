import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'

function TestConsumer() {
  const { isAuthenticated, login, logout } = useAuth()
  return (
    <div>
      <span data-testid="status">{isAuthenticated ? 'yes' : 'no'}</span>
      <button onClick={() => login('tok123')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  )
}

beforeEach(() => localStorage.clear())

describe('AuthContext', () => {
  it('starts unauthenticated when localStorage is empty', () => {
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    expect(screen.getByTestId('status').textContent).toBe('no')
  })

  it('starts authenticated when localStorage has a token', () => {
    localStorage.setItem('access_token', 'existing')
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    expect(screen.getByTestId('status').textContent).toBe('yes')
  })

  it('login() stores token and sets isAuthenticated true', async () => {
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    await act(async () => screen.getByText('Login').click())
    expect(localStorage.getItem('access_token')).toBe('tok123')
    expect(screen.getByTestId('status').textContent).toBe('yes')
  })

  it('logout() clears token and sets isAuthenticated false', async () => {
    localStorage.setItem('access_token', 'tok123')
    render(<AuthProvider><TestConsumer /></AuthProvider>)
    await act(async () => screen.getByText('Logout').click())
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(screen.getByTestId('status').textContent).toBe('no')
  })
})
