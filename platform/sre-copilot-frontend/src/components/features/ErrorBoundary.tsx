import React from 'react'
import { Card } from '../ui/Card'
import { Button } from '../ui/Button'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: React.ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6">
          <Card className="max-w-lg">
            <div className="text-center py-8">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-danger/10 mb-6">
                <AlertTriangle className="w-10 h-10 text-danger" />
              </div>
              
              <h1 className="text-2xl font-bold text-text-primary mb-3">
                Something Went Wrong
              </h1>
              
              <p className="text-text-secondary mb-6">
                An unexpected error occurred. Please try refreshing the page.
              </p>
              
              {this.state.error && (
                <div className="mb-6 p-4 bg-red-50 rounded-xl border border-red-200 text-left">
                  <p className="text-sm font-mono text-red-700">
                    {this.state.error.message}
                  </p>
                </div>
              )}
              
              <Button
                onClick={() => window.location.reload()}
                size="lg"
              >
                <RefreshCw className="w-5 h-5" />
                Refresh Page
              </Button>
            </div>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
