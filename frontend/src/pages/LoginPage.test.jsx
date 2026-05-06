import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import LoginPage from './LoginPage'
import { api } from '../api/client'

vi.mock('../api/client', () => ({
  api: { login: vi.fn(), signup: vi.fn() },
  TOKEN_KEY: 'access_token',
}))

function renderLogin() {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/receipts" element={<div>receipts page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

beforeEach(() => {
  localStorage.clear()
  vi.clearAllMocks()
})

describe('LoginPage', () => {
  it('renders email and password inputs', () => {
    renderLogin()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('shows a toggle to switch to sign up', () => {
    renderLogin()
    expect(screen.getByText(/sign up/i)).toBeInTheDocument()
  })

  it('calls api.login on submit and navigates to /receipts on success', async () => {
    api.login.mockResolvedValue({ access_token: 'tok', user_id: 'u1' })
    renderLogin()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(api.login).toHaveBeenCalledWith('a@b.com', 'password123'))
    await waitFor(() => expect(screen.getByText('receipts page')).toBeInTheDocument())
  })

  it('shows error message when login fails', async () => {
    api.login.mockRejectedValue(new Error('Invalid credentials'))
    renderLogin()

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'wrongpass' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => expect(screen.getByText('Invalid credentials')).toBeInTheDocument())
  })

  it('clears form fields when switching modes', async () => {
    renderLogin()
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.com' } })
    fireEvent.click(screen.getByText(/sign up/i))
    expect(screen.getByLabelText(/email/i).value).toBe('')
  })

  it('calls api.signup when in signup mode', async () => {
    api.signup.mockResolvedValue({ access_token: 'tok', user_id: 'u1' })
    renderLogin()

    fireEvent.click(screen.getByText(/sign up/i))
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'new@user.com' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password123' } })
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }))

    await waitFor(() => expect(api.signup).toHaveBeenCalledWith('new@user.com', 'password123'))
    await waitFor(() => expect(screen.getByText('receipts page')).toBeInTheDocument())
  })
})
