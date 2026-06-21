# Frontend – Persona Style Analyzer

React + TypeScript + Vite frontend for the Arabic persona style analyzer API.

## Setup

```bash
cd frontend
npm install
npm run dev   # dev server on http://localhost:5173
npm run build # production build → dist/
```

The frontend proxies to `http://127.0.0.1:8000` (the FastAPI backend).

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Profiles | Default | View all extracted style profiles |
| Extract | Extract tab | Submit tweets → get style profile |
| Verify | Verify tab | Check if text matches an account's style |
| Generate | Generate tab | Generate text in an account's style |
