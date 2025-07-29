# backend/api/utility.py
from fastapi import APIRouter
import socket

router = APIRouter()

@router.get("/api/hostip")
def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 不需實際連外，只為自動取得區網 IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return {"ip": ip}
