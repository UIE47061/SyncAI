from fastapi import APIRouter, Request, Query, Body
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

participants = {}  # { room: [ { device_id, nickname, last_seen } ] }
room_status = {}  # { room_id: "waiting" or "discussion" }
room_data = {}  # { room_id: { "topic": str, "countdown": int, "time_start": datetime, "comments": [ {nickname, content, ts} ] } }

class JoinRequest(BaseModel):
    room: str
    nickname: str
    device_id: str

@router.post("/api/participants/join")
def join_participant(data: JoinRequest):
    room = data.room
    device_id = data.device_id
    nickname = data.nickname
    now = datetime.utcnow()
    if room not in participants:
        participants[room] = []
    # 先檢查 device_id 是否已存在
    found = None
    for p in participants[room]:
        if p['device_id'] == device_id:
            found = p
            break
    if found:
        found['last_seen'] = now
        found['nickname'] = nickname  # 更新暱稱
    else:
        participants[room].append({"device_id": device_id, "nickname": nickname, "last_seen": now})
    return {"success": True}

class HeartbeatRequest(BaseModel):
    room: str
    device_id: str

@router.post("/api/participants/heartbeat")
def participant_heartbeat(data: HeartbeatRequest):
    now = datetime.utcnow()
    room = data.room
    device_id = data.device_id
    for p in participants.get(room, []):
        if p['device_id'] == device_id:
            p['last_seen'] = now
            break
    return {"success": True}

@router.get("/api/participants")
def get_participants(room: str):
    now = datetime.utcnow()
    online = []
    if room in participants:
        print('DEBUG participants:', participants[room])  # 加這行
        online = [
            {"device_id": p["device_id"], "nickname": p["nickname"]}
            for p in participants[room]
            if (now - p["last_seen"]).total_seconds() <= 5
        ]
        participants[room] = [
            p for p in participants[room]
            if (now - p["last_seen"]).total_seconds() <= 30
        ]
    return {"participants": online}

@router.post("/api/room_status")
def set_room_status(room: str = Body(...), status: str = Body(...)):
    room_status[room] = status
    return {"success": True}

@router.get("/api/room_status")
def get_room_status(room: str):
    return {"status": room_status.get(room, "waiting")}

# 主持人設定主題與倒數
@router.post("/api/room_state")
def set_room_state(
    room: str = Body(...),
    topic: str = Body(...),
    countdown: int = Body(...),
    time_start: float = Body(...)
):
    from datetime import datetime
    if room not in room_data:
        room_data[room] = {"topic": "", "countdown": 0, "time_start": 0, "comments": []}
    room_data[room]["topic"] = topic
    room_data[room]["countdown"] = countdown
    room_data[room]["time_start"] = time_start
    return {"success": True}

# 取得主題、倒數、留言
@router.get("/api/room_state")
def get_room_state(room: str):
    import time
    data = room_data.get(room, {"topic": "", "countdown": 0, "time_start": 0, "comments": []})
    now = time.time()
    left = max(0, int(data["countdown"] - (now - data["time_start"]))) if data["time_start"] else 0
    return {
        "topic": data["topic"],
        "countdown": left,
        "comments": data["comments"]
    }

# 新增留言
class CommentRequest(BaseModel):
    room: str
    nickname: str
    content: str

@router.post("/api/room_comment")
def add_comment(data: CommentRequest):
    import time
    if data.room not in room_data:
        room_data[data.room] = {"topic": "", "countdown": 0, "time_start": 0, "comments": []}
    room_data[data.room]["comments"].append({
        "nickname": data.nickname,
        "content": data.content,
        "ts": time.time()
    })
    return {"success": True}
