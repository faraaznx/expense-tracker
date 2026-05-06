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
  return `AED ${Number(amount).toFixed(2)}`
}
