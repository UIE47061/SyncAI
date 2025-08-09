from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
import random, string, time

router = APIRouter()

# 時間處理輔助函數
def get_current_timestamp():
    """獲取當前時間戳"""
    return time.time()

def format_timestamp_for_display(timestamp):
    """將時間戳格式化為易讀格式 (用於調試和日誌)"""
    try:
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

# 簡化後的資料結構
ROOMS = {}
"""
{
    room_id: {
        "code": str,
        "title": str,
        "created_at": float,  # timestamp
        "settings": {"allowQuestions": bool, "allowVoting": bool},
        "status": str,  # NotFound, Stop, Discussion, End
        "participants": [{"device_id": str, "nickname": str, "last_seen": float}],  # timestamp
        "current_topic": str,
        "countdown": int,
        "time_start": float  # timestamp
    }
}
"""

topics = {}
"""
{
    topic_id: {
        "room_id": str,
        "topic_name": str,
        "comments": [{"id": str, "nickname": str, "content": str, "ts": float}]
    }
}
"""

votes = {}
"""
{
    comment_id: {
        "good": [device_id1, device_id2, ...],
        "bad": [device_id1, device_id2, ...]
    }
}
"""

class RoomCreate(BaseModel):
    title: str
    topic: str
    topic_summary: Optional[str] = None
    desired_outcome: Optional[str] = None
    topic_count: int = 1  # 1~5
    countdown: int = 15 * 60  # 預設15分鐘

@router.post("/api/create_room")
def create_room(room: RoomCreate):
    """
    建立會議室

    [POST] /api/create_room

    描述：
    建立一個新的會議室。

    參數：
    - room.title (str): 會議室標題
    - room.topic (str): 第一個主題名稱
    - room.topic_summary (str, 選填): 題目摘要資訊
    - room.desired_outcome (str, 選填): 想達到效果
    - room.topic_count (int): 問題/主題數量 (1~5)
    - room.countdown (int): 預設倒數時間（秒）

    回傳：
    - code (str): 房間代碼
    """
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while code in ROOMS:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    # 正規化輸入
    title = room.title.strip()
    topic = room.topic.strip() or "主題 1"
    topic_count = max(1, min(5, int(room.topic_count or 1)))
    countdown = int(room.countdown or 0)
    countdown = max(0, countdown)

    ROOMS[code] = {
        "code": code,
        "title": title,
        "created_at": get_current_timestamp(),
        "participants": 0,
        "settings": {"allowQuestions": True, "allowVoting": True},
        "status": "Stop",  # 初始化房間狀態為 Stop
        "participants_list": [],  # 參與者列表
        "current_topic": topic,
        "countdown": countdown,
        "time_start": 0,
        # 新增建立時的描述資訊與預設時長
        "topic_summary": (room.topic_summary or "").strip(),
        "desired_outcome": (room.desired_outcome or "").strip(),
        "topic_count": topic_count,
    }
    # 建立主題列表：第一個使用指定題目，其餘為 主題 2..N
    # 第一個主題
    topics[f"{code}_{topic}"] = {
        "room_id": code,
        "topic_name": topic,
        "comments": [],
    }
    # 額外主題
    for i in range(2, topic_count + 1):
        tname = f"主題 {i}"
        topics[f"{code}_{tname}"] = {
            "room_id": code,
            "topic_name": tname,
            "comments": [],
        }
    return {
        "code": ROOMS[code]["code"],
        "title": ROOMS[code]["title"],
        "created_at": ROOMS[code]["created_at"],
        "participants": ROOMS[code]["participants"],
        "settings": ROOMS[code]["settings"]
    }

@router.get("/api/rooms")
def get_rooms():
    """
    獲取所有會議室資訊

    [GET] /api/rooms

    描述：
    獲取所有已建立的會議室資訊。

    回傳：
    - rooms (list): 所有會議室的資訊列表，每個房間包含 code、title、created_at、participants、status、current_topic、topic_count、topic_summary、desired_outcome、countdown。
    """
    # 將房間狀態加入到每個房間資訊中
    rooms = []
    for room in ROOMS.values():
        room_info = {
            "code": room["code"],
            "title": room["title"],
            "created_at": room["created_at"],
            "participants": room["participants"],
            "status": room["status"],
            "current_topic": room.get("current_topic", ""),
            "topic_count": room.get("topic_count", 1),
            "topic_summary": room.get("topic_summary", ""),
            "desired_outcome": room.get("desired_outcome", ""),
            "countdown": room.get("countdown", 0),
        }
        rooms.append(room_info)
    return {"rooms": rooms}

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
    now = get_current_timestamp()
    
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 初始化參與者列表
    if "participants_list" not in ROOMS[room]:
        ROOMS[room]["participants_list"] = []
    
    # 先檢查 device_id 是否已存在
    found = None
    for p in ROOMS[room]["participants_list"]:
        if p['device_id'] == device_id:
            found = p
            break
    
    if found:
        found['last_seen'] = now
        found['nickname'] = nickname  # 更新暱稱
    else:
        ROOMS[room]["participants_list"].append({"device_id": device_id, "nickname": nickname, "last_seen": now})

    # 更新房間參與者人數（以在線人數為準，10秒內視為在線）
    try:
        online_count = sum(1 for p in ROOMS[room]["participants_list"] if (now - p["last_seen"]) <= 10)
        ROOMS[room]["participants"] = online_count
    except Exception:
        # 後備：若出錯則使用列表長度
        ROOMS[room]["participants"] = len(ROOMS[room].get("participants_list", []))

    return {"success": True}

class HeartbeatRequest(BaseModel):
    room: str
    device_id: str

class SwitchTopicRequest(BaseModel):
    room: str
    topic: str

class RenameTopicRequest(BaseModel):
    room: str
    old_topic: str
    new_topic: str

class DeleteTopicCommentsRequest(BaseModel):
    room: str
    topic: str

class UpdateNicknameRequest(BaseModel):
    room: str
    device_id: str
    old_nickname: str
    new_nickname: str

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
    now = get_current_timestamp()
    room = data.room
    device_id = data.device_id
    
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    if "participants_list" not in ROOMS[room]:
        ROOMS[room]["participants_list"] = []
    
    for p in ROOMS[room]["participants_list"]:
        if p['device_id'] == device_id:
            p['last_seen'] = now
            break
    # 更新在線人數
    try:
        online_count = sum(1 for p in ROOMS[room]["participants_list"] if (now - p["last_seen"]) <= 10)
        ROOMS[room]["participants"] = online_count
    except Exception:
        ROOMS[room]["participants"] = len(ROOMS[room].get("participants_list", []))
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
    now = get_current_timestamp()
    online = []
    
    if room in ROOMS and "participants_list" in ROOMS[room]:
        online = [
            {"device_id": p["device_id"], "nickname": p["nickname"]}
            for p in ROOMS[room]["participants_list"]
            if (now - p["last_seen"]) <= 10
        ]
        ROOMS[room]["participants_list"] = [
            p for p in ROOMS[room]["participants_list"]
            if (now - p["last_seen"]) <= 30
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
    
    if room not in ROOMS:
        return {"success": True, "status": "NotFound"}
    
    ROOMS[room]["status"] = status
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
    if room not in ROOMS:
        return {"status": "NotFound"}
    return {"status": ROOMS[room]["status"]}

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
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 更新房間資料
    ROOMS[room]["current_topic"] = topic
    ROOMS[room]["countdown"] = countdown
    ROOMS[room]["time_start"] = time_start
    
    # 創建主題ID並確保主題存在於 topics 字典中
    topic_id = f"{room}_{topic}"
    if topic_id not in topics:
        topics[topic_id] = {
            "room_id": room,
            "topic_name": topic,
            "comments": []
        }
    
    # 當設定主題和倒數時，自動將房間狀態設為 Discussion
    ROOMS[room]["status"] = "Discussion"
    
    return {"success": True, "status": "Discussion"}

@router.post("/api/room_switch_topic")
def switch_topic(data: SwitchTopicRequest):
    """
    切換房間主題
    
    [POST] /api/room_switch_topic
    
    描述：
    切換指定房間的討論主題，保持原有的倒數計時和房間狀態不變。
    
    參數：
    - room (str): 房間代碼
    - topic (str): 新的討論主題
    
    回傳：
    - success (bool): 是否成功切換主題
    - topic (str): 當前主題名稱
    - status (str): 當前房間狀態
    """
    room = data.room
    topic = data.topic
    
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 更新房間的當前主題
    ROOMS[room]["current_topic"] = topic
    
    # 創建主題ID並確保主題存在於 topics 字典中
    topic_id = f"{room}_{topic}"
    if topic_id not in topics:
        topics[topic_id] = {
            "room_id": room,
            "topic_name": topic,
            "comments": []
        }
    
    return {
        "success": True, 
        "topic": topic,
        "status": ROOMS[room]["status"]
    }

@router.post("/api/room_rename_topic")
def rename_topic(data: RenameTopicRequest):
    """
    重新命名房間主題
    
    [POST] /api/room_rename_topic
    
    描述：
    重新命名指定房間的主題，會更新主題名稱並保留所有評論和投票記錄。
    如果重命名的是當前主題，則會同時更新房間的當前主題。
    
    參數：
    - room (str): 房間代碼
    - old_topic (str): 原主題名稱
    - new_topic (str): 新主題名稱
    
    回傳：
    - success (bool): 是否成功重新命名主題
    - old_topic (str): 原主題名稱
    - new_topic (str): 新主題名稱
    - is_current_topic (bool): 是否為當前主題
    """
    room = data.room
    old_topic = data.old_topic
    new_topic = data.new_topic
    
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    if not old_topic or not new_topic:
        return {"success": False, "error": "主題名稱不能為空"}
    
    # 檢查舊主題是否存在
    old_topic_id = f"{room}_{old_topic}"
    if old_topic_id not in topics:
        return {"success": False, "error": "原主題不存在"}
    
    # 檢查新主題名稱是否已存在
    new_topic_id = f"{room}_{new_topic}"
    if new_topic_id in topics:
        return {"success": False, "error": "新主題名稱已存在"}
    
    # 執行重命名操作
    # 1. 複製舊主題資料到新主題ID
    topics[new_topic_id] = {
        "room_id": room,
        "topic_name": new_topic,
        "comments": topics[old_topic_id]["comments"]
    }
    
    # 2. 刪除舊主題
    del topics[old_topic_id]
    
    # 3. 檢查是否為當前主題，如果是則更新房間的當前主題
    is_current_topic = False
    if ROOMS[room]["current_topic"] == old_topic:
        ROOMS[room]["current_topic"] = new_topic
        is_current_topic = True
    
    return {
        "success": True,
        "old_topic": old_topic,
        "new_topic": new_topic,
        "is_current_topic": is_current_topic
    }

@router.delete("/api/room_topic_comments")
def delete_topic_comments(data: DeleteTopicCommentsRequest):
    """
    刪除指定房間主題的所有評論
    
    [DELETE] /api/room_topic_comments
    
    描述：
    刪除指定房間中指定主題的所有評論，同時清除相關的投票記錄。
    如果刪除的是當前主題的評論，會清空當前主題的所有討論內容。
    
    參數：
    - room (str): 房間代碼
    - topic (str): 主題名稱
    
    回傳：
    - success (bool): 是否成功刪除評論
    - topic (str): 被清空的主題名稱
    - deleted_comments_count (int): 刪除的評論數量
    - deleted_votes_count (int): 刪除的投票記錄數量
    """
    room = data.room
    topic = data.topic
    
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    if not topic:
        return {"success": False, "error": "主題名稱不能為空"}
    
    # 檢查主題是否存在
    topic_id = f"{room}_{topic}"
    if topic_id not in topics:
        return {"success": False, "error": "主題不存在"}
    
    # 統計將要刪除的評論和投票數量
    comments = topics[topic_id]["comments"]
    deleted_comments_count = len(comments)
    deleted_votes_count = 0
    
    # 刪除所有相關的投票記錄
    for comment in comments:
        comment_id = comment["id"]
        if comment_id in votes:
            # 統計投票數量
            deleted_votes_count += len(votes[comment_id].get("good", []))
            deleted_votes_count += len(votes[comment_id].get("bad", []))
            # 刪除投票記錄
            del votes[comment_id]
    
    # 清空主題的評論列表
    topics[topic_id]["comments"] = []
    
    return {
        "success": True,
        "topic": topic,
        "deleted_comments_count": deleted_comments_count,
        "deleted_votes_count": deleted_votes_count,
    }

# 取得主題、倒數、留言
@router.get("/api/room_state")
def get_room_state(room: str):
    """
    取得房間狀態
    
    [GET] /api/room_state
    
    描述：
    取得指定房間的當前狀態，包括主題、倒數計時和當前主題的留言。
    
    參數：
    - room (str): 房間代碼
    
    返回值：
    - topic (str): 當前討論主題
    - countdown (int): 剩餘倒數時間（秒）
    - comments (list): 當前主題的留言列表，每個留言包含 nickname、content 和 ts（時間戳）
    """
    if room not in ROOMS:
        return {"topic": "", "countdown": 0, "comments": []}
    
    room_info = ROOMS[room]
    
    # 檢查房間狀態，如果房間已結束或停止，倒數計時應為0
    current_status = room_info["status"]
    if current_status in ["End", "Stop", "NotFound"]:
        left = 0
    else:
        now = get_current_timestamp()
        left = max(0, int(room_info["countdown"] - (now - room_info["time_start"]))) if room_info["time_start"] else 0
    
    # 獲取當前主題的評論
    current_topic = room_info["current_topic"]
    current_comments = []
    if current_topic:
        topic_id = f"{room}_{current_topic}"
        if topic_id in topics:
            # 計算投票數並添加到留言中
            comments_with_votes = []
            for comment in topics[topic_id]["comments"]:
                comment_id = comment["id"]
                vote_good = len(votes.get(comment_id, {}).get("good", []))
                vote_bad = len(votes.get(comment_id, {}).get("bad", []))
                
                comment_with_votes = comment.copy()
                comment_with_votes["vote_good"] = vote_good
                comment_with_votes["vote_bad"] = vote_bad
                comment_with_votes["votes"] = vote_good
                comments_with_votes.append(comment_with_votes)
            
            current_comments = comments_with_votes
    
    return {
        "topic": current_topic,
        "countdown": left,
        "comments": current_comments
    }

# 新增留言
class CommentRequest(BaseModel):
    room: str
    nickname: str
    content: str

class VoteRequest(BaseModel):
    room: str
    comment_id: str
    device_id: str
    vote_type: str  # "good" 或 "bad"

class DeleteCommentRequest(BaseModel):
    room: str
    comment_id: str

# 取得所有留言，回傳順序依 ts 時間升冪
@router.get("/api/room_comments")
def get_room_comments(room: str):
    """
    取得房間當前主題的留言 
    
    [GET] /api/room_comments
    
    描述：
    取得指定房間當前主題的所有留言，並按照時間戳升冪排序。
    
    參數：
    - room (str): 房間代碼
    
    返回值：
    - comments (list): 當前主題的留言列表，每個留言包含 nickname、content 和 ts（時間戳）
    """
    comments = []
    if room in ROOMS:
        current_topic = ROOMS[room]["current_topic"]
        if current_topic:
            topic_id = f"{room}_{current_topic}"
            if topic_id in topics:
                # 獲取留言並計算投票數
                comments_with_votes = []
                for comment in topics[topic_id]["comments"]:
                    comment_id = comment["id"]
                    vote_good = len(votes.get(comment_id, {}).get("good", []))
                    vote_bad = len(votes.get(comment_id, {}).get("bad", []))
                    
                    comment_with_votes = comment.copy()
                    comment_with_votes["vote_good"] = vote_good
                    comment_with_votes["vote_bad"] = vote_bad
                    comment_with_votes["votes"] = vote_good
                    comments_with_votes.append(comment_with_votes)
                
                comments = sorted(comments_with_votes, key=lambda x: x["ts"])
    
    return {"comments": comments}

@router.post("/api/room_comment")
def add_comment(data: CommentRequest):
    """
    新增留言到當前主題
    
    [POST] /api/room_comment
    
    描述：
    在指定房間的當前主題下新增一則留言。
    
    參數：
    - room (str): 房間代碼
    - nickname (str): 使用者暱稱
    - content (str): 留言內容
    
    返回值：
    - success (bool): 是否成功新增留言
    - comment_id (str): 新增留言的ID
    """
    import uuid
    
    if data.room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 獲取當前主題
    current_topic = ROOMS[data.room]["current_topic"]
    if not current_topic:
        return {"success": False, "error": "目前沒有設定主題"}
    
    # 確保主題存在
    topic_id = f"{data.room}_{current_topic}"
    if topic_id not in topics:
        topics[topic_id] = {
            "room_id": data.room,
            "topic_name": current_topic,
            "comments": []
        }
    
    comment_id = str(uuid.uuid4())
    new_comment = {
        "id": comment_id,
        "nickname": data.nickname,
        "content": data.content,
        "ts": get_current_timestamp()
    }
    
    topics[topic_id]["comments"].append(new_comment)
    return {"success": True, "comment_id": comment_id}

@router.delete("/api/room_comment_single")
def delete_comment_single(data: DeleteCommentRequest):
    """
    刪除單一留言與其投票紀錄

    [DELETE] /api/room_comment_single

    描述：
    傳入房號與留言 ID，刪除該留言與其所有投票紀錄（good/bad）。

    參數：
    - room (str): 房間代碼
    - comment_id (str): 留言ID

    回傳：
    - success (bool): 是否刪除成功
    - comment_id (str): 已刪除的留言ID
    - topic (str): 所屬主題名稱（若找到）
    - deleted_votes_count (int): 被清除的投票紀錄數量
    """
    room = (data.room or "").strip()
    comment_id = (data.comment_id or "").strip()

    if not room or not comment_id:
        return {"success": False, "error": "參數不完整"}

    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}

    # 在該房間的所有主題中尋找該留言
    found = False
    affected_topic_name = None

    for topic_key, topic_obj in list(topics.items()):
        if topic_obj.get("room_id") != room:
            continue
        comments_list = topic_obj.get("comments", [])
        # 找到索引以便安全移除
        idx = next((i for i, c in enumerate(comments_list) if c.get("id") == comment_id), None)
        if idx is not None:
            # 紀錄主題名稱（若不存在則回傳空字串）
            affected_topic_name = topic_obj.get("topic_name", "")
            # 移除該留言
            comments_list.pop(idx)
            found = True
            break

    if not found:
        return {"success": False, "error": "留言不存在"}

    # 刪除對應投票紀錄
    deleted_votes_count = 0
    if comment_id in votes:
        deleted_votes_count += len(votes[comment_id].get("good", []))
        deleted_votes_count += len(votes[comment_id].get("bad", []))
        del votes[comment_id]

    return {
        "success": True,
        "comment_id": comment_id,
        "topic": affected_topic_name or "",
        "deleted_votes_count": deleted_votes_count,
    }

# 投票功能
@router.post("/api/questions/vote")
def vote_comment(data: VoteRequest):
    """
    為留言投票
    
    [POST] /api/questions/vote
    
    描述：
    為指定留言投好評或差評票，每個設備ID只能為同一則留言的同一類型投票一次。
    
    參數：
    - room (str): 房間代碼
    - comment_id (str): 留言ID
    - device_id (str): 設備ID
    - vote_type (str): 投票類型，"good" 或 "bad"
    
    返回值：
    - success (bool): 是否成功投票
    - vote_good (int): 該留言的好評票數
    - vote_bad (int): 該留言的差評票數
    - already_voted (bool): 是否已經投過該類型的票
    """
    room = data.room
    comment_id = data.comment_id
    device_id = data.device_id
    vote_type = data.vote_type
    
    # 驗證投票類型
    if vote_type not in ["good", "bad"]:
        return {"success": False, "error": "無效的投票類型"}
    
    # 檢查房間是否存在
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 找到對應的留言
    comment = None
    current_topic = ROOMS[room]["current_topic"]
    if current_topic:
        topic_id = f"{room}_{current_topic}"
        if topic_id in topics:
            for c in topics[topic_id]["comments"]:
                if c["id"] == comment_id:
                    comment = c
                    break
    
    if not comment:
        return {"success": False, "error": "留言不存在"}
    
    # 初始化投票記錄
    if comment_id not in votes:
        votes[comment_id] = {"good": [], "bad": []}
    
    # 檢查是否已經投過該類型的票
    if device_id in votes[comment_id][vote_type]:
        return {
            "success": False, 
            "already_voted": True, 
            "vote_good": len(votes[comment_id]["good"]),
            "vote_bad": len(votes[comment_id]["bad"])
        }
    
    # 檢查是否投過相反類型的票，如果有則先移除
    opposite_type = "bad" if vote_type == "good" else "good"
    if device_id in votes[comment_id][opposite_type]:
        votes[comment_id][opposite_type].remove(device_id)
    
    # 添加投票記錄
    votes[comment_id][vote_type].append(device_id)
    
    vote_good = len(votes[comment_id]["good"])
    vote_bad = len(votes[comment_id]["bad"])
    
    return {
        "success": True, 
        "vote_good": vote_good, 
        "vote_bad": vote_bad,
        "already_voted": False
    }

@router.delete("/api/questions/vote")
def remove_vote_comment(data: VoteRequest):
    """
    取消投票
    
    [DELETE] /api/questions/vote
    
    描述：
    取消對指定留言的指定類型投票。
    
    參數：
    - room (str): 房間代碼
    - comment_id (str): 留言ID
    - device_id (str): 設備ID
    - vote_type (str): 投票類型，"good" 或 "bad"
    
    返回值：
    - success (bool): 是否成功取消投票
    - vote_good (int): 該留言的好評票數
    - vote_bad (int): 該留言的差評票數
    """
    room = data.room
    comment_id = data.comment_id
    device_id = data.device_id
    vote_type = data.vote_type
    
    # 驗證投票類型
    if vote_type not in ["good", "bad"]:
        return {"success": False, "error": "無效的投票類型"}
    
    # 檢查房間是否存在
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 找到對應的留言
    comment = None
    current_topic = ROOMS[room]["current_topic"]
    if current_topic:
        topic_id = f"{room}_{current_topic}"
        if topic_id in topics:
            for c in topics[topic_id]["comments"]:
                if c["id"] == comment_id:
                    comment = c
                    break
    
    if not comment:
        return {"success": False, "error": "留言不存在"}
    
    # 檢查是否有投票記錄
    if comment_id not in votes or device_id not in votes[comment_id][vote_type]:
        return {"success": False, "error": "未找到投票記錄"}
    
    # 移除投票記錄
    votes[comment_id][vote_type].remove(device_id)
    
    vote_good = len(votes[comment_id]["good"])
    vote_bad = len(votes[comment_id]["bad"])
    
    return {
        "success": True, 
        "vote_good": vote_good, 
        "vote_bad": vote_bad
    }

@router.get("/api/questions/votes")
def get_user_votes(room: str, device_id: str):
    """
    獲取用戶的投票記錄
    
    [GET] /api/questions/votes
    
    描述：
    獲取指定設備在指定房間的所有投票記錄。
    
    參數：
    - room (str): 房間代碼
    - device_id (str): 設備ID
    
    返回值：
    - voted_good (list): 已投好評的留言ID列表
    - voted_bad (list): 已投差評的留言ID列表
    """
    voted_good = []
    voted_bad = []
    
    # 檢查該房間當前主題的所有留言
    if room in ROOMS:
        current_topic = ROOMS[room]["current_topic"]
        if current_topic:
            topic_id = f"{room}_{current_topic}"
            if topic_id in topics:
                for comment in topics[topic_id]["comments"]:
                    comment_id = comment["id"]
                    if comment_id in votes:
                        if device_id in votes[comment_id].get("good", []):
                            voted_good.append(comment_id)
                        if device_id in votes[comment_id].get("bad", []):
                            voted_bad.append(comment_id)
    
    return {"voted_good": voted_good, "voted_bad": voted_bad}

@router.post("/api/participants/update_nickname")
def update_participant_nickname(data: UpdateNicknameRequest):
    """
    更新參與者暱稱
    
    [POST] /api/participants/update_nickname
    
    描述：
    更新指定參與者的暱稱，同時會更新該參與者在當前主題下所有留言的暱稱顯示。
    
    參數：
    - room (str): 房間代碼
    - device_id (str): 參與者裝置ID
    - old_nickname (str): 舊暱稱
    - new_nickname (str): 新暱稱
    
    回傳：
    - success (bool): 是否成功更新暱稱
    - new_nickname (str): 更新後的暱稱
    - updated_comments_count (int): 更新的留言數量
    """
    room = data.room
    device_id = data.device_id
    old_nickname = data.old_nickname
    new_nickname = data.new_nickname.strip()
    
    # 驗證輸入
    if not new_nickname:
        return {"success": False, "error": "暱稱不能為空"}
    
    if len(new_nickname) > 10:
        return {"success": False, "error": "暱稱不能超過10個字元"}

    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 更新參與者列表中的暱稱
    participant_found = False
    if "participants_list" in ROOMS[room]:
        for p in ROOMS[room]["participants_list"]:
            if p['device_id'] == device_id:
                p['nickname'] = new_nickname
                participant_found = True
                break
    
    if not participant_found:
        return {"success": False, "error": "參與者不存在"}
    
    # 更新當前主題下該用戶所有留言的暱稱
    updated_comments_count = 0
    for topic in list(topics.keys()):
        if topic.find(room) != -1:
            topic_id = topic
            for comment in topics[topic_id]["comments"]:
                # 通過暱稱匹配更新（因為留言中沒有直接存儲device_id）
                if comment["nickname"] == old_nickname:
                    comment["nickname"] = new_nickname
                    updated_comments_count += 1
    
    return {
        "success": True,
        "new_nickname": new_nickname,
        "updated_comments_count": updated_comments_count
    }

@router.get("/api/all_rooms")
def get_all_rooms():
    """
    取得所有房間資訊

    [GET] /api/all_rooms

    描述：
    獲取所有房間的資訊（調試用）。

    返回值：
    - rooms (list): 所有房間的資訊列表
    - topics (list): 所有主題的資訊列表
    - votes (dict): 所有投票的資訊
    """
    return {
        "ROOMS": ROOMS, 
        "topics": topics, 
        "votes": votes
    }

class AllowJoinRequest(BaseModel):
    room: str
    allow_join: bool

class UpdateRoomInfoRequest(BaseModel):
    room: str
    new_title: str
    new_summary: Optional[str] = None

# 修改房間資訊
@router.post("/api/room_update_info")
def update_room_info(data: UpdateRoomInfoRequest):
    """
    修改房間資訊

    [POST] /api/room_update_info

    描述：
    修改指定房間的名稱與摘要資訊。

    參數：
    - room (str): 房間代碼
    - new_title (str): 新的房間名稱
    - new_summary (str): 新的題目摘要資訊（可為空字串）

    回傳：
    - success (bool): 是否成功修改
    - room_code (str): 房間代碼
    - new_title (str): 新房間名稱
    """
    room = data.room.strip()
    new_title = data.new_title.strip()
    new_summary = None if data.new_summary is None else (data.new_summary or "").strip()
    
    # 驗證輸入
    if not room:
        return {"success": False, "error": "房間代碼不能為空"}
    
    if not new_title:
        return {"success": False, "error": "房間名稱不能為空"}
        
    if len(new_title) > 50:
        return {"success": False, "error": "房間名稱不能超過50個字元"}
    
    # 限制摘要長度，避免過長內容
    if new_summary is not None and len(new_summary) > 2000:
        return {"success": False, "error": "摘要資訊不能超過2000個字元"}

    # 檢查房間是否存在
    if room not in ROOMS:
        return {"success": False, "error": "房間不存在"}
    
    # 更新房間資訊
    ROOMS[room]["title"] = new_title
    if new_summary is not None:
        ROOMS[room]["topic_summary"] = new_summary
    
    return {
        "success": True,
        "room_code": room,
        "new_title": new_title,
        "topic_summary": ROOMS[room].get("topic_summary", "")
    }

# 設定房間是否允許新參與者加入
@router.post("/api/room_allow_join")
def set_room_allow_join(data: AllowJoinRequest):
    """
    設定房間是否允許新參與者加入

    [POST] /api/room_allow_join

    描述：
    根據傳入的參數設定房間是否允許新參與者加入。

    參數：
    - room (str): 房間代碼
    - allow_join (bool): 是否允許加入

    回傳：
    - success (bool): 是否成功設定
    - allow_join (bool): 當前允許加入的狀態
    """
    if data.room not in ROOMS:
        return {"success": False, "error": "房間不存在"}

    ROOMS[data.room]["allow_join"] = data.allow_join
    return {"success": True, "allow_join": data.allow_join}