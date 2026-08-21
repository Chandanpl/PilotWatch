import { ShieldAlert } from 'lucide-react'

function AlertPanel() {
  return (
    <div className="rounded-xl border border-panel-border bg-panel shadow-console">
      <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">Alert Log</p>
        <span className="rounded-full border border-status-safe/30 bg-status-safe/10 px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-wide text-status-safe">
          Clear
        </span>
      </div>
      <div className="flex flex-col items-center justify-center gap-2 px-6 py-8 text-center">
        <ShieldAlert className="h-8 w-8 text-ink-faint" strokeWidth={1.5} />
        <p className="font-display text-base font-semibold tracking-wide text-ink-primary">
          No Active Alerts
        </p>
        <p className="font-mono text-xs text-ink-faint">
          Waiting for AI Detection System...
        </p>
      </div>
    </div>
  )
}

export default AlertPanel
