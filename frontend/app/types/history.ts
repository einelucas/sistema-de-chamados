// Tipos relacionados ao histórico de alterações de uma solicitação.
import type { User } from './user'

export type HistoryAction =
  | 'CRIACAO'
  | 'ALTERACAO_STATUS'
  | 'ALTERACAO_PRIORIDADE'
  | 'MUDANCA_RESPONSAVEL'
  | 'EDICAO_DADOS'
  | 'CONCLUSAO'
  | 'CANCELAMENTO'
  | 'COMENTARIO_ADICIONADO'
  | 'ANEXO_ADICIONADO'

export interface HistoryEntry {
  id: number
  action: HistoryAction
  previous_value: string | null
  new_value: string | null
  user: User
  created_at: string
}

export const HISTORY_ACTION_LABELS: Record<HistoryAction, string> = {
  CRIACAO: 'Solicitação criada',
  ALTERACAO_STATUS: 'Status alterado',
  ALTERACAO_PRIORIDADE: 'Prioridade alterada',
  MUDANCA_RESPONSAVEL: 'Responsável alterado',
  EDICAO_DADOS: 'Dados editados',
  CONCLUSAO: 'Solicitação concluída',
  CANCELAMENTO: 'Solicitação cancelada',
  COMENTARIO_ADICIONADO: 'Comentário adicionado',
  ANEXO_ADICIONADO: 'Anexo adicionado',
}
