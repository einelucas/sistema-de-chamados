// Extrai uma mensagem de erro legível a partir de erros retornados pelo $fetch/ofetch.
export function extractErrorMessage(error: unknown, fallback = 'Ocorreu um erro inesperado. Tente novamente.'): string {
  if (error && typeof error === 'object' && 'data' in error) {
    const data = (error as { data?: { detail?: unknown } }).data
    if (data?.detail) {
      if (typeof data.detail === 'string') return data.detail
      if (Array.isArray(data.detail)) {
        return data.detail.map((item: any) => item.msg).join(', ')
      }
    }
  }
  if (error instanceof Error) return error.message
  return fallback
}
