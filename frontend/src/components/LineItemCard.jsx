import { formatAed, CATEGORIES } from '../constants'

export default function LineItemCard({ item, onChange }) {
  const total = (Number(item.quantity) * Number(item.unit_price_aed)).toFixed(2)

  function update(field, value) {
    onChange({ ...item, [field]: value })
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
      <div>
        <label className="text-xs text-stone-400 font-medium uppercase tracking-wide">Item name</label>
        <input
          value={item.name}
          onChange={(e) => update('name', e.target.value)}
          className="w-full text-sm text-stone-800 border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-stone-400 font-medium uppercase tracking-wide">Qty</label>
          <input
            type="number"
            min="0.001"
            step="any"
            value={item.quantity}
            onChange={(e) => update('quantity', e.target.value)}
            className="w-full text-sm border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5"
          />
        </div>
        <div>
          <label className="text-xs text-stone-400 font-medium uppercase tracking-wide">Unit price (AED)</label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={item.unit_price_aed}
            onChange={(e) => update('unit_price_aed', e.target.value)}
            className="w-full text-sm border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5"
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex-1 mr-3">
          <label className="text-xs text-stone-400 font-medium uppercase tracking-wide">Category</label>
          <select
            value={item.category}
            onChange={(e) => update('category', e.target.value)}
            className="w-full text-sm border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5 bg-transparent"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div className="text-right">
          <p className="text-xs text-stone-400">Total</p>
          <p className="text-sm font-semibold text-app-gold">{formatAed(total)}</p>
        </div>
      </div>
    </div>
  )
}
