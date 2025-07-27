from llama_cpp import Llama

# 路徑要換成你電腦上的實際路徑
# llm = Llama(model_path="ai_models/TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf")
llm = Llama(model_path="ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf")

output = llm(
    "請問你是誰？ 中文回覆",
    max_tokens=128,
    stop=["</s>"],
    echo=False,
    temperature=0.8,
)
print(output["choices"][0]["text"].strip())

