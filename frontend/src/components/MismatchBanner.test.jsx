import { render, screen } from '@testing-library/react'
import MismatchBanner from './MismatchBanner'

describe('MismatchBanner', () => {
  it('renders nothing when mismatchAed is null', () => {
    const { container } = render(<MismatchBanner mismatchAed={null} totalAed={100} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders warning with mismatch amount when non-null', () => {
    render(<MismatchBanner mismatchAed={2.5} totalAed={100} />)
    expect(screen.getByText(/AED 2.50/)).toBeInTheDocument()
  })

  it('shows the receipt total in the banner', () => {
    render(<MismatchBanner mismatchAed={5} totalAed={143.5} />)
    expect(screen.getByText(/AED 143.50/)).toBeInTheDocument()
  })
})
