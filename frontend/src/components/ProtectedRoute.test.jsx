import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import ProtectedRoute from './ProtectedRoute'

function renderProtected(initialToken) {
  if (initialToken) localStorage.setItem('access_token', initialToken)
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>login page</div>} />
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>secret content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

beforeEach(() => localStorage.clear())

describe('ProtectedRoute', () => {
  it('renders children when authenticated', () => {
    renderProtected('valid-token')
    expect(screen.getByText('secret content')).toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    renderProtected(null)
    expect(screen.getByText('login page')).toBeInTheDocument()
    expect(screen.queryByText('secret content')).not.toBeInTheDocument()
  })
})
