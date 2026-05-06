import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import ReceiptCard from '../components/ReceiptCard'
import { api } from '../api/client'

export default function ReceiptListPage() {
  const [receipts, setReceipts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.listReceipts(1)
      .then((data) => {
        if (!Array.isArray(data)) throw new Error('Unexpected response from server')
        setReceipts(data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="px-4 pt-6 pb-4 max-w-lg mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-app-green">My Receipts</h1>
        <button
          onClick={() => navigate('/upload')}
          className="bg-app-green text-white rounded-full p-2"
          aria-label="Upload receipt"
        >
          <Plus size={18} />
        </button>
      </div>

      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-4 h-20 animate-pulse" />
          ))}
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && receipts.length === 0 && !error && (
        <div className="text-center py-16">
          <p className="text-stone-400 text-sm">No receipts yet</p>
          <button
            onClick={() => navigate('/upload')}
            className="mt-4 bg-app-green text-white rounded-xl px-6 py-2.5 text-sm font-medium"
          >
            Upload your first receipt
          </button>
        </div>
      )}

      {!loading && receipts.length > 0 && (
        <div className="space-y-3">
          {receipts.map((r) => (
            <ReceiptCard key={r.id} receipt={r} />
          ))}
        </div>
      )}
    </div>
  )
}
