// Funções utilitárias de formatação usadas em várias telas.
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}

export function formatDateOnly(value: string | null | undefined): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(new Date(value))
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function isOverdue(dueDate: string | null, status: string): boolean {
  if (!dueDate) return false
  if (status === 'CONCLUIDA' || status === 'CANCELADA') return false
  return new Date(dueDate).getTime() < Date.now()
}
