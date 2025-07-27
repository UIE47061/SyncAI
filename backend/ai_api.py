# SyncAI/backend/ai_api.py
from fastapi import APIRouter
from pydantic import BaseModel
from llama_cpp import Llama

router = APIRouter(prefix="/ai", tags=["AI"])

llm = Llama(model_path="ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf")

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
