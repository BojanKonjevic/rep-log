import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getExercises, createExercise, deleteExercise } from '@/api/exercises'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, Trash2, Search, Dumbbell } from 'lucide-react'
import type { Exercise } from '@/types'

const MUSCLE_GROUPS = [
  'chest', 'back', 'delts', 'traps', 'biceps', 'triceps',
  'forearms', 'abs', 'lower back', 'glutes', 'quadriceps',
  'hamstrings', 'calves', 'adductors', 'abductors', 'hip flexors', 'neck',
]

function ExerciseCard({ exercise, onDelete }: { exercise: Exercise, onDelete: (id: string) => void }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base">{exercise.name}</CardTitle>
          <Button
            variant="ghost"
            size="icon"
            className="text-muted-foreground hover:text-destructive shrink-0"
            onClick={() => onDelete(exercise.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-1.5">
          {exercise.muscle_groups.map(mg => (
            <Badge key={mg.id} variant="secondary" className="text-xs capitalize">
              {mg.name}
            </Badge>
          ))}
          {exercise.muscle_groups.length === 0 && (
            <span className="text-xs text-muted-foreground">No muscle groups</span>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function CreateExerciseForm({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<string[]>([])

  const mutation = useMutation({
    mutationFn: createExercise,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['exercises'] })
      onClose()
    },
  })

  function toggleMuscleGroup(mg: string) {
    setSelected(prev =>
      prev.includes(mg) ? prev.filter(m => m !== mg) : [...prev, mg]
    )
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    mutation.mutate({ name: name.trim(), muscle_group_names: selected })
  }

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-base">New Exercise</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Input
            placeholder="Exercise name"
            value={name}
            onChange={e => setName(e.target.value)}
            required
          />
          <div>
            <p className="text-xs text-muted-foreground mb-2">Muscle groups</p>
            <div className="flex flex-wrap gap-1.5">
              {MUSCLE_GROUPS.map(mg => (
                <button
                  key={mg}
                  type="button"
                  onClick={() => toggleMuscleGroup(mg)}
                  className={`text-xs px-2.5 py-1 rounded-full border transition-colors capitalize ${
                    selected.includes(mg)
                      ? 'bg-foreground text-background border-foreground'
                      : 'border-border text-muted-foreground hover:border-foreground hover:text-foreground'
                  }`}
                >
                  {mg}
                </button>
              ))}
            </div>
          </div>
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

export default function ExercisesPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [muscleFilter, setMuscleFilter] = useState<string | null>(null)

  const { data: exercises = [], isLoading } = useQuery({
    queryKey: ['exercises', muscleFilter],
    queryFn: () => getExercises({
      muscle_group_name: muscleFilter ?? undefined,
      limit: 100,
    }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteExercise,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['exercises'] }),
  })

  const filtered = search
    ? exercises.filter(e => e.name.toLowerCase().includes(search.toLowerCase()))
    : exercises

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Exercises</h1>
        <Button size="sm" onClick={() => setShowCreate(v => !v)}>
          <Plus className="h-4 w-4 mr-1" />
          New
        </Button>
      </div>

      {showCreate && <CreateExerciseForm onClose={() => setShowCreate(false)} />}

      <div className="relative mb-3">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search exercises…"
          className="pl-9"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      <div className="flex gap-1.5 overflow-x-auto pb-2 mb-4 no-scrollbar">
        <button
          onClick={() => setMuscleFilter(null)}
          className={`text-xs px-3 py-1.5 rounded-full border whitespace-nowrap transition-colors ${
            muscleFilter === null
              ? 'bg-foreground text-background border-foreground'
              : 'border-border text-muted-foreground hover:border-foreground hover:text-foreground'
          }`}
        >
          All
        </button>
        {MUSCLE_GROUPS.map(mg => (
          <button
            key={mg}
            onClick={() => setMuscleFilter(muscleFilter === mg ? null : mg)}
            className={`text-xs px-3 py-1.5 rounded-full border whitespace-nowrap transition-colors capitalize ${
              muscleFilter === mg
                ? 'bg-foreground text-background border-foreground'
                : 'border-border text-muted-foreground hover:border-foreground hover:text-foreground'
            }`}
          >
            {mg}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-foreground" />
        </div>
      )}

      <div className="flex flex-col gap-3">
        {filtered.map(exercise => (
          <ExerciseCard
            key={exercise.id}
            exercise={exercise}
            onDelete={id => deleteMutation.mutate(id)}
          />
        ))}
        {filtered.length === 0 && !isLoading && (
          <div className="text-center py-12 text-muted-foreground">
            <Dumbbell className="h-10 w-10 mx-auto mb-3 opacity-20" />
            <p>No exercises found.</p>
          </div>
        )}
      </div>
    </div>
  )
}
