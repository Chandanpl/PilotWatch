import { useState, useEffect } from 'react'
import {
  Camera,
  Radar as RadarIcon,
  Volume2,
  ServerCog,
  Database,
  Wifi,
  Crosshair,
  Volume2 as SpeakerIcon,
  Aperture,
  Siren,
  Lock,
  Unlock,
} from 'lucide-react'
import Header from '../components/Header.jsx'
import CameraPanel from '../components/CameraPanel.jsx'
import StatusCard from '../components/StatusCard.jsx'
import AlertPanel from '../components/AlertPanel.jsx'
import Footer from '../components/Footer.jsx'

const API_BASE_URL = 'http://127.0.0.1:8000'

const emergencyControls = [
  { icon: SpeakerIcon, label: 'Trigger Speaker', action: 'Speaker broadcast sent' },
  { icon: Aperture, label: 'Capture Image', action: 'Snapshot request triggered' },
  { icon: Siren, label: 'Emergency Alert', action: 'Emergency siren broadcasted' },
]

function LocoDashboard() {
  const [backendStatus, setBackendStatus] = useState('Disconnected')
  const [dbStatus, setDbStatus] = useState('Disconnected')
  const [wifiStatus, setWifiStatus] = useState('Disconnected')

  const [activeAlerts, setActiveAlerts] = useState([])

  useEffect(() => {
    // Wi-Fi / Online status
    setWifiStatus(navigator.onLine ? 'Connected' : 'Disconnected')

    const checkOnline = () => {
      setWifiStatus(navigator.onLine ? 'Connected' : 'Disconnected')
    }

    window.addEventListener('online', checkOnline)
    window.addEventListener('offline', checkOnline)

    // Backend connectivity
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`)

        if (response.ok) {
          setBackendStatus('Connected')
          setDbStatus('Connected')
        } else {
          setBackendStatus('Disconnected')
          setDbStatus('Disconnected')
        }
      } catch (err) {
        setBackendStatus('Disconnected')
        setDbStatus('Disconnected')
      }
    }

    checkBackend()
    const backendInterval = setInterval(checkBackend, 5000)

    return () => {
      window.removeEventListener('online', checkOnline)
      window.removeEventListener('offline', checkOnline)
      clearInterval(backendInterval)
    }
  }, [])

  // Fetch real AI alerts
  useEffect(() => {
    const fetchActiveAlerts = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/ai/alerts/active`)

        if (!response.ok) {
          throw new Error('Failed to fetch AI alerts')
        }

        const data = await response.json()

        setActiveAlerts(data.active_alerts || [])
      } catch (err) {
        console.error('AI alert fetch error:', err)
        setActiveAlerts([])
      }
    }

    fetchActiveAlerts()

    // Update dashboard every 2 seconds
    const alertInterval = setInterval(fetchActiveAlerts, 2000)

    return () => clearInterval(alertInterval)
  }, [])

  const systemStatus = [
    { icon: Camera, label: 'Camera', status: 'Offline' },
    { icon: RadarIcon, label: 'Radar', status: 'Offline' },
    { icon: Volume2, label: 'Speaker', status: 'Offline' },
    { icon: ServerCog, label: 'Backend', status: backendStatus },
    { icon: Database, label: 'Database', status: dbStatus },
    { icon: Wifi, label: 'Wi-Fi', status: wifiStatus },
  ]

  // Latest active alert
  const latestAlert = activeAlerts.length > 0
    ? activeAlerts[activeAlerts.length - 1]
    : null

  const detectionObject = latestAlert?.object_type || '--'

  const detectionConfidence = '--'

  const detectionDistance = '-- m'

  const detectionSpeed = latestAlert
    ? `${latestAlert.speed_pixels_per_second} px/s`
    : '-- km/h'

  const detectionDirection = latestAlert?.direction || '--'

  const riskLevel = latestAlert?.risk_level || 'SAFE'

  const getRiskClasses = (risk) => {
    switch (risk) {
      case 'CRITICAL':
        return {
          badge:
            'border-status-danger/30 bg-status-danger/10 text-status-danger',
          panel:
            'border-status-danger/30 bg-status-danger/10',
          text: 'text-status-danger',
          dot: 'bg-status-danger',
        }

      case 'HIGH':
        return {
          badge:
            'border-status-danger/30 bg-status-danger/10 text-status-danger',
          panel:
            'border-status-danger/30 bg-status-danger/10',
          text: 'text-status-danger',
          dot: 'bg-status-danger',
        }

      case 'WARNING':
        return {
          badge:
            'border-status-warning/30 bg-status-warning/10 text-status-warning',
          panel:
            'border-status-warning/30 bg-status-warning/10',
          text: 'text-status-warning',
          dot: 'bg-status-warning',
        }

      default:
        return {
          badge:
            'border-status-safe/30 bg-status-safe/10 text-status-safe',
          panel:
            'border-status-safe/30 bg-status-safe/10',
          text: 'text-status-safe',
          dot: 'bg-status-safe',
        }
    }
  }

  const riskClasses = getRiskClasses(riskLevel)

  return (
    <div className="flex min-h-screen flex-col bg-void console-vignette">
      <div className="console-texture pointer-events-none fixed inset-0 opacity-40" />

      <div className="relative z-10 flex min-h-screen flex-col">
        <Header />

        <main className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-5 md:px-6">

          {/* Camera + Detection row */}
          <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.6fr_1fr]">

            <div className="min-h-[420px]">
              <CameraPanel />
            </div>

            {/* Object Detection Card */}
            <div className="flex flex-col rounded-xl border border-panel-border bg-panel shadow-console">

              <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">

                <div className="flex items-center gap-2">
                  <Crosshair className="h-4 w-4 text-signal-blue" />

                  <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
                    Object Detection
                  </p>
                </div>

                <span
                  className={`rounded-full border px-3 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide ${riskClasses.badge}`}
                >
                  {riskLevel}
                </span>

              </div>

              <div className="grid flex-1 grid-cols-2 gap-px bg-panel-border">

                <ReadoutTile
                  label="Object"
                  value={detectionObject}
                />

                <ReadoutTile
                  label="Confidence"
                  value={detectionConfidence}
                />

                <ReadoutTile
                  label="Distance"
                  value={detectionDistance}
                />

                <ReadoutTile
                  label="Speed"
                  value={detectionSpeed}
                />

                <ReadoutTile
                  label="Direction"
                  value={detectionDirection}
                  className="col-span-2"
                />

              </div>

              {/* Risk Level */}
              <div className="border-t border-panel-border px-4 py-3">

                <p className="mb-1.5 font-mono text-[10px] uppercase tracking-widest text-ink-faint">
                  Risk Level
                </p>

                <div
                  className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${riskClasses.panel}`}
                >

                  <span
                    className={`h-2 w-2 rounded-full ${riskClasses.dot} led ${riskLevel !== 'SAFE' ? 'animate-blink' : ''
                      }`}
                  />

                  <span
                    className={`font-display text-sm font-bold uppercase tracking-widest ${riskClasses.text}`}
                  >
                    {riskLevel}
                  </span>

                </div>

              </div>

            </div>
          </div>

          {/* Backend Offline Warning */}
          {backendStatus === 'Disconnected' && (
            <div className="mt-5 rounded-lg border border-status-danger/30 bg-status-danger/10 px-4 py-3 font-mono text-xs text-status-danger led shadow-glow-red animate-pulse flex flex-col sm:flex-row sm:items-center justify-between gap-3">

              <div>
                <span className="font-bold">
                  ⚠️ DATABASE CONNECTION OFFLINE:
                </span>{' '}
                The front-end cannot connect to the SQLite database. Please run{' '}
                <code className="bg-void px-1.5 py-0.5 rounded border border-panel-border text-ink-primary font-bold">
                  python backend/app.py
                </code>{' '}
                in a new command prompt to start the backend.
              </div>

              <button
                type="button"
                onClick={() =>
                  window.open('http://127.0.0.1:8000/docs', '_blank')
                }
                className="shrink-0 rounded border border-status-danger/40 bg-status-danger/20 px-3 py-1 font-bold hover:bg-status-danger/30 transition-all text-[10px] uppercase tracking-wider cursor-pointer text-status-danger text-center"
              >
                Inspect API Docs
              </button>

            </div>
          )}

          {/* System Status */}
          <section className="mt-5">

            <p className="mb-3 font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
              System Status
            </p>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">

              {systemStatus.map((s) => (
                <StatusCard
                  key={s.label}
                  icon={s.icon}
                  label={s.label}
                  status={s.status}
                />
              ))}

            </div>

          </section>

          {/* Alerts + Emergency */}
          <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">

            <AlertPanel />

            <div className="rounded-xl border border-panel-border bg-panel shadow-console">

              <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">

                <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
                  Emergency Controls
                </p>

                <div className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide">

                  {backendStatus === 'Connected' ? (
                    <div className="flex items-center gap-1.5 text-status-safe">
                      <Unlock className="h-3.5 w-3.5" />
                      <span>Ready — Secure Connection</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1.5 text-ink-faint">
                      <Lock className="h-3.5 w-3.5" />
                      <span>Locked — Backend Offline</span>
                    </div>
                  )}

                </div>

              </div>

              <div className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-3">

                {emergencyControls.map((c) => {

                  const isConnected = backendStatus === 'Connected'

                  return (
                    <button
                      key={c.label}
                      type="button"
                      disabled={!isConnected}
                      onClick={() => alert(`${c.action} successfully!`)}
                      className={`flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-all ${isConnected
                          ? 'border-status-danger/45 bg-status-danger/5 text-status-danger hover:bg-status-danger/15 active:scale-[0.98] cursor-pointer'
                          : 'border-panel-border bg-void/40 opacity-40 cursor-not-allowed text-ink-faint'
                        }`}
                    >

                      <c.icon
                        className={`h-5 w-5 ${isConnected
                            ? 'text-status-danger'
                            : 'text-ink-faint'
                          }`}
                        strokeWidth={1.75}
                      />

                      <span
                        className={`text-center font-body text-xs font-medium ${isConnected
                            ? 'text-ink-primary'
                            : 'text-ink-faint'
                          }`}
                      >
                        {c.label}
                      </span>

                    </button>
                  )
                })}

              </div>

            </div>
          </div>

        </main>

        <Footer />

      </div>
    </div>
  )
}

function ReadoutTile({
  label,
  value,
  className = '',
}) {
  return (
    <div className={`bg-panel px-4 py-3 ${className}`}>

      <p className="mb-1 font-mono text-[10px] uppercase tracking-widest text-ink-faint">
        {label}
      </p>

      <p className="font-mono text-lg font-medium text-ink-primary">
        {value}
      </p>

    </div>
  )
}

export default LocoDashboard