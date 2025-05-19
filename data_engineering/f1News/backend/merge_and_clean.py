import os
import json
import re
import logging
from bs4 import BeautifulSoup


def clean_data(data):
    """
    清理資料的函式。
    Args:
        data (list): 從 JSON 文件中讀取的新聞資料列表。
    Returns:
        list: 清理後的新聞資料列表。
    """
    for item in data:
        if "content" in item and isinstance(item["content"], str):
            # 使用BeautifulSoup處理HTML
            # 使用BeautifulSoup處理HTML
            soup = BeautifulSoup(item["content"], "html.parser")

            # 記錄處理前的狀態
            has_alignright_before = bool(soup.select("div.alignright"))
            logging.debug(
                f"Before cleaning: has alignright div: {has_alignright_before}"
            )

            # 移除所有指定標籤 - 使用一致的方法
            tags_to_remove = [
                "span",
                "strong",
                "em",
                "section",
                "small",
                "figcaption",
                "img",
                "figure",
                "script",
                "h4",
            ]
            for tag_name in tags_to_remove:
                for tag in soup.find_all(tag_name):
                    tag.decompose()

            # 移除特定class的標籤
            class_selectors = {
                "ul": ["lcp_catlist"],
                "div": ["tnp", "tnp-subscription", "alignright"],
                "p": ["text-above-ad"],
            }

            for tag_name, class_list in class_selectors.items():
                for class_name in class_list:
                    for tag in soup.find_all(
                        tag_name, class_=lambda x: x and class_name in x
                    ):
                        tag.decompose()

            # 移除特定ID的標籤
            id_selectors = ["article-mpu"]
            for id_prefix in id_selectors:
                for tag in soup.find_all(id=lambda x: x and x.startswith(id_prefix)):
                    tag.decompose()

            # 特別處理 snack_dex 系列ID
            for tag in soup.find_all(id=lambda x: x and "snack_dex" in x):
                tag.decompose()

            # 記錄處理後的狀態
            has_alignright_after = bool(soup.select("div.alignright"))
            logging.debug(f"After cleaning: has alignright div: {has_alignright_after}")

            # 替換a to b
            a_tags = soup.find_all("a")
            for a_tag in a_tags:
                b_tag = soup.new_tag("b")
                b_tag.string = a_tag.get_text()
                a_tag.replace_with(b_tag)

            unwanted_texts = [
                "Become a RaceFans supporter",
                "Go ad-free for just £1 per month",
                "Find out more and sign up",
            ]
            for text in unwanted_texts:
                # 在所有文本節點中尋找並移除包含這些文本的標籤
                for text_node in soup.find_all(text=True):
                    if text in text_node:
                        # 如果包含不需要的文本，則替換或移除該文本
                        text_node.replace_with(text_node.replace(text, ""))

            item["content"] = str(soup)
            item["translation_status"] = "pending"
            item["content_zh"] = ""

    # 過濾掉沒有content的項目
    cleaned_data = [item for item in data if item.get("content")]
    return cleaned_data


def merge_and_clean_data(news_data, output_dir=None, debug=False):
    """
    合併並清理新聞資料，去除重複的 URL，並根據 debug 決定是否儲存到檔案。
    Args:
        news_data (list): 所有來源的新聞資料列表。
        output_dir (str, optional): 儲存清理後資料的檔案路徑（僅在 debug=True 時使用）。
        debug (bool): 是否啟用除錯模式，啟用時會將清理後的資料儲存到檔案。
    Returns:
        list: 清理後的新聞資料列表。
    """
    seen_links = set()
    unique_data = []

    # 去除重複的 URL
    for item in news_data:
        link = item.get("link")
        if link and link not in seen_links:
            seen_links.add(link)
            unique_data.append(item)

    # 清理資料

    cleaned_data = clean_data(unique_data)

    # 如果 debug=True，將清理後的資料儲存到檔案
    if debug and output_dir:
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        with open(output_dir, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Cleaned data saved to {output_dir}")
    else:
        logging.info("Debug mode is off in Step 2, not saving translated data.")

    return cleaned_data
