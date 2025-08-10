# Authix

FastAPI + React minimal auth example (JWT, async SQLAlchemy, CORS). Default DB is SQLite; switchable via env.

- Frontend: React 18 (CRA), `react-router-dom`, `three`, `ogl`, `framer-motion`
- Backend: FastAPI, async SQLAlchemy, JWT (HS256)

## Quick Start

Backend (API):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# set env in backend/.env (see below)
uvicorn main:app --reload --port 8000
```

Frontend (Web):
```bash
cd frontend
npm install
npm start
```

- API: http://localhost:8000
- Web: http://localhost:3000

## Env Vars (backend/.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
JWT_SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
- Use Postgres: `postgresql+asyncpg://user:pass@host:5432/db`.

## PREVIEW

- ![Login](./assets/login.png)

- ![Register](./assets/register.png)

## Notes
- CORS allows `http://localhost:3000` (adjust in `backend/main.py`).
- DB tables auto-created on startup.

## License
[LICENSE](LICENSE)
