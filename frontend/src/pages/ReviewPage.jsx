import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import MismatchBanner from '../components/MismatchBanner'
import LineItemCard from '../components/LineItemCard'
import { api } from '../api/client'
import { formatAed } from '../constants'

export default function ReviewPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const draft = state?.draft

  const [items, setItems] = useState(() =>
    (draft?.items ?? []).map((item) => ({
      ...item,
      quantity: Number(item.quantity),
      unit_price_aed: Number(item.unit_price_aed),
    }))
  )
  const [storeName, setStoreName] = useState(draft?.store_name ?? '')
  const [date, setDate] = useState(draft?.date ?? '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (!draft) {
    navigate('/upload', { replace: true })
    return null
  }

  function updateItem(idx, updated) {
    setItems((prev) => prev.map((item, i) => (i === idx ? updated : item)))
  }

  const itemSum = items.reduce(
    (acc, item) => acc + Number(item.quantity) * Number(item.unit_price_aed),
    0
  )
  const mismatchAed =
    Math.abs(itemSum - Number(draft.total_aed)) > 0.01
      ? Number(draft.total_aed) - itemSum
      : null

  async function handleConfirm() {
    setLoading(true)
    setError(null)
    try {
      const body = {
        temp_image_paths: draft.temp_image_paths,
        store_name: storeName,
        date,
        total_aed: Number(draft.total_aed),
        source: draft.source,
        items: items.map((item) => ({
          name: item.name,
          normalized_name: item.normalized_name,
          quantity: Number(item.quantity),
          unit_price_aed: Number(item.unit_price_aed),
          category: item.category,
        })),
      }
      await api.confirmReceipt(body)
      navigate('/receipts', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 pt-6 pb-8 max-w-lg mx-auto space-y-4">
      <div>
        <h1 className="text-xl font-bold text-app-green">Review Receipt</h1>
        <p className="text-sm text-stone-500">Edit items before saving</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
        <div>
          <label htmlFor="store-name" className="text-xs text-stone-400 font-medium uppercase tracking-wide">Store</label>
          <input
            id="store-name"
            value={storeName}
            onChange={(e) => setStoreName(e.target.value)}
            className="w-full text-sm border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5"
          />
        </div>
        <div>
          <label htmlFor="receipt-date" className="text-xs text-stone-400 font-medium uppercase tracking-wide">Date</label>
          <input
            id="receipt-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full text-sm border-b border-stone-100 focus:outline-none focus:border-app-green mt-0.5 py-0.5"
          />
        </div>
        <div className="flex justify-between items-center pt-1">
          <span className="text-sm text-stone-500">Receipt total</span>
          <span className="text-base font-bold text-app-green">{formatAed(draft.total_aed)}</span>
        </div>
      </div>

      {mismatchAed !== null && (
        <MismatchBanner mismatchAed={mismatchAed} totalAed={draft.total_aed} />
      )}

      <h2 className="text-sm font-semibold text-stone-700 pt-1">
        {items.length} item{items.length !== 1 ? 's' : ''} · {formatAed(itemSum)}
      </h2>

      <div className="space-y-3">
        {items.map((item, i) => (
          <LineItemCard
            key={i}
            index={i}
            item={item}
            onChange={(updated) => updateItem(i, updated)}
          />
        ))}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        onClick={handleConfirm}
        disabled={loading || !storeName.trim() || !date}
        className="w-full bg-app-green text-white rounded-xl py-3 font-medium disabled:opacity-40 flex items-center justify-center gap-2"
      >
        <CheckCircle size={18} />
        {loading ? 'Saving…' : 'Save receipt'}
      </button>
    </div>
  )
}
