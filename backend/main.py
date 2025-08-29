# backend/main.py
from fastapi import FastAPI
from backend.api import ai_api
from fastapi.middleware.cors import CORSMiddleware
from backend.api import participants_api
from backend.api import network_api

app = FastAPI(title="MBBuddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://localhost:5173", "http://192.168.0.214:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(participants_api.router)
app.include_router(ai_api.router)
app.include_router(network_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
