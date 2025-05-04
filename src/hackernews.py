import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

# Constants
DEFAULT_HN_RSS_URL = "https://news.ycombinator.com/rss"
USER_AGENT = "hackernews-reader/1.0"


async def fetch_hn_rss(feed_url: str) -> str:
    """
    Fetch Hacker News RSS feed.

    Args:
        feed_url: URL of the RSS feed to fetch (defaults to Hacker News)
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(feed_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            return f"HTTP Error fetching RSS: {str(e)}"
        except httpx.TimeoutException:
            return f"Timeout fetching RSS from {feed_url}"
        except Exception as e:
            return f"Error fetching RSS: {str(e)}"


def parse_hn_rss(rss_content: str) -> List[Dict[str, Any]]:
    """Parse RSS content into a list of story dictionaries."""
    stories = []
    try:
        root = ET.fromstring(rss_content)
        items = root.findall(".//item")

        for item in items:
            story = {
                "title": item.find("title").text
                if item.find("title") is not None
                else "No title",
                "link": item.find("link").text if item.find("link") is not None else "",
                "description": item.find("description").text
                if item.find("description") is not None
                else "No description",
                "pubDate": item.find("pubDate").text
                if item.find("pubDate") is not None
                else "",
                # Any other fields we want to extract
            }
            stories.append(story)

        return stories
    except Exception as e:
        return [{"error": f"Error parsing RSS: {str(e)}"}]


def format_hn_story(story: Dict[str, Any]) -> str:
    """Format a story into a readable string."""
    formatted = f"""
Title: {story.get("title", "Unknown")}
Link: {story.get("link", "No link")}
Published: {story.get("pubDate", "Unknown")}
"""

    return formatted
