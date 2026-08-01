// Tipos relacionados ao resumo do dashboard.
import type { RequestListItem } from './request'

export interface CountByLabel {
  label: string
  total: number
}

export interface PeriodCount {
  period: string
  total: number
}

export interface DashboardSummary {
  total_requests: number
  open_requests: number
  in_progress_requests: number
  completed_requests: number
  overdue_requests: number
  by_priority: CountByLabel[]
  by_status: CountByLabel[]
  by_category: CountByLabel[]
  created_by_period: PeriodCount[]
  average_completion_hours: number | null
  recent_requests: RequestListItem[]
  generated_at: string
}
