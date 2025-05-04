import html
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

# Register XML namespaces to make parsing cleaner
ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

# Constants
DEFAULT_AINEWS_RSS_URL = "https://news.smol.ai/rss.xml"
USER_AGENT = "ainews-reader/1.0"


async def fetch_ainews_rss(feed_url: str = DEFAULT_AINEWS_RSS_URL) -> str:
    """
    Fetch AI News RSS feed.

    Args:
        feed_url: URL of the RSS feed to fetch (defaults to AI News)

    Returns:
        RSS content as string or error message
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


def extract_twitter_recap(content: str) -> List[Dict[str, str]]:
    """
    Extract AI Twitter Recap section from the full content.

    Args:
        content: Full HTML content from the article

    Returns:
        List of dictionaries containing title, description and link for each recap item
    """
    # Convert HTML entities
    content = html.unescape(content)

    # Find the Twitter Recap section
    twitter_recap_match = re.search(
        r"<h1>AI Twitter Recap</h1>(.*?)(?:<h1>|$)", content, re.DOTALL
    )
    if not twitter_recap_match:
        return []

    twitter_recap_section = twitter_recap_match.group(1)

    # Extract bullet points from the Twitter Recap section
    bullet_points = []
    bullet_pattern = re.findall(r"<li>(.*?)</li>", twitter_recap_section, re.DOTALL)

    for bullet in bullet_pattern:
        clean_bullet = re.sub(r"<.*?>", "", bullet).strip()

        # Extract title (part before the colon)
        title_match = re.match(r"^(.*?):", clean_bullet)
        if title_match:
            title = title_match.group(1).strip()
            description = clean_bullet[len(title_match.group(0)) :].strip()
        else:
            title = clean_bullet
            description = ""

        # Extract first link
        link_match = re.search(r'<a href="([^"]+)"', bullet)
        link = link_match.group(1) if link_match else ""

        bullet_points.append({"title": title, "description": description, "link": link})

    return bullet_points


def parse_ainews_rss(rss_content: str) -> List[Dict[str, Any]]:
    """
    Parse RSS content and extract the latest story only.

    Args:
        rss_content: RSS XML content as string

    Returns:
        List containing only the latest article as dictionary
    """
    stories = []
    try:
        root = ET.fromstring(rss_content)
        items = root.findall(".//item")

        if items:
            # Only process the latest item (the first one in the RSS feed)
            item = items[0]
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
            }

            # Get full content if available
            content_element = item.find(
                ".//{http://purl.org/rss/1.0/modules/content/}encoded"
            )
            if content_element is not None and content_element.text:
                story["content"] = content_element.text
                # Extract Twitter recap items
                story["twitter_recap"] = extract_twitter_recap(content_element.text)
            else:
                story["content"] = ""
                story["twitter_recap"] = []

            # Extract categories if available
            categories = item.findall("category")
            if categories:
                story["categories"] = [cat.text for cat in categories if cat.text]
            else:
                story["categories"] = []

            stories.append(story)

        return stories
    except ET.ParseError as e:
        return [{"error": f"Error parsing XML: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error parsing RSS: {str(e)}"}]


def format_ainews_story(story: Dict[str, Any]) -> str:
    """
    Format an AI News story into a readable string.

    Args:
        story: Dictionary containing article data

    Returns:
        Formatted article string
    """
    # Check if this is an error message
    if "error" in story:
        return f"ERROR: {story['error']}"

    # Format the article
    title = story.get("title", "Unknown Title")
    link = story.get("link", "No link available")
    pub_date = story.get("pubDate", "Unknown publication date")
    description = story.get("description", "No description available")

    # Build the formatted string with the new order
    formatted = f"""
Title: {title}
Link: {link}
Description: {description}
Published: {pub_date}
"""

    # Add Twitter recap if available, but without the header
    twitter_recap = story.get("twitter_recap", [])
    if twitter_recap:
        formatted += "\n\n"  # Add space but no header
        for item in twitter_recap:
            formatted += f"Title: {item['title']}\nLink: {item['link']}\nDescription: {item['description']}\n\n"

    # Add categories if available
    categories = story.get("categories", [])
    if categories:
        formatted += f"\nCategories: {', '.join(categories)}"

    return formatted
