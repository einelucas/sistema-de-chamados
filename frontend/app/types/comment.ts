// Tipos relacionados a comentários de uma solicitação.
import type { User } from './user'

export interface Comment {
  id: number
  public_reply: boolean
  content: string
  author: User
  request_id: number
  created_at: string
  updated_at: string
}
