// Composable de chamadas à API administrativa de usuários.
import type { MessageResponse, PaginatedResponse } from '~/types/api'
import type { User, UserCreatePayload, UserUpdatePayload } from '~/types/user'

export function useUsers() {
  const { $api } = useNuxtApp()

  function listUsers(page = 1, pageSize = 20) {
    return $api<PaginatedResponse<User>>('/users', { query: { page, page_size: pageSize } })
  }

  function getUser(id: number) {
    return $api<User>(`/users/${id}`)
  }

  function createUser(payload: UserCreatePayload) {
    return $api<User>('/users', { method: 'POST', body: payload })
  }

  function updateUser(id: number, payload: UserUpdatePayload) {
    return $api<User>(`/users/${id}`, { method: 'PUT', body: payload })
  }

  function deleteUser(id: number) {
    return $api<MessageResponse>(`/users/${id}`, { method: 'DELETE' })
  }

  function resetPassword(id: number, newPassword: string) {
    return $api<User>(`/users/${id}/reset-password`, { method: 'POST', body: { new_password: newPassword } })
  }

  function activateUser(id: number) {
    return $api<User>(`/users/${id}/activate`, { method: 'POST' })
  }

  function deactivateUser(id: number) {
    return $api<User>(`/users/${id}/deactivate`, { method: 'POST' })
  }

  return { listUsers, getUser, createUser, updateUser, deleteUser, resetPassword, activateUser, deactivateUser }
}
