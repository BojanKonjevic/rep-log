import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/context/ThemeContext'
import BottomNav from './BottomNav'
import { Button } from '@/components/ui/button'
import { LogOut, Dumbbell, Sun, Moon } from 'lucide-react'

interface AppShellProps {
  children: React.ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b bg-background">
        <div className="flex items-center justify-between h-14 px-4 max-w-lg mx-auto">
          <div className="flex items-center gap-2">
            <Dumbbell className="h-5 w-5" />
            <span className="font-bold tracking-tight">Rep Log</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-muted-foreground hidden sm:block mr-2">{user?.email}</span>
            <Button variant="ghost" size="icon" onClick={toggle}>
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 pt-6 pb-24">
        {children}
      </main>

      <BottomNav />
    </div>
  )
}
