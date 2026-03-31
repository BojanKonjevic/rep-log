import { api, setTokens, clearTokens, getRefreshToken } from './client'
import type { User, Token } from '@/types'

export async function login(email: string, password: string): Promise<Token> {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)

  const res = await fetch('/api/auth/token', {
    method: 'POST',
    body: form,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Invalid credentials' }))
    throw new Error(error.detail ?? 'Login failed')
  }

  const token: Token = await res.json()
  setTokens(token.access_token, token.refresh_token)
  return token
}

export async function register(email: string, password: string): Promise<User> {
  return api.post<User>('/auth/register', { email, password })
}

export async function getMe(): Promise<User> {
  return api.get<User>('/auth/me')
}

export async function logout(): Promise<void> {
  const refresh_token = getRefreshToken()
  if (refresh_token) {
    await api.post('/auth/logout', { refresh_token }).catch(() => {})
  }
  clearTokens()
}
