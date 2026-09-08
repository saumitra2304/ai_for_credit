# Credit AI frontend

React + Vite UI for Kuber. In production it is hosted on Vercel and talks to the EC2 API.

## Local

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api/*` to the local backend.

Optional: copy `.env.example` to `.env` and set `VITE_API_URL` if the API is not on the same origin.

## Production

See [../deploy/README.md](../deploy/README.md). Set `VITE_API_URL=https://api.yourdomain.com` in Vercel.
