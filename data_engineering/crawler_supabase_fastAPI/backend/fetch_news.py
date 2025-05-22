import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
from dateutil import parser
import json
import os
import re
from pytz import timezone
import logging


def fetch_f1_news(rss_url, days=3, container_attrs=None):
    """
    Fetch the F1 news RSS feed and parse news data from the past three days, including the content and image URLs.

    Args:
        rss_url (str): The URL of the F1 news RSS feed.
        days (int): The number of days to fetch news for.
        container_attrs (dict): Attributes to find the content container in the article.

    Returns:
        list: A list of news from the past specified days, where each news item is a dictionary
              containing 'title', 'link', 'published_at', 'summary', 'content', and 'image_url'.
              Returns None if an error occurs.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    now = datetime.datetime.now(datetime.timezone.utc)
    n_days_ago = now - datetime.timedelta(days)
    feed = feedparser.parse(rss_url)
    news_items = []

    try:
        for entry in feed.entries:
            published_at = parser.parse(entry.published)
            if n_days_ago <= published_at <= now:
                article_url = entry.link
                logging.info(
                    f"Fetching article content: published at {published_at}, {article_url}"
                )
                response = requests.get(article_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                article_author = author(entry, soup)
                article_content = scrape_article_content(
                    soup, container_attrs=container_attrs
                )

                # Modify the summary to remove content after "..."
                modified_summary = (
                    entry.summary.split("...")[0] + "..."
                    if "..." in entry.summary
                    else entry.summary
                )

                # Extract image URL from RSS entry
                image_url = extract_image_url(entry)

                # If no image in RSS, try to get the first image from the article
                # if not image_url:
                #     image_url = extract_first_image_from_article(soup)

                news_items.append(
                    {
                        "title": entry.title,
                        "link": entry.link,
                        "published_at": published_at.strftime("%Y-%m-%d_%H:%M:%S"),
                        "summary": modified_summary,
                        "author": article_author,
                        "content": article_content,
                        "image_url": image_url,
                    }
                )
        return news_items
    except requests.exceptions.RequestException as e:
        logging.error(
            f"An error occurred while fetching the article: {e}", exc_info=True
        )
        return None
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while fetching news: {e}", exc_info=True
        )
        return None


def extract_image_url(entry):
    """
    Extract the image URL from the RSS entry.

    Args:
        entry: RSS feed entry object

    Returns:
        str: URL of the image if found, otherwise None
    """
    # Method 1: Check for media_thumbnail (like BBC)
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        return entry.media_thumbnail[0]["url"]

    # Method 2: Check for enclosure in links (like Motorsport.com and Autosport)
    if hasattr(entry, "links"):
        for link in entry.links:
            if link.get("type", "").startswith("image/") and "href" in link:
                return link["href"]

    return None


def extract_first_image_from_article(soup):
    """
    Extract the first meaningful image from an article.

    Args:
        soup (BeautifulSoup): Parsed webpage content

    Returns:
        str: URL of the first image if found, otherwise None
    """
    try:
        # Try to find main content area first
        content_areas = [
            soup.find(class_=re.compile(r"article|content|main|story", re.IGNORECASE)),
            soup.find(id=re.compile(r"article|content|main|story", re.IGNORECASE)),
            soup,  # Fallback to entire document
        ]

        for area in content_areas:
            if not area:
                continue

            # Look for large/featured images first
            for img_class in [
                "featured-image",
                "hero-image",
                "main-image",
                "article-image",
            ]:
                img = area.find(class_=re.compile(img_class, re.IGNORECASE))
                if img and img.name == "img" and img.get("src"):
                    return img["src"]
                if img:
                    img_tag = img.find("img")
                    if img_tag and img_tag.get("src"):
                        return img_tag["src"]

            # Find first substantial image (exclude icons, avatars, etc.)
            images = area.find_all("img")
            for img in images:
                src = img.get("src", "")
                if src and not re.search(
                    r"(icon|avatar|logo|banner|ad)", src, re.IGNORECASE
                ):
                    # Filter out very small images
                    width = img.get("width")
                    height = img.get("height")
                    if width and height and int(width) > 100 and int(height) > 100:
                        return src
                    elif not width or not height:
                        # If no dimensions specified, assume it's a content image
                        return src

        return None
    except Exception as e:
        logging.error(f"Error extracting image from article: {e}", exc_info=True)
        return None


def clean_bbc_intro_paragraphs(html_content):
    """
    Remove BBC intro paragraphs that contain mostly metadata (e.g. Venue, Coverage).
    These typically appear at the start and contain lots of <b> tags.

    Args:
        html_content (str): Raw HTML content of the article.

    Returns:
        str: Cleaned HTML content.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    cleaned_paragraphs = []

    for p in soup.find_all("p"):
        text = p.get_text(strip=True)

        # Skip if it contains only bolded metadata-like structure
        if (
            text.lower().startswith("venue:")
            or text.lower().startswith("coverage:")
            or text.lower().startswith("dates:")
            or len(p.find_all("b")) > 2  # like multiple <b> in one <p>
        ):
            continue

        cleaned_paragraphs.append(str(p))

    return "\n".join(cleaned_paragraphs)


def scrape_article_content(soup, container_attrs=None, paragraph_tag="p", source=None):
    """
    Extract the content of a news article from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed webpage content of the article.
        container_attrs (dict, optional): Attributes to identify specific content containers.
        paragraph_tag (str): Tag used for paragraphs (default: "p").
        source (str, optional): News source name (e.g., "BBC") for special handling.

    Returns:
        str: Extracted article content with HTML tags (e.g., <b>, <h3>, <table>) kept.
    """
    all_text = []

    # First layer: if container is specified, try using it
    if container_attrs:
        containers = soup.find_all(attrs=container_attrs)
    else:
        containers = [soup]  # No container specified, use entire soup

    for container in containers:
        # Recursively find all relevant tags inside the container
        svg_tags = container.find_all(["g", "rect", "path"])
        all_text.extend([str(tag) for tag in svg_tags])
        paragraphs_headers_tables = container.find_all()
        # paragraphs_headers_tables = container.find_all(
        #     lambda tag: (
        #         tag.name in [paragraph_tag, "h3", "table"]
        #         and tag.name not in ["h4", "strong"]
        #         and not (
        #             tag.name == "div" and tag.get("class") in [["alignright"], ["tnp"]]
        #         )
        #     )
        # )
        container_text = "\n".join([str(tag) for tag in paragraphs_headers_tables])
        all_text.append(container_text)

    article_content = "\n\n".join(all_text).strip()

    # Fallback: if nothing was found, try searching full soup
    if not article_content:
        paragraphs_headers_tables = soup.find_all(
            lambda tag: (
                tag.name in [paragraph_tag, "h3", "table"]
                and tag.name not in ["h4", "strong"]
                and not (
                    tag.name == "div" and tag.get("class") in [["alignright"], ["tnp"]]
                )
            )
        )
        article_content = "\n".join(
            [str(tag) for tag in paragraphs_headers_tables]
        ).strip()

    # Special fallback for specific sources
    if not article_content and source == "BBC":
        # Try grabbing all <p> regardless of context
        paragraphs = soup.find_all("p")
        article_content = "\n".join(str(p) for p in paragraphs).strip()

    if source == "BBC":
        article_content = clean_bbc_intro_paragraphs(article_content)

    return article_content


def author(entry, soup):
    """
    Extract the author's name from the article content using a regular expression
    to find classes containing 'author'.
    """
    try:
        if hasattr(entry, "author"):
            return entry.author

        # Find all elements with a class containing 'author'
        author_element = soup.find(class_=re.compile(r".*author.*", re.IGNORECASE))
        if author_element:
            author_text = author_element.get_text(strip=True)
            # Remove content after the month abbreviation (e.g., "Apr")
            author_text = re.sub(
                r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*",
                "",
                author_text,
            )
            # Handle cases like "CleerenRonald" -> "Cleeren, Ronald"
            author_text = re.sub(r"([a-z])([A-Z])", r"\1, \2", author_text)
            return author_text.strip()
        return ""
    except Exception as e:
        logging.error(
            f"An error occurred while extracting the author's name: {e}",
            exc_info=True,
        )
        return ""


def run_f1_news_crawler(
    rss_url, fetch_days, container_attrs, output_dir, source_name, debug=False
):
    """
    Run the F1 news crawler for a specific RSS feed.
    Args:
        rss_url (str): The URL of the F1 news RSS feed.
        fetch_days (int): Number of days to fetch news for.
        container_attrs (dict): Attributes to find the content container in the article.
        output_dir (str): The directory to save the JSON file.
        source_name (str): The name of the news source.
        debug (bool): Whether to save output in debug mode.
    """
    executed_at = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    news_data = fetch_f1_news(rss_url, fetch_days, container_attrs=container_attrs)
    if news_data is not None:
        for item in news_data:
            item["source"] = source_name

    if debug:
        current_time = datetime.datetime.now()
        fetch_dir = f"raw/{source_name}_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("raw", exist_ok=True)
        with open(fetch_dir, "w", encoding="utf-8") as f:
            json.dump(news_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Fetched data saved to {fetch_dir}")
    else:
        logging.info("Debug mode is off in Step 1, not saving translated data.")

    return news_data
