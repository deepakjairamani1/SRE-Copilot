import { Card } from '../ui/Card'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'

interface MetricChartProps {
  title: string
  data: Array<{ time: string; value: number }>
  color: string
  unit?: string
  type?: 'line' | 'area'
}

export function MetricChart({ title, data, color, unit = '', type = 'area' }: MetricChartProps) {
  // Generate mock historical data for demo
  const historicalData = Array.from({ length: 20 }, (_, i) => ({
    time: `${20 - i}m`,
    value: Math.random() * 100
  }))

  const chartData = data.length > 0 ? data : historicalData

  return (
    <Card className="hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <TrendingUp className="w-4 h-4" />
          <span>Last 20min</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        {type === 'area' ? (
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="time" 
              stroke="#6B7280" 
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280" 
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `${value}${unit}`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: 'none',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
              formatter={(value: number) => [`${value.toFixed(2)}${unit}`, title]}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              strokeWidth={2}
              fill={`url(#gradient-${color})`}
              animationDuration={1000}
            />
          </AreaChart>
        ) : (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="time" 
              stroke="#6B7280" 
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6B7280" 
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `${value}${unit}`}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: 'none',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
              formatter={(value: number) => [`${value.toFixed(2)}${unit}`, title]}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              strokeWidth={3}
              dot={false}
              animationDuration={1000}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </Card>
  )
}