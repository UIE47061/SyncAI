from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import random, string, time, json, re, os
from typing import Union, List
from .participants_api import ROOMS, topics, votes

router = APIRouter(prefix="/ai", tags=["AI"])

# AnythingLLM API 配置
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_BASE_URL", "http://localhost:3001")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "PNB2B7R-4EC4P21-NM0XHTX-4BHZBHJ")
ANYTHINGLLM_WORKSPACE_SLUG = os.getenv("ANYTHINGLLM_WORKSPACE_SLUG", "syncai")

if not ANYTHINGLLM_API_KEY:
    print("警告：未設置 ANYTHINGLLM_API_KEY 環境變數")

# HTTP 客戶端配置
httpx_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0, connect=10.0),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

def filter_thinking_tags(text: str, debug_mode: bool = False) -> str:
    """
    過濾思考型模型回覆中的 <think> 標籤和思考內容
    
    Args:
        text: 包含可能的 <think> 標籤的原始回覆
        debug_mode: 如果為 True，保留思考內容用於調試
    
    Returns:
        過濾後的純回覆內容
    """
    if not text:
        return text
    
    # 調試模式下保留思考內容
    debug_thinking = os.getenv("ANYTHINGLLM_DEBUG_THINKING", "false").lower() == "true"
    if debug_mode or debug_thinking:
        print(f"調試模式：保留思考內容，原始回覆長度: {len(text)}")
        return text
    
    # 使用正則表達式移除 <think>...</think> 標籤及其內容
    import re
    
    # 匹配 <think> 到 </think> 之間的所有內容（包括換行符）
    pattern = r'<think>.*?</think>'
    filtered_text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # 清理多餘的空白字符和換行符
    filtered_text = filtered_text.strip()
    
    # 移除開頭的多餘換行符
    while filtered_text.startswith('\n'):
        filtered_text = filtered_text[1:]
    
    print(f"原始回覆長度: {len(text)}, 過濾後長度: {len(filtered_text)}")
    
    return filtered_text

async def ensure_workspace_exists(room_code: str, room_title: str) -> str:
    """
    確保指定會議室的工作區存在，如果不存在則創建
    
    Args:
        room_code: 會議室代碼
        room_title: 會議室名稱
    
    Returns:
        工作區的slug
    
    Raises:
        HTTPException: 當操作失敗時
    """
    if not ANYTHINGLLM_API_KEY:
        raise HTTPException(status_code=500, detail="未配置 AnythingLLM API Key")
    
    # 生成工作區slug（使用會議室代碼，確保唯一性）
    workspace_slug = f"syncai-{room_code.lower()}"
    
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 1. 檢查工作區是否已存在（通過列出所有工作區）
        list_response = await httpx_client.get(
            f"{ANYTHINGLLM_BASE_URL}/api/v1/workspaces",
            headers=headers
        )
        
        workspace_exists = False
        if list_response.status_code == 200:
            workspaces_data = list_response.json()
            existing_workspaces = workspaces_data.get("workspaces", [])
            
            for ws in existing_workspaces:
                if ws.get("slug") == workspace_slug:
                    print(f"工作區 '{workspace_slug}' 已存在 (ID: {ws.get('id')})")
                    workspace_exists = True
                    break
        
        if workspace_exists:
            return workspace_slug
        
        # 2. 如果不存在，創建新工作區
        print(f"工作區 '{workspace_slug}' 不存在，開始創建...")
        if True:  # 替代原來的 404 檢查
            create_payload = {
                "name": f"SyncAI-{room_title}"
            }
            
            create_response = await httpx_client.post(
                f"{ANYTHINGLLM_BASE_URL}/api/v1/workspace/new",
                headers=headers,
                json=create_payload
            )
            
            if create_response.status_code == 200:
                result = create_response.json()
                # 根據AnythingLLM API的響應格式提取工作區信息
                if "workspace" in result:
                    created_workspace = result["workspace"]
                    created_slug = created_workspace.get("slug", workspace_slug)
                    print(f"成功創建工作區 '{created_slug}' (ID: {created_workspace.get('id')}) 用於會議: {room_title}")
                    print(f"響應訊息: {result.get('message', 'Workspace created')}")
                    return created_slug
                else:
                    print(f"成功創建工作區，響應: {result}")
                    return workspace_slug
            else:
                error_detail = f"創建工作區失敗: {create_response.status_code}"
                try:
                    error_data = create_response.json()
                    error_detail += f" - {error_data.get('message', '未知錯誤')}"
                except:
                    error_detail += f" - {create_response.text}"
                raise HTTPException(status_code=500, detail=error_detail)
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=500, detail="AnythingLLM API 請求超時")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"AnythingLLM API 連接錯誤: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"確保工作區存在時發生未知錯誤: {str(e)}")

async def call_anythingllm_chat(message: str, workspace_slug: str = None, mode: str = "chat") -> str:
    """
    調用 AnythingLLM 的聊天 API
    
    Args:
        message: 要發送的訊息
        workspace_slug: 工作區slug，如果未提供則使用預設
        mode: 聊天模式 (chat, query, 等)
    
    Returns:
        AI 的回覆文字
    
    Raises:
        HTTPException: 當 API 調用失敗時
    """
    if not ANYTHINGLLM_API_KEY:
        raise HTTPException(status_code=500, detail="未配置 AnythingLLM API Key")
    
    # 如果沒有提供workspace_slug，使用預設的
    if not workspace_slug:
        workspace_slug = ANYTHINGLLM_WORKSPACE_SLUG
    
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message,
        "mode": mode
    }
    
    try:
        response = await httpx_client.post(
            f"{ANYTHINGLLM_BASE_URL}/api/v1/workspace/{workspace_slug}/chat",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            error_detail = f"AnythingLLM API 錯誤: {response.status_code}"
            try:
                error_data = response.json()
                error_detail += f" - {error_data.get('message', '未知錯誤')}"
            except:
                pass
            raise HTTPException(status_code=500, detail=error_detail)
        
        result = response.json()
        
        # 提取回覆文字（根據 AnythingLLM 的回覆格式調整）
        print(f"AnythingLLM 回覆: {result}")  # 調試日誌
        
        # 檢查是否有錯誤
        if "error" in result and result["error"]:
            raise HTTPException(status_code=500, detail=f"AnythingLLM 錯誤: {result['error']}")
        
        raw_response = ""
        if "textResponse" in result and result["textResponse"]:
            raw_response = result["textResponse"]
        elif "message" in result:
            raw_response = result["message"]
        elif "response" in result:
            raw_response = result["response"]
        else:
            # 如果找不到預期的欄位，返回整個回覆
            raw_response = str(result)
        
        # 過濾思考型模型的 <think> 標籤
        filtered_response = filter_thinking_tags(raw_response)
        return filtered_response
            
    except httpx.TimeoutException as e:
        print(f"AnythingLLM API 超時: {e}")
        raise HTTPException(status_code=500, detail="AnythingLLM API 請求超時")
    except httpx.RequestError as e:
        print(f"AnythingLLM 請求錯誤: {e}")
        print(f"請求URL: {ANYTHINGLLM_BASE_URL}/api/v1/workspace/{workspace_slug}/chat")
        raise HTTPException(status_code=500, detail=f"AnythingLLM API 連接錯誤: {str(e)}")
    except Exception as e:
        print(f"AnythingLLM 未知錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"調用 AnythingLLM API 時發生未知錯誤: {str(e)}")

class AskRequest(BaseModel):
    prompt: str

@router.get("/test_connection")
async def test_anythingllm_connection():
    """測試AnythingLLM連接的端點"""
    try:
        # 直接測試連接到AnythingLLM
        response = await httpx_client.get(
            f"{ANYTHINGLLM_BASE_URL}/api/v1/workspaces", 
            headers={"Authorization": f"Bearer {ANYTHINGLLM_API_KEY}"}
        )
        
        if response.status_code == 200:
            workspaces = response.json()
            return {
                "status": "success", 
                "message": "成功連接到AnythingLLM",
                "workspaces": workspaces.get("workspaces", [])
            }
        else:
            return {
                "status": "error", 
                "message": f"連接失敗: {response.status_code}",
                "response": response.text
            }
    except Exception as e:
        return {"status": "error", "message": f"連接錯誤: {str(e)}"}

class TestWorkspaceRequest(BaseModel):
    room_code: str
    room_title: str

@router.post("/test_create_workspace")
async def test_create_workspace(req: TestWorkspaceRequest):
    """測試創建工作區的端點"""
    try:
        workspace_slug = await ensure_workspace_exists(req.room_code, req.room_title)
        return {
            "status": "success",
            "message": f"工作區操作成功",
            "workspace_slug": workspace_slug,
            "room_code": req.room_code,
            "room_title": req.room_title
        }
    except Exception as e:
        return {"status": "error", "message": f"創建工作區失敗: {str(e)}"}

@router.post("/ask")
async def ask_ai(req: AskRequest):
    try:
        answer = await call_anythingllm_chat(req.prompt)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 處理失敗: {str(e)}")

# 定義用於 AI 總結的請求模型
class SummaryRequest(BaseModel):
    room: str  # 會議室代碼
    topic: str # 要總結的主題

# --- 重寫 summary_ai 函式 ---
@router.post("/summary")
async def summary_ai(req: SummaryRequest):
    """
    對指定會議室的特定主題進行 AI 總結

    [POST] /ai/summary

    參數：
    - room (str): 會議室代碼
    - topic (str): 要進行總結的主題名稱

    回傳：
    - summary (str): AI 生成的總結文字
    """
    # 檢查會議室是否存在
    if req.room not in ROOMS:
        return {"summary": "錯誤：找不到指定的會議室。"}

    # 組合主題 ID 並檢查主題是否存在
    topic_id = f"{req.room}_{req.topic}"
    if topic_id not in topics:
        return {"summary": "錯誤：在該會議室中找不到指定的主題。"}

    room_data = ROOMS[req.room]
    topic_data = topics[topic_id]
    
    # --- 開始建立 Prompt ---
    prompt = f"主題: {req.topic}\n"

    # 取得參與者列表
    participants = [p.get("nickname", "匿名") for p in room_data.get("participants_list", [])]
    if participants:
        prompt += f"參與者: {', '.join(participants)}\n"

    prompt += "\n留言與票數:\n"

    # 取得該主題的所有留言與其對應的票數
    comments_for_prompt = []
    if "comments" in topic_data:
        for c in topic_data["comments"]:
            comment_id = c.get("id")
            nickname = c.get("nickname", "匿名")
            content = c.get("content", "")
            
            # 從 votes 字典中取得票數
            good_votes = len(votes.get(comment_id, {}).get("good", []))
            bad_votes = len(votes.get(comment_id, {}).get("bad", []))

            comments_for_prompt.append(
                f"- {nickname}：{content}（👍{good_votes}、👎{bad_votes}）"
            )

    if not comments_for_prompt:
        prompt += "目前這個主題還沒有任何留言。\n"
    else:
        prompt += "\n".join(comments_for_prompt)

    # 加上固定的指令模板
    prompt += """

                    你的任務是擔任一個專業的會議記錄員。
                    你必須嚴格根據上方提供的「留言與票數」資訊，進行條列式彙整。
                    禁止臆測或生成任何未在資料中出現的數字、名稱或觀點。
                    你的回答內容，只能包含彙整後的結果，禁止加入任何開場白、問候語或結尾的免責聲明。

                    請直接以以下格式輸出，並將真實的內容填入：
                    ---
                    1. [第一個重點主題]
                    - 主流意見：
                    - 分歧點：（若無則寫“無”）
                    - 可能決議：
                    ---
                    2. [第二個重點主題]
                    - 主流意見：
                    - 分歧點：（若無則寫“無”）
                    - 可能決議：
                    ---
                    總結：
                    [此處條列會議的最重要共識或後續追蹤事項]
                """

    # 呼叫 AnythingLLM API
    try:
        # 獲取會議室資訊並確保工作區存在
        room_title = room_data.get('title', f'會議室-{req.room}')
        workspace_slug = await ensure_workspace_exists(req.room, room_title)
        
        summary_text = await call_anythingllm_chat(prompt, workspace_slug, mode="chat")
        return {"summary": summary_text}
    except HTTPException:
        raise
    except Exception as e:
        return {"summary": f"AI 總結生成失敗: {str(e)}"}

async def _generate_topics_from_title(meeting_title: str, topic_count: int, workspace_slug: str = None) -> List[str]:
    """
    根據會議標題生成主題的核心邏輯。
    這是一個內部函式，旨在被其他 API 端點調用。
    """
    topic_count = max(1, min(10, topic_count))
    meeting_title = meeting_title.strip()

    if not meeting_title:
        return ["錯誤：會議名稱不可為空。"]

    prompt = f"""
        你的任務是一位專業且高效的會議主持人。
        請根據以下提供的「會議名稱」，為這次會議腦力激盪出 {topic_count} 個最關鍵、最相關的討論議程主題。

        會議名稱："{meeting_title}"

        你的回覆必須是一個單層的 JSON 格式陣列 (a flat JSON array)，陣列中只包含簡潔且非空的主題字串。
        禁止在陣列中包含任何空字串 ("")、巢狀陣列或字串化的 JSON。
        請不要包含任何數字編號、破折號、或任何其他的開場白與解釋。

        正確範例：
        ["回顧第二季銷售數據", "討論新功能優先級", "設定第三季KPI"]

        錯誤範例：
        ["", "主題A", "[\"主題B\", \"主題C\"]"]
    """

    try:
        raw_text = await call_anythingllm_chat(prompt, workspace_slug, mode="chat")

        # --- 4. 解析 AI 的回覆 (v4 終極版) ---
        
        # 遞迴函式，用於攤平所有可能的巢狀結構
        def flatten_and_clean_topics(items):
            if not isinstance(items, list):
                return []
            
            flat_list = []
            for item in items:
                # 如果項目是列表，遞迴攤平
                if isinstance(item, list):
                    flat_list.extend(flatten_and_clean_topics(item))
                # 如果項目是字串
                elif isinstance(item, str):
                    # 去除頭尾空白
                    item = item.strip()
                    # 嘗試將其視為 JSON 進行解析
                    if item.startswith('[') and item.endswith(']'):
                        try:
                            nested_list = json.loads(item)
                            flat_list.extend(flatten_and_clean_topics(nested_list))
                        except json.JSONDecodeError:
                            # 解析失敗，當作普通字串，但過濾空值
                            if item:
                                flat_list.append(item)
                    # 如果是普通字串，過濾空值
                    elif item:
                        flat_list.append(item)
            return flat_list

        try:
            # 步驟 1: 移除潛在的 Markdown 程式碼區塊標籤
            cleaned_text = re.sub(r'```(json)?\s*', '', raw_text)
            cleaned_text = cleaned_text.strip('`').strip()

            # 步驟 2: 找到最外層的 []
            start_index = cleaned_text.find('[')
            end_index = cleaned_text.rfind(']') + 1
            
            if start_index != -1 and end_index != 0:
                json_str = cleaned_text[start_index:end_index]
                initial_topics = json.loads(json_str)
            else:
                # 如果找不到 JSON 結構，直接按行分割
                raise ValueError("找不到 JSON 陣列結構")

            # 步驟 3: 使用遞迴函式進行徹底的攤平與清理
            generated_topics = flatten_and_clean_topics(initial_topics)

        except (json.JSONDecodeError, ValueError):
            # 步驟 4: 如果 JSON 解析失敗，使用備用方案 (按行分割)
            cleaned_text = re.sub(r'```(json)?\s*', '', raw_text)
            cleaned_text = cleaned_text.strip('`').strip()
            generated_topics = [
                line.strip().lstrip('-*').lstrip('123456789.').strip()
                for line in cleaned_text.split('\n')
                if line.strip() and line.strip() not in ['[', ']']
            ]
        
        # --- 5. 最後的清理與數量控制 ---
        final_topics = [topic for topic in generated_topics if topic]
        return final_topics[:topic_count]

    except Exception as e:
        print(f"Error calling LLM for topic generation: {e}")
        return [f"AI服務暫時無法連線，請稍後再試。"]


class GenerateTopicsRequest(BaseModel):
    """用於 AI 生成主題請求的模型"""
    meeting_title: str
    topic_count: int

@router.post("/generate_topics")
async def generate_ai_topics(req: GenerateTopicsRequest):
    """
    根據會議名稱和指定數量，使用 AI 生成議程主題。

    [POST] /ai/generate_topics

    參數：
    - meeting_title (str): 會議的標題或主要目的。
    - topic_count (int): 希望生成的主題數量。

    回傳：
    - topics (list[str]): 一個包含 AI 生成的主題字串的列表。
    """
    # --- 1. 基本驗證 ---
    # 確保主題數量在一個合理的範圍內
    topic_count = max(1, min(10, req.topic_count)) 
    meeting_title = req.meeting_title.strip()

    if not meeting_title:
        return {"topics": ["錯誤：會議名稱不可為空。"]}

    # --- 2. 設計 Prompt (指令) ---
    # 這是與 AI 溝通的關鍵，我們給予它角色、任務和明確的輸出格式要求。
    prompt = f"""
        你的任務是一位專業且高效的會議主持人。
        請根據以下提供的「會議名稱」，為這次會議腦力激盪出 {topic_count} 個最關鍵、最相關的討論議程主題，並使用繁體中文回覆．

        會議名稱："{meeting_title}"

        你的回覆必須是一個 JSON 格式的陣列 (array)，陣列中只包含主題的字串。
        請不要包含任何數字編號、破折號、或任何其他的開場白與解釋。

        例如，如果會議名稱是「2025年第三季產品開發策略會議」，並且主題數量是3的話，你應該回傳：
        ["回顧第二季銷售數據與客戶回饋", "討論新功能優先級與開發時程", "設定第三季的關鍵績效指標 (KPI)"]
    """

    # --- 3. 呼叫 AnythingLLM API ---
    try:
        # 為會議創建專用工作區（使用會議標題作為唯一識別）
        room_code = f"topics-{hash(meeting_title) % 10000}"  # 生成基於標題的唯一代碼
        workspace_slug = await ensure_workspace_exists(room_code, meeting_title)
        
        raw_text = await call_anythingllm_chat(prompt, workspace_slug, mode="chat")

        # --- 4. 解析 AI 的回覆 ---
        # 我們優先嘗試將回覆直接解析為 JSON
        try:
            # 找到 JSON 陣列的開始和結束位置，以應對 AI 可能加入多餘文字的情況
            start_index = raw_text.find('[')
            end_index = raw_text.rfind(']') + 1
            if start_index != -1 and end_index != 0:
                json_str = raw_text[start_index:end_index]
                generated_topics = json.loads(json_str)
                # 確保結果是一個列表
                if not isinstance(generated_topics, list):
                    raise ValueError("AI 回傳的不是一個列表")
            else:
                 raise ValueError("在 AI 回應中找不到 JSON 陣列")

        except (json.JSONDecodeError, ValueError):
            # 如果 JSON 解析失敗，我們退一步，嘗試按行分割作為備用方案
            # 這能應對 AI 未完全遵循格式要求的情況
            generated_topics = [
                line.strip().lstrip('-').lstrip('*').lstrip('123456789.').strip() 
                for line in raw_text.split('\n') 
                if line.strip()
            ]
            # 只取回我們需要的數量
            generated_topics = generated_topics[:topic_count]

        return {"topics": generated_topics}

    except Exception as e:
        # 處理呼叫 AI 時可能發生的任何錯誤
        print(f"Error calling LLM for topic generation: {e}")
        return {"topics": [f"AI 服務暫時無法連線，請稍後再試。"]}

# 新增的請求模型，用於 generate_single_topic 端點
class GenerateSingleTopicRequest(BaseModel):
    room: str
    custom_prompt: str

@router.post("/generate_single_topic")
async def generate_single_topic(req: GenerateSingleTopicRequest):
    """
    根據會議室和自訂提示，使用 AI 生成單一議程主題。

    [POST] /ai/generate_single_topic

    參數：
    - room (str): 會議室代碼
    - custom_prompt (str): 自訂的提示語句，用於引導 AI 生成主題

    回傳：
    - topic (str): AI 生成的主題字串
    """
    # 檢查會議室是否存在
    if req.room not in ROOMS:
        return {"topic": "錯誤：找不到指定的會議室。"}

    room_data = ROOMS[req.room]

    # --- 開始建立 Prompt ---
    prompt = f"會議名稱: {room_data.get('title', '未命名會議')}\n"
    prompt += f"會議代碼: {req.room}\n"
    
    # 添加會議描述/摘要（如果有）
    if room_data.get('topic_summary'):
        prompt += f"會議摘要: {room_data['topic_summary']}\n"
    if room_data.get('desired_outcome'):
        prompt += f"預期成果: {room_data['desired_outcome']}\n"
    
    # 取得參與者列表
    participants = [p.get("nickname", "匿名") for p in room_data.get("participants_list", [])]
    if participants:
        prompt += f"參與者: {', '.join(participants)}\n"
    
    # 找出該會議室的所有已有主題
    existing_topics = [
        t["topic_name"] for t_id, t in topics.items() 
        if t["room_id"] == req.room and "topic_name" in t
    ]
    
    if existing_topics:
        prompt += "\n已有的主題:\n"
        for i, topic_name in enumerate(existing_topics, 1):
            prompt += f"{i}. {topic_name}\n"
        
        prompt += "\n請生成一個與已有主題互補但不重複的新議程主題。主題應該既要與會議整體目標相關，又能夠覆蓋尚未討論的重要方面。"
    else:
        prompt += "\n目前會議尚未有任何主題。請生成一個適合作為第一個討論主題的議程。"

    # 加上使用者自訂的提示
    if req.custom_prompt:
        prompt += f"\n\n自訂提示: {req.custom_prompt}"
    
    prompt += "\n\n請直接返回一個簡潔、具體且不超過10個字的主題，不需要任何前綴或解釋。"

    # 呼叫 AnythingLLM API
    try:
        # 獲取會議室資訊並確保工作區存在
        room_title = room_data.get('title', f'會議室-{req.room}')
        workspace_slug = await ensure_workspace_exists(req.room, room_title)
        
        topic = await call_anythingllm_chat(prompt, workspace_slug, mode="chat")
        return {"topic": topic.strip()}
    except HTTPException:
        raise
    except Exception as e:
        return {"topic": f"AI 主題生成失敗: {str(e)}"}