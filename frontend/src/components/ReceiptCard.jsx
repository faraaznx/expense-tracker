import { Link } from 'react-router-dom'
import { Camera, Monitor } from 'lucide-react'
import { formatAed } from '../constants'

export default function ReceiptCard({ receipt }) {
  const Icon = receipt.source === 'online_screenshot' ? Monitor : Camera

  return (
    <Link
      to={`/receipts/${receipt.id}`}
      className="block bg-white rounded-xl shadow-sm p-4 active:scale-[0.99] transition-transform"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold text-stone-800 truncate">{receipt.store_name}</p>
          <p className="text-xs text-stone-400 mt-0.5">{receipt.date}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="font-bold text-app-gold">{formatAed(receipt.total_aed)}</p>
          <p className="text-xs text-stone-400 mt-0.5">{receipt.item_count} items</p>
        </div>
      </div>
      <div className="flex items-center gap-1 mt-2">
        <Icon size={12} className="text-stone-300" />
        <span className="text-xs text-stone-300">
          {receipt.source === 'physical_photo' ? 'Physical receipt' : 'Online order'}
        </span>
      </div>
    </Link>
  )
}
