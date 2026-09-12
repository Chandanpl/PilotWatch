import { useEffect, useState } from 'react'
import { ShieldAlert, Clock, Gauge, Move } from 'lucide-react'

const API_BASE_URL = 'http://127.0.0.1:8000'

function AlertPanel() {
  const [activeAlerts, setActiveAlerts] = useState([])
  const [alertHistory, setAlertHistory] = useState([])

  const fetchAlerts = async () => {
    try {
      const [activeResponse, historyResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/ai/alerts/active`),
        fetch(`${API_BASE_URL}/ai/alerts/history`),
      ])

      if (!activeResponse.ok || !historyResponse.ok) {
        throw new Error('Failed to fetch alerts')
      }

      const activeData = await activeResponse.json()
      const historyData = await historyResponse.json()

      setActiveAlerts(activeData.active_alerts || [])
      setAlertHistory(historyData.alert_history || [])
    } catch (error) {
      console.error('Alert fetch error:', error)
    }
  }

  useEffect(() => {
    fetchAlerts()

    const interval = setInterval(fetchAlerts, 2000)

    return () => clearInterval(interval)
  }, [])

  const getRiskClasses = (risk) => {
    switch (risk) {
      case 'CRITICAL':
        return {
          border: 'border-status-danger/40',
          bg: 'bg-status-danger/10',
          text: 'text-status-danger',
        }

      case 'HIGH':
        return {
          border: 'border-status-danger/30',
          bg: 'bg-status-danger/5',
          text: 'text-status-danger',
        }

      case 'WARNING':
        return {
          border: 'border-status-warning/30',
          bg: 'bg-status-warning/10',
          text: 'text-status-warning',
        }

      default:
        return {
          border: 'border-panel-border',
          bg: 'bg-void/30',
          text: 'text-ink-muted',
        }
    }
  }

  const formatTime = (timestamp) => {
    if (!timestamp) return '--'

    try {
      return new Date(timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    } catch {
      return timestamp
    }
  }

  return (
    <div className="rounded-xl border border-panel-border bg-panel shadow-console">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">

        <div className="flex items-center gap-2">
          <ShieldAlert
            className={`h-4 w-4 ${activeAlerts.length > 0
                ? 'text-status-danger'
                : 'text-ink-muted'
              }`}
            strokeWidth={1.75}
          />

          <p className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
            Alert Log
          </p>
        </div>

        <span
          className={`rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-wide ${activeAlerts.length > 0
              ? 'border-status-danger/40 bg-status-danger/10 text-status-danger'
              : 'border-status-safe/30 bg-status-safe/10 text-status-safe'
            }`}
        >
          {activeAlerts.length > 0
            ? `${activeAlerts.length} Active`
            : 'Clear'}
        </span>

      </div>

      {/* Content */}
      <div className="max-h-[420px] overflow-y-auto p-4">

        {/* Active Alerts */}
        {activeAlerts.length > 0 && (
          <div className="space-y-3">

            <p className="font-mono text-[10px] uppercase tracking-widest text-status-danger">
              Active Alerts
            </p>

            {activeAlerts.map((alert) => {

              const risk = getRiskClasses(alert.risk_level)

              return (
                <div
                  key={alert.alert_id}
                  className={`rounded-lg border ${risk.border} ${risk.bg} p-3`}
                >

                  <div className="flex items-start justify-between gap-3">

                    <div>
                      <p className={`font-display text-sm font-bold uppercase ${risk.text}`}>
                        {alert.risk_level} — {alert.object_type}
                      </p>

                      <p className="mt-1 font-mono text-[10px] text-ink-muted">
                        Alert #{alert.alert_id} • Track #{alert.track_id}
                      </p>
                    </div>

                    <span className="rounded border border-status-danger/30 px-2 py-0.5 font-mono text-[9px] uppercase text-status-danger">
                      ACTIVE
                    </span>

                  </div>

                  <div className="mt-3 grid grid-cols-2 gap-2">

                    <AlertInfo
                      icon={Move}
                      label="Direction"
                      value={alert.direction || '--'}
                    />

                    <AlertInfo
                      icon={Gauge}
                      label="Speed"
                      value={`${alert.speed_pixels_per_second ?? '--'} px/s`}
                    />

                    <AlertInfo
                      icon={Clock}
                      label="Time"
                      value={formatTime(alert.timestamp)}
                    />

                    <AlertInfo
                      label="Location"
                      value={alert.location || '--'}
                    />

                  </div>

                </div>
              )
            })}

          </div>
        )}

        {/* No active alerts */}
        {activeAlerts.length === 0 && (
          <div className="flex flex-col items-center justify-center gap-2 px-6 py-8 text-center">

            <ShieldAlert
              className="h-8 w-8 text-status-safe"
              strokeWidth={1.5}
            />

            <p className="font-display text-base font-semibold tracking-wide text-ink-primary">
              No Active Alerts
            </p>

            <p className="font-mono text-xs text-ink-faint">
              AI monitoring system is clear.
            </p>

          </div>
        )}

        {/* Recent History */}
        {alertHistory.length > 0 && (
          <div className="mt-5 border-t border-panel-border pt-4">

            <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-ink-faint">
              Recent Alert History
            </p>

            <div className="space-y-2">

              {alertHistory
                .slice()
                .reverse()
                .slice(0, 5)
                .map((alert) => {

                  const risk = getRiskClasses(alert.risk_level)

                  return (
                    <div
                      key={alert.alert_id}
                      className="flex items-center justify-between rounded-lg border border-panel-border bg-void/30 px-3 py-2"
                    >

                      <div className="min-w-0">

                        <p className={`font-mono text-[10px] font-semibold uppercase ${risk.text}`}>
                          {alert.risk_level} • {alert.object_type}
                        </p>

                        <p className="mt-0.5 font-mono text-[9px] text-ink-faint">
                          Track #{alert.track_id} • {alert.status}
                        </p>

                      </div>

                      <span className="ml-3 shrink-0 font-mono text-[9px] text-ink-faint">
                        {formatTime(alert.resolved_at || alert.timestamp)}
                      </span>

                    </div>
                  )
                })}

            </div>

          </div>
        )}

      </div>
    </div>
  )
}

function AlertInfo({ icon: Icon, label, value }) {
  return (
    <div className="rounded border border-panel-border bg-void/30 px-2 py-1.5">

      <div className="flex items-center gap-1">

        {Icon && (
          <Icon
            className="h-3 w-3 text-ink-faint"
            strokeWidth={1.5}
          />
        )}

        <span className="font-mono text-[8px] uppercase tracking-wide text-ink-faint">
          {label}
        </span>

      </div>

      <p className="mt-0.5 truncate font-mono text-[10px] text-ink-primary">
        {value}
      </p>

    </div>
  )
}

export default AlertPanel