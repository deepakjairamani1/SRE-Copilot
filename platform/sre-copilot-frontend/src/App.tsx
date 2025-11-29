import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from './components/ui/Toast'
import { ErrorBoundary } from './components/features/ErrorBoundary'
import { ChatBot } from './components/ui/ChatBot'
import Dashboard from './pages/Dashboard'
import IncidentsList from './pages/IncidentsList'
import IncidentDetails from './pages/IncidentDetails'
import Investigate from './pages/Investigate'
import ObservabilityDashboard from './pages/ObservabilityDashboard'
import NotFound from './pages/NotFound'
import { ComponentShowcase } from './pages/ComponentShowcase'
import { APITest } from './pages/APITest'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<IncidentsList />} />
            <Route path="/incidents/:incident_id" element={<IncidentDetails />} />
            <Route path="/investigate" element={<Investigate />} />
            <Route path="/observability" element={<ObservabilityDashboard />} />
            <Route path="/showcase" element={<ComponentShowcase />} />
            <Route path="/api-test" element={<APITest />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <ChatBot />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App