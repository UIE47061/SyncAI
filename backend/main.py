# backend/main.py
from fastapi import FastAPI
from backend.api import ai_api
from fastapi.middleware.cors import CORSMiddleware
from backend.api import participants_api
from backend.api import network_api
from backend.api import mindmap_api as mindmap_api
import asyncio
import logging

app = FastAPI(title="MBBuddy API")

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://localhost:5173", "http://192.168.0.214:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(participants_api.router)
app.include_router(ai_api.router)
app.include_router(network_api.router)
app.include_router(mindmap_api.router)

@app.on_event("startup")
async def startup_event():
    """應用啟動時預載入AI模型"""
    logger.info("🚀 SyncAI 後端服務啟動中...")
    
    # 預載入 CPU LLM 模型
    try:
        from backend.api.local_llm_client import local_llm_client
        logger.info("📥 開始預載入 CPU LLM 模型...")
        
        # 檢查模型文件是否存在
        model_dir = local_llm_client.models_dir / "qwen2-1.5b"
        if model_dir.exists():
            model_files = list(model_dir.glob("*.gguf"))
            if model_files:
                model_path = str(model_files[0])
                logger.info(f"📁 找到模型文件: {model_path}")
                
                # 預載入模型
                success = await local_llm_client.load_model(model_path, "qwen2-1.5b")
                if success:
                    logger.info("✅ CPU LLM 模型預載入成功")
                else:
                    logger.warning("⚠️ CPU LLM 模型預載入失敗")
            else:
                logger.warning("⚠️ 找不到 .gguf 模型文件")
        else:
            logger.warning("⚠️ 模型目錄不存在，將在首次調用時下載")
            
    except Exception as e:
        logger.error(f"❌ 預載入 CPU LLM 模型時發生錯誤: {e}")
    
    # 測試 AnythingLLM 連接
    try:
        from backend.api.ai_client import ai_client
        logger.info("🔗 測試 AnythingLLM 連接...")
        
        # 簡單的連接測試
        test_result = await ai_client.test_connection()
        if test_result:
            logger.info("✅ AnythingLLM 連接正常")
        else:
            logger.warning("⚠️ AnythingLLM 連接測試失敗")
            
    except Exception as e:
        logger.error(f"❌ AnythingLLM 連接測試時發生錯誤: {e}")
    
    logger.info("🎉 SyncAI 後端服務啟動完成！")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時清理資源"""
    logger.info("🛑 SyncAI 後端服務正在關閉...")
    
    try:
        from backend.api.local_llm_client import local_llm_client
        if local_llm_client.is_model_loaded():
            local_llm_client.unload_model()
            logger.info("✅ CPU LLM 模型已卸載")
    except Exception as e:
        logger.error(f"❌ 卸載模型時發生錯誤: {e}")
    
    logger.info("👋 SyncAI 後端服務已關閉")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
