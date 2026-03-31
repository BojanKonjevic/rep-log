import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Dumbbell, ClipboardList } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/workouts', label: 'Workouts', icon: ClipboardList },
  { to: '/exercises', label: 'Exercises', icon: Dumbbell },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background">
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center gap-1 px-4 py-2 text-xs transition-colors',
                isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground'
              )
            }
          >
            <Icon className="h-5 w-5" />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
