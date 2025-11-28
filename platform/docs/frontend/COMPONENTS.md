# Frontend Components Documentation

Complete reference for all React components in the Albeyla frontend.

## Table of Contents

- [UI Components](#ui-components)
- [Layout Components](#layout-components)
- [Feature Components](#feature-components)
- [Pages](#pages)
- [Hooks](#hooks)
- [Utilities](#utilities)

---

## UI Components

### Card
**Location:** `src/components/ui/Card.tsx`

Reusable card container with glassmorphism styling.

**Props:**
```typescript
interface CardProps {
  variant?: 'glass' | 'solid' | 'neumorphic'
  children: React.ReactNode
  hoverable?: boolean  // Enables hover animations
  className?: string
}
```

**Usage:**
```tsx
<Card variant="glass" hoverable>
  <h2>Card Title</h2>
  <p>Card content</p>
</Card>
```

**Variants:**
- `glass` - Glassmorphism with backdrop blur (default)
- `solid` - Solid white background with shadow
- `neumorphic` - Neumorphic design with soft shadows

---

### Badge
**Location:** `src/components/ui/Badge.tsx`

Status badge with color variants.

**Props:**
```typescript
interface BadgeProps {
  variant?: 'ok' | 'warning' | 'critical' | 'low' | 'medium' | 'high'
  withDot?: boolean  // Shows pulsing dot
  children: React.ReactNode
  className?: string
}
```

**Usage:**
```tsx
<Badge variant="critical" withDot>
  Critical
</Badge>
```

**Color Mapping:**
- `ok` - Green (#10B981)
- `warning` - Yellow (#F59E0B)
- `critical` - Red (#EF4444)
- `low` - Green
- `medium` - Orange (#F97316)
- `high` - Amber (#F59E0B)

---

### Button
**Location:** `src/components/ui/Button.tsx`

Customizable button component.

**Props:**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  children: React.ReactNode
  onClick?: () => void
  className?: string
}
```

**Usage:**
```tsx
<Button variant="primary" size="lg" loading={isPending}>
  Submit
</Button>
```

**Sizes:**
- `sm` - Small (px-3 py-1.5, text-sm)
- `md` - Medium (px-4 py-2, text-base) - default
- `lg` - Large (px-6 py-3, text-lg)

---

### StatCard
**Location:** `src/components/ui/StatCard.tsx`

Displays metric statistics with trend indicators.

**Props:**
```typescript
interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  color: string  // Hex color
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
  className?: string
}
```

**Usage:**
```tsx
<StatCard
  title="Total Incidents"
  value={42}
  icon={<Activity />}
  color="#6366F1"
  trend={{ value: 12, direction: 'down' }}
/>
```

---

### LoadingSpinner
**Location:** `src/components/ui/LoadingSpinner.tsx`

Animated loading spinner.

**Props:**
```typescript
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  message?: string
}
```

**Usage:**
```tsx
<LoadingSpinner size="lg" message="Loading data..." />
```

---

### SkeletonCard
**Location:** `src/components/ui/SkeletonCard.tsx`

Skeleton loader for card content.

**Props:**
```typescript
interface SkeletonCardProps {
  className?: string
  lines?: number  // Number of skeleton lines (default: 3)
}
```

**Usage:**
```tsx
<SkeletonCard lines={4} />
```

---

### ProgressBar
**Location:** `src/components/ui/ProgressBar.tsx`

Animated progress bar.

**Props:**
```typescript
interface ProgressBarProps {
  progress: number  // 0-100
  className?: string
  color?: string  // Hex color (default: #6366F1)
  showLabel?: boolean
}
```

**Usage:**
```tsx
<ProgressBar progress={75} color="#10B981" showLabel />
```

---

### PageTransition
**Location:** `src/components/ui/PageTransition.tsx`

Wrapper for smooth page transitions.

**Props:**
```typescript
interface PageTransitionProps {
  children: React.ReactNode
}
```

**Usage:**
```tsx
<PageTransition>
  <YourPageContent />
</PageTransition>
```

---

### ToastProvider
**Location:** `src/components/ui/Toast.tsx`

Toast notification provider using Sonner.

**Usage:**
```tsx
// In App.tsx
<ToastProvider />

// In components
import { toast } from 'sonner'

toast.success('Success message')
toast.error('Error message', { description: 'Details' })
toast.loading('Loading...', { id: 'unique-id' })
```

---

## Layout Components

### Header
**Location:** `src/components/layout/Header.tsx`

Main navigation header with glassmorphism.

**Features:**
- Logo and app name (Albeyla)
- Navigation links (Dashboard, Incidents, Investigate)
- Notification bell with indicator
- Settings button

**Usage:**
```tsx
<Header />
```

---

### Sidebar
**Location:** `src/components/layout/Sidebar.tsx`

Side navigation panel.

**Features:**
- Navigation menu items
- Active route highlighting
- Glassmorphism styling

**Usage:**
```tsx
<Sidebar />
```

---

## Feature Components

### MetricChart
**Location:** `src/components/features/MetricChart.tsx`

Chart component for metric visualization using Recharts.

**Props:**
```typescript
interface MetricChartProps {
  title: string
  data: Array<{ timestamp: string; value: number }>
  color: string
  unit: string
  type?: 'area' | 'line'
}
```

**Usage:**
```tsx
<MetricChart
  title="CPU Usage"
  data={cpuData}
  color="#6366F1"
  unit="%"
  type="area"
/>
```

---

### RemediationActions
**Location:** `src/components/features/RemediationActions.tsx`

Displays remediation steps with copy-to-clipboard.

**Props:**
```typescript
interface RemediationActionsProps {
  immediateActions: Array<{
    action: string
    command: string
    estimated_time: string
    expected_impact: string
  }>
  permanentFixes: Array<{
    fix: string
    priority: string
  }>
}
```

**Usage:**
```tsx
<RemediationActions
  immediateActions={incident.rca_report.remediation.immediate_actions}
  permanentFixes={incident.rca_report.remediation.permanent_fixes}
/>
```

**Features:**
- Copy command to clipboard with toast feedback
- Color-coded sections (red for immediate, green for permanent)
- Priority badges

---

### IncidentTimeline
**Location:** `src/components/features/IncidentTimeline.tsx`

Chronological event timeline visualization.

**Props:**
```typescript
interface IncidentTimelineProps {
  timeline: Array<{
    timestamp: string
    event: string
    source: string
  }>
}
```

**Usage:**
```tsx
<IncidentTimeline timeline={incident.rca_report.timeline} />
```

**Features:**
- Gradient timeline visualization
- Source badges (prometheus, loki, jaeger)
- Chronological ordering

---

### ErrorBoundary
**Location:** `src/components/features/ErrorBoundary.tsx`

React error boundary for catching errors.

**Usage:**
```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

**Features:**
- Catches React errors
- Displays friendly error page
- Shows error message
- Refresh button

---

## Pages

### Dashboard
**Location:** `src/pages/Dashboard.tsx`

Main monitoring dashboard.

**Features:**
- Incident statistics cards
- Host metrics (CPU, Memory, Network)
- Application metrics (Error Rate, Latency, Requests)
- Metric trend charts
- Recent incidents list

**Route:** `/`

---

### IncidentsList
**Location:** `src/pages/IncidentsList.tsx`

Comprehensive incidents list with filtering.

**Features:**
- Search by ID, title, or service
- Filter by severity, status, service
- Sortable columns (severity, date, confidence)
- Quick filter stat boxes
- CSV export
- Confidence progress bars

**Route:** `/incidents`

---

### IncidentDetails
**Location:** `src/pages/IncidentDetails.tsx`

Detailed incident view with RCA report.

**Features:**
- Executive summary
- Investigation timeline (agentic loop)
- Root cause analysis with evidence
- Remediation actions
- Event timeline
- Technical details
- Impact assessment
- Contributing factors
- Potential causes with probabilities
- Prevention measures
- Confidence analysis
- Learning metadata

**Route:** `/incidents/:incident_id`

---

### Investigate
**Location:** `src/pages/Investigate.tsx`

Trigger new RCA investigations.

**Features:**
- Service selection (predefined + custom)
- Investigation info panel
- Real-time progress tracking
- Success state with metrics
- Auto-redirect to incident details
- Toast notifications

**Route:** `/investigate`

---

### NotFound
**Location:** `src/pages/NotFound.tsx`

404 error page.

**Features:**
- Friendly error message
- Navigation buttons
- Glassmorphism design

**Route:** `*` (catch-all)

---

## Hooks

### useMetrics
**Location:** `src/hooks/useMetrics.ts`

Fetches observability metrics.

**Usage:**
```typescript
const { data: metrics, isLoading, error } = useMetrics()
```

**Returns:**
```typescript
{
  host_metrics: {
    cpu_usage_percent: { current: number, avg: number, status: string }
    memory_usage_percent: { current: number, avg: number, status: string }
    // ... more metrics
  }
  otlp_metrics: {
    http_error_rate_percent: { current: number, status: string }
    http_latency_p95_ms: { current: number, status: string }
    // ... more metrics
  }
}
```

**Polling:** 5 minutes (300000ms)

---

### useIncidents
**Location:** `src/hooks/useIncidents.ts`

Fetches incidents list.

**Usage:**
```typescript
const { data: incidents, isLoading } = useIncidents({
  severity: 'critical',
  status: 'open',
  service: 'api-gateway',
  limit: 10
})
```

**Parameters:**
```typescript
{
  severity?: 'critical' | 'high' | 'medium' | 'low'
  status?: 'open' | 'resolved'
  service?: string
  limit?: number
}
```

**Polling:** 5 minutes

---

### useIncidentStats
**Location:** `src/hooks/useIncidents.ts`

Fetches incident statistics.

**Usage:**
```typescript
const { data: stats } = useIncidentStats()
```

**Returns:**
```typescript
{
  total_incidents: number
  by_severity: {
    critical: number
    high: number
    medium: number
    low: number
  }
  by_service: {
    [service: string]: number
  }
}
```

---

### useIncidentDetails
**Location:** `src/hooks/useIncidents.ts`

Fetches detailed incident information.

**Usage:**
```typescript
const { data: incident, isLoading } = useIncidentDetails(incident_id)
```

**Returns:** Complete incident object with RCA report

---

### useTriggerInvestigation
**Location:** `src/hooks/useIncidents.ts`

Triggers new RCA investigation.

**Usage:**
```typescript
const { mutate: triggerInvestigation, isPending, data, error } = useTriggerInvestigation()

triggerInvestigation('core-athenamind', {
  onSuccess: (data) => {
    console.log('Incident created:', data.incident_id)
  },
  onError: (error) => {
    console.error('Investigation failed:', error)
  }
})
```

---

### useLogs
**Location:** `src/hooks/useLogs.ts`

Fetches log data from Loki.

**Usage:**
```typescript
const { data: logs, isLoading } = useLogs()
```

**Polling:** 5 minutes

---

### useTraces
**Location:** `src/hooks/useTraces.ts`

Fetches trace data from Jaeger.

**Usage:**
```typescript
const { data: traces, isLoading } = useTraces()
```

**Polling:** 5 minutes

---

## Utilities

### formatDate
**Location:** `src/lib/utils.ts`

Formats ISO date string to readable format.

**Usage:**
```typescript
formatDate('2024-01-15T10:30:00Z')
// Returns: "Jan 15, 2024 10:30 AM"
```

---

### formatDuration
**Location:** `src/lib/utils.ts`

Formats seconds to human-readable duration.

**Usage:**
```typescript
formatDuration(125)  // "2m 5s"
formatDuration(45)   // "45s"
```

---

### formatCost
**Location:** `src/lib/utils.ts`

Formats USD cost with proper decimals.

**Usage:**
```typescript
formatCost(0.0234)  // "$0.0234"
formatCost(1.5)     // "$1.50"
```

---

### cn (classNames)
**Location:** `src/lib/utils.ts`

Merges Tailwind classes with clsx.

**Usage:**
```typescript
cn('base-class', condition && 'conditional-class', className)
```

---

## Configuration

### SEVERITY_CONFIG
**Location:** `src/config.ts`

Severity level configuration.

```typescript
{
  critical: { label: 'Critical', color: '#EF4444' }
  high: { label: 'High', color: '#F59E0B' }
  medium: { label: 'Medium', color: '#F97316' }
  low: { label: 'Low', color: '#10B981' }
}
```

---

### API_BASE_URL
**Location:** `src/config.ts`

Backend API base URL: `http://localhost:7474`

---

## Types

### Incident
**Location:** `src/types/index.ts`

```typescript
interface Incident {
  id: number
  incident_id: string
  service: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'resolved'
  title: string
  root_cause: string
  confidence_score: number
  detected_at: string
  resolved_at?: string
  duration_seconds: number
  cost_usd: number
  tokens_used: number
  investigation_steps: InvestigationStep[]
  rca_report: RCAReport
  observability_data: any
}
```

---

### RCAReport
**Location:** `src/types/index.ts`

```typescript
interface RCAReport {
  executive_summary: {
    title: string
    severity: string
    impact: string
    user_impact: string
  }
  timeline: Array<{
    timestamp: string
    event: string
    source: string
  }>
  root_cause: {
    primary_cause: string
    contributing_factors: string[]
    evidence: Array<{
      type: string
      description: string
      value: string
    }>
    confidence_score: number
  }
  technical_details: {
    affected_components: Array<{
      component: string
      status: string
    }>
    metrics_snapshot: Record<string, number>
  }
  impact_assessment: {
    severity: string
    users_affected: string
  }
  remediation: {
    immediate_actions: Array<{
      action: string
      command: string
      estimated_time: string
      expected_impact: string
    }>
    permanent_fixes: Array<{
      fix: string
      priority: string
    }>
  }
  prevention: {
    code_changes: string[]
    monitoring_enhancements: string[]
  }
  potential_causes: Array<{
    hypothesis: string
    probability: number
    evidence: string[]
  }>
  confidence: {
    overall_score: number
    uncertainties: string[]
    recommendation: string
  }
  learning_metadata: {
    worth_learning: boolean
    reason: string
    keywords: string[]
  }
}
```

---

## Styling

### Theme Colors

```css
--primary: #6366F1 (Indigo)
--accent: #8B5CF6 (Purple)
--success: #10B981 (Green)
--warning: #F59E0B (Amber)
--danger: #EF4444 (Red)
--text-primary: #1F2937 (Gray-900)
--text-secondary: #6B7280 (Gray-600)
--background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)
```

### Custom Classes

- `.glass-card` - Glassmorphism card
- `.status-badge` - Status badge styling
- `.pulse-dot` - Pulsing dot animation
- `.hover-lift` - Hover lift effect
- `.animate-shimmer` - Shimmer loading effect

---

## Best Practices

1. **Always use TypeScript types** for props and data
2. **Use React Query hooks** for data fetching
3. **Add loading states** with SkeletonCard or LoadingSpinner
4. **Show toast notifications** for user actions
5. **Handle errors gracefully** with try-catch and error states
6. **Use optional chaining** for nested data access
7. **Add fallback values** for null/undefined data
8. **Keep components small** and focused on single responsibility
9. **Use Tailwind classes** for styling consistency
10. **Add animations** with framer-motion for better UX
