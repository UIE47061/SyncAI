from fastapi import APIRouter
from pydantic import BaseModel
from llama_cpp import Llama
import os
import json
from typing import Union, List
from .participants_api import ROOMS, topics, votes

router = APIRouter(prefix="/ai", tags=["AI"])

# 載入模型，只做一次（全域單例）
MODEL_PATH = 'ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf'
llm = Llama(model_path=MODEL_PATH, n_ctx=2048)

class AskRequest(BaseModel):
    prompt: str

@router.post("/ask")
def ask_ai(req: AskRequest):
    output = llm(
        req.prompt,
        max_tokens=128,
        stop=["</s>"],
        echo=False,
        temperature=0.8,
    )
    answer = output["choices"][0]["text"].strip()
    return {"answer": answer}

# 定義用於 AI 總結的請求模型
class SummaryRequest(BaseModel):
    room: str  # 會議室代碼
    topic: str # 要總結的主題

# --- 重寫 summary_ai 函式 ---
@router.post("/summary")
def summary_ai(req: SummaryRequest):
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

    # 呼叫 AI 模型
    output = llm(
        prompt,
        max_tokens=1024,
        stop=["</s>"],
        echo=False,
        temperature=0.8,
    )
    
    summary_text = output["choices"][0]["text"].strip()
    return {"summary": summary_text}