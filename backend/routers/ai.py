from fastapi import APIRouter
from pydantic import BaseModel
from llama_cpp import Llama
import os

router = APIRouter(prefix="/ai", tags=["AI"])

# 載入模型，只做一次（全域單例）
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf'))
llm = Llama(model_path=MODEL_PATH)

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
