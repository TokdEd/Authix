# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import auth
from db.database import init_db #xs

app = FastAPI(title="專案後端API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
    print("後端服務啟動中，正在初始化資料庫...")
    await init_db()
    print("資料庫初始化完成。")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "後端服務已成功啟動"}