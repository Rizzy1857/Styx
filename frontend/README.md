# STYX Frontend

React + Vite + Tailwind CSS frontend for API Lifecycle Intelligence.

## Setup

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Structure

- `/src/pages/` - Page components (Inventory, Security, Graph, etc.)
- `/src/components/` - Reusable React components
- `/src/services/api.js` - Axios API client
- `/src/utils/formatters.js` - Display formatting utilities

## Development

- `npm run dev` - Start dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Architecture

- **Inventory**: View and filter all APIs
- **Security**: OWASP findings and security posture
- **Dependencies**: D3.js graph visualization
- **Simulator**: Blast radius impact analysis
- **Alerts**: Real-time alert feed
