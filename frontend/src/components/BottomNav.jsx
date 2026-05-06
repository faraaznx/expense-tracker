import { NavLink } from 'react-router-dom'
import { Receipt, Upload } from 'lucide-react'

export default function BottomNav() {
  const base = 'flex flex-col items-center gap-0.5 text-xs font-medium py-2 px-6'
  const active = 'text-app-green'
  const inactive = 'text-stone-400'

  return (
    <nav className="fixed bottom-0 inset-x-0 bg-white border-t border-stone-100 flex justify-around">
      <NavLink to="/receipts" className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
        <Receipt size={22} />
        Receipts
      </NavLink>
      <NavLink to="/upload" className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
        <Upload size={22} />
        Upload
      </NavLink>
    </nav>
  )
}
