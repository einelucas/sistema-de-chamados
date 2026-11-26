import type { User } from '~/types/user'
export function validateSessionUser(value:unknown):User{
  if(!value||typeof value!=='object')throw new Error('Resposta de autenticação inválida. Tente novamente.')
  const u=value as Partial<User>
  if(typeof u.id!=='number'||typeof u.email!=='string'||typeof u.name!=='string'||typeof u.must_change_password!=='boolean'||!['ADMIN','ANALYST','USER'].includes(u.role??'')||u.is_active!==true)throw new Error('Resposta de autenticação inválida. Tente novamente.')
  return u as User
}
