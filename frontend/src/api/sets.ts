import { api } from './client'
import type { Set } from '@/types'

export async function createSet(data: {
  workout_exercise_id: string
  set_number: number
  reps: number
  weight: number
}): Promise<Set> {
  return api.post<Set>('/sets', data)
}

export async function updateSet(
  id: string,
  data: { reps?: number; weight?: number; set_number?: number }
): Promise<Set> {
  return api.patch<Set>(`/sets/${id}`, data)
}

export async function deleteSet(id: string): Promise<void> {
  return api.delete(`/sets/${id}`)
}
