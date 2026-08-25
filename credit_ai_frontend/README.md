# Credit AI Frontend

Modern React chatbot UI for company credit analysis.

## Setup

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Backend APIs

Ensure these services are running:

- **Chat API**: `http://127.0.0.1:8001/chat`
- **Search API**: `http://127.0.0.1:3000/search_company`

Vite dev server proxies requests to avoid CORS:

- `/api/chat` → chat API
- `/api/search` → search API

## Usage

1. Search for a company in the left sidebar (e.g. "Coca", "Godrej")
2. Click a result to select it
3. Ask a question or use a suggested prompt
4. View the markdown-formatted credit analysis with progress tracking

## Stack

- React + Vite (JavaScript)
- Tailwind CSS v4
- shadcn/ui components
- react-markdown + remark-gfm
