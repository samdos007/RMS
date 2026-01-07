# Investment Research Management System (RMS)

A local-first application for managing investment research, trade ideas, and earnings tracking.

## Features

- **Folder Organization**: Group research by single ticker or ticker pairs
- **Trade Ideas**: Track LONG, SHORT, or PAIR trades with thesis, targets, and stops
- **P&L Tracking**: Real-time P&L calculations with yfinance price integration
- **Earnings Tracking**: Log estimates vs actuals with visualization
- **Notes & Attachments**: Markdown notes and file attachments per idea
- **Search**: Global search across all notes

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 + SQLite
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + Recharts
- **Authentication**: Single-user password auth with bcrypt

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## Quick Start

### 1. Clone and Setup Environment

```bash
cd RMS

# Create Python virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# From project root
cp .env.example .env

# Edit .env and set a secure SECRET_KEY (minimum 32 characters)
```

### 3. Initialize Database

```bash
cd backend

# Run database migrations
alembic upgrade head
```

### 4. Start Backend Server

```bash
# From backend directory with venv activated
uvicorn app.main:app --reload --port 8000
```

### 5. Setup Frontend

```bash
# Open new terminal, from project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 6. Access Application

Open http://localhost:5173 in your browser.

On first visit, you'll be prompted to set up your password.

## Development

### Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run server with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Type checking
npm run typecheck

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
RMS/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/    # API route handlers
│   │   ├── database/         # SQLAlchemy setup
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── config.py         # Settings
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   └── tests/                # Backend tests
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── context/          # React context
│   │   ├── pages/            # Page components
│   │   └── types/            # TypeScript types
│   └── ...
└── data/                     # SQLite database & uploads (gitignored)
```

## P&L Calculations

### Single Ticker - LONG
```
P&L = (current_price - entry_price) / entry_price
```

### Single Ticker - SHORT
```
P&L = (entry_price - current_price) / entry_price
```

### Pair Trade (Log Spread)
```
P&L = ln(P_long / P_long_entry) - ln(P_short / P_short_entry)
```

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Data Storage

All data is stored locally:
- **Database**: `data/rms.db` (SQLite)
- **Uploads**: `data/uploads/` (file attachments)

## License

Private - All rights reserved
