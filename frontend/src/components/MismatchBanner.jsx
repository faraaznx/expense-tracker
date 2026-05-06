import { AlertTriangle } from 'lucide-react'
import { formatAed } from '../constants'

export default function MismatchBanner({ mismatchAed, totalAed }) {
  if (!mismatchAed) return null

  const itemSum = Number(totalAed) - Number(mismatchAed)

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
      <AlertTriangle size={18} className="text-amber-500 flex-shrink-0 mt-0.5" />
      <div className="text-sm text-amber-800">
        <p className="font-medium">Item total doesn't match receipt total</p>
        <p className="mt-0.5">
          Items sum to <span className="font-medium">{formatAed(itemSum)}</span>{' '}
          but receipt total is <span className="font-medium">{formatAed(totalAed)}</span>.{' '}
          Difference: {formatAed(Math.abs(mismatchAed))}. Please review items below.
        </p>
      </div>
    </div>
  )
}
