# Medication Leaflet Q&A - Web Frontend

A Next.js frontend for the Medication Leaflet Q&A RAG system, providing an intuitive interface for querying medication information from official labels.

## Features

- **Chat Interface**: Interactive Q&A with medication information
- **Drug Ingestion**: Upload and process new medication labels
- **System Evaluation**: Run performance evaluations and view metrics
- **Health Monitoring**: Real-time system health status
- **Responsive Design**: Mobile-first responsive layout
- **Type Safety**: Full TypeScript support with strict mode
- **Accessibility**: Semantic HTML and ARIA support

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS + shadcn/ui
- **Icons**: Lucide React
- **State Management**: React hooks (no external state library)
- **API**: Direct calls to FastAPI backend with optional proxy routes

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm
- Running FastAPI backend on port 8002

### Installation

From the project root:

```bash
# Install dependencies
pnpm install

# Start development server
pnpm --filter web dev
```

The app will be available at http://localhost:3000

### Environment Setup

Create `.env.local` in `apps/web/`:

```env
NEXT_PUBLIC_API_BASE=http://localhost:8002
NEXT_PUBLIC_APP_NAME="Medication Leaflet Q&A"
# NEXT_PUBLIC_API_KEY=your_api_key_here
```

## Available Scripts

```bash
# Development
pnpm --filter web dev          # Start dev server on port 3000

# Production
pnpm --filter web build        # Build for production
pnpm --filter web start        # Start production server

# Code Quality
pnpm --filter web lint         # Run ESLint
pnpm --filter web typecheck    # Run TypeScript checks
```

## Project Structure

```
apps/web/
├── app/                    # Next.js App Router
│   ├── api/               # Optional API proxy routes
│   ├── evals/             # Evaluation page
│   ├── ingest/            # Drug ingestion page
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Chat page (home)
├── src/
│   ├── components/        # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── header.tsx    # Navigation header
│   │   ├── footer.tsx    # Footer with disclaimer
│   │   └── ...           # Other components
│   ├── lib/              # Utilities
│   │   ├── env.ts        # Environment validation
│   │   ├── fetch.ts      # API client
│   │   └── utils.ts      # Helper functions
│   └── types/            # TypeScript types
│       └── api.ts        # API interfaces
├── public/               # Static assets
└── package.json
```

## API Integration

The frontend communicates with the FastAPI backend through:

- **Direct calls**: Default mode, calls backend directly
- **Proxy routes**: Optional, routes through Next.js API routes for CORS handling

### API Endpoints

- `POST /ask` - Submit questions about medications
- `POST /ingest` - Ingest new drug data
- `POST /eval/run` - Run system evaluations
- `GET /health` - Check system health

## Key Components

### Chat Interface (`app/page.tsx`)
- Message bubbles with citations
- Quick prompt buttons
- Drug-specific queries
- Session storage persistence
- Real-time typing indicators

### Drug Ingestion (`app/ingest/page.tsx`)
- Simple form for drug name input
- Recent ingestion history
- Progress indicators

### System Evaluation (`app/evals/page.tsx`)
- One-click evaluation runs
- Performance metrics display
- Raw results JSON viewer

### Health Monitoring
- Real-time system status
- Visual health indicators
- Automatic refresh

## Data Persistence

- **Chat messages**: Stored in `sessionStorage` (cleared on browser close)
- **Ingestion history**: Stored in `localStorage` (persistent across sessions)

## Accessibility Features

- Semantic HTML structure
- ARIA labels and descriptions
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- High contrast support

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Notes

- All components are under 200 LOC
- TypeScript strict mode enabled
- No `any` types allowed
- ESLint + Prettier configured
- Responsive design with mobile-first approach
- Error boundaries and loading states
- Proper error handling and user feedback

## Deployment

The app can be deployed to any platform that supports Next.js:

- Vercel (recommended)
- Netlify
- AWS Amplify
- Docker containers

Build command: `pnpm --filter web build`
Start command: `pnpm --filter web start`
