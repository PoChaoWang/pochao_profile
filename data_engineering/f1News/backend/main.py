from fetch_news import run_f1_news_crawler
from merge_and_clean import merge_and_clean_data
from upload_to_supabase import upload_to_supabase
import datetime
import json
import logging
import sys
from dotenv import load_dotenv
from translate_news import fetch_and_translate_column
from content_editor import content_edit
from title_editor import title_edit

# 設置 logging，輸出到標準輸出 (stdout)
logging.basicConfig(
    stream=sys.stdout,  # 將日誌輸出到標準輸出
    level=logging.INFO,  # 設定日誌等級（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日誌格式
)

if __name__ == "__main__":
    try:
        # Set the output directory for saving the news data
        output_dir = "raw"
        table_name = "f1_news"
        # Number of days to fetch news from
        fetch_days = 1

        # Debug flags for different steps
        step1_debug = False  # For Fetch News
        step2_debug = False  # For Merge and Clean Data
        step3_debug = False  # For Translate News

        current_time = datetime.datetime.now()

        clean_dir = (
            f"data/all_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            if step2_debug
            else None
        )

        translated_output_dir = f"data" if step3_debug else None

        # 用於存放所有資料來源的新聞
        all_news_data = []

        # Step 1: Fetch news from different sources
        logging.info("Step 1: Fetching news from different sources.")

        # Autosport
        autosport_url = "https://www.autosport.com/rss/feed/f1"
        autosport_container_attrs = {"class": "ms-article-content"}
        autosport_source = "Autosport"
        autosport_news = run_f1_news_crawler(
            autosport_url,
            fetch_days,
            autosport_container_attrs,
            output_dir,
            autosport_source,
            debug=step1_debug,
        )
        if autosport_news:
            all_news_data.extend(autosport_news)

        # BBC
        bbc_url = "https://feeds.bbci.co.uk/sport/formula1/rss.xml"
        bbc_container_attrs = {"data-component": "text-block"}
        bbc_source = "BBC"
        bbc_news = run_f1_news_crawler(
            bbc_url,
            fetch_days,
            bbc_container_attrs,
            output_dir,
            bbc_source,
            debug=step1_debug,
        )
        if bbc_news:
            all_news_data.extend(bbc_news)

        # # Motorsport
        motorsport_url = "https://www.motorsport.com/rss/f1/news/"
        motorsport_container_attrs = {"class": "ms-article-content"}
        motorsport_source = "Motorsport"
        motorsport_news = run_f1_news_crawler(
            motorsport_url,
            fetch_days,
            motorsport_container_attrs,
            output_dir,
            motorsport_source,
            debug=step1_debug,
        )
        if motorsport_news:
            all_news_data.extend(motorsport_news)

        # Racefans
        racefans_url = "https://www.racefans.net/feed/"
        racefans_container_attrs = {"class": "entry-content"}
        racefans_source = "RaceFans"
        racefans_news = run_f1_news_crawler(
            racefans_url,
            fetch_days,
            racefans_container_attrs,
            output_dir,
            racefans_source,
            debug=step1_debug,
        )
        if racefans_news:
            all_news_data.extend(racefans_news)

        # # Pitpass
        pitpass_url = "https://www.pitpass.com/fes_php/fes_usr_sit_newsfeed.php"
        pitpass_container_attrs = {"class": "KonaBody"}
        pitpass_source = "Pitpass"
        pitpass_news = run_f1_news_crawler(
            pitpass_url,
            fetch_days,
            pitpass_container_attrs,
            output_dir,
            pitpass_source,
            debug=step1_debug,
        )
        if pitpass_news:
            all_news_data.extend(pitpass_news)

        # # f1technical_news
        f1technical_news_url = "https://www.f1technical.net/rss/news.xml"
        f1technical_news_container_attrs = {"class": "content article"}
        f1technical_news_source = "F1 Technical News"
        f1technical_news = run_f1_news_crawler(
            f1technical_news_url,
            fetch_days,
            f1technical_news_container_attrs,
            output_dir,
            f1technical_news_source,
            debug=step1_debug,
        )
        if f1technical_news:
            all_news_data.extend(f1technical_news)

        # # f1technical_articles
        f1technical_articles_url = "https://www.f1technical.net/rss/articles.xml"
        f1technical_articles_container_attrs = {"class": "content article"}
        f1technical_articles_source = "F1 Technical Articles"
        f1technical_articles = run_f1_news_crawler(
            f1technical_articles_url,
            fetch_days,
            f1technical_articles_container_attrs,
            output_dir,
            f1technical_articles_source,
            debug=step1_debug,
        )
        if f1technical_articles:
            all_news_data.extend(f1technical_articles)

        logging.info(f"Fetched {len(all_news_data)} news articles from all sources.")
        # logging.info("Step 2: Merging and cleaning fetched data.")

        # Step 2: Merge and clean the fetched data

        cleaned_data = merge_and_clean_data(
            all_news_data, output_dir=clean_dir, debug=step2_debug
        )

        raw_data = upload_to_supabase(
            table_name, cleaned_data, created=True, updated=True
        )

        if raw_data:
            logging.info(f"Uploaded {len(cleaned_data)} articles to Supabase.")
        else:
            logging.error("Failed to upload articles to Supabase.")

        logging.info("Step 2: completed successfully.")
        logging.info("Step 3: Please wait, Translating the cleaned data......")

        # Step 3: Translate the merged data
        try:
            translated = fetch_and_translate_column(
                cleaned_data, output_dir=translated_output_dir, debug=step3_debug
            )
            if translated:
                logging.info(f"Translated {len(translated)} articles.")
                logging.info("Translation completed successfully.")
            else:
                logging.warning("No data was returned from fetch_and_translate_column.")
        except Exception as e:
            logging.error(f"Error during translation: {e}", exc_info=True)

        try:
            content_edit(translated_output_dir, debug=step3_debug)
            title_edit(translated_output_dir, debug=step3_debug)

        except Exception as e:
            logging.error(f"Error during editing: {e}", exc_info=True)

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
