// Tipos relacionados a solicitações, espelhando os schemas do backend.
import type { User } from './user'

export type RequestCategory = 'TI' | 'MANUTENCAO' | 'RH' | 'COMPRAS' | 'ADMINISTRATIVO' | 'OUTROS'
export type RequestPriority = 'BAIXA' | 'MEDIA' | 'ALTA' | 'CRITICA'
export type RequestStatus = 'ABERTA' | 'EM_ANDAMENTO' | 'AGUARDANDO' | 'CONCLUIDA' | 'CANCELADA'

export interface RequestItem {
  id: number
  title: string
  description: string
  category: RequestCategory
  priority: RequestPriority
  status: RequestStatus
  requester: User
  assignee: User | null
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export type RequestListItem = Omit<RequestItem, 'description' | 'completed_at'>

export interface RequestCreatePayload {
  title: string
  description: string
  category: RequestCategory
  priority: RequestPriority
  due_date?: string | null
}

export interface RequestUpdatePayload {
  title?: string
  description?: string
  category?: RequestCategory
  due_date?: string | null
}

export interface RequestFilters {
  page?: number
  page_size?: number
  search?: string
  status?: RequestStatus | ''
  priority?: RequestPriority | ''
  category?: RequestCategory | ''
  requester_id?: number
  assignee_id?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export const CATEGORY_LABELS: Record<RequestCategory, string> = {
  TI: 'TI',
  MANUTENCAO: 'Manutenção',
  RH: 'RH',
  COMPRAS: 'Compras',
  ADMINISTRATIVO: 'Administrativo',
  OUTROS: 'Outros',
}

export const PRIORITY_LABELS: Record<RequestPriority, string> = {
  BAIXA: 'Baixa',
  MEDIA: 'Média',
  ALTA: 'Alta',
  CRITICA: 'Crítica',
}

export const STATUS_LABELS: Record<RequestStatus, string> = {
  ABERTA: 'Aberta',
  EM_ANDAMENTO: 'Em andamento',
  AGUARDANDO: 'Aguardando',
  CONCLUIDA: 'Concluída',
  CANCELADA: 'Cancelada',
}
