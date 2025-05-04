import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

# Register XML namespaces to make parsing cleaner
ET.register_namespace("media", "http://search.yahoo.com/mrss/")
ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

# Constants
DEFAULT_WSJ_RSS_URL = "https://feeds.content.dowjones.io/public/rss/RSSWSJD"
USER_AGENT = "wsj-reader/1.0"


async def fetch_wsj_rss(feed_url: str) -> str:
    """
    Fetch Wall Street Journal RSS feed.

    Args:
        feed_url: URL to fetch

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


def parse_wsj_rss(rss_content: str) -> List[Dict[str, Any]]:
    """
    Parse RSS content into a list of article dictionaries.

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
            # Extract all common fields
            article = {}

            # Required fields (with fallbacks)
            article["title"] = get_element_text(item, "title", "No title")
            article["link"] = get_element_text(item, "link", "")
            article["pubDate"] = get_element_text(item, "pubDate", "")
            article["description"] = get_element_text(
                item, "description", "No description"
            )

            # Handle multiple authors (dc:creator elements)
            authors = item.findall(".//{http://purl.org/dc/elements/1.1/}creator")
            if authors:
                article["author"] = ", ".join([a.text for a in authors if a.text])
            else:
                article["author"] = ""

            article["guid"] = get_element_text(item, "guid", "")
            article["category"] = get_element_text(item, "category", "")

            # Optional WSJ-specific field for article ID
            article["id"] = get_element_text(item, "id", "")

            # Extract image URL if available
            article["image_url"] = extract_image_url(item)

            articles.append(article)

        return articles
    except ET.ParseError as e:
        return [{"error": f"Error parsing XML: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Error parsing RSS: {str(e)}"}]


def get_element_text(element, tag, default=""):
    """Helper function to safely extract element text."""
    # Handle both regular tags and namespaced tags
    el = element.find(tag)

    # Look for namespaced tags
    if el is None:
        # Handle specific namespaces
        if tag == "creator":
            el = element.find(".//{http://purl.org/dc/elements/1.1/}creator")
        else:
            # Try various namespace paths
            el = element.find(f"*//{tag}")

    return el.text if el is not None and el.text else default


def extract_image_url(item: ET.Element) -> str:
    """Extract image URL from various possible elements."""
    # Try different possible locations for image
    media_content = item.find(".//{http://search.yahoo.com/mrss/}content")
    if media_content is not None and "url" in media_content.attrib:
        return media_content.attrib["url"]

    media_thumbnail = item.find(".//{http://search.yahoo.com/mrss/}thumbnail")
    if media_thumbnail is not None and "url" in media_thumbnail.attrib:
        return media_thumbnail.attrib["url"]

    enclosure = item.find("enclosure")
    if enclosure is not None and "url" in enclosure.attrib:
        return enclosure.attrib["url"]

    return ""


def format_wsj_story(story: Dict[str, Any]) -> str:
    """
    Format a WSJ story into a readable string.

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

    # Build the formatted string
    formatted = f"""
Title: {title}
Link: {link}"""

    if author:
        formatted += f"\nAuthor: {author}"

    formatted += f"""
Published: {pub_date}

{description}
"""

    return formatted
