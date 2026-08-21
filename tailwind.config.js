/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        void: {
          DEFAULT: '#050A12',
          soft: '#0A121D',
        },
        panel: {
          DEFAULT: '#0D1826',
          border: '#1B3A5C',
          hair: '#152538',
        },
        signal: {
          blue: '#2E9BFF',
          cyan: '#22D3EE',
          dim: '#3E6690',
        },
        status: {
          danger: '#FF3B4E',
          amber: '#FFB020',
          safe: '#22C55E',
        },
        ink: {
          primary: '#E7EDF6',
          muted: '#7D93AC',
          faint: '#4C617A',
        },
      },
      fontFamily: {
        display: ['"Rajdhani"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        console: '0 0 0 1px rgba(46,155,255,0.08), 0 20px 60px -20px rgba(0,0,0,0.8)',
        glow: '0 0 16px rgba(46,155,255,0.35)',
        'glow-red': '0 0 12px rgba(255,59,78,0.55)',
        'glow-amber': '0 0 12px rgba(255,176,32,0.5)',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        blink: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.35 },
        },
        scanline: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '0 -200px' },
        },
      },
      animation: {
        sweep: 'sweep 4s linear infinite',
        blink: 'blink 1.8s ease-in-out infinite',
        scan: 'scanline 6s linear infinite',
      },
    },
  },
  plugins: [],
}
