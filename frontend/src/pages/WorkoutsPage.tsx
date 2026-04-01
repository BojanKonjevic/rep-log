import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getWorkouts, createWorkout, deleteWorkout } from '@/api/workouts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Trash2, Search, Dumbbell } from 'lucide-react'
import type { Workout } from '@/types'
import { useNavigate } from 'react-router-dom'

function WorkoutCard({ workout, onDelete }: { workout: Workout, onDelete: (id: string) => void }) {
  const navigate = useNavigate()
  const totalSets = workout.exercises.reduce((acc, ex) => acc + ex.sets.length, 0)

  return (
    <Card
      className="cursor-pointer hover:border-foreground/30 transition-colors"
      onClick={() => navigate(`/workouts/${workout.id}`)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle className="text-base">
              {workout.name ?? 'Untitled Workout'}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-0.5">
              {new Date(workout.workout_date).toLocaleDateString('en-GB', {
                weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
              })}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-destructive shrink-0"
            onClick={e => { e.stopPropagation(); onDelete(workout.id) }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {workout.exercises.map(ex => (
            <Badge key={ex.id} variant="secondary" className="text-xs">
              {ex.exercise.name}
            </Badge>
          ))}
          {workout.exercises.length === 0 && (
            <span className="text-xs text-muted-foreground">No exercises yet</span>
          )}
        </div>
        <div className="flex gap-3 text-xs text-muted-foreground mt-2">
          <span className="flex items-center gap-1">
            <Dumbbell className="h-3 w-3" />
            {workout.exercises.length} exercises
          </span>
          <span>{totalSets} sets</span>
          {workout.notes && <span className="truncate">{workout.notes}</span>}
        </div>
      </CardContent>
    </Card>
  )
}

function CreateWorkoutForm({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [notes, setNotes] = useState('')
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])

  const mutation = useMutation({
    mutationFn: createWorkout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workouts'] })
      onClose()
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    mutation.mutate({
      name: name || undefined,
      notes: notes || undefined,
      workout_date: date,
    })
  }

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-base">New Workout</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Input
            placeholder="Workout name (optional)"
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <Input
            placeholder="Notes (optional)"
            value={notes}
            onChange={e => setNotes(e.target.value)}
          />
          <Input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            required
          />
          {mutation.error && (
            <p className="text-sm text-destructive">{mutation.error.message}</p>
          )}
          <div className="flex gap-2">
            <Button type="submit" disabled={mutation.isPending} className="flex-1">
              {mutation.isPending ? 'Creating…' : 'Create'}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

export default function WorkoutsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['workouts', search],
    queryFn: () => getWorkouts({ search, limit: 20 }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteWorkout,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workouts'] }),
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Workouts</h1>
        <Button size="sm" onClick={() => setShowCreate(v => !v)}>
          <Plus className="h-4 w-4 mr-1" />
          New
        </Button>
      </div>

      {showCreate && <CreateWorkoutForm onClose={() => setShowCreate(false)} />}

      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search workouts…"
          className="pl-9"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-foreground" />
        </div>
      )}

      <div className="flex flex-col gap-3">
        {data?.workouts.map(workout => (
          <WorkoutCard
            key={workout.id}
            workout={workout}
            onDelete={id => deleteMutation.mutate(id)}
          />
        ))}
        {data?.workouts.length === 0 && !isLoading && (
          <div className="text-center py-12 text-muted-foreground">
            <Dumbbell className="h-10 w-10 mx-auto mb-3 opacity-20" />
            <p>No workouts yet. Create your first one!</p>
          </div>
        )}
      </div>

      {data && data.total > 20 && (
        <p className="text-center text-sm text-muted-foreground mt-4">
          Showing 20 of {data.total} workouts
        </p>
      )}
    </div>
  )
}
