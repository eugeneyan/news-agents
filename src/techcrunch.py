import xml.etree.ElementTree as ET
from typing import Any, Dict, List

import httpx

# Register XML namespaces to make parsing cleaner
ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")
ET.register_namespace("wfw", "http://wellformedweb.org/CommentAPI/")
ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
ET.register_namespace("sy", "http://purl.org/rss/1.0/modules/syndication/")
ET.register_namespace("slash", "http://purl.org/rss/1.0/modules/slash/")

# Constants
DEFAULT_TC_RSS_URL = "https://techcrunch.com/feed/"
USER_AGENT = "techcrunch-reader/1.0"


async def fetch_tc_rss(feed_url: str) -> str:
    """
    Fetch TechCrunch RSS feed.

    Args:
        feed_url: URL to fetch (defaults to TechCrunch main feed)

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


def parse_tc_rss(rss_content: str) -> List[Dict[str, Any]]:
    """
    Parse TechCrunch RSS content into a list of article dictionaries.

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

            # Required fields (with fallbacks)
            article["title"] = get_element_text(item, "title", "No title")
            article["link"] = get_element_text(item, "link", "")
            article["pubDate"] = get_element_text(item, "pubDate", "")
            article["description"] = get_element_text(
                item, "description", "No description"
            )

            # Handle author (dc:creator)
            author = item.find(".//{http://purl.org/dc/elements/1.1/}creator")
            article["author"] = (
                author.text if author is not None and author.text else ""
            )

            # Handle GUID
            guid_element = item.find("guid")
            if guid_element is not None:
                article["guid"] = guid_element.text or ""
                article["guid_permalink"] = guid_element.attrib.get(
                    "isPermaLink", "false"
                )
            else:
                article["guid"] = ""
                article["guid_permalink"] = "false"

            # Handle multiple categories
            categories = item.findall("category")
            if categories:
                article["categories"] = [cat.text for cat in categories if cat.text]
            else:
                article["categories"] = []

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


def format_tc_story(story: Dict[str, Any]) -> str:
    """
    Format a TechCrunch story into a readable string.

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
    categories = story.get("categories", [])

    # Build the formatted string
    formatted = f"""
Title: {title}
Link: {link}"""

    if author:
        formatted += f"\nAuthor: {author}"

    formatted += f"\nPublished: {pub_date}"

    if categories:
        formatted += f"\nCategories: {', '.join(categories)}"

    formatted += f"\n\n{description}\n"

    return formatted
