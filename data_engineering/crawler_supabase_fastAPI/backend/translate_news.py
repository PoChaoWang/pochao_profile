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


def translate_text(combined_text, prompt_template):
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


def fetch_and_translate_column(cleaning_data, output_dir, debug=False):
    try:
        if debug:
            data = cleaning_data
        else:
            response = (
                supabase.table("f1_news")
                .select(
                    "id,link, title, title_zh, content, content_zh, translation_status"
                )
                .or_("title_zh.is.null,content_zh.is.null")
                .execute()
            )
            data = response.data
        result = []

        def try_translate(text, translation_prompt, retries=3):
            for attempt in range(1, retries + 1):
                try:
                    translated = translate_text(text, translation_prompt)
                    if translated and "Result:" in translated:
                        return translated.split("Result:", 1)[1].strip()
                    logging.warning(
                        f"Translation attempt {attempt} failed. Retrying..."
                    )
                except Timeout:
                    if attempt == retries:
                        logging.warning(
                            f"Translation timeout on attempt {attempt}. Skipping for now."
                        )
                        break
                    else:
                        logging.warning(
                            f"Translation timeout on attempt {attempt}. Retrying..."
                        )
                except Exception as e:
                    logging.warning(f"Unexpected error on attempt {attempt}: {e}")
                time.sleep(random.uniform(3, 5))
            return None

        prompt1 = (
            "You are a professional translator specializing in translating English F1 news articles into fluent Traditional Chinese.\n\n"
            "Please translate the following news title into natural and fluent Traditional Chinese.\n\n"
            "Remove all original HTML tags and structure (e.g., <p>...</p>, <h1>, etc.).\n\n"
            "Keep all brand names and personal names (such as Apple, Nike, Elon Musk, Formula 1, Stefano Domenicali) in English without translation.\n\n"
            "Do not add any explanations, interpretations, or additional comments.\n\n"
            "Strictly follow the output format below:\n\n"
            "Result: <Translated Title in Traditional Chinese>\n\n"
            "Example:\n\n"
            "Input:\n"
            'Verstappen "not very confident" of keeping Piastri behind in F1 Saudi GP. ```html <h1>Why Verstappen feels Red Bull cannot put its woes down to just old wind tunnel</h1> <p>Max Verstappen believes that Red Bull\'\s</p>\n\n'
            "Output:\n"
            "Result: Verstappen「不太有信心」能在 F1 沙烏地大獎賽中將 Piastri 擋在身後。\n\n"
            "Now, here is the title to translate:\n\n{text}"
        )

        prompt2 = (
            "You are a professional translator specializing in translating English F1 news articles into fluent Traditional Chinese.\n\n"
            "Please translate the following news article into natural and fluent Traditional Chinese.\n\n"
            "Preserve all original HTML tags and structure (e.g., <p>...</p>, <h1>, etc.).\n\n"
            "Keep all brand names and personal names (such as Apple, Nike, Elon Musk, Formula 1, Stefano Domenicali) in English without translation.\n\n"
            "Do not add any explanations, interpretations, or additional comments.\n\n"
            "Strictly follow the output format below:\n\n"
            "Result: <Translated Title or Content in Traditional Chinese>\n\n"
            "Additionally, please:\n\n"
            "Retain meaningful paragraphs, comments, driver statements, race highlights, and other relevant content.\n\n"
            "Remove duplicates, advertisements, embedded videos, meaningless <script> tags, social sharing links, birthday greetings, historical trivia, and any unnecessary sections.\n\n"
            "Keep the HTML structure tags like <p>, <h3>, <blockquote>, <a>, etc., and do not convert them into plain text.\n\n"
            "Please output the processed HTML result so I can use it for subsequent organization or conversion.\n\n"
            "Example:\n\n"
            "Input:\n"
            'Verstappen "not very confident" of keeping Piastri behind in F1 Saudi GP.\n\n'
            "Output:\n"
            "Result: Verstappen「不太有信心」能在 F1 沙烏地大獎賽中將 Piastri 擋在身後。\n\n"
            "or\n\n"
            "Input:\n"
            "<p>Max Verstappen says he is \"not very confident\" of beating McLaren's Oscar Piastri in Jeddah on Sunday. The reigning world champion's Red Bull <b>claimed pole by a mere 0.010s</b> after the McLarens had looked faster all weekend, with Piastri joining him on the front row. The other McLaren of Lando Norris is starting from 10th after the Briton crashed on his first Q3 lap.</p>....\n\n"
            "Output:\n"
            "Result: <p>Max Verstappen 表示，他「沒有太大信心」能在週日的吉達站擊敗 McLaren 車隊的 Oscar Piastri。這位衛冕世界冠軍的 Red Bull 賽車<b>僅以 0.010 秒的微弱優勢奪得桿位</b>，此前 McLaren 車隊在整個週末都顯得更快，Piastri 也加入了他的前排發車。另一輛 McLaren 車隊的 Lando Norris 在 Q3 的第一圈發生撞車事故後，將從第 10 位起跑。</p>...\n\n"
            "Now, here is the content to translate:\n\n{text}"
        )

        for i, row in enumerate(data):
            if debug:
                id = row.setdefault("id", f"debug_{i}")
                title, title_zh = row.get("title"), row.get("title_zh")
                content, content_zh = row.get("content"), row.get("content_zh")

                translated_title = title_zh
                translated_content = content_zh

            else:
                id = row["id"]
                title, title_zh = row.get("title"), row.get("title_zh")
                content, content_zh = row.get("content"), row.get("content_zh")

                translated_title = title_zh
                translated_content = content_zh
            logging.info(
                "---------------------------------------------------------------------------------------"
            )
            logging.info(f"Translating title: {title}")
            try:
                if not title_zh and title:
                    translated_title = try_translate(title, prompt1)
                if not content_zh and content:
                    translated_content = try_translate(content, prompt2)

                if translated_title and translated_content:
                    status = "translated"
                elif translated_title == "null":
                    status = "title failed"
                elif translated_content == "null":
                    status = "content failed"
                else:
                    status = "All failed"

                result.append(
                    {
                        "id": id,
                        "title": title,
                        "title_zh": translated_title or "null",
                        "content": content,
                        "content_zh": translated_content or "null",
                        "translation_status": status,
                        "link": row.get("link"),
                    }
                )
                if not debug:
                    upload_to_supabase(
                        "f1_news",
                        [result[-1]],
                        created=False,
                        updated=True,
                    )

                logging.info(f"✅ Title '{title}' processed. Status: {status}")

            except Exception as e:
                logging.error(f"Error processing row {id}: {e}", exc_info=True)

            time.sleep(random.uniform(10, 20))

        if debug and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            now = datetime.datetime.now()
            filename = f"all_translated_{now.strftime('%Y%m%d_%H%M%S')}.json"
            path = os.path.join(output_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            logging.info(f"Saved debug data to {path}")

        translated_count = sum(
            1 for item in result if item["translation_status"] == "translated"
        )
        title_failed_count = sum(
            1 for item in result if item["translation_status"] == "title failed"
        )
        content_failed_count = sum(
            1 for item in result if item["translation_status"] == "content failed"
        )
        all_failed_count = sum(
            1 for item in result if item["translation_status"] == "All failed"
        )

        logging.info(
            f"\n📊 Summary:\n✅ Successfully translated: {translated_count}\n🔠 Title failed: {title_failed_count}\n📄 Content failed: {content_failed_count}\n💥 All failed: {all_failed_count}"
        )

        return result

    except Exception as e:
        logging.error(f"❌ Error in fetch_and_translate_all", exc_info=True)
        return None


if __name__ == "__main__":
    cleaned_data = None
    translated_output_dir = "data"
    fetch_and_translate_column(
        cleaned_data, output_dir=translated_output_dir, debug=False
    )
