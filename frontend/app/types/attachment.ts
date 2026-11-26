// Tipos relacionados a anexos de uma solicitação.
import type { User } from './user'

export interface Attachment {
  id: number
  request_id: number
  original_filename: string
  content_type: string
  size_bytes: number
  shared_with_customer:boolean
  uploaded_by: User
  created_at: string
}
