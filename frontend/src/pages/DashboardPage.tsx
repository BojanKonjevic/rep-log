import { useQuery } from '@tanstack/react-query'
import { getStreak, getSetCounts } from '@/api/workouts'
import { getExerciseFrequency } from '@/api/exercises'
import { getMuscleGroupVolume, getMuscleGroups } from '@/api/muscle_groups'
import { getExercises } from '@/api/exercises'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Flame, Dumbbell, BarChart2, TrendingUp } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/context/ThemeContext'

function StatCard({ icon: Icon, label, value, accent }: {
  icon: React.ElementType
  label: string
  value: string | number
  accent?: string
}) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="flex items-center gap-3 pt-4 pb-4">
        <div className={`p-2 rounded-lg ${accent ?? 'bg-muted'}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-xl font-bold leading-tight">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { theme } = useTheme()

  const color = theme === 'dark' ? '#a78bfa' : '#6d28d9'
  const barColor = theme === 'dark' ? '#818cf8' : '#4f46e5'
  const mutedColor = theme === 'dark' ? '#71717a' : '#9ca3af'
  const tooltipStyle = {
    backgroundColor: theme === 'dark' ? '#27272a' : '#ffffff',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '8px',
    fontSize: '12px',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
  }

  const { data: streak = 0 } = useQuery({
    queryKey: ['streak'],
    queryFn: getStreak,
  })

  const { data: setCounts = [] } = useQuery({
    queryKey: ['setCounts'],
    queryFn: () => getSetCounts(),
  })

  const { data: frequency = [] } = useQuery({
    queryKey: ['frequency'],
    queryFn: () => getExerciseFrequency({ limit: 5 }),
  })

  const { data: exercises = [] } = useQuery({
    queryKey: ['exercises', null],
    queryFn: () => getExercises({ limit: 100 }),
  })

  const { data: muscleGroups = [] } = useQuery({
    queryKey: ['muscleGroups'],
    queryFn: getMuscleGroups,
  })

  const { data: volume = [] } = useQuery({
    queryKey: ['volume'],
    queryFn: () => getMuscleGroupVolume(),
  })

  const totalWorkouts = setCounts.length > 0
    ? new Set(setCounts.map(s => s.workout_id)).size
    : 0

  const totalSets = setCounts.reduce((acc, s) => acc + s.set_count, 0)

  const setCountChartData = [...setCounts]
    .slice(-10)
    .map(s => ({
      date: new Date(s.workout_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }),
      sets: s.set_count,
    }))

  const frequencyChartData = frequency.map(f => {
    const exercise = exercises.find(e => e.id === f.exercise_id)
    return {
      name: exercise?.name ?? 'Unknown',
      count: f.exercise_count,
    }
  })

  const muscleGroupMap = Object.fromEntries(muscleGroups.map(mg => [mg.id, mg.name]))
  const radarData = volume.map(v => ({
    muscle: muscleGroupMap[v.muscle_group_id] ?? 'Unknown',
    sets: v.all_weeks.reduce((acc, w) => acc + w.weekly_sets, 0),
  })).sort((a, b) => b.sets - a.sets).slice(0, 8)

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted-foreground">{user?.email}</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard icon={Flame} label="Week streak" value={`${streak}w`} accent="bg-orange-100 dark:bg-orange-900/30 text-orange-600" />
        <StatCard icon={Dumbbell} label="Total workouts" value={totalWorkouts} accent="bg-blue-100 dark:bg-blue-900/30 text-blue-600" />
        <StatCard icon={BarChart2} label="Total sets" value={totalSets} accent="bg-violet-100 dark:bg-violet-900/30 text-violet-600" />
        <StatCard icon={TrendingUp} label="Exercises" value={exercises.length} accent="bg-green-100 dark:bg-green-900/30 text-green-600" />
      </div>

      {setCountChartData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Sets per workout
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={setCountChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: mutedColor }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: mutedColor }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: theme === 'dark' ? '#3f3f46' : '#f4f4f5' }} />
                <Bar dataKey="sets" fill={barColor} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {frequencyChartData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Most trained exercises
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart
                data={frequencyChartData}
                layout="vertical"
                margin={{ top: 0, right: 0, left: 70, bottom: 0 }}
              >
                <XAxis type="number" tick={{ fontSize: 11, fill: mutedColor }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: mutedColor }} width={70} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: theme === 'dark' ? '#3f3f46' : '#f4f4f5' }} />
                <Bar dataKey="count" fill={barColor} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {radarData.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Muscle group volume
            </CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width="100%" height={240}>
              <RadarChart data={radarData}>
                <PolarGrid stroke={mutedColor} />
                <PolarAngleAxis dataKey="muscle" tick={{ fontSize: 11, fill: mutedColor }} />
                <PolarRadiusAxis tick={{ fontSize: 10, fill: mutedColor }} />
                <Radar dataKey="sets" fill={color} fillOpacity={0.15} stroke={color} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {setCounts.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <Dumbbell className="h-10 w-10 mx-auto mb-3 opacity-20" />
          <p>No data yet. Log your first workout to see analytics!</p>
        </div>
      )}
    </div>
  )
}
