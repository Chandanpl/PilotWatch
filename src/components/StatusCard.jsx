function StatusCard({ icon: Icon, label, status = 'Offline', tone }) {
  const toneMap = {
    danger: {
      dot: 'bg-status-danger text-status-danger',
      text: 'text-status-danger',
      border: 'border-status-danger/30',
      ring: 'shadow-glow-red',
    },
    amber: {
      dot: 'bg-status-amber text-status-amber',
      text: 'text-status-amber',
      border: 'border-status-amber/30',
      ring: 'shadow-glow-amber',
    },
    safe: {
      dot: 'bg-status-safe text-status-safe',
      text: 'text-status-safe',
      border: 'border-status-safe/30',
      ring: 'shadow-glow',
    },
  }

  // Automatically determine color tone from the status value if no tone prop is provided
  const resolvedTone = tone || (
    (status === 'Connected' || status === 'Online' || status === 'Safe' || status === 'Active') 
      ? 'safe' 
      : (status === 'Warning' || status === 'Caution' || status === 'Pending') 
      ? 'amber' 
      : 'danger'
  )

  const t = toneMap[resolvedTone]

  return (
    <div
      className={`flex items-center justify-between rounded-lg border ${t.border} bg-panel/70 px-4 py-3 transition-colors hover:bg-panel`}
    >
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md border border-panel-border bg-void/60">
          <Icon className="h-4 w-4 text-ink-muted" strokeWidth={1.75} />
        </div>
        <div className="leading-tight">
          <p className="font-body text-sm font-medium text-ink-primary">{label}</p>
          <p className={`font-mono text-[11px] uppercase tracking-wide ${t.text}`}>{status}</p>
        </div>
      </div>
      <span className={`h-2 w-2 rounded-full led animate-blink ${t.dot}`} />
    </div>
  )
}

export default StatusCard
