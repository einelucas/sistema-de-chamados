// Composable de chamadas à API de comentários.
import type { MessageResponse } from '~/types/api'
import type { Comment } from '~/types/comment'

export function useComments() {
  const { $api } = useNuxtApp()

  function listComments(requestId: number) {
    return $api<Comment[]>(`/requests/${requestId}/comments`)
  }

  function createComment(requestId: number, content: string, public_reply = false) {
    return $api<Comment>(`/requests/${requestId}/comments`, { method: 'POST', body: { content, public_reply } })
  }

  function updateComment(commentId: number, content: string) {
    return $api<Comment>(`/comments/${commentId}`, { method: 'PUT', body: { content } })
  }

  function deleteComment(commentId: number) {
    return $api<MessageResponse>(`/comments/${commentId}`, { method: 'DELETE' })
  }

  return { listComments, createComment, updateComment, deleteComment }
}
