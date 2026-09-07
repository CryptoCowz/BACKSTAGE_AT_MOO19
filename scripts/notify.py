"""
scripts/notify.py
Dispatches alerts and summaries to Discord webhooks or creates GitHub Issues.
"""

import os
import json
import requests
from typing import Optional


def send_discord_alert(
    episode_title: str,
    headline: str,
    file_path: str,
    webhook_url: Optional[str] = None,
) -> bool:
    """Sends a formatted embed message to a Discord webhook."""
    target_url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
    if not target_url:
        print("No DISCORD_WEBHOOK_URL provided. Skipping Discord ping.")
        return False

    payload = {
        "username": "MOO19 Automated Wire",
        "embeds": [
            {
                "title": f"🎬 New MOO19 Episode Ready: {episode_title}",
                "description": f"**Reacting to:** {headline}\n**Output:** `{file_path}`",
                "color": 15158332,  # Crimson Red
                "footer": {"text": "Google Flow Production Packet Ready for AE Sync"},
            }
        ],
    }

    try:
        res = requests.post(
            target_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10,
        )
        res.raise_for_status()
        print("Discord notification delivered.")
        return True
    except requests.RequestException as exc:
        print(f"Failed to post to Discord: {exc}")
        return False


def create_github_issue(title: str, markdown_body: str) -> bool:
    """Creates a GitHub Issue containing the full prompt packet for quick mobile access."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")  # Populated automatically in Actions

    if not token or not repo:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY unset. Skipping Issue creation.")
        return False

    api_url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": f"[Episode Packet] {title}",
        "body": markdown_body,
        "labels": ["episode", "prompts"],
    }

    try:
        res = requests.post(api_url, headers=headers, json=data, timeout=10)
        res.raise_for_status()
        print(f"GitHub Issue created: {res.json().get('html_url')}")
        return True
    except requests.RequestException as exc:
        print(f"Failed to create GitHub Issue: {exc}")
        return False
