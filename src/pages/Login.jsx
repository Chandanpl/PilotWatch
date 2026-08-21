import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TrainFront, Contact, KeyRound, Eye, EyeOff, ArrowRight, UserRound } from 'lucide-react'

function Login() {
  const navigate = useNavigate()
  const [isSignUp, setIsSignUp] = useState(false)
  const [role, setRole] = useState('loco') // 'loco' or 'gate'
  const [employeeId, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [remember, setRemember] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  // Handle Login submission
  function handleSubmit(e) {
    e.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    if (!employeeId.trim() || !password.trim()) {
      setErrorMessage('Please fill in all fields.')
      return
    }

    // Default built-in users
    const defaultUsers = [
      { employeeId: 'LP001', password: 'pilot@123', fullName: 'Loco Pilot (Demo)', role: 'loco' },
      { employeeId: 'GM001', password: 'gate@123', fullName: 'Gateman (Demo)', role: 'gate' }
    ]

    // Read stored users from localStorage
    const storedUsers = JSON.parse(localStorage.getItem('pilotwatch_users') || '[]')
    const allUsers = [...defaultUsers, ...storedUsers]

    // Validate credentials
    const matchedUser = allUsers.find(
      (u) =>
        u.employeeId.toUpperCase() === employeeId.trim().toUpperCase() &&
        u.password === password
    )

    if (!matchedUser) {
      setErrorMessage('Invalid Employee ID or Password.')
      return
    }

    // Store active user session info
    sessionStorage.setItem('pilotwatch_session', JSON.stringify(matchedUser))

    // Redirect to correct dashboard
    if (matchedUser.role === 'loco') {
      navigate('/loco-dashboard')
    } else {
      navigate('/gate-dashboard')
    }
  }

  // Handle Sign Up registration
  function handleSignUp(e) {
    e.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

    if (!fullName.trim() || !employeeId.trim() || !password.trim()) {
      setErrorMessage('Please fill in all fields.')
      return
    }

    // Read registered users
    const storedUsers = JSON.parse(localStorage.getItem('pilotwatch_users') || '[]')

    // Check if ID is taken (either by default accounts or existing stored accounts)
    const isDefaultId = (employeeId.toUpperCase() === 'LP001' || employeeId.toUpperCase() === 'GM001')
    const isAlreadyTaken = storedUsers.some(
      (u) => u.employeeId.toUpperCase() === employeeId.trim().toUpperCase()
    ) || isDefaultId

    if (isAlreadyTaken) {
      setErrorMessage('Employee ID already registered.')
      return
    }

    // Register user
    const newUser = {
      fullName: fullName.trim(),
      employeeId: employeeId.trim(),
      password,
      role
    }

    storedUsers.push(newUser)
    localStorage.setItem('pilotwatch_users', JSON.stringify(storedUsers))

    setSuccessMessage('Account created successfully! Switching to Login...')

    // Switch back to Login after 2 seconds
    setTimeout(() => {
      setIsSignUp(false)
      setFullName('')
      setSuccessMessage('')
    }, 2000)
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-void px-4 py-10 console-vignette">
      {/* ambient texture + faint rail-line motif */}
      <div className="console-texture pointer-events-none absolute inset-0" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-signal-blue/10 to-transparent" />

      <div className="relative z-10 flex w-full max-w-md flex-col items-center">
        {/* Logo */}
        <div className="mb-6 flex flex-col items-center gap-3">
          <div className={`flex h-16 w-16 items-center justify-center rounded-2xl border bg-void/80 shadow-glow transition-all ${
            role === 'loco' ? 'border-signal-blue/40 text-signal-blue' : 'border-signal-cyan/40 text-signal-cyan'
          }`}>
            <TrainFront className="h-8 w-8" strokeWidth={2} />
          </div>
          <div className="text-center">
            <h1 className="font-display text-3xl font-bold tracking-[0.08em] text-ink-primary">
              PilotWatch
            </h1>
          </div>
        </div>

        {/* Auth Card */}
        <form
          onSubmit={isSignUp ? handleSignUp : handleSubmit}
          className="glass w-full rounded-2xl border border-panel-border p-7 shadow-console transition-all"
        >
          {/* Role Tabs */}
          <div className="mb-5 flex rounded-lg border border-panel-border bg-void/50 p-1">
            <button
              type="button"
              onClick={() => {
                setRole('loco')
                setEmployeeId('')
                setPassword('')
                setErrorMessage('')
              }}
              className={`flex-1 rounded-md py-1.5 text-center font-mono text-xs uppercase tracking-wider font-semibold transition-all ${
                role === 'loco'
                  ? 'bg-signal-blue/20 text-signal-blue border border-signal-blue/30 shadow-glow'
                  : 'text-ink-muted hover:text-ink-primary'
              }`}
            >
              Loco Pilot
            </button>
            <button
              type="button"
              onClick={() => {
                setRole('gate')
                setEmployeeId('')
                setPassword('')
                setErrorMessage('')
              }}
              className={`flex-1 rounded-md py-1.5 text-center font-mono text-xs uppercase tracking-wider font-semibold transition-all ${
                role === 'gate'
                  ? 'bg-signal-cyan/20 text-signal-cyan border border-signal-cyan/30 shadow-glow'
                  : 'text-ink-muted hover:text-ink-primary'
              }`}
            >
              Gateman
            </button>
          </div>

          <p className="mb-5 text-center font-mono text-[11px] uppercase tracking-[0.25em] text-ink-muted">
            {isSignUp
              ? role === 'loco'
                ? 'Register Locomotive Pilot Account'
                : 'Register Gateman Account'
              : role === 'loco'
              ? 'Locomotive Pilot Login'
              : 'Gateman Login'}
          </p>

          {/* Error Message */}
          {errorMessage && (
            <div className="mb-4 rounded-lg border border-status-danger/30 bg-status-danger/10 px-3.5 py-2.5 font-mono text-xs text-status-danger led shadow-glow-red">
              {errorMessage}
            </div>
          )}

          {/* Success Message */}
          {successMessage && (
            <div className="mb-4 rounded-lg border border-status-safe/30 bg-status-safe/10 px-3.5 py-2.5 font-mono text-xs text-status-safe led shadow-glow">
              {successMessage}
            </div>
          )}

          {/* Full Name field (Only in Sign Up Mode) */}
          {isSignUp && (
            <div className="mb-4">
              <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
                Full Name
              </label>
              <div className={`flex items-center gap-2 rounded-lg border border-panel-border bg-void/60 px-3 py-2.5 transition-colors focus-within:shadow-glow ${
                role === 'loco' ? 'focus-within:border-signal-blue/60' : 'focus-within:border-signal-cyan/60'
              }`}>
                <UserRound className="h-4 w-4 shrink-0 text-ink-faint" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Jane Doe"
                  className="w-full bg-transparent font-mono text-sm text-ink-primary placeholder:text-ink-faint focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* Employee ID field */}
          <div className="mb-4">
            <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
              Employee ID
            </label>
            <div className={`flex items-center gap-2 rounded-lg border border-panel-border bg-void/60 px-3 py-2.5 transition-colors focus-within:shadow-glow ${
              role === 'loco' ? 'focus-within:border-signal-blue/60' : 'focus-within:border-signal-cyan/60'
            }`}>
              <Contact className="h-4 w-4 shrink-0 text-ink-faint" />
              <input
                type="text"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                placeholder={role === 'loco' ? 'e.g. LP001' : 'e.g. GM001'}
                className="w-full bg-transparent font-mono text-sm text-ink-primary placeholder:text-ink-faint focus:outline-none"
              />
            </div>
          </div>

          {/* Password field */}
          <div className="mb-4">
            <label className="mb-1.5 block font-body text-xs font-medium uppercase tracking-wide text-ink-muted">
              Password
            </label>
            <div className={`flex items-center gap-2 rounded-lg border border-panel-border bg-void/60 px-3 py-2.5 transition-colors focus-within:shadow-glow ${
              role === 'loco' ? 'focus-within:border-signal-blue/60' : 'focus-within:border-signal-cyan/60'
            }`}>
              <KeyRound className="h-4 w-4 shrink-0 text-ink-faint" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-transparent font-mono text-sm text-ink-primary placeholder:text-ink-faint focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword((s) => !s)}
                className="shrink-0 text-ink-faint transition-colors hover:text-ink-muted"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Remember Me (Only in Login Mode) */}
          {!isSignUp && (
            <div className="mb-6 flex items-center justify-between">
              <label className="flex cursor-pointer items-center gap-2">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className={`h-3.5 w-3.5 rounded border-panel-border bg-void ${
                    role === 'loco' ? 'accent-signal-blue' : 'accent-signal-cyan'
                  }`}
                />
                <span className="font-body text-xs text-ink-muted">Remember Me</span>
              </label>
            </div>
          )}

          {/* Action button */}
          <button
            type="submit"
            className={`group mt-2 flex w-full items-center justify-center gap-2 rounded-lg border py-2.5 font-body text-sm font-semibold uppercase tracking-wide transition-all active:scale-[0.99] ${
              role === 'loco'
                ? 'border-signal-blue/50 bg-signal-blue/15 text-signal-blue shadow-glow hover:bg-signal-blue/25'
                : 'border-signal-cyan/50 bg-signal-cyan/15 text-signal-cyan shadow-glow hover:bg-signal-cyan/25'
            }`}
          >
            {isSignUp ? 'Create Account' : 'Login'}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </button>

          {/* Dynamic Switch Bottom Link */}
          <div className="mt-5 text-center font-body text-xs text-ink-muted">
            {isSignUp ? (
              <span>
                Already registered?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(false)
                    setErrorMessage('')
                    setSuccessMessage('')
                  }}
                  className={`font-semibold underline hover:text-ink-primary ${
                    role === 'loco' ? 'text-signal-blue' : 'text-signal-cyan'
                  }`}
                >
                  Sign in instead
                </button>
              </span>
            ) : (
              <span>
                New staff member?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(true)
                    setEmployeeId('')
                    setPassword('')
                    setErrorMessage('')
                    setSuccessMessage('')
                  }}
                  className={`font-semibold underline hover:text-ink-primary ${
                    role === 'loco' ? 'text-signal-blue' : 'text-signal-cyan'
                  }`}
                >
                  Create an account
                </button>
              </span>
            )}
          </div>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
            PilotWatch Railway Safety System
          </p>
          <p className="mt-0.5 font-mono text-[11px] text-ink-faint">Version 1.0 &nbsp;·&nbsp; © 2026</p>
        </div>
      </div>
    </div>
  )
}

export default Login
