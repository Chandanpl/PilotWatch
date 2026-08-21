# PilotWatch — Loco Cabin Display

Frontend-only React application for a railway safety monitoring dashboard. No backend, no API calls — all values are placeholders representing an offline/disconnected state.

## Stack
- React 18 + React Router 6
- Tailwind CSS
- Lucide React icons
- Vite

## Getting started

```bash
npm install
npm run dev
```

Then open the printed local URL. The app starts on the Login page (`/`); any credentials submit successfully (authentication is simulated) and route to `/loco-dashboard`. Logout returns to `/`.

## Build

```bash
npm run build
```

## Project structure

```
src/
├── components/
│   ├── Header.jsx
│   ├── CameraPanel.jsx
│   ├── StatusCard.jsx
│   ├── AlertPanel.jsx
│   └── Footer.jsx
├── pages/
│   ├── Login.jsx
│   └── LocoDashboard.jsx
├── routes/
│   └── AppRoutes.jsx
├── App.jsx
├── main.jsx
└── index.css
```
