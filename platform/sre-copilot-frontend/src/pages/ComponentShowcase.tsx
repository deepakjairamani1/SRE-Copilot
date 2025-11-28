import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { StatCard } from '../components/ui/StatCard'
import { Header } from '../components/layout/Header'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Server,
  Zap,
  Users,
  Database
} from 'lucide-react'

export function ComponentShowcase() {
  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="container mx-auto px-6 py-8 space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Component Showcase</h1>
          <p className="text-gray-600">Testing all UI components with glassmorphism design</p>
        </div>

        {/* Cards Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card variant="glass">
              <h3 className="text-lg font-semibold mb-2">Glass Card</h3>
              <p className="text-gray-600">Glassmorphism effect with backdrop blur</p>
            </Card>
            
            <Card variant="solid">
              <h3 className="text-lg font-semibold mb-2">Solid Card</h3>
              <p className="text-gray-600">Traditional solid background card</p>
            </Card>
            
            <Card variant="neumorphic">
              <h3 className="text-lg font-semibold mb-2">Neumorphic Card</h3>
              <p className="text-gray-600">Soft shadow neumorphic design</p>
            </Card>
          </div>
        </section>

        {/* Badges Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Badges</h2>
          <Card>
            <div className="flex flex-wrap gap-4">
              <Badge variant="critical" withDot>Critical</Badge>
              <Badge variant="high" withDot>High</Badge>
              <Badge variant="medium" withDot>Medium</Badge>
              <Badge variant="low" withDot>Low</Badge>
              <Badge variant="ok" withDot>OK</Badge>
              <Badge variant="warning" withDot>Warning</Badge>
            </div>
            
            <div className="flex flex-wrap gap-4 mt-4">
              <Badge variant="critical">Critical</Badge>
              <Badge variant="high">High</Badge>
              <Badge variant="medium">Medium</Badge>
              <Badge variant="low">Low</Badge>
              <Badge variant="ok">OK</Badge>
              <Badge variant="warning">Warning</Badge>
            </div>
          </Card>
        </section>

        {/* Buttons Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Buttons</h2>
          <Card>
            <div className="space-y-4">
              <div className="flex flex-wrap gap-4">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="ghost">Ghost</Button>
              </div>
              
              <div className="flex flex-wrap gap-4">
                <Button variant="primary" size="sm">Small</Button>
                <Button variant="primary" size="md">Medium</Button>
                <Button variant="primary" size="lg">Large</Button>
              </div>
              
              <div className="flex flex-wrap gap-4">
                <Button variant="primary" loading>Loading</Button>
                <Button variant="secondary" disabled>Disabled</Button>
              </div>
            </div>
          </Card>
        </section>

        {/* Stat Cards Section */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Stat Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="System Uptime"
              value="99.9%"
              icon={<Activity className="w-6 h-6" />}
              trend={{ value: 0.1, direction: 'up' }}
              color="#10B981"
            />
            
            <StatCard
              title="Active Incidents"
              value={3}
              icon={<AlertTriangle className="w-6 h-6" />}
              trend={{ value: 50, direction: 'up' }}
              color="#EF4444"
            />
            
            <StatCard
              title="Response Time"
              value="245ms"
              icon={<Zap className="w-6 h-6" />}
              trend={{ value: 5.2, direction: 'down' }}
              color="#F59E0B"
            />
            
            <StatCard
              title="Services Online"
              value={12}
              icon={<Server className="w-6 h-6" />}
              trend={{ value: 0, direction: 'neutral' }}
              color="#6366F1"
            />
          </div>
        </section>

        {/* Complex Layout Example */}
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Complex Layout</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Incidents</h3>
                <Badge variant="critical" withDot>3 Active</Badge>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <div>
                      <p className="font-medium text-gray-900">Database Connection Pool</p>
                      <p className="text-sm text-gray-600">5 minutes ago</p>
                    </div>
                  </div>
                  <Badge variant="critical">Critical</Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-yellow-500" />
                    <div>
                      <p className="font-medium text-gray-900">High Memory Usage</p>
                      <p className="text-sm text-gray-600">12 minutes ago</p>
                    </div>
                  </div>
                  <Badge variant="high">High</Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <div>
                      <p className="font-medium text-gray-900">SSL Certificate Renewed</p>
                      <p className="text-sm text-gray-600">1 hour ago</p>
                    </div>
                  </div>
                  <Badge variant="ok">Resolved</Badge>
                </div>
              </div>
            </Card>
            
            <Card>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <Button variant="primary" className="h-16 flex-col">
                  <Database className="w-6 h-6 mb-1" />
                  <span className="text-sm">Check DB</span>
                </Button>
                
                <Button variant="secondary" className="h-16 flex-col">
                  <Server className="w-6 h-6 mb-1" />
                  <span className="text-sm">Restart Services</span>
                </Button>
                
                <Button variant="ghost" className="h-16 flex-col">
                  <Users className="w-6 h-6 mb-1" />
                  <span className="text-sm">Team Chat</span>
                </Button>
                
                <Button variant="danger" className="h-16 flex-col">
                  <AlertTriangle className="w-6 h-6 mb-1" />
                  <span className="text-sm">Emergency</span>
                </Button>
              </div>
            </Card>
          </div>
        </section>
      </div>
    </div>
  )
}