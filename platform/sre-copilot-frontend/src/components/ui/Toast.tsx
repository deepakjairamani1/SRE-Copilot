import { Toaster } from 'sonner'

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        style: {
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '16px',
          padding: '16px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
        },
        className: 'glass-toast',
      }}
      richColors
    />
  )
}
