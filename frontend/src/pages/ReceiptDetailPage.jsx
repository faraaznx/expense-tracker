import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Trash2, ChevronLeft } from 'lucide-react'
import { api } from '../api/client'
import { formatAed } from '../constants'

export default function ReceiptDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [receipt, setReceipt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    api.getReceipt(id)
      .then(setReceipt)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  async function handleDelete() {
    if (!window.confirm('Delete this receipt? This cannot be undone.')) return
    setDeleting(true)
    try {
      await api.deleteReceipt(id)
      navigate('/receipts', { replace: true })
    } catch (err) {
      setError(err.message)
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="px-4 pt-6 max-w-lg mx-auto space-y-3">
        <div className="h-6 w-32 bg-stone-200 rounded animate-pulse" />
        <div className="h-40 bg-white rounded-xl animate-pulse" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-white rounded-xl animate-pulse" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4 pt-6 max-w-lg mx-auto">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 text-app-green text-sm font-medium mb-4"
        >
          <ChevronLeft size={18} /> Back
        </button>
        <p className="text-sm text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="px-4 pt-4 pb-8 max-w-lg mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1 text-app-green text-sm font-medium"
        >
          <ChevronLeft size={18} /> Back
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting}
          aria-label="Delete receipt"
          className="text-red-500 disabled:opacity-40 p-2"
        >
          <Trash2 size={20} />
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-4">
        <p className="font-bold text-stone-800 text-lg">{receipt.store_name}</p>
        <p className="text-sm text-stone-400">{receipt.date}</p>
        <p className="text-2xl font-bold text-app-gold mt-2">{formatAed(receipt.total_aed)}</p>
        <p className="text-xs text-stone-300 mt-1">
          {receipt.source === 'physical_photo' ? 'Physical receipt' : 'Online order'}
        </p>
      </div>

      {receipt.images.length > 0 && (
        <div
          className="flex gap-2 overflow-x-auto pb-1 -mx-4 px-4"
          aria-label="Receipt images"
        >
          {receipt.images.map((img, i) => (
            <img
              key={i}
              src={img.signed_url}
              alt={`Receipt image ${i + 1}`}
              className="h-48 w-auto rounded-xl flex-shrink-0 object-cover shadow-sm"
            />
          ))}
        </div>
      )}

      <h2 className="text-sm font-semibold text-stone-700">
        {receipt.items.length} item{receipt.items.length !== 1 ? 's' : ''}
      </h2>

      <div className="space-y-2">
        {receipt.items.map((item) => (
          <div
            key={item.id}
            className="bg-white rounded-xl shadow-sm p-3 flex justify-between items-start"
          >
            <div className="min-w-0 mr-3">
              <p className="text-sm font-medium text-stone-800 truncate">{item.name}</p>
              <p className="text-xs text-stone-400 mt-0.5">
                {item.category} · {Number(item.quantity)} × {formatAed(item.unit_price_aed)}
              </p>
            </div>
            <p className="text-sm font-semibold text-app-gold flex-shrink-0">
              {formatAed(item.total_price_aed)}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
