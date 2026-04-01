import { api } from './client'
import type { Workout, SetCountPerWorkout } from '@/types'

export interface WorkoutFilters {
  search?: string
  date_from?: string
  date_to?: string
  page?: number
  limit?: number
}

export async function getWorkouts(filters: WorkoutFilters = {}): Promise<{ workouts: Workout[], total: number }> {
  const params = new URLSearchParams()
  if (filters.search) params.set('search', filters.search)
  if (filters.date_from) params.set('date_from', filters.date_from)
  if (filters.date_to) params.set('date_to', filters.date_to)
  params.set('page', String(filters.page ?? 1))
  params.set('limit', String(filters.limit ?? 20))

  const res = await fetch(`/api/workouts?${params}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
  })
  const total = Number(res.headers.get('x-total-count') ?? 0)
  const workouts: Workout[] = await res.json()
  return { workouts, total }
}

export async function getWorkout(id: string): Promise<Workout> {
  return api.get<Workout>(`/workouts/${id}`)
}

export async function createWorkout(data: {
  name?: string
  notes?: string
  workout_date?: string
}): Promise<Workout> {
  return api.post<Workout>('/workouts', data)
}

export async function updateWorkout(id: string, data: {
  name?: string | null
  notes?: string | null
  workout_date?: string
}): Promise<Workout> {
  return api.patch<Workout>(`/workouts/${id}`, data)
}

export async function deleteWorkout(id: string): Promise<void> {
  return api.delete(`/workouts/${id}`)
}

export async function getStreak(): Promise<number> {
  return api.get<number>('/workouts/streak')
}

export async function getSetCounts(filters: { date_from?: string, date_to?: string } = {}): Promise<SetCountPerWorkout[]> {
  const params = new URLSearchParams()
  if (filters.date_from) params.set('date_from', filters.date_from)
  if (filters.date_to) params.set('date_to', filters.date_to)
  return api.get<SetCountPerWorkout[]>(`/workouts/setcounts?${params}`)
}
