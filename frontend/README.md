# AI Health Intelligence Platform - Frontend

React + TypeScript frontend for the AI Health Intelligence Platform.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **API Client**: Axios
- **Authentication**: Firebase SDK
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with Firebase Web SDK configuration
```

3. Start development server:
```bash
npm run dev
```

4. Access at: http://localhost:3000

## Firebase Configuration

Get your Firebase Web SDK configuration from:
1. Firebase Console → Project Settings
2. General → Your apps → Web app
3. Copy configuration values to `.env`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/     # React components
├── pages/          # Page components
├── services/       # API and Firebase services
├── stores/         # Zustand state management
├── utils/          # Utility functions
├── types/          # TypeScript types
└── routes/         # React Router config
```

## Implementation Tasks

See `.kiro/specs/ai-health-frontend/tasks.md` for implementation tasks.

## API Integration

Backend API: http://localhost:8000

All API requests are proxied through Vite dev server.
