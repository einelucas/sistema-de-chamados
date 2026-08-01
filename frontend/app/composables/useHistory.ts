// Composable de chamadas à API de histórico de uma solicitação.
import type { HistoryEntry } from '~/types/history'

export function useHistory() {
  const { $api } = useNuxtApp()

  function listHistory(requestId: number) {
    return $api<HistoryEntry[]>(`/requests/${requestId}/history`)
  }

  return { listHistory }
}
