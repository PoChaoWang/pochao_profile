from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

# 加載環境變數
load_dotenv()

# 初始化 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. 取得所有 f1_news
news_response = supabase.table("f1_news").select("id, title, content").execute()
news_data = news_response.data
df = pd.DataFrame(news_data)
df["text"] = df["title"] + " " + df["content"]

# 2. 取得 related_news 中已經計算過的 news_id
related_response = supabase.table("related_news").select("news_id").execute()
processed_ids = set([row["news_id"] for row in related_response.data])

# 3. 找出還沒被處理過的新聞
unprocessed_df = df[~df["id"].isin(processed_ids)].reset_index(drop=True)

# 如果都處理過了就不做事
if unprocessed_df.empty:
    print("✅ 所有新聞都已經建立過相關新聞")
else:
    print(f"🔍 共 {len(unprocessed_df)} 筆新聞尚未建立相似度")

    # 4. 全部做 embedding（因為要比較用）
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(df["text"].tolist(), convert_to_tensor=True)
    cosine_sim = cosine_similarity(embeddings.cpu())

    related_news = []

    # 5. 只針對未處理的新聞跑相似新聞
    for i, row in unprocessed_df.iterrows():
        current_id = row["id"]
        df_index = df[df["id"] == current_id].index[0]  # 在原始 df 的位置
        similarities = cosine_sim[df_index]
        similar_indices = similarities.argsort()[::-1][1:6]  # 取前 5 個

        for j in similar_indices:
            score = float(similarities[j])
            if score < 0.2:
                continue
            related_news.append(
                {
                    "news_id": str(current_id),
                    "related_news_id": str(df.iloc[j]["id"]),
                    "similarity_score": round(score, 4),
                }
            )

    # 6. 批次寫入
    if related_news:
        supabase.table("related_news").insert(related_news).execute()
        print(f"✅ 寫入 {len(related_news)} 筆相關新聞資料")
    else:
        print("⚠️ 沒有找到符合條件的相似新聞")
