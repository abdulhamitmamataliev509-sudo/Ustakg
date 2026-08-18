# Usta kg — Web & Admin (Phase 6)

This folder contains a Next.js App Router application with public landing, categories and masters directories, and an Admin Panel under `/admin`.

Run locally:

```bash
cd web
npm install
npm run dev
```

Notes:
- API client uses `http://localhost:8000/api/v1` — adjust if backend runs elsewhere.
- Admin routes call `/auth/me` to verify `role === 'ADMIN'`.
