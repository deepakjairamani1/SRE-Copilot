import { Link } from 'react-router-dom'
import { Header } from '../components/layout/Header'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { AlertTriangle, Home, Search } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-16">
        <Card className="max-w-2xl mx-auto text-center">
          <div className="py-12">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-warning/10 mb-6">
              <AlertTriangle className="w-12 h-12 text-warning" />
            </div>
            
            <h1 className="text-6xl font-bold text-text-primary mb-4">404</h1>
            <h2 className="text-2xl font-bold text-text-primary mb-3">
              Page Not Found
            </h2>
            <p className="text-text-secondary text-lg mb-8">
              The page you're looking for doesn't exist or has been moved.
            </p>
            
            <div className="flex items-center justify-center gap-4">
              <Link to="/">
                <Button size="lg">
                  <Home className="w-5 h-5" />
                  Back to Dashboard
                </Button>
              </Link>
              <Link to="/incidents">
                <Button size="lg" variant="secondary">
                  <Search className="w-5 h-5" />
                  View Incidents
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </main>
    </div>
  )
}
