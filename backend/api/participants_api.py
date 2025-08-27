from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
import random, string, time, datetime, uuid
from fastapi.responses import StreamingResponse, JSONResponse
import io
import platform
from urllib.parse import quote
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import navy, black, gray

# --- Pydantic Models for RESTful API ---
class CommentRequest(BaseModel):
    nickname: str
    content: str
    isAISummary: Optional[bool] = False

class VoteRequest(BaseModel):
    device_id: str
    vote_type: str

class UpdateNicknameRequest(BaseModel):
    new_nickname: str
    old_nickname: Optional[str] = None

class TopicUpdateRequest(BaseModel):
    topic: str

class RenameTopicRequest(BaseModel):
    old_topic: str
    new_topic: str

# --- Pydantic Models for older/specific APIs ---
class RoomCreate(BaseModel):
    title: str
    topics: List[str]
    topic_summary: Optional[str] = None
    desired_outcome: Optional[str] = None
    topic_count: int
    countdown: int = 15 * 60

class AddTopicsRequest(BaseModel):
    room: str
    topics: List[str]

class JoinRequest(BaseModel):
    room: str
    nickname: str
    device_id: str

class HeartbeatRequest(BaseModel):
    room: str
    device_id: str

class UpdateRoomInfoRequest(BaseModel):
    room: str
    new_title: str
    new_summary: Optional[str] = None

class AllowJoinRequest(BaseModel):
    room: str
    allow_join: bool


router = APIRouter()

# --- PDF 匯出設定 (智慧型字型選擇) ---
def get_chinese_font():
    """
    自動偵測作業系統並回傳可用的中文字型名稱與路徑。
    """
    os_type = platform.system()
    
    # 定義不同作業系統的字型搜尋路徑
    if os_type == 'Darwin':  # macOS
        font_map = {
            'PingFang': '/System/Library/Fonts/PingFang.ttc',
            'STHeiti': '/System/Library/Fonts/STHeiti Light.ttc',
            '儷黑 Pro': '/System/Library/Fonts/儷黑 Pro.ttf',
        }
    elif os_type == 'Windows':
        font_map = {
            'MSJH': 'C:/Windows/Fonts/msjh.ttc',      # 微軟正黑體
            'SimSun': 'C:/Windows/Fonts/simsun.ttc',   # 新宋體
            'KaiTi': 'C:/Windows/Fonts/simkai.ttf',    # 楷體
        }
    else:  # Linux and others (常見路徑)
        font_map = {
            'WenQuanYiMicroHei': '/usr/share/fonts/wenquanyi/wqy-microhei/wqy-microhei.ttc',
            'NotoSansCJK': '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf',
        }

    # 遍歷字典，嘗試註冊第一個找到的字型
    for font_name, font_path in font_map.items():
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            print(f"PDF匯出：成功註冊字型 '{font_name}'")
            return font_name
        except Exception:
            continue # 如果找不到或註冊失敗，繼續嘗試下一個
            
    # 如果所有預設字型都找不到，發出警告並使用備用字型
    print("警告：在系統預設路徑中找不到任何可用的中文字型，PDF 中文可能無法正常顯示。")
    return 'Helvetica'

FONT_NAME = get_chinese_font()


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
    topics: List[str] # 改為接收 topics 列表
    topic_summary: Optional[str] = None
    desired_outcome: Optional[str] = None
    topic_count: int # 從前端接收主題數量
    countdown: int = 15 * 60

@router.post("/api/create_room")
def create_room(room: RoomCreate):
    """
    建立會議室

    [POST] /api/create_room

    描述：
    建立一個新的會議室。

    參數：
    - room.title (str): 會議室標題
    - room.topics (List[str]): 主題名稱列表
    - room.topic_summary (str, 選填): 題目摘要資訊
    - room.desired_outcome (str, 選填): 想達到效果
    - room.topic_count (int): 問題/主題數量
    - room.countdown (int): 預設倒數時間（秒）

    回傳：
    - code (str): 房間代碼
    """
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    while code in ROOMS:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    title = room.title.strip()
    countdown = int(room.countdown or 0)
    countdown = max(0, countdown)
    room_topics = room.topics if room.topics else ["預設主題"]
    first_topic = room_topics[0]

    ROOMS[code] = {
        "code": code,
        "title": title,
        "created_at": get_current_timestamp(),
        "participants": 0,
        "settings": {"allowQuestions": True, "allowVoting": True},
        "status": "Stop",
        "participants_list": [],
        "current_topic": first_topic,
        "countdown": countdown,
        "time_start": 0,
        "topic_summary": (room.topic_summary or "").strip(),
        "desired_outcome": (room.desired_outcome or "").strip(),
        "topic_count": room.topic_count, # 使用前端傳來的值
    }
    
    for topic_name in room_topics:
        topic_name_stripped = topic_name.strip()
        if not topic_name_stripped:
            continue
        topics[f"{code}_{topic_name_stripped}"] = {
            "room_id": code,
            "topic_name": topic_name_stripped,
            "comments": [],
        }
    
    return {
        "code": ROOMS[code]["code"],
        "title": ROOMS[code]["title"],
        "created_at": ROOMS[code]["created_at"],
        "participants": ROOMS[code]["participants"],
        "settings": ROOMS[code]["settings"]
    }

@router.get("/api/export_pdf")
def export_pdf(room: str):
    """
    匯出指定會議室的完整記錄為 PDF 檔案。
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="找不到會議室")

    room_data = ROOMS[room]
    room_topics = [t for t_id, t in topics.items() if t["room_id"] == room]
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleStyle', fontName=FONT_NAME, fontSize=24, alignment=TA_CENTER, spaceAfter=20, textColor=navy))
    styles.add(ParagraphStyle(name='HeaderStyle', fontName=FONT_NAME, fontSize=18, spaceAfter=10, textColor=black))
    styles.add(ParagraphStyle(name='SubHeaderStyle', fontName=FONT_NAME, fontSize=14, spaceAfter=8, textColor=gray))
    styles.add(ParagraphStyle(name='BodyStyle', fontName=FONT_NAME, fontSize=11, leading=16, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='CommentStyle', fontName=FONT_NAME, fontSize=10, leading=14, leftIndent=20, spaceBefore=5))

    story = []

    # 1. 會議標題和元數據
    story.append(Paragraph(room_data.get('title', '會議記錄'), styles['TitleStyle']))
    story.append(Spacer(1, 12))
    
    created_time = datetime.datetime.fromtimestamp(room_data.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M')
    story.append(Paragraph(f"會議代碼: {room}", styles['SubHeaderStyle']))
    story.append(Paragraph(f"建立時間: {created_time}", styles['SubHeaderStyle']))
    
    if room_data.get('topic_summary'):
        story.append(Paragraph(f"摘要: {room_data['topic_summary']}", styles['BodyStyle']))
    if room_data.get('desired_outcome'):
        story.append(Paragraph(f"預期成果: {room_data['desired_outcome']}", styles['BodyStyle']))
    
    story.append(Spacer(1, 24))
    story.append(PageBreak())

    # 2. 遍歷所有主題
    for topic in room_topics:
        story.append(Paragraph(topic.get('topic_name', '未命名主題'), styles['HeaderStyle']))
        story.append(Spacer(1, 12))

        comments = topic.get('comments', [])
        if not comments:
            story.append(Paragraph("此主題下沒有任何留言。", styles['BodyStyle']))
        else:
            for comment in comments:
                nickname = comment.get('nickname', '匿名')
                content = comment.get('content', '').replace('\n', '<br/>')
                good_votes = len(votes.get(comment.get('id', ''), {}).get('good', []))
                bad_votes = len(votes.get(comment.get('id', ''), {}).get('bad', []))
                
                comment_text = f"<b>{nickname}</b> (👍{good_votes} 👎{bad_votes}):<br/>{content}"
                story.append(Paragraph(comment_text, styles['CommentStyle']))
                story.append(Spacer(1, 6))
        
        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)

    # 取得會議標題，並提供預設值
    meeting_title = room_data.get('title', f'SyncAI-Report-{room}')
    
    # 使用 quote 對檔名進行 URL 編碼，使其支援中文及特殊字元
    encoded_filename = quote(meeting_title)

    return StreamingResponse(buffer, media_type='application/pdf', headers={
        'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_filename}.pdf"
    })


@router.get("/api/room_topics")
def get_room_topics(room: str):
    """取得指定房間的所有主題列表"""
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_topics = [
        t["topic_name"] for t_id, t in topics.items() if t["room_id"] == room
    ]
    return {"topics": room_topics}

class AddTopicsRequest(BaseModel):
    room: str
    topics: List[str]

@router.post("/api/room/add_topics")
def add_topics_to_room(req: AddTopicsRequest):
    """為指定房間添加多個主題，並清除舊的「預設主題」"""
    if req.room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")

    # 1. 刪除舊的預設主題（如果存在）
    default_topic_id = f"{req.room}_預設主題"
    if default_topic_id in topics:
        del topics[default_topic_id]

    # 2. 添加新主題
    for topic_name in req.topics:
        topic_name_stripped = topic_name.strip()
        if not topic_name_stripped:
            continue
        
        topic_id = f"{req.room}_{topic_name_stripped}"
        if topic_id not in topics:
            topics[topic_id] = {
                "room_id": req.room,
                "topic_name": topic_name_stripped,
                "comments": [],
            }
    
    # 3. 更新房間的 current_topic 為新的第一個主題
    if req.topics:
        ROOMS[req.room]["current_topic"] = req.topics[0].strip()

    return {"success": True, "message": f"已成功為房間 {req.room} 添加 {len(req.topics)} 個主題。"}


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
    
    return {"success": True, "status": "Discussion"}

# 取得主題、倒數、留言 (RESTful 風格)
@router.get("/api/rooms/{room}/state")
def get_room_state(room: str):
    """
    取得房間狀態
    
    [GET] /api/rooms/{room}/state
    
    描述：
    取得指定房間的當前狀態，包括主題、倒數計時和當前主題的留言。
    
    參數：
    - room (str): 房間代碼 (路徑參數)
    
    返回值：
    - topic (str): 當前討論主題
    - countdown (int): 剩餘倒數時間（秒）
    - comments (list): 當前主題的留言列表
    - status (str): 房間狀態
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_info = ROOMS[room]
    
    current_status = room_info["status"]
    if current_status in ["End", "Stop", "NotFound"]:
        left = 0
    else:
        now = get_current_timestamp()
        left = max(0, int(room_info["countdown"] - (now - room_info["time_start"]))) if room_info["time_start"] else 0
    
    current_topic = room_info["current_topic"]
    current_comments = []
    if current_topic:
        topic_id = f"{room}_{current_topic}"
        if topic_id in topics:
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
        "comments": current_comments,
        "status": current_status
    }

# 新增留言 (RESTful 風格)
@router.post("/api/rooms/{room}/comments")
def add_comment(room: str, data: CommentRequest):
    """
    新增留言到當前主題
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    current_topic = ROOMS[room]["current_topic"]
    if not current_topic:
        raise HTTPException(status_code=400, detail="No active topic in the room")
    
    topic_id = f"{room}_{current_topic}"
    if topic_id not in topics:
        topics[topic_id] = {
            "room_id": room,
            "topic_name": current_topic,
            "comments": []
        }
    
    # 取得提交者的 device_id
    # 這是一個簡化的假設，正式產品中應有更安全的驗證
    device_id = None
    if "participants_list" in ROOMS[room]:
        for p in ROOMS[room]["participants_list"]:
            if p['nickname'] == data.nickname:
                device_id = p['device_id']
                break

    comment_id = str(uuid.uuid4())
    new_comment = {
        "id": comment_id,
        "nickname": data.nickname,
        "content": data.content,
        "ts": get_current_timestamp(),
        "isAISummary": data.isAISummary,
        "device_id": device_id  # *** 重要：儲存 device_id ***
    }
    
    topics[topic_id]["comments"].append(new_comment)
    return {"success": True, "comment_id": comment_id}

# 取得所有留言 (RESTful 風格)
@router.get("/api/rooms/{room}/comments")
def get_room_comments(room: str):
    """
    取得房間當前主題的留言 
    
    [GET] /api/rooms/{room}/comments
    
    描述：
    取得指定房間當前主題的所有留言，並按照時間戳升冪排序。
    
    參數：
    - room (str): 房間代碼 (路徑參數)
    
    返回值：
    - comments (list): 當前主題的留言列表
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
        
    current_topic = ROOMS[room]["current_topic"]
    if not current_topic:
        return {"comments": []}
        
    topic_id = f"{room}_{current_topic}"
    if topic_id not in topics:
        return {"comments": []}

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
    
    return {"comments": sorted(comments_with_votes, key=lambda x: x["ts"])}

# 刪除單一留言 (RESTful 風格)
@router.delete("/api/rooms/{room}/comments/{comment_id}")
def delete_comment_single(room: str, comment_id: str):
    """
    刪除單一留言與其投票紀錄

    [DELETE] /api/rooms/{room}/comments/{comment_id}

    描述：
    傳入房號與留言 ID，刪除該留言與其所有投票紀錄。

    參數：
    - room (str): 房間代碼 (路徑參數)
    - comment_id (str): 留言ID (路徑參數)

    回傳：
    - success (bool): 是否刪除成功
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")

    found = False
    affected_topic_name = None
    for topic_key, topic_obj in list(topics.items()):
        if topic_obj.get("room_id") != room:
            continue
        comments_list = topic_obj.get("comments", [])
        idx = next((i for i, c in enumerate(comments_list) if c.get("id") == comment_id), None)
        if idx is not None:
            affected_topic_name = topic_obj.get("topic_name", "")
            comments_list.pop(idx)
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment_id in votes:
        del votes[comment_id]

    return {"success": True}

# 投票功能 (RESTful 風格)
@router.post("/api/rooms/{room}/comments/{comment_id}/vote")
def vote_comment(room: str, comment_id: str, data: VoteRequest):
    """
    為留言投票
    
    [POST] /api/rooms/{room}/comments/{comment_id}/vote
    
    描述：
    為指定留言投好評或差評票。
    
    參數：
    - room (str): 房間代碼 (路徑參數)
    - comment_id (str): 留言ID (路徑參數)
    - data.device_id (str): 設備ID
    - data.vote_type (str): "good" 或 "bad"
    
    返回值：
    - success (bool): 是否成功投票
    """
    vote_type = data.vote_type
    device_id = data.device_id
    
    if vote_type not in ["good", "bad"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    comment_found = any(
        c["id"] == comment_id 
        for t in topics.values() if t["room_id"] == room 
        for c in t["comments"]
    )
    if not comment_found:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment_id not in votes:
        votes[comment_id] = {"good": [], "bad": []}
    
    if device_id in votes[comment_id][vote_type]:
        raise HTTPException(status_code=409, detail="Already voted")
    
    opposite_type = "bad" if vote_type == "good" else "good"
    if device_id in votes[comment_id][opposite_type]:
        votes[comment_id][opposite_type].remove(device_id)
    
    votes[comment_id][vote_type].append(device_id)
    
    return {"success": True}

# 取消投票 (RESTful 風格)
@router.delete("/api/rooms/{room}/comments/{comment_id}/vote")
def remove_vote_comment(room: str, comment_id: str, data: VoteRequest):
    """
    取消投票
    
    [DELETE] /api/rooms/{room}/comments/{comment_id}/vote
    
    描述：
    取消對指定留言的指定類型投票。
    
    參數：
    - room (str): 房間代碼 (路徑參數)
    - comment_id (str): 留言ID (路徑參數)
    - data.device_id (str): 設備ID
    - data.vote_type (str): "good" 或 "bad"
    
    返回值：
    - success (bool): 是否成功取消投票
    """
    vote_type = data.vote_type
    device_id = data.device_id

    if vote_type not in ["good", "bad"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
        
    if comment_id not in votes or device_id not in votes[comment_id][vote_type]:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    votes[comment_id][vote_type].remove(device_id)
    
    return {"success": True}

# 獲取用戶投票記錄 (RESTful 風格)
@router.get("/api/rooms/{room}/votes")
def get_user_votes(room: str, device_id: str):
    """
    獲取用戶的投票記錄
    
    [GET] /api/rooms/{room}/votes?device_id={device_id}
    
    描述：
    獲取指定設備在指定房間的所有投票記錄。
    
    參數：
    - room (str): 房間代碼 (路徑參數)
    - device_id (str): 設備ID (查詢參數)
    
    返回值：
    - voted_good (list): 已投好評的留言ID列表
    - voted_bad (list): 已投差評的留言ID列表
    """
    voted_good = []
    voted_bad = []
    
    if room in ROOMS:
        for topic_id, topic_data in topics.items():
            if topic_data["room_id"] == room:
                for comment in topic_data["comments"]:
                    comment_id = comment["id"]
                    if comment_id in votes:
                        if device_id in votes[comment_id].get("good", []):
                            voted_good.append(comment_id)
                        if device_id in votes[comment_id].get("bad", []):
                            voted_bad.append(comment_id)
    
    return {"voted_good": voted_good, "voted_bad": voted_bad}

# 更新參與者暱稱 (RESTful 風格)

@router.put("/api/rooms/{room}/participants/{device_id}/nickname")
def update_participant_nickname(room: str, device_id: str, data: UpdateNicknameRequest):
    """
    更新參與者暱稱，並同步更新該用戶的所有留言。
    """
    new_nickname = data.new_nickname.strip()
    
    if not new_nickname or len(new_nickname) > 10:
        raise HTTPException(status_code=400, detail="暱稱格式不符或過長")

    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="會議室不存在")
    
    # 1. 更新參與者列表中的暱稱
    participant_found = False
    if "participants_list" in ROOMS[room]:
        for p in ROOMS[room]["participants_list"]:
            if p['device_id'] == device_id:
                p['nickname'] = new_nickname
                participant_found = True
                break
    
    if not participant_found:
        raise HTTPException(status_code=404, detail="參與者不存在")
    
    # 2. *** 重要：使用 device_id 更新該用戶所有留言的暱稱 ***
    for topic in topics.values():
        if topic["room_id"] == room:
            for comment in topic["comments"]:
                if comment.get("device_id") == device_id:
                    comment["nickname"] = new_nickname
    
    return {"success": True, "message": "暱稱已更新"}

# 更新當前主題 (RESTful 風格)
@router.put("/api/rooms/{room}/topic")
def update_current_topic(room: str, data: TopicUpdateRequest):
    """
    更新房間的當前主題

    [PUT] /api/rooms/{room}/topic

    描述：
    設定指定房間當前正在討論的主題。

    參數：
    - room (str): 房間代碼 (路徑參數)
    - data.topic (str): 新的當前主題名稱

    回傳：
    - success (bool): 是否成功更新
    - status (str): 更新後房間的狀態
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    new_topic = data.topic.strip()
    
    # 檢查新主題是否存在於該房間的主題列表中
    topic_id = f"{room}_{new_topic}"
    if topic_id not in topics:
        # 如果主題不存在，可以選擇創建它或返回錯誤
        # 這裡我們選擇創建它，以符合新增主題後直接切換的流程
        topics[topic_id] = {
            "room_id": room,
            "topic_name": new_topic,
            "comments": []
        }

    ROOMS[room]["current_topic"] = new_topic
    ROOMS[room]["status"] = "Discussion" # 切換主題時自動進入討論狀態
    
    return {"success": True, "status": ROOMS[room]["status"]}

# 重新命名主題 (RESTful 風格)
@router.post("/api/rooms/{room}/topics/rename")
def rename_topic(room: str, data: RenameTopicRequest):
    """
    重新命名一個主題

    [POST] /api/rooms/{room}/topics/rename

    描述：
    更新指定房間中一個主題的名稱。

    參數：
    - room (str): 房間代碼 (路徑參數)
    - data.old_topic (str): 舊的主題名稱
    - data.new_topic (str): 新的主題名稱

    回傳：
    - success (bool): 是否成功
    - is_current_topic (bool): 被重新命名的主題是否為當前主題
    """
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")

    old_topic_name = data.old_topic.strip()
    new_topic_name = data.new_topic.strip()

    if not old_topic_name or not new_topic_name:
        raise HTTPException(status_code=400, detail="Topic names cannot be empty")

    old_topic_id = f"{room}_{old_topic_name}"
    new_topic_id = f"{room}_{new_topic_name}"

    if old_topic_id not in topics:
        raise HTTPException(status_code=404, detail="Old topic not found")
    
    if new_topic_id in topics:
        raise HTTPException(status_code=409, detail="New topic name already exists")

    # 更新 topics 字典
    topics[new_topic_id] = topics.pop(old_topic_id)
    topics[new_topic_id]['topic_name'] = new_topic_name

    # 檢查是否為當前主題
    is_current = (ROOMS[room].get("current_topic") == old_topic_name)
    if is_current:
        ROOMS[room]["current_topic"] = new_topic_name

    return {"success": True, "is_current_topic": is_current}


# --- 舊的 API 端點 (標記為棄用，稍後移除) ---

# @router.get("/api/room_state") ...
# @router.post("/api/room_comment") ...
# @router.get("/api/room_comments") ...
# @router.delete("/api/room_comment_single") ...
# @router.post("/api/questions/vote") ...
# @router.delete("/api/questions/vote") ...
# @router.get("/api/questions/votes") ...
# @router.post("/api/participants/update_nickname") ...

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
    
    if not room or not new_title or len(new_title) > 50:
        raise HTTPException(status_code=400, detail="Invalid input")
    
    if new_summary is not None and len(new_summary) > 2000:
        raise HTTPException(status_code=400, detail="Summary is too long")

    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    ROOMS[room]["title"] = new_title
    if new_summary is not None:
        ROOMS[room]["topic_summary"] = new_summary
        
    return {
        "success": True,
        "room_code": room,
        "new_title": new_title
    }

# 設定房間是否允許新參與者加入
@router.post("/api/room_allow_join")
def set_room_allow_join(data: AllowJoinRequest):
    """
    設定房間是否允許新參與者加入

    [POST] /api/room_allow_join

    描述：
    設定指定房間是否允許新參與者加入。

    參數：
    - room (str): 房間代碼
    - allow_join (bool): 是否允許加入

    回傳：
    - success (bool): 是否成功設定
    """
    room = data.room.strip()
    if room not in ROOMS:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # 這裡我們假設有一個設定來控制，如果沒有，可以添加到 ROOMS 結構中
    ROOMS[room].setdefault("settings", {})["allowJoin"] = data.allow_join
    
    return {"success": True}
