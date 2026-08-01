// Composable de chamada à API do dashboard.
import type { DashboardSummary } from '~/types/dashboard'

export function useDashboard() {
  const { $api } = useNuxtApp()

  function getSummary() {
    return $api<DashboardSummary>('/dashboard/summary')
  }

  return { getSummary }
}
