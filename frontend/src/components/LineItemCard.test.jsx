import { render, screen, fireEvent } from '@testing-library/react'
import LineItemCard from './LineItemCard'

const item = {
  name: 'Lacnor Full Cream Milk 1L',
  normalized_name: 'Full Cream Milk 1L',
  quantity: 2,
  unit_price_aed: 6.25,
  category: 'Dairy & Eggs',
}

describe('LineItemCard', () => {
  it('renders item name and quantity', () => {
    render(<LineItemCard item={item} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('Lacnor Full Cream Milk 1L')).toBeInTheDocument()
    expect(screen.getByDisplayValue('2')).toBeInTheDocument()
  })

  it('displays total price as quantity × unit_price', () => {
    render(<LineItemCard item={item} onChange={vi.fn()} />)
    expect(screen.getByText('AED 12.50')).toBeInTheDocument()
  })

  it('calls onChange with updated item when quantity changes', () => {
    const onChange = vi.fn()
    render(<LineItemCard item={item} onChange={onChange} />)
    fireEvent.change(screen.getByDisplayValue('2'), { target: { value: '3' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ quantity: 3 }))
  })

  it('calls onChange with updated item when unit price changes', () => {
    const onChange = vi.fn()
    render(<LineItemCard item={item} onChange={onChange} />)
    fireEvent.change(screen.getByDisplayValue('6.25'), { target: { value: '7.00' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ unit_price_aed: 7 }))
  })
})
