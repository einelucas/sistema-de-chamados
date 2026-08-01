// Composable central de chamadas à API de solicitações.
import type { PaginatedResponse, MessageResponse } from '~/types/api'
import type {
  RequestItem,
  RequestListItem,
  RequestCreatePayload,
  RequestUpdatePayload,
  RequestFilters,
  RequestStatus,
  RequestPriority,
} from '~/types/request'

export function useRequests() {
  const { $api } = useNuxtApp()

  function listRequests(filters: RequestFilters) {
    const query: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(filters)) {
      if (value !== undefined && value !== '') query[key] = value
    }
    return $api<PaginatedResponse<RequestListItem>>('/requests', { query })
  }

  function getRequest(id: number) {
    return $api<RequestItem>(`/requests/${id}`)
  }

  function createRequest(payload: RequestCreatePayload) {
    return $api<RequestItem>('/requests', { method: 'POST', body: payload })
  }

  function updateRequest(id: number, payload: RequestUpdatePayload) {
    return $api<RequestItem>(`/requests/${id}`, { method: 'PUT', body: payload })
  }

  function deleteRequest(id: number) {
    return $api<MessageResponse>(`/requests/${id}`, { method: 'DELETE' })
  }

  function changeStatus(id: number, status: RequestStatus) {
    return $api<RequestItem>(`/requests/${id}/status`, { method: 'PATCH', body: { status } })
  }

  function changePriority(id: number, priority: RequestPriority) {
    return $api<RequestItem>(`/requests/${id}/priority`, { method: 'PATCH', body: { priority } })
  }

  function changeAssignee(id: number, assignee_id: number | null) {
    return $api<RequestItem>(`/requests/${id}/assignee`, { method: 'PATCH', body: { assignee_id } })
  }

  return {
    listRequests,
    getRequest,
    createRequest,
    updateRequest,
    deleteRequest,
    changeStatus,
    changePriority,
    changeAssignee,
  }
}
