import requests
import os
import json
from dotenv import load_dotenv
import time
import logging
import random
from supabase import create_client, Client
from requests.exceptions import Timeout
import datetime
from upload_to_supabase import upload_to_supabase

load_dotenv()

# Init Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REQUESTS_PER_MINUTE = 5
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(level=logging.INFO)


def edit_text(combined_text, prompt_template):
    prompt = prompt_template.format(text=combined_text)
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
            timeout=120,
        )
        if response.status_code == 200:
            response_data = response.json()
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                return response_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logging.error(
                    f"Unexpected response format: {response_data}", exc_info=True
                )
                return None
        else:
            logging.error(
                f"Translation failed with status code {response.status_code}: {response.text}",
                exc_info=True,
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed with error: {e}", exc_info=True)
        return None


def content_edit(output_dir, debug=False):
    try:
        response = (
            supabase.table("f1_news")
            .select("id,link, title_zh, content_zh, translation_status")
            .eq("translation_status", "translated")
            .is_("content_status", "NULL")
            .execute()
        )
        data = response.data

        result = []

        def try_edit(text, translation_prompt, retries=3):
            for attempt in range(1, retries + 1):
                try:
                    edited = edit_text(text, translation_prompt)
                    if edited and "Result:" in edited:
                        return edited.split("Result:", 1)[1].strip()
                    logging.warning(
                        f"Translation attempt {attempt} failed. Retrying..."
                    )
                except Timeout:
                    if attempt == retries:
                        logging.warning(
                            f"Translation timeout on attempt {attempt}. Skipping for now."
                        )
                        return "TIMEOUT_ERROR"  # 新增特殊返回值標記timeout失敗
                    else:
                        logging.warning(
                            f"Translation timeout on attempt {attempt}. Retrying..."
                        )
                except Exception as e:
                    logging.warning(f"Unexpected error on attempt {attempt}: {e}")
                time.sleep(random.uniform(3, 5))
            return None

        prompt = (
            "你是一位經驗豐富的 F1 賽車新聞編輯，擅長將中文新聞內容整理為條理清楚、精簡但保留重點的中文。請幫我處理以下 HTML 格式的文章內容：\n\n"
            "只要段落之間語意通順，就保留該段內容\n\n"
            "保留有意義的段落、評論、車手發言、賽事重點等資訊\n\n"
            "移除所有重複內容、廣告、影片嵌入、無意義的 <script>、社群分享連結、類似「透過每日電子郵件獲取我們所有最新的報導 - 沒有其他內容。沒有行銷，沒有廣告。在此註冊」、生日祝賀與歷史花絮等無關段落\n\n"
            "保留 HTML 的結構標籤，如 <p>、<h3>、<blockquote>、<a>、<table>、<td>、<rd> 等，不要轉為純文字\n\n"
            "若整篇文章沒有任何值得保留的內容，請僅回傳 Result：Skilled\n\n"
            "Strictly follow the output format below:\n\n"
            "Result: <整理好的內容>\n\n"
            "Now, here is the content:\n\n{text}"
        )

        for i, row in enumerate(data):

            id = row.get("id")
            title_zh = row.get("title_zh")
            content_zh = row.get("content_zh")

            logging.info(
                "---------------------------------------------------------------------------------------"
            )
            logging.info(f"{title_zh} Translation completed")
            logging.info(
                "---------------------------------------------------------------------------------------"
            )

            try:
                if content_zh:
                    edited_content = try_edit(content_zh, prompt)
                    if edited_content == "TIMEOUT_ERROR":  # 檢查是否為timeout三次
                        edited_content = row.get("content_zh")
                        status = "didNothing"  # timeout三次後將status設為didNothing
                    elif edited_content is None:
                        edited_content = row.get("content_zh")
                        status = "didNothing"  # 表示沒改動
                    elif "Skilled" in edited_content:
                        edited_content = row.get("content_zh")
                        status = "skilled"  # 表示該篇沒有值得保留的內容
                    else:
                        status = "edited"  # 表示成功編輯過

                result.append(
                    {
                        "id": id,
                        "content_zh": edited_content,
                        "content_status": status,
                        "link": row.get("link"),
                    }
                )
                if not debug:
                    logging.info(f"Uploading to Supabase: {id}")
                    upload_to_supabase(
                        "f1_news",
                        [result[-1]],
                        created=False,
                        updated=True,
                    )

            except Exception as e:
                logging.error(f"Error processing row {id}: {e}", exc_info=True)

            time.sleep(random.uniform(10, 20))

        if debug:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"edited_result_{timestamp}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logging.info(f"✅ Translated result saved to {output_path}")

        return result

    except Exception as e:
        logging.error(f"❌ Error in fetch_and_edit_all", exc_info=True)
        return None


if __name__ == "__main__":
    # Example usage
    output_dir = "data"

    content_edit(output_dir, debug=False)
