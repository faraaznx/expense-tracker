export const CATEGORIES = [
  'Produce',
  'Meat & Seafood',
  'Dairy & Eggs',
  'Bakery',
  'Beverages',
  'Frozen & Snacks',
  'Dry Goods & Pantry',
  'Cleaning & Household',
  'Personal Care',
  'Baby & Kids',
  'Electronics',
  'Delivery Fee',
  'VAT',
  'Other',
]

export function formatAed(amount) {
  const n = Number(amount)
  if (!Number.isFinite(n)) return 'AED —'
  return `AED ${n.toFixed(2)}`
}
