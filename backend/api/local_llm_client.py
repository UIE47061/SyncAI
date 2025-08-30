"""
Local LLM Client - CPU推理引擎，使用llama-cpp-python
針對Snapdragon Elite X進行優化配置
"""

import asyncio
import os
import threading
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging
from huggingface_hub import hf_hub_download, snapshot_download
from llama_cpp import Llama
from .snapdragon_config import snapdragon_config

class LocalLLMClient:
    """Local LLM客戶端 - 使用llama-cpp-python進行CPU推理"""
    
    def __init__(self):
        self.model = None
        self.model_path = None
        self.is_loaded = False
        self.loading_lock = threading.Lock()
        
        # 初始化日志器
        self.logger = logging.getLogger(__name__)
        
        # 使用Snapdragon Elite X優化配置
        self.config = snapdragon_config.get_cpu_llm_config()
        self.is_snapdragon = snapdragon_config.is_snapdragon_elite_x
        
        # 平台信息日志
        self.logger.info(f"平台檢測: {snapdragon_config.platform_info}")
        if self.is_snapdragon:
            self.logger.info("Snapdragon Elite X優化已啟用")
        else:
            self.logger.info("使用通用CPU配置")
        
        # 模型存儲目錄
        self.models_dir = Path("ai_models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用平台推薦的模型配置
        self.model_recommendations = snapdragon_config.get_model_recommendations()
        
        # 支持的模型配置
        self.supported_models = {
            "llama2-7b-chat": {
                "repo_id": "microsoft/Llama-2-7b-chat-hf",
                "filename": "ggml-model-q4_0.gguf",
                "quantized_repo": "TheBloke/Llama-2-7B-Chat-GGUF",
                "quantized_filename": "llama-2-7b-chat.Q4_0.gguf",
                "description": "Llama 2 7B Chat量化版本，適合CPU推理"
            },
            "phi3-mini": {
                "repo_id": "microsoft/Phi-3-mini-4k-instruct",
                "quantized_repo": "microsoft/Phi-3-mini-4k-instruct-gguf",
                "quantized_filename": "Phi-3-mini-4k-instruct-q4.gguf",
                "description": "Phi-3 Mini 4K，輕量級模型，適合Snapdragon平台"
            },
            "qwen2-1.5b": {
                "repo_id": "Qwen/Qwen2-1.5B-Instruct",
                "quantized_repo": "Qwen/Qwen2-1.5B-Instruct-GGUF",
                "quantized_filename": "qwen2-1_5b-instruct-q4_0.gguf",
                "description": "Qwen2 1.5B指令調優版本，極輕量級"
            }
        }
    
    async def download_model(self, model_name: str = "phi3-mini") -> str:
        """
        從Hugging Face下載模型
        
        Args:
            model_name: 支持的模型名稱
            
        Returns:
            下載的模型文件路徑
        """
        if model_name not in self.supported_models:
            raise ValueError(f"不支持的模型: {model_name}，支持的模型: {list(self.supported_models.keys())}")
        
        model_config = self.supported_models[model_name]
        model_dir = self.models_dir / model_name
        model_dir.mkdir(exist_ok=True)
        
        # 檢查是否已下載
        if "quantized_filename" in model_config:
            model_file = model_dir / model_config["quantized_filename"]
            
            if model_file.exists():
                self.logger.info(f"模型已存在: {model_file}")
                return str(model_file)
            
            # 下載量化版本（推薦用於CPU推理）
            self.logger.info(f"正在下載量化模型: {model_config['quantized_repo']}")
            try:
                downloaded_path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: hf_hub_download(
                        repo_id=model_config["quantized_repo"],
                        filename=model_config["quantized_filename"],
                        local_dir=str(model_dir),
                        local_dir_use_symlinks=False
                    )
                )
                self.logger.info(f"模型下載完成: {downloaded_path}")
                return downloaded_path
                
            except Exception as e:
                self.logger.error(f"量化模型下載失敗: {e}")
                raise
        else:
            # 下載完整模型並嘗試轉換（備選方案）
            self.logger.info(f"正在下載完整模型: {model_config['repo_id']}")
            try:
                model_path = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: snapshot_download(
                        repo_id=model_config["repo_id"],
                        local_dir=str(model_dir),
                        local_dir_use_symlinks=False
                    )
                )
                self.logger.info(f"模型下載完成: {model_path}")
                return model_path
                
            except Exception as e:
                self.logger.error(f"模型下載失敗: {e}")
                raise
    
    async def load_model(self, model_path: Optional[str] = None, model_name: str = "phi3-mini") -> bool:
        """
        加載本地LLM模型
        
        Args:
            model_path: 模型文件路徑，如果為None則自動下載
            model_name: 模型名稱
            
        Returns:
            是否加載成功
        """
        with self.loading_lock:
            if self.is_loaded and self.model_path == model_path:
                return True
            
            try:
                # 如果沒有提供路徑，嘗試下載模型
                if model_path is None:
                    model_path = await self.download_model(model_name)
                
                # 檢查模型文件是否存在
                if not Path(model_path).exists():
                    raise FileNotFoundError(f"模型文件不存在: {model_path}")
                
                self.logger.info(f"正在加載模型: {model_path}")
                self.logger.info(f"Snapdragon Elite X優化配置: {self.config}")
                
                # 在線程池中加載模型，避免阻塞
                def load_model_sync():
                    return Llama(
                        model_path=model_path,
                        **{k: v for k, v in self.config.items() 
                           if k in ['n_ctx', 'n_threads', 'n_threads_batch', 'n_batch', 
                                   'n_gpu_layers', 'use_mlock', 'use_mmap', 'verbose']}
                    )
                
                self.model = await asyncio.get_event_loop().run_in_executor(
                    None, load_model_sync
                )
                
                self.model_path = model_path
                self.is_loaded = True
                self.logger.info("模型加載成功")
                return True
                
            except Exception as e:
                self.logger.error(f"模型加載失敗: {e}")
                self.model = None
                self.is_loaded = False
                return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本回應
        
        Args:
            prompt: 輸入提示
            **kwargs: 生成參數覆蓋
            
        Returns:
            生成的文本
        """
        if not self.is_loaded or self.model is None:
            # 嘗試自動加載默認模型
            success = await self.load_model()
            if not success:
                raise RuntimeError("模型未加載且自動加載失敗")
        
        # 合併生成參數
        gen_params = {**self.config, **kwargs}
        generation_params = {k: v for k, v in gen_params.items() 
                           if k in ['temperature', 'top_p', 'top_k', 'max_tokens', 'repeat_penalty']}
        
        try:
            # 在線程池中執行生成，避免阻塞
            def generate_sync():
                response = self.model(
                    prompt,
                    **generation_params,
                    echo=False,  # 不回傳原始提示
                    stream=False  # 同步模式
                )
                return response['choices'][0]['text'].strip()
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, generate_sync
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"文本生成失敗: {e}")
            raise
    
    def is_model_loaded(self) -> bool:
        """檢查模型是否已加載"""
        return self.is_loaded and self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        return {
            "is_loaded": self.is_loaded,
            "model_path": self.model_path,
            "config": self.config,
            "supported_models": self.supported_models
        }
    
    def unload_model(self):
        """卸載模型，釋放內存"""
        with self.loading_lock:
            if self.model is not None:
                del self.model
                self.model = None
                self.is_loaded = False
                self.model_path = None
                self.logger.info("模型已卸載")
    
    async def test_generation(self) -> Dict[str, Any]:
        """測試生成功能"""
        test_prompt = "你好，請簡單介紹一下你自己。"
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await self.generate(test_prompt, max_tokens=100)
            end_time = asyncio.get_event_loop().time()
            
            return {
                "success": True,
                "prompt": test_prompt,
                "response": result,
                "inference_time": round(end_time - start_time, 2),
                "model_info": self.get_model_info()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_info": self.get_model_info()
            }

# 全局客戶端實例
local_llm_client = LocalLLMClient()