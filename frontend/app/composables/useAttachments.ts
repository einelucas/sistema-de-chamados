// Composable de chamadas à API de anexos.
import type { MessageResponse } from '~/types/api'
import type { Attachment } from '~/types/attachment'

export function useAttachments() {
  const { $api } = useNuxtApp()

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

  async function downloadAttachment(attachmentId: number, filename: string) {
    const blob=await $api<Blob>('/attachments/'+attachmentId+'/download',{responseType:'blob'})
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    setTimeout(()=>window.URL.revokeObjectURL(url),1000)
  }

  return { listAttachments, uploadAttachment, deleteAttachment, downloadAttachment }
}
