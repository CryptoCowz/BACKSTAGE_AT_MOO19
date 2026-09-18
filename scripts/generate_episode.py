import json
import os
from datetime import datetime
import feedparser
from google import genai
from google.genai import types
from google.oauth2 import service_account
from googleapiclient.discovery import build

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


def fetch_bts_production_notes():
  sa_json_str = os.environ.get("GCP_SA_KEY")
  folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

  if not sa_json_str or not folder_id:
    print(
        "Missing GCP_SA_KEY or GOOGLE_DRIVE_FOLDER_ID. Using default newsroom"
        " lore."
    )
    return (
        "No specific BTS draft provided. Rely on general newsroom workplace"
        " tension (Metrics vs. Mood War, Thaddeus managing chaotic talent)."
    )

  try:
    service_account_info = json.loads(sa_json_str)
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    drive_service = build("drive", "v3", credentials=creds)

    # Search for Google Docs containing 'Cowrent Affairs' inside the specified folder
    query = (
        f"'{folder_id}' in parents and name contains 'Cowrent Affairs' and"
        " mimeType = 'application/vnd.google-apps.document' and trashed = false"
    )

    results = (
        drive_service.files()
        .list(
            q=query,
            orderBy="modifiedTime desc",  # Dynamically selects the most recently updated doc
            pageSize=1,
            fields="files(id, name, modifiedTime)",
        )
        .execute()
    )

    files = results.get("files", [])
    if not files:
      print("No matching 'Cowrent Affairs' documents found in folder.")
      return (
          "No matching BTS draft found in folder. Rely on general newsroom"
          " dynamics."
      )

    latest_file = files[0]
    print(
        f"Found latest production doc: {latest_file['name']} (ID:"
        f" {latest_file['id']})"
    )

    # Export document text as plain text
    request = drive_service.files().export_media(
        fileId=latest_file["id"], mimeType="text/plain"
    )
    content = request.execute().decode("utf-8")
    print(f"Successfully loaded {len(content)} characters from Google Doc.")
    return content[:4500]

  except Exception as e:
    print(f"Warning: Could not fetch from Google Drive: {e}")
    return (
        "No specific BTS draft loaded. Rely on standard newsroom workplace"
        " tension."
    )


def generate_episode_bundle(news_context, bts_context):
  client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

  system_instruction = """
    You are the head writer and showrunner for "MOO19 News / Cowrent Affairs," an animated workplace 
    satire modeled after The Mary Tyler Moore Show and Murphy Brown, set inside The Pasture universe.
    
    Cast of Characters:
    - Thaddeus: Grumpy bull Editor-in-Chief, flat-top head, lit cigar, powder blue shirt, orange tie (Jonah.jpg).
    - Tiffany Rees-Moog: Conservative blonde cow, gold hoops, cross necklace, posh and fiery (R_exp2.jpg).
    - Valhalla Spiker: Progressive afro bull, charcoal blazer, bead choker, sarcastic justice realist (valhalla2k.jpg).
    - Skip Zinfandel: Smug pompadour bull lead anchor, purple tie, obsessed with golf and liquor (NEWSCASTER_v2.jpg).
    - Noelle Piper Grace: Glamorous blonde cow co-anchor, green dress, pearl necklace, cultured airhead (CO ANCHOR.jpg).
    - Cinnamon Champagne: Sassy red-blazer cow reporter, loves social justice, morale rituals, and gratitude tools (political reporter.jpg).
    - Miles: Hyper-analytical producer obsessed with workflow metrics, spreadsheets, and vibe-risk scores.
    - Sunshine Innocent Nimbus: Deadpan goth weather girl cow, black lipstick, pentagram necklace (weather_v2.jpg).

    Visual Style: Clean, bold 2D cartoon animation with defined black outlines and flat cel shading matching The Pasture ecosystem.
    """

  user_prompt = f"""
    CURRENT NEWS HEADLINES:
    {news_context}

    INTERNAL PRODUCTION DRAFT & BEHIND-THE-SCENES HIGHLIGHTS:
    {bts_context}

    Generate the complete 3-post publishing package for our 3-column Instagram grid cadence:

    ### COLUMN 1: 60-SECOND EPISODE REEL (9:16 Vertical Video — 1080x1920)
    Generate 6 sequential 10-second clips integrating the physical BTS gags and props from the production draft:
    - Clip 1: Thaddeus' Corner Office (assignment clash using props/memos from draft)
    - Clip 2: Station Hallway Walk-and-Talk (Tiffany & Valhalla bickering over the headline topic)
    - Clip 3: Newsroom Bullpen (Animate the specific "Metrics vs. Mood War" gag between Miles & Cinnamon)
    - Clip 4: MOO19 News Anchor Desk (Skip & Noelle pre-show vanity and oblivious banter)
    - Clip 5: Live Pundit Crossfire Desk (Tiffany vs. Valhalla using dialogue beats from the draft)
    - Clip 6: Hallway Fallout / Slammed Door (Thaddeus reacting to the physical prop disaster)
    For each clip: Google Flow Prompt, character reference tag, camera directions, and dialogue. Include Reel caption + hashtags.

    ### COLUMN 2: NEWSROOM MEMO / ARTIFACT (4:5 Portrait Graphic — 1080x1350)
    - Exact Google Flow image prompt for the physical artifact featured in this draft (e.g., the 41-page trust matrix, the cardboard evidence board, or the sealed envelope with lavender wax stamp). Keep all key items inside the center 1080x1080 safe zone.
    - The full typed text of the memo or document from Thaddeus addressing the incident.
    - Accompanying Instagram caption + hashtags.

    ### COLUMN 3: PUNDIT QUOTE CARD / COGNITIVE DISSONANCE TRAP (4:5 Portrait Graphic — 1080x1350)
    - Exact Google Flow image prompt for a split 4:5 visual (Tiffany on the left, Valhalla on the right, keeping faces centered).
    - Left/Right contrasting quotes pulled directly from the bicker thread in the draft.
    - Provocative caption designed to trigger comments and debate.
    """

  response = client.models.generate_content(
      model="gemini-3.6-flash",
      contents=user_prompt,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction,
          temperature=0.7,
      ),
  )
  return response.text


if __name__ == "__main__":
  os.makedirs("episodes", exist_ok=True)
  news = fetch_top_stories()
  bts = fetch_bts_production_notes()
  bundle_content = generate_episode_bundle(news, bts)

  date_str = datetime.utcnow().strftime("%Y-%m-%d")
  file_path = f"episodes/{date_str}-content-bundle.md"

  with open(file_path, "w", encoding="utf-8") as f:
    f.write(f"# MOO19 3-Column Instagram Package — {date_str}\n\n")
    f.write(
        f"### Source Context\n**Headlines:**\n{news}\n\n**BTS Production"
        f" Draft:**\n{bts}\n\n---\n\n"
    )
    f.write(bundle_content)

  print(f"Successfully generated 3-column bundle at {file_path}")
