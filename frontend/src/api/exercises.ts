import { api } from './client'
import type { Exercise, ExercisePR, ExerciseProgression, ExerciseFrequency } from '@/types'

export async function getExercises(params: {
  muscle_group_name?: string
  page?: number
  limit?: number
} = {}): Promise<Exercise[]> {
  const p = new URLSearchParams()
  if (params.muscle_group_name) p.set('muscle_group_name', params.muscle_group_name)
  p.set('page', String(params.page ?? 1))
  p.set('limit', String(params.limit ?? 50))
  return api.get<Exercise[]>(`/exercises?${p}`)
}

export async function getExercise(id: string): Promise<Exercise> {
  return api.get<Exercise>(`/exercises/${id}`)
}

export async function createExercise(data: {
  name: string
  muscle_group_names?: string[]
}): Promise<Exercise> {
  return api.post<Exercise>('/exercises', data)
}

export async function updateExercise(id: string, data: {
  name?: string
  muscle_group_names?: string[]
}): Promise<Exercise> {
  return api.patch<Exercise>(`/exercises/${id}`, data)
}

export async function deleteExercise(id: string): Promise<void> {
  return api.delete(`/exercises/${id}`)
}

export async function getExercisePRs(id: string): Promise<ExercisePR[]> {
  return api.get<ExercisePR[]>(`/exercises/${id}/pr`)
}

export async function getExerciseProgress(id: string, params: {
  date_from?: string
  date_to?: string
} = {}): Promise<ExerciseProgression[]> {
  const p = new URLSearchParams()
  if (params.date_from) p.set('date_from', params.date_from)
  if (params.date_to) p.set('date_to', params.date_to)
  return api.get<ExerciseProgression[]>(`/exercises/${id}/progress?${p}`)
}

export async function getExerciseFrequency(params: {
  limit?: number
  date_from?: string
  date_to?: string
} = {}): Promise<ExerciseFrequency[]> {
  const p = new URLSearchParams()
  if (params.limit) p.set('limit', String(params.limit))
  if (params.date_from) p.set('date_from', params.date_from)
  if (params.date_to) p.set('date_to', params.date_to)
  return api.get<ExerciseFrequency[]>(`/exercises/frequency?${p}`)
}
