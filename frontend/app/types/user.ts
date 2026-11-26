// Tipos relacionados a usuários, espelhando os schemas do backend.
export type UserRole = 'ADMIN' | 'ANALYST' | 'USER'
export type ThemePreference = 'light' | 'dark'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  is_active: boolean
  must_change_password: boolean
  theme_preference: ThemePreference
  created_at: string
  updated_at: string
}

export interface UserCreatePayload {
  name: string
  email: string
  password: string
  role: UserRole
}

export interface UserUpdatePayload {
  name?: string
  email?: string
  role?: UserRole
  is_active?: boolean
}
