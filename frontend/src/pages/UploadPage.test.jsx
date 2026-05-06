import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import UploadPage from './UploadPage'
import { api } from '../api/client'

vi.mock('../api/client', () => ({
  api: { parseReceipt: vi.fn() },
  TOKEN_KEY: 'access_token',
}))

function renderUpload() {
  localStorage.setItem('access_token', 'tok')
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/upload']}>
        <Routes>
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/review" element={<div>review page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

beforeAll(() => {
  global.URL.createObjectURL = vi.fn((file) => `blob:mock/${file.name}`)
  global.URL.revokeObjectURL = vi.fn()
})

beforeEach(() => { localStorage.clear(); vi.clearAllMocks() })

describe('UploadPage', () => {
  it('shows a button to choose files', () => {
    renderUpload()
    expect(screen.getByRole('button', { name: /choose/i })).toBeInTheDocument()
  })

  it('Parse button is disabled until files are selected', () => {
    renderUpload()
    expect(screen.getByRole('button', { name: /parse/i })).toBeDisabled()
  })

  it('navigates to /review with draft on successful parse', async () => {
    const draft = { store_name: 'Lulu', items: [], temp_image_paths: [], total_aed: 10, mismatch_aed: null }
    api.parseReceipt.mockResolvedValue(draft)
    renderUpload()

    const file = new File(['img'], 'receipt.jpg', { type: 'image/jpeg' })
    const input = screen.getByTestId('file-input')
    fireEvent.change(input, { target: { files: [file] } })

    fireEvent.click(screen.getByRole('button', { name: /parse/i }))

    await waitFor(() => expect(screen.getByText('review page')).toBeInTheDocument())
  })

  it('shows error when parse fails', async () => {
    api.parseReceipt.mockRejectedValue(new Error('Parsing failed'))
    renderUpload()

    const file = new File(['img'], 'receipt.jpg', { type: 'image/jpeg' })
    fireEvent.change(screen.getByTestId('file-input'), { target: { files: [file] } })
    fireEvent.click(screen.getByRole('button', { name: /parse/i }))

    await waitFor(() => expect(screen.getByText('Parsing failed')).toBeInTheDocument())
  })

  it('accepts at most 5 files', () => {
    renderUpload()
    const files = Array.from({ length: 10 }, (_, i) =>
      new File(['img'], `receipt${i}.jpg`, { type: 'image/jpeg' })
    )
    fireEvent.change(screen.getByTestId('file-input'), { target: { files } })
    // After selecting 10 files, only 5 images should be previewed
    const images = screen.getAllByAltText(/^receipt \d+$/)
    expect(images).toHaveLength(5)
  })
})
