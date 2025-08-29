# backend/api/network_api.py
from fastapi import APIRouter
import socket

router = APIRouter(tags=["Network"])

@router.get("/api/hostip")
def get_host_ip():
    """
    取得主機的本地網路IP位址
    
    Returns:
        dict: 包含IP位址的字典
    """
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

@router.get("/api/network/info")
def get_network_info():
    """
    取得網路相關資訊
    
    Returns:
        dict: 包含網路資訊的字典
    """
    import platform
    
    # 取得主機IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    
    # 取得主機名稱
    hostname = socket.gethostname()
    
    # 取得系統資訊
    system_info = {
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform()
    }
    
    return {
        "local_ip": local_ip,
        "hostname": hostname,
        "system_info": system_info
    }
