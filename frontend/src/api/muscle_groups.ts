import { api } from './client'
import type { MuscleGroup, MuscleGroupVolume } from '@/types'

export async function getMuscleGroups(): Promise<MuscleGroup[]> {
  return api.get<MuscleGroup[]>('/muscle_groups')
}

export async function getMuscleGroupVolume(params: {
  date_from?: string
  date_to?: string
} = {}): Promise<MuscleGroupVolume[]> {
  const p = new URLSearchParams()
  if (params.date_from) p.set('date_from', params.date_from)
  if (params.date_to) p.set('date_to', params.date_to)
  return api.get<MuscleGroupVolume[]>(`/muscle_groups/volume?${p}`)
}
