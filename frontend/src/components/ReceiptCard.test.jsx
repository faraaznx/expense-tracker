import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ReceiptCard from './ReceiptCard'

const receipt = {
  id: 'r1',
  store_name: 'Lulu Hypermarket',
  date: '2026-05-03',
  total_aed: '143.50',
  source: 'physical_photo',
  item_count: 7,
}

describe('ReceiptCard', () => {
  it('renders store name', () => {
    render(<MemoryRouter><ReceiptCard receipt={receipt} /></MemoryRouter>)
    expect(screen.getByText('Lulu Hypermarket')).toBeInTheDocument()
  })

  it('renders total formatted as AED', () => {
    render(<MemoryRouter><ReceiptCard receipt={receipt} /></MemoryRouter>)
    expect(screen.getByText('AED 143.50')).toBeInTheDocument()
  })

  it('renders item count', () => {
    render(<MemoryRouter><ReceiptCard receipt={receipt} /></MemoryRouter>)
    expect(screen.getByText(/7 items/)).toBeInTheDocument()
  })

  it('links to the receipt detail page', () => {
    render(<MemoryRouter><ReceiptCard receipt={receipt} /></MemoryRouter>)
    expect(screen.getByRole('link').getAttribute('href')).toBe('/receipts/r1')
  })
})
