import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ComponentShowcase } from './pages/ComponentShowcase'

const queryClient = new QueryClient()

function Dashboard() {
  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="glass-card p-8 mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">SRE</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SRE Copilot</h1>
              <p className="text-gray-600">Site Reliability Engineering Dashboard</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
                <div className="status-badge bg-green-100 text-green-800">
                  <div className="pulse-dot bg-green-500"></div>
                  Healthy
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">99.9%</div>
              <p className="text-sm text-gray-600">Uptime</p>
            </div>
            
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Response Time</h3>
                <div className="status-badge bg-yellow-100 text-yellow-800">
                  <div className="pulse-dot bg-yellow-500"></div>
                  Warning
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">245ms</div>
              <p className="text-sm text-gray-600">Average</p>
            </div>
            
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Active Incidents</h3>
                <div className="status-badge bg-red-100 text-red-800">
                  <div className="pulse-dot bg-red-500"></div>
                  Critical
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-2">3</div>
              <p className="text-sm text-gray-600">Open</p>
            </div>
          </div>
        </div>
        
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-white/50 rounded-lg">
              <div className="pulse-dot bg-red-500"></div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">Database Connection Pool Exhausted</h4>
                <p className="text-sm text-gray-600">5 minutes ago</p>
              </div>
              <div className="status-badge bg-red-100 text-red-800">Critical</div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 bg-white/50 rounded-lg">
              <div className="pulse-dot bg-yellow-500"></div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">High Memory Usage on Web Servers</h4>
                <p className="text-sm text-gray-600">12 minutes ago</p>
              </div>
              <div className="status-badge bg-yellow-100 text-yellow-800">High</div>
            </div>
            
            <div className="flex items-center space-x-4 p-4 bg-white/50 rounded-lg">
              <div className="pulse-dot bg-green-500"></div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">SSL Certificate Renewed Successfully</h4>
                <p className="text-sm text-gray-600">1 hour ago</p>
              </div>
              <div className="status-badge bg-green-100 text-green-800">Resolved</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/showcase" element={<ComponentShowcase />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App