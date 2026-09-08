"""
scripts/generate_episode.py
Generates the complete 3-column Instagram content cadence for MOO19 News:
- Column 1: 60s Reel (Script + Google Flow Prompts + After Effects Plan)
- Column 2: Newsroom Artifact / Memo (Thaddeus Memos, Redlines, Production Notes)
- Column 3: Pundit Quote Trap (Tiffany vs. Valhalla Debate Card)
"""

import datetime
import json
import os
import sys
from pathlib import Path
from google import genai
from google.genai import types

from fetch_news import get_top_news_item
from notify import send_discord_alert, create_github_issue


def load_character_config(config_path: str = "config/characters.json") -> dict:
    path = Path(config_path)
    if not path.exists():
        return {"setting": "MOO19 Backstage Bullpen", "characters": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("CRITICAL: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)

    print("Fetching top news headline...")
    news_item = get_top_news_item()
    print(f"Target News Headline: {news_item['title']}")

    char_config = load_character_config()
    roster_lines = [
        f"- {name}: {meta.get('handle', f'@{name}')} ({meta.get('role', '')})"
        for name, meta in char_config.get("characters", {}).items()
    ]
    roster_text = "\n".join(roster_lines)

    system_instruction = f"""
You are the Executive Showrunner and Social Media Director for "COWRENT AFFAIRS: BACKSTAGE AT MOO19" set in "The Pasture" animated universe.
Visual Style: Bold black ink outlines, saturated colors, flat 2D cel shading.
Tone: Fast-paced workplace satire (The Mary Tyler Moore Show / Murphy Brown / Lou Grant dynamic). The Instagram feed @moo19news is run in-universe by Thaddeus, the stressed, cynical news director.

EVERY BROADCAST CADENCE REQUIRES THREE POSTS (THE 3-COLUMN GRID):
1. COLUMN 1 (Reel): 60-second video broken into 6 x 10-second segments. Prompts must use character handles (@Thaddeus, @Skip, @Noelle, @Frank, @Isaac, @Tiffany, @Valhalla, @Sunshine).
2. COLUMN 2 (Memo Artifact): In-universe typed memos, coffee-stained production directives, or redlined teleprompter copy signed by Thaddeus.
3. COLUMN 3 (Pundit Trap Card): Split-screen ideological debate between Tiffany Rees-Moog (Conservative elitist in pearls) and Valhalla Spiker (Progressive firebrand anti-corporate). High cognitive dissonance clash.
"""

    user_prompt = f"""
BREAKING HEADLINE TO PARODY:
Title: {news_item['title']}
Summary: {news_item['summary']}

Generate the complete production packet for this 4-day cycle. Format strictly in Markdown:

# EPISODE CADENCE: [Catchy Satirical Title]
**Real Headline:** {news_item['title']}
**Core Backstage Conflict:** [One sentence on how MOO19 implodes reacting to this news]

---

## 📱 COLUMN 1: THE 60-SECOND SITCOM REEL
### Locked Dialogue Script (0:00 - 1:00)
[Complete fast-paced backstage banter between crew and talent]

### Google Flow 10-Second Generation Prompts
Provide six distinct clip prompts (Clip 01 to Clip 06).
Each clip MUST include:
- **Time:** [e.g. 0:00-0:10]
- **Locked Audio:** [Dialogue spoken in this clip]
- **Google Flow Prompt:** [Wide/Medium/Close shot, @Handles used with minimal redundant adjectives, blocking, backstage fluorescent lighting, cel-shaded 2D aesthetic, camera move]
- **After Effects Edit:** [Punch-in, whip-pan, split-screen, or caption snap]

### Instagram Feed Copy (Column 1)
- **Headline:** [Hook with emojis]
- **Caption:** [Workplace comedy context in Thaddeus' voice]
- **Call-to-Action:** [Audience comment question]
- **Hashtags:** [#MOO19 #CowrentAffairs #WorkplaceComedy #ThePasture #Animation #MurphyBrownVibes]

---

## 📄 COLUMN 2: NEWSROOM ARTIFACT / MEMO
### Graphic Asset Concept
- **Asset Type:** [e.g., Coffee-stained memo / Redlined teleprompter / Whiteboard policy ban]
- **Visual Design Spec:** [Letterhead styling, handwritten scribbles, coffee rings, bold black outlines]
- **Text On Graphic:**
  [Provide exact verbatim text formatted on MOO19 BROADCAST OPERATIONS letterhead, signed by Thaddeus]

### Instagram Feed Copy (Column 2)
- **Caption:** [Dry bulletin announcement from management]
- **Hashtags:** [#NewsroomHumor #ThaddeusTakes #BullpenLife #MOO19News]

---

## ⚡ COLUMN 3: PUNDIT QUOTE CARD / TRAP
### Split-Screen Visual Spec
- **Left Panel (Tiffany Rees-Moog):** [Visual pose, pearl necklace, condescending posture, bold quote]
- **Right Panel (Valhalla Spiker):** [Visual pose, disheveled suit, angry pointing, counter-quote]
- **Graphic Color Scheme:** [Broadcast Navy Blue vs. Studio Orange with Yellow divider]

### The Debate Quotes
- **Tiffany Rees-Moog:** "[High-society constitutional clapback on the news]"
- **Valhalla Spiker:** "[Working-class populist outrage clapback]"

### Instagram Feed Copy (Column 3)
- **Caption:** [Cognitive dissonance trap hook framing the green room fight]
- **Call-to-Action:** [Ask audience to pick a side in comments]
- **Hashtags:** [#MooMentum #SpikeTheSpin #CowrentAffairs #MediaDebate #PearlsAndPolicy]
"""

    print("Requesting 3-column production packet from Gemini...")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.8,
        ),
    )

    cadence_output = response.text

    # Write to local file
    now = datetime.datetime.now()
    timestamp_slug = now.strftime("%Y-%m-%d_%H%M")
    episodes_dir = Path("episodes")
    episodes_dir.mkdir(exist_ok=True)
    file_path = episodes_dir / f"{timestamp_slug}_grid_cadence.md"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cadence_output)

    print(f"Cadence package saved: {file_path}")

    # Dispatch alerts
    send_discord_alert(
        episode_title=f"Grid Cadence {now.strftime('%b %d')}",
        headline=news_item["title"],
        file_path=str(file_path),
    )
    create_github_issue(
        title=f"Grid Cadence [{now.strftime('%b %d')}]: {news_item['title'][:45]}...",
        markdown_body=cadence_output,
    )


if __name__ == "__main__":
    main()
