import { api } from './client'
import type { WorkoutExercise } from '@/types'

export async function createWorkoutExercise(
  workoutId: string,
  data: { exercise_id: string; order: number }
): Promise<WorkoutExercise> {
  return api.post<WorkoutExercise>(`/workouts/${workoutId}/exercises`, data)
}

export async function deleteWorkoutExercise(
  workoutId: string,
  workoutExerciseId: string
): Promise<void> {
  return api.delete(`/workouts/${workoutId}/exercises/${workoutExerciseId}`)
}
