import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getWorkout } from '@/api/workouts'
import { getExercises } from '@/api/exercises'
import { createWorkoutExercise, deleteWorkoutExercise } from '@/api/workout_exercises'
import { createSet, updateSet, deleteSet } from '@/api/sets'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import type { WorkoutExercise, Set as SetType } from '@/types'

function SetRow({
  set,
  onUpdate,
  onDelete,
}: {
  set: SetType
  onUpdate: (id: string, reps: number, weight: number) => void
  onDelete: (id: string) => void
}) {
  const [reps, setReps] = useState(String(set.reps))
  const [weight, setWeight] = useState(String(set.weight))

  function handleBlur() {
    const r = parseInt(reps)
    const w = parseFloat(weight)
    if (!isNaN(r) && !isNaN(w)) {
      onUpdate(set.id, r, w)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground w-6 text-center">{set.set_number}</span>
      <Input
        className="h-8 text-sm text-center"
        value={reps}
        onChange={e => setReps(e.target.value)}
        onBlur={handleBlur}
        inputMode="numeric"
        placeholder="Reps"
      />
      <Input
        className="h-8 text-sm text-center"
        value={weight}
        onChange={e => setWeight(e.target.value)}
        onBlur={handleBlur}
        inputMode="decimal"
        placeholder="kg"
      />
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-muted-foreground hover:text-destructive shrink-0"
        onClick={() => onDelete(set.id)}
      >
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
    </div>
  )
}

function WorkoutExerciseCard({
  workoutExercise,
  workoutId,
}: {
  workoutExercise: WorkoutExercise
  workoutId: string
}) {
  const queryClient = useQueryClient()
  const [expanded, setExpanded] = useState(true)

  const addSetMutation = useMutation({
    mutationFn: () =>
      createSet({
        workout_exercise_id: workoutExercise.id,
        set_number: workoutExercise.sets.length + 1,
        reps: 8,
        weight: 0,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workout', workoutId] }),
  })

  const updateSetMutation = useMutation({
    mutationFn: ({ id, reps, weight }: { id: string; reps: number; weight: number }) =>
      updateSet(id, { reps, weight }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workout', workoutId] }),
  })

  const deleteSetMutation = useMutation({
    mutationFn: deleteSet,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workout', workoutId] }),
  })

  const deleteExerciseMutation = useMutation({
    mutationFn: () => deleteWorkoutExercise(workoutId, workoutExercise.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workout', workoutId] }),
  })

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <button onClick={() => setExpanded(v => !v)} className="flex items-center gap-2 flex-1 min-w-0">
              {expanded ? <ChevronUp className="h-4 w-4 shrink-0 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />}
              <CardTitle className="text-sm truncate">{workoutExercise.exercise.name}</CardTitle>
            </button>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Badge variant="secondary" className="text-xs">
              {workoutExercise.sets.length} sets
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-destructive"
              onClick={() => deleteExerciseMutation.mutate()}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardHeader>

      {expanded && (
        <CardContent className="flex flex-col gap-2">
          {workoutExercise.sets.length > 0 && (
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-muted-foreground w-6" />
              <span className="text-xs text-muted-foreground flex-1 text-center">Reps</span>
              <span className="text-xs text-muted-foreground flex-1 text-center">Weight (kg)</span>
              <span className="w-8" />
            </div>
          )}
          {workoutExercise.sets.map(set => (
            <SetRow
              key={set.id}
              set={set}
              onUpdate={(id, reps, weight) => updateSetMutation.mutate({ id, reps, weight })}
              onDelete={id => deleteSetMutation.mutate(id)}
            />
          ))}
          <Button
            variant="outline"
            size="sm"
            className="mt-1 w-full"
            onClick={() => addSetMutation.mutate()}
            disabled={addSetMutation.isPending}
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Add set
          </Button>
        </CardContent>
      )}
    </Card>
  )
}

function AddExercisePanel({
  workoutId,
  currentExerciseIds,
  onClose,
}: {
  workoutId: string
  currentExerciseIds: string[]
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')

  const { data: exercises = [] } = useQuery({
    queryKey: ['exercises', null],
    queryFn: () => getExercises({ limit: 100 }),
  })

  const addMutation = useMutation({
    mutationFn: (exerciseId: string) =>
      createWorkoutExercise(workoutId, {
        exercise_id: exerciseId,
        order: currentExerciseIds.length + 1,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workout', workoutId] })
      onClose()
    },
  })

  const filtered = exercises.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <Card className="mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Add exercise</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <Input
          placeholder="Search exercises…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          autoFocus
        />
        <div className="flex flex-col gap-1 max-h-64 overflow-y-auto">
          {filtered.map(exercise => (
            <button
              key={exercise.id}
              onClick={() => addMutation.mutate(exercise.id)}
              disabled={currentExerciseIds.includes(exercise.id) || addMutation.isPending}
              className="flex items-center justify-between px-3 py-2 rounded-lg text-sm hover:bg-muted transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-left"
            >
              <span>{exercise.name}</span>
              <div className="flex gap-1">
                {exercise.muscle_groups.slice(0, 2).map(mg => (
                  <Badge key={mg.id} variant="secondary" className="text-xs capitalize">
                    {mg.name}
                  </Badge>
                ))}
              </div>
            </button>
          ))}
        </div>
        <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
      </CardContent>
    </Card>
  )
}

export default function WorkoutDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showAddExercise, setShowAddExercise] = useState(false)

  const { data: workout, isLoading } = useQuery({
    queryKey: ['workout', id],
    queryFn: () => getWorkout(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-foreground" />
      </div>
    )
  }

  if (!workout) return <p className="text-muted-foreground">Workout not found.</p>

  const currentExerciseIds = workout.exercises.map(e => e.exercise_id)

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate('/workouts')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-xl font-bold">{workout.name ?? 'Untitled Workout'}</h1>
          <p className="text-sm text-muted-foreground">
            {new Date(workout.workout_date).toLocaleDateString('en-GB', {
              weekday: 'long', day: 'numeric', month: 'long',
            })}
          </p>
        </div>
      </div>

      {showAddExercise && (
        <AddExercisePanel
          workoutId={workout.id}
          currentExerciseIds={currentExerciseIds}
          onClose={() => setShowAddExercise(false)}
        />
      )}

      {workout.exercises.map(we => (
        <WorkoutExerciseCard
          key={we.id}
          workoutExercise={we}
          workoutId={workout.id}
        />
      ))}

      {workout.exercises.length === 0 && !showAddExercise && (
        <div className="text-center py-8 text-muted-foreground">
          <p className="mb-3">No exercises yet.</p>
        </div>
      )}

      {!showAddExercise && (
        <Button onClick={() => setShowAddExercise(true)} className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          Add exercise
        </Button>
      )}
    </div>
  )
}
