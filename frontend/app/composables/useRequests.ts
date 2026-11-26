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

  function changeStatus(id: number, status: RequestStatus, expected_version?:number) {
    return $api<RequestItem>(`/requests/${id}/status`, { method: 'PATCH', body: { status, expected_version } })
  }

  function changePriority(id: number, priority: RequestPriority, expected_version?:number) {
    return $api<RequestItem>(`/requests/${id}/priority`, { method: 'PATCH', body: { priority, expected_version } })
  }

  function changeAssignee(id: number, assignee_id: number | null, expected_version?:number) {
    return $api<RequestItem>(`/requests/${id}/assignee`, { method: 'PATCH', body: { assignee_id, expected_version } })
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
