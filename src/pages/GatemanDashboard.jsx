import { useState, useEffect, useRef } from 'react'
import {
  Compass,
  Thermometer,
  Wind,
  DoorClosed,
  AlertTriangle,
  Flame,
  MessageSquare,
  Plus,
  Send,
  Radio,
  Megaphone,
  UserRound,
  Check,
  Activity,
  Bell,
  Lock,
  Unlock,
  ShieldAlert,
  Flag,
} from 'lucide-react'
import Header from '../components/Header.jsx'
import Footer from '../components/Footer.jsx'

function GatemanDashboard() {
  // 1. Gate Status State
  const [gateStatus, setGateStatus] = useState({
    id: 'Gate No. 42 (Level Crossing)',
    barrierState: 'Locked & Closed', // 'Locked & Closed', 'Open to Traffic', 'Emergency Override'
    roadSignal: 'Red (Stop Traffic)', // 'Red (Stop Traffic)', 'Green (Allow Traffic)'
    trackSensor: 'Clear', // 'Clear', 'Obstruction Detected'
    handSignal: 'Green (Proceed)', // 'Green (Proceed)', 'Red (Stop Train)'
    audibleAlarm: 'Off', // 'Off', 'Active (Siren)'
    systemBattery: '94%',
  })

  // Approaching Trains State
  const [approachingTrains, setApproachingTrains] = useState([
    { id: 1, name: 'Rajdhani Express (12301)', speed: '110 km/h', status: 'Approaching', distance: '3.2 km', eta: '1m 45s' },
    { id: 2, name: 'Goods Freight (G402)', speed: '55 km/h', status: 'In Block Section', distance: '12.4 km', eta: '13m 30s' },
  ])

  // 2. Incident Log State
  const [incidents, setIncidents] = useState([
    {
      id: 1,
      gateArea: 'Crossing Zone A',
      type: 'Obstruction on Track',
      status: 'Resolved',
      description: 'Stuck handcart cleared from the tracks. Verified clear by Gateman.',
      time: '21:05',
    },
    {
      id: 2,
      gateArea: 'Barrier West',
      type: 'Barrier Signal Fault',
      status: 'Active',
      description: 'West side barrier sensor reported minor telemetry mismatch. Manual inspection completed.',
      time: '21:20',
    },
  ])

  // 3. Intercom Messages State
  const [messages, setMessages] = useState([
    { sender: 'Loco Pilot', text: 'Approaching Gate 42 block section. Confirm barrier lock status and track clearance.', time: '21:18' },
    { sender: 'Gateman', text: 'Gate 42 is Locked & Closed to road traffic. Hand signal is GREEN. Track is verified clear.', time: '21:19' },
    { sender: 'Loco Pilot', text: 'Copy that. Proceeding at standard track speed (110 km/h). Thanks, Gateman.', time: '21:20' },
  ])

  // Form Inputs
  const [inputArea, setInputArea] = useState('Crossing Zone A')
  const [inputType, setInputType] = useState('Obstruction on Track')
  const [inputDesc, setInputDesc] = useState('')

  // Intercom input
  const [chatInput, setChatInput] = useState('')

  // Scroll ref for chat
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Toggle Gate Barrier state
  function toggleBarrier() {
    setGateStatus((prev) => {
      const isClosed = prev.barrierState === 'Locked & Closed'
      return {
        ...prev,
        barrierState: isClosed ? 'Open to Traffic' : 'Locked & Closed',
        roadSignal: isClosed ? 'Green (Allow Traffic)' : 'Red (Stop Traffic)',
      }
    })
  }

  // Toggle Hand Signal flag (Green Proceed vs Red Stop)
  function toggleHandSignal() {
    setGateStatus((prev) => {
      const isGreen = prev.handSignal.includes('Green')
      return {
        ...prev,
        handSignal: isGreen ? 'Red (Stop Train)' : 'Green (Proceed)',
      }
    })
  }

  // Handle reporting incident
  function handleReportIncident(e) {
    e.preventDefault()
    if (!inputDesc.trim()) return

    const now = new Date()
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })

    const newIncident = {
      id: Date.now(),
      gateArea: inputArea,
      type: inputType,
      status: 'Active',
      description: inputDesc,
      time: timeStr,
    }

    setIncidents([newIncident, ...incidents])

    // Update gate telemetry dynamically
    if (inputType === 'Obstruction on Track') {
      setGateStatus((prev) => ({
        ...prev,
        trackSensor: 'Obstruction Detected',
        handSignal: 'Red (Stop Train)', // Force hand signal to Red upon track obstruction
      }))
    } else if (inputType === 'Barrier Signal Fault') {
      setGateStatus((prev) => ({
        ...prev,
        barrierState: 'Emergency Override',
      }))
    }

    // Automatically alert Pilot in intercom
    const alertMsg = {
      sender: 'Gateman',
      text: `[ALERT] ${inputType} in ${inputArea}: ${inputDesc}`,
      time: timeStr,
    }

    setMessages((prev) => [...prev, alertMsg])

    // Pilot auto reply
    setTimeout(() => {
      const replyTime = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })
      let pilotReplyText = `Acknowledged: ${inputType} in ${inputArea}. Applying caution speeds.`
      if (inputType === 'Obstruction on Track') {
        pilotReplyText = `EMERGENCY COPY: Obstruction on track at Gate 42! Engaging emergency train brakes immediately.`
      }
      const pilotReply = {
        sender: 'Loco Pilot',
        text: pilotReplyText,
        time: replyTime,
      }
      setMessages((prev) => [...prev, pilotReply])
    }, 2000)

    setInputDesc('')
  }

  // Handle sending chat message
  function handleSendMessage(e) {
    e.preventDefault()
    if (!chatInput.trim()) return

    const now = new Date()
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })

    const newMsg = {
      sender: 'Gateman',
      text: chatInput,
      time: timeStr,
    }

    setMessages((prev) => [...prev, newMsg])
    setChatInput('')

    // Auto pilot reply
    setTimeout(() => {
      const replyTime = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })
      const autoReply = {
        sender: 'Loco Pilot',
        text: `Received message from Gate 42: "${chatInput}". Understood, Gateman.`,
        time: replyTime,
      }
      setMessages((prev) => [...prev, autoReply])
    }, 2500)
  }

  // Handle resolving an incident
  function handleResolveIncident(id, type) {
    setIncidents(
      incidents.map((inc) => {
        if (inc.id === id) {
          return { ...inc, status: 'Resolved' }
        }
        return inc
      })
    )

    // Clear alert triggers
    if (type === 'Obstruction on Track') {
      setGateStatus((prev) => ({
        ...prev,
        trackSensor: 'Clear',
        handSignal: 'Green (Proceed)',
      }))
    } else if (type === 'Barrier Signal Fault') {
      setGateStatus((prev) => ({
        ...prev,
        barrierState: 'Locked & Closed',
      }))
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-void console-vignette">
      {/* ambient scanlines overlay */}
      <div className="console-texture pointer-events-none fixed inset-0 opacity-40" />

      <div className="relative z-10 flex min-h-screen flex-col">
        {/* Header pointing to Gateman and GATEMAN CONSOLE */}
        <Header role="Gateman" displayTitle="GATEMAN CONSOLE" />

        <main className="mx-auto w-full max-w-[1600px] flex-1 px-4 py-5 md:px-6">
          {/* Top Panel: Live Gate Metrics */}
          <section className="mb-5 rounded-xl border border-panel-border bg-panel p-4 shadow-console">
            <div className="mb-4 flex items-center justify-between border-b border-panel-border pb-3">
              <div className="flex items-center gap-2">
                <Compass className="h-4.5 w-4.5 text-signal-cyan animate-spin-slow" />
                <h2 className="font-mono text-xs uppercase tracking-[0.2em] text-ink-primary">
                  Level Crossing Status Telemetry &mdash; {gateStatus.id}
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-status-safe led" />
                <span className="font-mono text-[10px] uppercase tracking-wide text-ink-muted">
                  Lock Sensors Connected
                </span>
              </div>
            </div>

            {/* Status Tiles */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
              <StatusTile
                label="Barrier Lock"
                value={gateStatus.barrierState}
                alert={gateStatus.barrierState.includes('Open') || gateStatus.barrierState.includes('Emergency')}
                color={gateStatus.barrierState === 'Locked & Closed' ? 'safe' : 'danger'}
              />
              <StatusTile
                label="Road Traffic Signals"
                value={gateStatus.roadSignal}
                alert={gateStatus.roadSignal.includes('Green')}
                color={gateStatus.roadSignal.includes('Red') ? 'safe' : 'amber'}
              />
              <StatusTile
                label="Track Intrusion Sensor"
                value={gateStatus.trackSensor}
                alert={gateStatus.trackSensor !== 'Clear'}
                color={gateStatus.trackSensor === 'Clear' ? 'safe' : 'danger'}
              />
              <StatusTile
                label="Gateman Hand Signal"
                value={gateStatus.handSignal}
                alert={gateStatus.handSignal.includes('Red')}
                color={gateStatus.handSignal.includes('Green') ? 'safe' : 'danger'}
              />
              <StatusTile
                label="Emergency Siren"
                value={gateStatus.audibleAlarm}
                alert={gateStatus.audibleAlarm !== 'Off'}
                color={gateStatus.audibleAlarm === 'Off' ? 'safe' : 'danger'}
              />
            </div>
          </section>

          {/* Main Grid */}
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1.3fr_1fr]">
            
            {/* LEFT COLUMN: Approaching Trains & Obstruction form */}
            <div className="flex flex-col gap-5">
              
              {/* Approaching Trains List */}
              <div className="rounded-xl border border-panel-border bg-panel p-4 shadow-console">
                <div className="mb-4 flex items-center justify-between border-b border-panel-border pb-3">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4.5 w-4.5 text-signal-cyan" />
                    <h3 className="font-mono text-xs uppercase tracking-[0.2em] text-ink-primary">
                      Approaching Trains Radar Feed
                    </h3>
                  </div>
                  <span className="rounded bg-signal-blue/15 px-2 py-0.5 font-mono text-[10px] font-semibold text-signal-blue uppercase">
                    Block occupancy live
                  </span>
                </div>

                <div className="flex flex-col gap-3">
                  {approachingTrains.map((t) => (
                    <div
                      key={t.id}
                      className="flex flex-col justify-between gap-3 rounded-lg border border-panel-border bg-void/50 p-4 sm:flex-row sm:items-center"
                    >
                      <div>
                        <h4 className="font-display text-base font-bold text-ink-primary">
                          {t.name}
                        </h4>
                        <div className="mt-1 flex gap-3 font-mono text-xs text-ink-muted">
                          <span>Speed: <strong className="text-signal-cyan">{t.speed}</strong></span>
                          <span>Distance: <strong className="text-signal-cyan">{t.distance}</strong></span>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="font-mono text-[10px] uppercase tracking-wider text-ink-faint">
                            ETA at Crossing
                          </p>
                          <p className="font-mono text-base font-bold text-status-amber">
                            {t.eta}
                          </p>
                        </div>
                        <span className="rounded bg-status-safe/10 border border-status-safe/30 px-3 py-1 font-mono text-xs font-semibold text-status-safe uppercase tracking-wider animate-pulse">
                          {t.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gate Incident Logger */}
              <div className="rounded-xl border border-panel-border bg-panel p-4 shadow-console">
                <div className="mb-4 flex items-center gap-2 border-b border-panel-border pb-3">
                  <Megaphone className="h-4.5 w-4.5 text-signal-cyan" />
                  <h3 className="font-mono text-xs uppercase tracking-[0.2em] text-ink-primary">
                    Gate Incident Logger &amp; Pilot Warning Trigger
                  </h3>
                </div>

                <form onSubmit={handleReportIncident} className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  {/* Select Gate Area */}
                  <div>
                    <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
                      Select Area
                    </label>
                    <select
                      value={inputArea}
                      onChange={(e) => setInputArea(e.target.value)}
                      className="w-full rounded-lg border border-panel-border bg-void px-3 py-2 font-mono text-sm text-ink-primary outline-none focus:border-signal-cyan/50 focus:shadow-glow"
                    >
                      <option className="bg-panel" value="Crossing Zone A">Crossing Zone A</option>
                      <option className="bg-panel" value="Crossing Zone B">Crossing Zone B</option>
                      <option className="bg-panel" value="Barrier East">Barrier East</option>
                      <option className="bg-panel" value="Barrier West">Barrier West</option>
                    </select>
                  </div>

                  {/* Incident Type */}
                  <div>
                    <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
                      Incident Type
                    </label>
                    <select
                      value={inputType}
                      onChange={(e) => setInputType(e.target.value)}
                      className="w-full rounded-lg border border-panel-border bg-void px-3 py-2 font-mono text-sm text-ink-primary outline-none focus:border-signal-cyan/50 focus:shadow-glow"
                    >
                      <option className="bg-panel" value="Obstruction on Track">Obstruction on Track</option>
                      <option className="bg-panel" value="Barrier Signal Fault">Barrier Signal Fault</option>
                      <option className="bg-panel" value="Road Traffic Collision">Road Traffic Collision</option>
                      <option className="bg-panel" value="Manual Override Engaged">Manual Override Engaged</option>
                      <option className="bg-panel" value="Other Event">Other Event</option>
                    </select>
                  </div>

                  {/* Submit warning */}
                  <div className="flex items-end">
                    <button
                      type="submit"
                      className="flex w-full items-center justify-center gap-2 rounded-lg border border-status-danger/50 bg-status-danger/15 py-2 font-body text-xs font-bold uppercase tracking-wider text-status-danger shadow-glow-red transition-all hover:bg-status-danger/25 active:scale-[0.99]"
                    >
                      <ShieldAlert className="h-4 w-4" />
                      Trigger Warning
                    </button>
                  </div>

                  {/* Description */}
                  <div className="md:col-span-3">
                    <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
                      Event / Warning Description
                    </label>
                    <input
                      type="text"
                      value={inputDesc}
                      onChange={(e) => setInputDesc(e.target.value)}
                      placeholder="e.g. Stuck vehicle identified on track; warning pilots in section."
                      className="w-full rounded-lg border border-panel-border bg-void px-4 py-2.5 font-mono text-sm text-ink-primary placeholder:text-ink-faint outline-none focus:border-signal-cyan/50 focus:shadow-glow"
                    />
                  </div>
                </form>
              </div>

            </div>

            {/* RIGHT COLUMN: Active warning logs & Pilot Intercom */}
            <div className="flex flex-col gap-5">
              
              {/* Warnings and Incidents Feed */}
              <div className="flex flex-col rounded-xl border border-panel-border bg-panel shadow-console">
                <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4 text-signal-cyan" />
                    <h2 className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
                      Gate Warning &amp; Event Logs
                    </h2>
                  </div>
                  <span className="rounded-full border border-status-danger/30 bg-status-danger/10 px-2 py-0.5 font-mono text-[9px] font-bold uppercase tracking-wide text-status-danger">
                    {incidents.filter((i) => i.status !== 'Resolved').length} Active Warning
                  </span>
                </div>

                <div className="flex max-h-[220px] flex-col gap-3 overflow-y-auto p-4">
                  {incidents.length === 0 ? (
                    <div className="py-6 text-center font-mono text-xs text-ink-faint">
                      No active gate warning logs.
                    </div>
                  ) : (
                    incidents.map((inc) => (
                      <div
                        key={inc.id}
                        className={`rounded-lg border p-3 ${
                          inc.status === 'Resolved'
                            ? 'border-panel-border bg-void/10 opacity-60'
                            : 'border-status-danger/30 bg-status-danger/5'
                        }`}
                      >
                        <div className="mb-1 flex items-start justify-between">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="font-display text-xs font-bold text-ink-primary">
                              {inc.gateArea}
                            </span>
                            <span className="font-mono text-[10px] text-ink-faint">
                              {inc.time}
                            </span>
                            <span
                              className={`rounded px-1.5 py-0.2 font-mono text-[9px] font-semibold uppercase tracking-wider ${
                                inc.status === 'Resolved'
                                  ? 'bg-panel-border text-ink-muted'
                                  : 'bg-status-danger/25 text-status-danger'
                              }`}
                            >
                              {inc.type}
                            </span>
                          </div>
                          {inc.status !== 'Resolved' && (
                            <button
                              onClick={() => handleResolveIncident(inc.id, inc.type)}
                              className="flex items-center gap-1 rounded border border-status-safe/40 bg-status-safe/15 px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-wider text-status-safe hover:bg-status-safe/30 transition-all"
                            >
                              <Check className="h-3 w-3" />
                              Clear Warning
                            </button>
                          )}
                        </div>
                        <p className="font-mono text-xs text-ink-muted">{inc.description}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Intercom Terminal */}
              <div className="flex flex-1 flex-col rounded-xl border border-panel-border bg-panel shadow-console">
                <div className="flex items-center justify-between border-b border-panel-border px-4 py-2.5">
                  <div className="flex items-center gap-2">
                    <Radio className="h-4 w-4 text-signal-cyan" />
                    <h2 className="font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
                      Gate-to-Cabin Pilot Intercom
                    </h2>
                  </div>
                  <span className="flex items-center gap-1.5 font-mono text-[9px] font-semibold uppercase tracking-wider text-status-safe">
                    <span className="h-1.5 w-1.5 rounded-full bg-status-safe led" />
                    Secure Radio Linked
                  </span>
                </div>

                <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4 min-h-[180px] max-h-[300px]">
                  {messages.map((msg, index) => {
                    const isPilot = msg.sender === 'Loco Pilot'
                    const isAlert = msg.text.startsWith('[ALERT]')

                    return (
                      <div
                        key={index}
                        className={`flex flex-col max-w-[85%] rounded-lg p-2.5 font-mono text-xs ${
                          isAlert
                            ? 'self-end bg-status-danger/10 border border-status-danger/30 text-ink-primary'
                            : isPilot
                            ? 'self-start bg-void border border-panel-border text-signal-blue'
                            : 'self-end bg-panel-border/30 border border-panel-border/60 text-signal-cyan'
                        }`}
                      >
                        <div className="mb-0.5 flex items-center justify-between gap-4 font-mono text-[9px] text-ink-faint font-semibold uppercase tracking-wider">
                          <span className={isPilot ? 'text-signal-blue/80' : 'text-signal-cyan/80'}>
                            {msg.sender}
                          </span>
                          <span>{msg.time}</span>
                        </div>
                        <p className={isAlert ? 'text-status-danger font-medium' : 'text-ink-primary'}>
                          {msg.text}
                        </p>
                      </div>
                    )
                  })}
                  <div ref={chatEndRef} />
                </div>

                <form onSubmit={handleSendMessage} className="border-t border-panel-border p-3 flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Send message to train pilot cabin..."
                    className="flex-1 rounded-lg border border-panel-border bg-void px-3 py-2 font-mono text-xs text-ink-primary placeholder:text-ink-faint outline-none focus:border-signal-cyan/50 focus:shadow-glow"
                  />
                  <button
                    type="submit"
                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-signal-cyan/50 bg-signal-cyan/15 text-signal-cyan shadow-glow hover:bg-signal-cyan/25 active:scale-[0.95] transition-all"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
              </div>

            </div>

          </div>

          {/* Action Console: Physical buttons */}
          <section className="mt-5 rounded-xl border border-panel-border bg-panel p-4 shadow-console">
            <h3 className="mb-3 font-mono text-xs uppercase tracking-[0.2em] text-ink-muted">
              Gateman Console Action Switchboard
            </h3>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <button
                type="button"
                onClick={toggleBarrier}
                className={`flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-all uppercase tracking-wider font-semibold active:scale-[0.98] ${
                  gateStatus.barrierState === 'Locked & Closed'
                    ? 'border-status-safe bg-status-safe/5 text-status-safe hover:bg-status-safe/15'
                    : 'border-status-danger bg-status-danger/10 text-status-danger hover:bg-status-danger/20 shadow-glow-red animate-pulse'
                }`}
              >
                {gateStatus.barrierState === 'Locked & Closed' ? <Lock className="h-5 w-5" /> : <Unlock className="h-5 w-5" />}
                <span className="text-center font-mono text-[10px]">
                  {gateStatus.barrierState === 'Locked & Closed' ? 'Open Road Barrier' : 'Lock Road Barrier'}
                </span>
              </button>

              <button
                type="button"
                onClick={toggleHandSignal}
                className={`flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-all uppercase tracking-wider font-semibold active:scale-[0.98] ${
                  gateStatus.handSignal.includes('Green')
                    ? 'border-status-safe bg-status-safe/5 text-status-safe hover:bg-status-safe/15'
                    : 'border-status-danger bg-status-danger/10 text-status-danger hover:bg-status-danger/20 shadow-glow-red animate-pulse'
                }`}
              >
                <Flag className="h-5 w-5" />
                <span className="text-center font-mono text-[10px]">
                  Hand Flag: {gateStatus.handSignal.includes('Green') ? 'Deploy RED' : 'Deploy GREEN'}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setGateStatus((prev) => ({ ...prev, audibleAlarm: prev.audibleAlarm === 'Off' ? 'Active' : 'Off' }))}
                className={`flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-all uppercase tracking-wider font-semibold active:scale-[0.98] ${
                  gateStatus.audibleAlarm === 'Off'
                    ? 'border-status-amber/40 bg-status-amber/5 text-status-amber/80 hover:bg-status-amber/15'
                    : 'border-status-amber bg-status-amber/25 text-status-amber shadow-glow-amber animate-pulse'
                }`}
              >
                <Megaphone className="h-5 w-5" />
                <span className="text-center font-mono text-[10px]">
                  {gateStatus.audibleAlarm === 'Off' ? 'Sound Crossing Siren' : 'Mute crossing siren'}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setGateStatus((prev) => ({ ...prev, roadSignal: prev.roadSignal.includes('Red') ? 'Green (Allow Traffic)' : 'Red (Stop Traffic)' }))}
                className="border-signal-cyan/40 bg-signal-cyan/5 text-signal-cyan/80 hover:bg-signal-cyan/15 flex flex-col items-center gap-2 rounded-lg border px-3 py-4 transition-all uppercase tracking-wider font-semibold active:scale-[0.98]"
              >
                <Radio className="h-5 w-5" />
                <span className="text-center font-mono text-[10px]">
                  Toggle Road Signals
                </span>
              </button>
            </div>
          </section>

        </main>

        <Footer />
      </div>
    </div>
  )
}

function StatusTile({ label, value, alert, color }) {
  return (
    <div className={`rounded-lg border p-3 bg-panel/60 ${
      alert ? 'border-status-danger/40 shadow-glow-red animate-pulse' : 'border-panel-border'
    }`}>
      <p className="mb-1 font-mono text-[10px] uppercase tracking-widest text-ink-faint">
        {label}
      </p>
      <div className="flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full led bg-status-${color}`} />
        <span className={`font-display text-sm font-bold tracking-wide uppercase ${
          color === 'safe' ? 'text-status-safe' : color === 'amber' ? 'text-status-amber' : 'text-status-danger'
        }`}>
          {value}
        </span>
      </div>
    </div>
  )
}

export default GatemanDashboard
