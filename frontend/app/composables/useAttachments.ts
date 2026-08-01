// Composable de chamadas à API de anexos.
import type { MessageResponse } from '~/types/api'
import type { Attachment } from '~/types/attachment'

export function useAttachments() {
  const { $api } = useNuxtApp()
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  function listAttachments(requestId: number) {
    return $api<Attachment[]>(`/requests/${requestId}/attachments`)
  }

  function uploadAttachment(requestId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return $api<Attachment>(`/requests/${requestId}/attachments`, { method: 'POST', body: formData })
  }

  function deleteAttachment(attachmentId: number) {
    return $api<MessageResponse>(`/attachments/${attachmentId}`, { method: 'DELETE' })
  }

  function downloadUrl(attachmentId: number) {
    return `${config.public.apiBase}/attachments/${attachmentId}/download`
  }

  async function downloadAttachment(attachmentId: number, filename: string) {
    const blob = await $fetch<Blob>(downloadUrl(attachmentId), {
      responseType: 'blob',
      headers: authStore.token ? { Authorization: `Bearer ${authStore.token}` } : undefined,
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
  }

  return { listAttachments, uploadAttachment, deleteAttachment, downloadAttachment }
}
