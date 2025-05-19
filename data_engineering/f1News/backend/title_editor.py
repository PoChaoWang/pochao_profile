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


def title_edit(output_dir, debug=True):
    try:
        response = (
            supabase.table("f1_news")
            .select("id,link, title_zh, title_zh, translation_status")
            .eq("translation_status", "translated")
            .is_("title_status", "null")
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
            "請你將標題內的標題保留不要更動\n\n"
            "請把包在標題外的HTML的標籤去除\n\n"
            "標題之後如果還有HTML的標籤及內容請全部刪除\n\n"
            "如果沒有以上狀況就回傳原本的內容\n\n"
            "Strictly follow the output format below:\n\n"
            "Result: <整理好的內容>\n\n"
            "Example:\n\n"
            "Input:<p>Stella 聲稱 Norris 在他的復出駕駛中「展現了韌性」</p>\n"
            "Result:Stella 聲稱 Norris 在他的復出駕駛中「展現了韌性」\n\n"
            "or\n\n"
            "Input: 為何 Verstappen 認為 Red Bull 無法將困境僅僅歸咎於舊風洞 ```html <h1>Why Verstappen feels Red Bull cannot put its woes down to just old wind tunnel</h1> <p>Max Verstappen believes that Red Bull's Formula 1 woes are not simply down to a correlation issue with its old wind tunnel that was recently retired.</p><p>After dominating the 2023 season, Red Bull has had a more challenging start to this year as it has faced a threat from rivals Ferrari and McLaren at recent races.</p>\n"
            "Result: 為何 Verstappen 認為 Red Bull 無法將困境僅僅歸咎於舊風洞\n\n"
            "Now, here is the title:\n\n{text}"
        )

        for i, row in enumerate(data):

            id = row.get("id")
            title_zh = row.get("title_zh")

            logging.info(
                "---------------------------------------------------------------------------------------"
            )
            logging.info(f"{title_zh} Translation started")
            logging.info(
                "---------------------------------------------------------------------------------------"
            )

            try:
                if title_zh:
                    edited_title = try_edit(title_zh, prompt)
                    if edited_title == "TIMEOUT_ERROR":  # 檢查是否為timeout三次
                        edited_title = row.get("title_zh")
                        status = "didNothing"  # timeout三次後將status設為didNothing
                    elif edited_title is None:
                        edited_title = row.get("title_zh")
                        status = "didNothing"  # 表示沒改動
                    else:
                        status = "edited"  # 表示成功編輯過

                result.append(
                    {
                        "id": id,
                        "title_zh": edited_title,
                        "title_status": status,  # 加入title_status
                        "link": row.get("link"),
                    }
                )
                logging.info(f"{result[-1]['title_zh']} Translation completed")
                logging.info(
                    "---------------------------------------------------------------------------------------"
                )

                if not debug:
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

    title_edit(output_dir, debug=True)
