import { useEffect, useState } from 'react'
import { TrainFront, WifiOff, ServerOff, UserRound, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function Header({ role = 'Loco Pilot', displayTitle = 'LOCO CABIN DISPLAY' }) {
  const navigate = useNavigate()
  const [now, setNow] = useState(new Date())
  const [userName, setUserName] = useState('')

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    try {
      const session = sessionStorage.getItem('pilotwatch_session')
      if (session) {
        const user = JSON.parse(session)
        if (user && user.fullName) {
          setUserName(user.fullName)
        }
      }
    } catch (e) {
      console.error('Error reading session:', e)
    }
  }, [])

  const dateStr = now.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
  const timeStr = now.toLocaleTimeString('en-IN', { hour12: false })

  function handleLogout() {
    sessionStorage.removeItem('pilotwatch_session')
    navigate('/')
  }

  return (
    <header className="glass border-b border-panel-border px-4 py-3 md:px-6">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4">
        {/* Logo + title */}
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-signal-blue/40 bg-signal-blue/10 shadow-glow">
            <TrainFront className="h-6 w-6 text-signal-blue" strokeWidth={2} />
          </div>
          <div className="leading-tight">
            <p className="font-display text-lg font-bold tracking-wide text-ink-primary md:text-xl">
              {displayTitle}
            </p>
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
              PilotWatch Console
            </p>
          </div>
        </div>

        {/* Date / time */}
        <div className="flex items-center gap-4 rounded-md border border-panel-border bg-panel/60 px-4 py-2 font-mono">
          <div className="text-center">
            <p className="text-[10px] uppercase tracking-widest text-ink-faint">Date</p>
            <p className="text-sm text-ink-primary">{dateStr}</p>
          </div>
          <div className="h-6 w-px bg-panel-border" />
          <div className="text-center">
            <p className="text-[10px] uppercase tracking-widest text-ink-faint">Time (IST)</p>
            <p className="text-sm text-signal-cyan">{timeStr}</p>
          </div>
        </div>

        {/* Status chips */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 rounded-full border border-status-danger/40 bg-status-danger/10 px-3 py-1.5">
            <WifiOff className="h-3.5 w-3.5 text-status-danger" />
            <span className="font-mono text-[11px] font-medium uppercase tracking-wide text-status-danger">
              Disconnected
            </span>
          </div>
          <div className="flex items-center gap-1.5 rounded-full border border-status-danger/40 bg-status-danger/10 px-3 py-1.5">
            <ServerOff className="h-3.5 w-3.5 text-status-danger" />
            <span className="font-mono text-[11px] font-medium uppercase tracking-wide text-status-danger">
              Backend Offline
            </span>
          </div>
        </div>

        {/* User + logout */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-md border border-panel-border bg-panel/60 px-3 py-1.5">
            <UserRound className="h-4 w-4 text-signal-blue" />
            <span className="font-body text-sm text-ink-primary">{userName || role}</span>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 rounded-md border border-status-danger/40 bg-status-danger/10 px-3 py-1.5 font-body text-sm font-medium text-status-danger transition-colors hover:bg-status-danger/20"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
