from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
import pandas as pd

# 加載環境變數
load_dotenv()

# 初始化 Supabase 客戶端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_to_supabase(table_name: str, data: list, created=False, updated=False):
    """
    將多筆資料上傳到 Supabase 資料表，使用 upsert 避免重複資料。
    Args:
        table_name (str): 資料表名稱。
        data (list): 要上傳的資料列表，每筆資料為字典格式。
    Returns:
        dict: 包含成功和失敗的結果。
    """
    try:
        now = datetime.now(timezone.utc).isoformat()
        df = pd.DataFrame(data)
        if created:
            # 將 created_at 欄位設置為當前時間
            for record in data:
                record["created_at"] = now
        if updated:
            # 將 updated_at 欄位設置為當前時間
            for record in data:
                record["updated_at"] = now

        # 使用 upsert 插入或更新資料，指定唯一性約束欄位
        response = (
            supabase.table(table_name).upsert(data, on_conflict=["link"]).execute()
        )

        # 檢查是否有錯誤
        if response.data:
            logging.info("Data uploaded successfully.")
            return {"success": True, "data": response.data}
        else:
            logging.warning("Upload succeeded but returned no data.")
            return {"success": False, "error": "No data returned from Supabase."}
    except Exception as e:
        logging.error(f"Error during upload process: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
