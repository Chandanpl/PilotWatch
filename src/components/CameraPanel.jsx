import { CameraOff, Radar } from 'lucide-react'

function CameraPanel() {
  return (
    <div className="flex h-full flex-col rounded-xl border border-panel-border bg-panel shadow-console">
      <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-status-danger led text-status-danger animate-blink" />
          <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
            Front Camera Feed
          </p>
        </div>
        <p className="font-mono text-[11px] text-ink-faint">CAM-01 // 0 FPS</p>
      </div>

      <div className="relative flex-1 overflow-hidden rounded-b-xl bg-black">
        {/* ambient scan texture */}
        <div className="console-texture absolute inset-0 opacity-60" />

        {/* radar sweep signature element */}
        <div className="absolute left-1/2 top-1/2 h-40 w-40 -translate-x-1/2 -translate-y-1/2 opacity-30 md:h-56 md:w-56">
          <div className="relative h-full w-full rounded-full border border-signal-dim/40">
            <div className="absolute inset-4 rounded-full border border-signal-dim/30" />
            <div className="absolute inset-8 rounded-full border border-signal-dim/20" />
            <div className="absolute inset-0 origin-center animate-sweep">
              <div className="h-1/2 w-full bg-gradient-to-t from-signal-blue/0 via-signal-blue/0 to-signal-blue/40" />
            </div>
          </div>
        </div>

        {/* centered status */}
        <div className="relative z-10 flex h-full flex-col items-center justify-center gap-3 px-6 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full border border-panel-border bg-panel/80">
            <CameraOff className="h-8 w-8 text-ink-faint" strokeWidth={1.5} />
          </div>
          <p className="font-display text-2xl font-bold tracking-[0.15em] text-ink-muted">
            NO SIGNAL
          </p>
          <p className="font-mono text-xs text-ink-faint">
            Waiting for backend connection...
          </p>
        </div>

        {/* corner frame markers for an instrument-panel feel */}
        <div className="pointer-events-none absolute inset-3 border border-panel-border/40" />
      </div>

      <div className="flex items-center justify-between border-t border-panel-border px-4 py-2">
        <div className="flex items-center gap-1.5 text-ink-faint">
          <Radar className="h-3.5 w-3.5" />
          <span className="font-mono text-[11px]">Awaiting stream handshake</span>
        </div>
        <span className="font-mono text-[11px] text-ink-faint">RES —</span>
      </div>
    </div>
  )
}

export default CameraPanel
