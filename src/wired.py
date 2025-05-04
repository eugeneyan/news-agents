import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

# Register XML namespaces
ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ET.register_namespace("media", "http://search.yahoo.com/mrss/")

# Constants
DEFAULT_WIRED_RSS_URL = "https://www.wired.com/feed/tag/ai/latest/rss"
USER_AGENT = "wired-reader/1.0"


async def fetch_wired_rss(feed_url: str = DEFAULT_WIRED_RSS_URL) -> str:
    """
    Fetch Wired AI RSS feed.

    Args:
        feed_url: URL of the RSS feed to fetch (defaults to Wired AI feed)

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


def parse_wired_rss(rss_content: str) -> List[Dict[str, Any]]:
    """
    Parse Wired RSS content into a list of article dictionaries.

    Args:
        rss_content: RSS XML content as string

    Returns:
        List of dictionaries containing article data
    """
    articles = []
    try:
        root = ET.fromstring(rss_content)
        channel = root.find("channel")

        # Check if we found a channel
        if channel is None:
            return [{"error": "Invalid RSS format: No channel element found"}]

        items = channel.findall("item")

        for item in items:
            article = {}

            # Basic fields
            article["title"] = get_element_text(item, "title", "No title")
            article["link"] = get_element_text(item, "link", "")
            article["pubDate"] = get_element_text(item, "pubDate", "")
            article["description"] = get_element_text(
                item, "description", "No description"
            )
            article["guid"] = get_element_text(item, "guid", "")

            # DC fields (author)
            creator = item.find(".//{http://purl.org/dc/elements/1.1/}creator")
            article["author"] = (
                creator.text if creator is not None and creator.text else ""
            )

            # DC subject (section)
            subject = item.find(".//{http://purl.org/dc/elements/1.1/}subject")
            article["subject"] = (
                subject.text if subject is not None and subject.text else ""
            )

            # Handle multiple categories
            categories = item.findall("category")
            if categories:
                article["categories"] = [cat.text for cat in categories if cat.text]
            else:
                article["categories"] = []

            # Media thumbnail
            thumbnail = item.find(".//{http://search.yahoo.com/mrss/}thumbnail")
            if thumbnail is not None and "url" in thumbnail.attrib:
                article["image_url"] = thumbnail.attrib["url"]
                article["image_width"] = thumbnail.attrib.get("width", "")
                article["image_height"] = thumbnail.attrib.get("height", "")
            else:
                article["image_url"] = ""
                article["image_width"] = ""
                article["image_height"] = ""

            articles.append(article)

        return articles
    except ET.ParseError as e:
        return [{"error": f"Error parsing XML: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error parsing RSS: {str(e)}"}]


def get_element_text(element, tag, default=""):
    """Helper function to safely extract element text."""
    el = element.find(tag)
    return el.text if el is not None and el.text else default


def format_wired_story(story: Dict[str, Any]) -> str:
    """
    Format a Wired story into a readable string.

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
    author = story.get("author", "")
    subject = story.get("subject", "")
    categories = story.get("categories", [])

    # Build the formatted string
    formatted = f"""
Title: {title}
Link: {link}"""

    if author:
        formatted += f"\nAuthor: {author}"

    if subject:
        formatted += f"\nSubject: {subject}"

    formatted += f"\nPublished: {pub_date}"

    if categories:
        formatted += f"\nCategories: {', '.join(categories)}"

    formatted += f"\n\n{description}\n"

    return formatted
