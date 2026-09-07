"""
scripts/fetch_news.py
Aggregates top news stories from multiple global RSS feeds.
"""

import html
import re
from typing import Dict, List, Optional
import feedparser

FEEDS: List[str] = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.npr.org/1004/rss.xml",
]


def clean_summary(raw_html: str) -> str:
    """Removes HTML tags and unescapes entities."""
    clean_text = re.sub(r"<[^>]+>", "", raw_html)
    return html.unescape(clean_text).strip()


def get_top_news_item() -> Dict[str, str]:
    """
    Pulls entries across feeds and returns the most complete top story.
    Falls back to a default tech/culture headline if feeds fail.
    """
    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                continue

            for entry in feed.entries[:3]:
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary") or entry.get("description") or ""
                summary = clean_summary(raw_summary)

                if title and len(summary) > 20:
                    return {
                        "title": title,
                        "summary": summary,
                        "link": entry.get("link", feed_url),
                        "source": feed.feed.get("title", "Global News Feed"),
                    }
        except Exception as err:
            print(f"Warning: Failed reading feed {feed_url}: {err}")
            continue

    # Fallback if internet connectivity or RSS endpoints fail
    return {
        "title": "Corporate Media Considers Shifting Primetime Slots to Automated Avatars",
        "summary": "Executives cite lower production overhead while broadcast talent unions voice fierce resistance.",
        "link": "https://example.com/fallback-news",
        "source": "Broadcast Industry Wire",
    }


if __name__ == "__main__":
    item = get_top_news_item()
    print(f"Source: {item['source']}")
    print(f"Headline: {item['title']}")
    print(f"Summary: {item['summary']}")
