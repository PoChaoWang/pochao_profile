# web.py
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
import traceback

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 若有固定網域可換成對應網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/index")
def get_news(page: int = Query(1, ge=1), page_size: int = Query(20, le=100)):
    start = (page - 1) * page_size
    end = start + page_size - 1
    total_count = supabase.table("f1_news").select("id", count="exact").execute().count
    response = (
        supabase.table("f1_news")
        .select("id, title_zh, published_at, author, content_zh, image_url , source")
        .eq("translation_status", "translated")
        .order("published_at", desc=True)
        .range(start, end)
        .execute()
    )
    return {"news": response.data, "total_count": total_count}


@app.get("/news/{id}")
def get_news_by_id(id: str = Path(..., description="News UUID")):
    try:
        logging.info(f"Received ID: {id}")

        # 查詢主新聞
        response = (
            supabase.table("f1_news")
            .select("id, title_zh, link, author, content_zh, published_at")
            .eq("id", id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="News not found")

        main_news = response.data[0]

        # 查詢相關新聞 ID
        related_response = (
            supabase.table("related_news")
            .select("related_news_id")
            .eq("news_id", id)
            .execute()
        )

        related_ids = [item["related_news_id"] for item in related_response.data]

        # 查詢相關新聞詳細資料
        related_news = []
        if related_ids:
            related_news_response = (
                supabase.table("f1_news")
                .select(
                    "id, title_zh, published_at, author, content_zh, image_url , source"
                )
                .in_("id", related_ids)
                .order("published_at", desc=True)
                .limit(6)
                .execute()
            )
            related_news = related_news_response.data

        # 合併結果
        return {"news": main_news, "related_news": related_news}
    except Exception as e:
        logging.error(
            f"An error occurred while fetching the news with ID {id}: {str(e)}"
        )
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=404, detail="Not Found")


@app.get("/health")
def health_check():
    return {"health": "working!"}


@app.get("/search")
def search_news(q: str = Query(..., min_length=1), limit: int = 10):
    # 使用 ilike 進行不區分大小寫的模糊匹配
    title_query = (
        supabase.table("f1_news")
        .select("id, title_zh, published_at, author, content_zh, image_url, source")
        .ilike("title", f"%{q}%")
        .eq("translation_status", "translated")
    )
    content_query = (
        supabase.table("f1_news")
        .select("id, title_zh, published_at, author, content_zh, image_url, source")
        .ilike("content", f"%{q}%")
        .eq("translation_status", "translated")
    )

    # 執行查詢
    title_results = title_query.execute().data
    content_results = content_query.execute().data

    # 合併結果並去重
    all_results = {item["id"]: item for item in title_results + content_results}
    sorted_results = sorted(
        all_results.values(), key=lambda x: x["published_at"], reverse=True
    )

    return sorted_results[:limit]
