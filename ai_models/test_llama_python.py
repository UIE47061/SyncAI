from llama_cpp import Llama
import json
import os

# 讀取測試json
json_path = 'meeting_log/test.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 組 prompt
prompt = f"""請根據以下討論主題與留言內容，自動歸納討論重點、主流意見、分歧點與可能決議，著重讚數較高的留言，必要時條列整理。
討論主題：{data.get('topic')}
討論目標：{data.get('discussion_goal')}
會議時長：{data.get('duration')} 分鐘
匿名狀態：{'匿名' if data.get('is_anonymous') else '署名'}
參與人員：{', '.join(data.get('participants', []))}

留言列表：
"""

for c in data.get('comments', []):
    # 條列每則留言（署名/匿名、內容、讚/倒讚、時間）
    nickname = c.get('nickname', '匿名')
    content = c.get('content', '')
    likes = c.get('likes', 0)
    dislikes = c.get('dislikes', 0)
    t = c.get('time', '')
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

# 路徑要換成你電腦上的實際路徑
llm = Llama(model_path="ai_models/mistral-7b-instruct-v0.2.Q5_K_M.gguf",
            n_ctx=2048)

output = llm(
    prompt,
    max_tokens=1024,
    stop=["</s>"],
    echo=False,
    temperature=0.8,
)

print("=== AI 摘要 ===\n")
print(output["choices"][0]["text"].strip())