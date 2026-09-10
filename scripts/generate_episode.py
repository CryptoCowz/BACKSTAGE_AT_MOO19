import os
from datetime import datetime
import feedparser
from google import genai
from google.genai import types

NEWS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

def fetch_top_stories(limit=5):
    headlines = []
    for url in NEWS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            headlines.append(f"- {entry.title}: {entry.summary}")
    return "\n".join(headlines[:8])

def generate_episode_bundle(news_context):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    system_instruction = """
    You are the showrunner for "MOO19 News / Cowrent Affairs," an animated workplace 
    satire modeled after The Mary Tyler Moore Show and Murphy Brown set inside The Pasture universe.
    
    Cast:
    - Thaddeus: Grumpy bull Editor-in-Chief, lit cigar, powder blue shirt, orange tie (Jonah.jpg).
    - Tiffany Rees-Moog: Conservative blonde cow, gold hoops, cross necklace (R_exp2.jpg).
    - Valhalla Spiker: Progressive afro bull, charcoal blazer, bead choker (valhalla2k.jpg).
    - Skip Zinfandel: Smug pompadour bull lead anchor, purple tie (NEWSCASTER_v2.jpg).
    - Noelle Piper Grace: Glamorous blonde cow co-anchor, green dress (CO ANCHOR.jpg).
    - Cinnamon Champagne: Sassy red-blazer cow reporter (political reporter.jpg).
    - Sunshine Innocent Nimbus: Deadpan goth weather girl cow (weather_v2.jpg).

    Visual style across all assets: Bold clean 2D vector line art, flat cel shading, The Pasture aesthetic.
    """

    user_prompt = f"""
    Current Headlines:
    {news_context}

    Generate a complete 3-post publishing package for our 3-column Instagram grid:

    ### COLUMN 1: 60-SECOND EPISODE REEL (9:16 Vertical Video — 1080x1920)
    Generate 6 sequential 10-second clips:
    - Clip 1: Thaddeus' Corner Office (assignment clash)
    - Clip 2: Station Hallway Walk-and-Talk (Tiffany & Valhalla bickering)
    - Clip 3: Newsroom Bullpen (Valhalla & Cinnamon production chaos)
    - Clip 4: MOO19 News Anchor Desk (Skip & Noelle pre-show vanity)
    - Clip 5: Live Pundit Crossfire Desk (Tiffany vs. Valhalla debate)
    - Clip 6: Hallway Fallout / Slammed Door (Thaddeus & Sunshine)
    For each clip: Google Flow Prompt, character reference tag, camera directions, and dialogue. Include Reel caption + hashtags.

    ### COLUMN 2: NEWSROOM MEMO / ARTIFACT (4:5 Portrait Graphic — 1080x1350)
    - Exact Google Flow image prompt for an in-universe desk artifact (1080x1350 portrait, with key elements kept inside the central 1080x1080 safe zone).
    - Memo text typed on MOO19 letterhead from Thaddeus addressing this week's newsroom chaos.
    - Accompanying Instagram caption + hashtags.

    ### COLUMN 3: PUNDIT QUOTE CARD / COGNITIVE DISSONANCE TRAP (4:5 Portrait Graphic — 1080x1350)
    - Exact Google Flow image prompt for a split 4:5 visual (Tiffany on the left, Valhalla on the right, keeping faces inside the middle 1080x1080 safe zone).
    - Left/Right contrasting quotes reacting to one of the headlines.
    - Provocative engagement caption designed to trigger comments + saves.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )
    return response.text

if __name__ == "__main__":
    os.makedirs("episodes", exist_ok=True)
    news = fetch_top_stories()
    bundle_content = generate_episode_bundle(news)
    
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = f"episodes/{date_str}-content-bundle.md"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# MOO19 3-Column Instagram Package — {date_str}\n\n")
        f.write(f"### Headlines Scanned\n{news}\n\n---\n\n")
        f.write(bundle_content)
    
    print(f"Successfully generated 3-column bundle at {file_path}")
