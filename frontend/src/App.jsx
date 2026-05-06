import { createBrowserRouter, RouterProvider, Outlet, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import BottomNav from './components/BottomNav'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import ReviewPage from './pages/ReviewPage'
import ReceiptListPage from './pages/ReceiptListPage'
import ReceiptDetailPage from './pages/ReceiptDetailPage'

function AppShell() {
  return (
    <div className="min-h-screen bg-app-bg pb-16">
      <Outlet />
      <BottomNav />
    </div>
  )
}

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/receipts" replace /> },
      { path: '/receipts', element: <ReceiptListPage /> },
      { path: '/receipts/:id', element: <ReceiptDetailPage /> },
      { path: '/upload', element: <UploadPage /> },
      { path: '/review', element: <ReviewPage /> },
    ],
  },
])

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )
}
