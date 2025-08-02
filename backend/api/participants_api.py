from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel
from datetime import datetime, timedelta
import random, string

router = APIRouter()

ROOMS = {}  # 可以放檔案上方
participants = {}  # { room: [ { device_id, nickname, last_seen } ] }
room_status = {}
"""
{room_id: status}

狀態值：
- NotFound: 查無房間，會議室不存在
- Stop: 有房間 但處於暫停或終止狀態，暫無討論進行
- Discussion: 計時討論中，表示正在進行會議討論
- End: 會議已結束
"""
room_data = {}  # { room_id: { "topic": str, "countdown": int, "time_start": datetime, "comments": [ {nickname, content, ts} ] } }

class RoomCreate(BaseModel):
    title: str
    host: str

@router.post("/api/create_room")
def create_room(room: RoomCreate):
    """
    建立會議室

    [POST] /api/create_room

    描述：
    建立一個新的會議室，需提供會議室標題與主持人名稱。

    參數：
    - room.title (str): 會議室標題
    - room.host (str): 主持人名稱

    回傳：
    - code (str): 房間代碼
    """
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while code in ROOMS:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    ROOMS[code] = {
        "code": code,
        "title": room.title,
        "host": room.host,
        "created_at": datetime.now().isoformat(),
        "participants": 0,
        "settings": {"allowQuestions": True, "allowVoting": True}
    }
    # 初始化房間狀態為 Stop（有房間但暫停或終止狀態）
    room_status[code] = "Stop"
    return ROOMS[code]

@router.get("/api/rooms")
def get_rooms():
    """
    獲取所有會議室資訊

    [GET] /api/rooms

    描述：
    獲取所有已建立的會議室資訊。

    回傳：
    - rooms (list): 所有會議室的資訊列表，每個房間包含 code、title、host、created_at、participants、status。
    """
    # 將房間狀態加入到每個房間資訊中
    for room in ROOMS.values():
        room["status"] = room_status.get(room["code"], "NotFound")
    return {"rooms": list(ROOMS.values())}

class JoinRequest(BaseModel):
    room: str
    nickname: str
    device_id: str

@router.post("/api/participants/join")
def join_participant(data: JoinRequest):
    """
    參與者加入會議室
    
    [POST] /api/participants/join
    
    描述：
    參與者加入會議室，需提供房間代碼、暱稱與裝置ID。
    
    參數：
    - room (str): 房間代碼
    - nickname (str): 參與者暱稱
    - device_id (str): 參與者裝置ID
    
    回傳：
    - success (bool): 是否成功加入會議室
    """
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
    """
    參與者在線檢測
    
    [POST] /api/participants/heartbeat
    
    描述：
    用於檢測參與者是否在線，更新其最後一次活動時間。
    
    參數：
    - room (str): 房間代碼
    - device_id (str): 參與者裝置ID
    
    回傳：
    - success (bool): 是否成功更新心跳時間
    """
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
    """
    獲取房間內的在線參與者列表
    
    [GET] /api/participants
    
    描述：
    獲取指定房間內的在線參與者列表，僅返回在線的參與者資訊。
    
    參數：
    - room (str): 房間代碼

    回傳：
    - participants (list): 在線的參與者資訊
    """
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
    """
    設置房間狀態
    
    [POST] /api/room_status
    
    描述：
    設置指定房間的狀態，狀態值可以是 Stop、Discussion 或 End。
    
    參數：
    - room (str): 房間代碼
    - status (str): 房間狀態，必須是 Stop、Discussion 或 End
    
    返回值：
    - success (bool): 是否成功設置狀態
    - status (str): 當前房間狀態
    """
    # 驗證狀態值必須是有效的狀態之一
    if status not in ["Stop", "Discussion", "End"]:
        return {"success": True, "status": "NotFound"}
    
    room_status[room] = status
    return {"success": True, "status": status}

@router.get("/api/room_status")
def get_room_status(room: str):
    """
    獲取房間狀態
    
    [GET] /api/room_status
    
    描述：
    獲取指定房間的當前狀態。
    
    參數：
    - room (str): 房間代碼
    
    返回值：
    - status (str): 當前房間狀態，可能的值有 NotFound、Stop、Discussion 或 End
    """
    # 如果找不到房間狀態，預設為 NotFound
    return {"status": room_status.get(room, "NotFound")}

# 主持人設定主題與倒數
@router.post("/api/room_state")
def set_room_state(room: str = Body(...),
                   topic: str = Body(...),
                   countdown: int = Body(...),
                   time_start: float = Body(...)):
    """
    設定房間主題與倒數計時
    
    [POST] /api/room_state
    
    描述：
    設定指定房間的討論主題和倒數計時，並自動將房間狀態設為 Discussion（計時討論中）。
    
    參數：
    - room (str): 房間代碼
    - topic (str): 討論主題
    - countdown (int): 倒數計時秒數
    - time_start (float): 計時開始時間的 Unix 時間戳（秒）
    
    回傳：
    - success (bool): 是否成功設定主題與倒數
    - status (str): 當前房間狀態，應為 Discussion
    """
    from datetime import datetime
    if room not in room_data:
        room_data[room] = {"topic": "", "countdown": 0, "time_start": 0, "comments": []}
    
    # 更新房間資料
    room_data[room]["topic"] = topic
    room_data[room]["countdown"] = countdown
    room_data[room]["time_start"] = time_start
    
    # 當設定主題和倒數時，自動將房間狀態設為 Discussion
    room_status[room] = "Discussion"
    
    return {"success": True, "status": "Discussion"}

# 取得主題、倒數、留言
@router.get("/api/room_state")
def get_room_state(room: str):
    """
    取得房間狀態
    
    [GET] /api/room_state
    
    描述：
    取得指定房間的當前狀態，包括主題、倒數計時和留言。
    
    參數：
    - room (str): 房間代碼
    
    返回值：
    - topic (str): 當前討論主題
    - countdown (int): 剩餘倒數時間（秒）
    - comments (list): 當前房間的留言列表，每個留言包含 nickname、content 和 ts（時間戳）
    """
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

# 取得所有留言，回傳順序依 ts 時間升冪
@router.get("/api/room_comments")
def get_room_comments(room: str):
    """
    取得房間留言 
    
    [GET] /api/room_comments
    
    描述：
    取得指定房間的所有留言，並按照時間戳升冪排序。
    
    參數：
    - room (str): 房間代碼
    
    返回值：
    - comments (list): 房間的留言列表，每個留言包含 nickname、content 和 ts（時間戳）
    """
    comments = []
    if room in room_data:
        comments = sorted(room_data[room]["comments"], key=lambda x: x["ts"])
    return {"comments": comments}

@router.post("/api/room_comment")
def add_comment(data: CommentRequest):
    """
    新增留言
    
    [POST] /api/room_comment
    
    描述：
    在指定房間新增一則留言。
    
    參數：
    - room (str): 房間代碼
    - nickname (str): 使用者暱稱
    - content (str): 留言內容
    
    返回值：
    - success (bool): 是否成功新增留言
    """
    import time
    if data.room not in room_data:
        room_data[data.room] = {"topic": "", "countdown": 0, "time_start": 0, "comments": []}
    room_data[data.room]["comments"].append({
        "nickname": data.nickname,
        "content": data.content,
        "ts": time.time()
    })
    return {"success": True}

@router.get("/api/all_rooms")
def get_all_rooms():
    """
    取得所有房間資訊

    [GET] /api/all_rooms

    描述：
    獲取所有房間的資訊，包括房間代碼、標題和主持人名稱。

    返回值：
    - rooms (list): 所有房間的資訊列表，每個房間包含 room_id、title 和 host
    """
    return {"ROOMS": ROOMS, "participants": participants, "room_status": room_status, "room_data": room_data}