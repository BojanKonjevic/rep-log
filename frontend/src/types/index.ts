export interface User {
  id: string
  email: string
  is_active: boolean
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface MuscleGroup {
  id: string
  name: string
}

export interface Exercise {
  id: string
  name: string
  muscle_groups: MuscleGroup[]
}

export interface Set {
  id: string
  workout_exercise_id: string
  set_number: number
  reps: number
  weight: string
}

export interface WorkoutExercise {
  id: string
  workout_id: string
  order: number
  exercise: Exercise
  sets: Set[]
}

export interface Workout {
  id: string
  name: string | null
  notes: string | null
  workout_date: string
  exercises: WorkoutExercise[]
}

export interface Template {
  id: string
  name: string
  exercises: TemplateExercise[]
}

export interface TemplateExercise {
  id: string
  template_id: string
  order: number
  exercise: Exercise
}

export interface ExercisePR {
  reps: number
  weight: string
  estimated_1rm: string
  achieved_on: string
  workout_id: string
}

export interface ExerciseProgression {
  workout_id: string
  workout_date: string
  best_sets: {
    reps: number
    weight: string
    estimated_1rm: string
  }[]
}

export interface MuscleGroupVolume {
  muscle_group_id: string
  all_weeks: {
    week_start: string
    weekly_sets: number
  }[]
}

export interface SetCountPerWorkout {
  workout_id: string
  workout_date: string
  set_count: number
}

export interface ExerciseFrequency {
  exercise_id: string
  rank: number
  exercise_count: number
}
