import os
import json
import datetime
import feedparser
from google import genai

# 1. Fetch top news story from RSS feeds
RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
]

def get_top_news():
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        if feed.entries:
            top_entry = feed.entries[0]
            return {
                "title": top_entry.title,
                "summary": top_entry.get("summary", "")
            }
    return {"title": "AI Adoption Surges in Media Industry", "summary": "Broadcasters face increasing automation."}

# 2. Main generation logic
def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)
    news_item = get_top_news()

    system_instruction = """
    You are the head writer and technical director for "COWRENT AFFAIRS: BACKSTAGE AT MOO19".
    You produce serialized 60-second animated workplace farce shorts divided into six 10-second segments.
    The setting is strictly backstage at MOO19 News.
    Defined character handles to use in visual prompts: @Thaddeus, @Skip, @Noelle, @Frank, @Isaac, @Vola.
    The satire must parody the absurdity of modern broadcast news reacting to real-world headlines.
    """

    prompt = f"""
    Write a 60-second episode of 'Cowrent Affairs' reacting to this current news story:
    HEADLINE: {news_item['title']}
    SUMMARY: {news_item['summary']}

    Output format must strictly include:
    1. Episode Title & Premise (incorporating the headline).
    2. Locked Dialogue Script (60 seconds total, fast-paced).
    3. Six distinct 10-second clips (Clip 01 to Clip 06).
       For each clip, provide:
       - Timestamp (e.g. 0:00-0:10)
       - Locked Audio lines
       - Google Flow Video Prompt (referencing defined characters like @Skip, @Thaddeus with minimal descriptive drift and clear camera/blocking instructions)
       - After Effects Assembly / Editing strategy.
    """

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config={"system_instruction": system_instruction}
    )

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    os.makedirs("episodes", exist_ok=True)
    filename = f"episodes/{today}_episode.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Cowrent Affairs — Broadcast {today}\n\n")
        f.write(f"**Based on:** {news_item['title']}\n\n")
        f.write(response.text)

    print(f"Successfully generated episode: {filename}")

if __name__ == "__main__":
    main()
