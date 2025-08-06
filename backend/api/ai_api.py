from fastapi import APIRouter
from pydantic import BaseModel
from llama_cpp import Llama
import os
import json
from typing import Union

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

class SummaryRequest(BaseModel):
    topic: str = None
    comments: list = None
    participants: list = None
    is_anonymous: bool = None
    discussion_goal: str = None
    duration: Union[str, int, None] = None

@router.post("/summary")
def summary_ai(req: SummaryRequest):
    if req.topic == "__from_file__":
        with open("meeting_log/test.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        req = SummaryRequest(**data)

    prompt = ""
    if req.topic:
        prompt += f"主題: {req.topic}\n"
    if req.participants:
        prompt += f"參與者: {', '.join(req.participants)}\n"
    if req.is_anonymous is not None:
        prompt += f"是否匿名: {'是' if req.is_anonymous else '否'}\n"
    if req.discussion_goal:
        prompt += f"討論目標: {req.discussion_goal}\n"

    prompt += "\n留言與票數:\n"

    if req.comments:
        for c in req.comments:
            nickname = c.get("nickname", "匿名")
            content = c.get("content", "")
            likes = c.get("likes", 0)
            dislikes = c.get("dislikes", 0)
            t = c.get("time", "")
            prompt += f"- {nickname}：{content}（👍{likes}、👎{dislikes}，{t}）\n"

    prompt += """
                請用條列式彙整本次討論的主要觀點與結論，若有明顯正反方意見請分開整理。
                請務必根據下方每一筆留言與統計資訊，不要自行臆測或生成不存在的數字或名稱。
                請按照以下格式輸出，每一項都要有主題、主流意見、分歧點、可能決議：
                ---
                1. <重點主題>
                - 主流意見：
                - 分歧點：（若無則寫“無”）
                - 可能決議：
                ---
                最後以「總結」區塊條列本次會議得到的最重要共識或AI建議後續追蹤事項。
            """

    output = llm(
        prompt,
        max_tokens=1024,
        stop=["</s>"],
        echo=False,
        temperature=0.8,
    )
    summary_text = output["choices"][0]["text"].strip()
    return {"summary": summary_text}
