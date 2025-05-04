from mcp.server.fastmcp import FastMCP

from ainews import (
    DEFAULT_AINEWS_RSS_URL,
    fetch_ainews_rss,
    format_ainews_story,
    parse_ainews_rss,
)
from hackernews import DEFAULT_HN_RSS_URL, fetch_hn_rss, format_hn_story, parse_hn_rss
from techcrunch import DEFAULT_TC_RSS_URL, fetch_tc_rss, format_tc_story, parse_tc_rss
from wired import (
    DEFAULT_WIRED_RSS_URL,
    fetch_wired_rss,
    format_wired_story,
    parse_wired_rss,
)
from wsj import DEFAULT_WSJ_RSS_URL, fetch_wsj_rss, format_wsj_story, parse_wsj_rss

# Initialize FastMCP server
mcp = FastMCP("news-mcp")


@mcp.tool()
async def get_hackernews_stories(
    feed_url: str = DEFAULT_HN_RSS_URL, count: int = 30
) -> str:
    """Get top stories from Hacker News.

    Args:
        feed_url: URL of the RSS feed to use (default: Hacker News)
        count: Number of stories to return (default: 5)
    """
    rss_content = await fetch_hn_rss(feed_url)
    if rss_content.startswith("Error"):
        return rss_content

    stories = parse_hn_rss(rss_content)

    # Limit to requested count
    stories = stories[: min(count, len(stories))]

    if not stories:
        return "No stories found."

    formatted_stories = [format_hn_story(story) for story in stories]
    return "\n---\n".join(formatted_stories)


@mcp.tool()
async def get_wallstreetjournal_stories(
    feed_url: str = DEFAULT_WSJ_RSS_URL, count: int = 30
) -> str:
    """Get stories from Wall Street Journal.

    Args:
        feed_url: URL of the WSJ RSS feed to use
        count: Number of stories to return (default: 5)
    """
    # Fetch the content
    rss_content = await fetch_wsj_rss(feed_url)
    if rss_content.startswith("Error"):
        return rss_content

    stories = parse_wsj_rss(rss_content)

    # Check for errors in parsing
    if stories and "error" in stories[0]:
        return stories[0]["error"]

    # Limit to requested count
    stories = stories[: min(count, len(stories))]

    if not stories:
        return "No stories found."

    formatted_stories = [format_wsj_story(story) for story in stories]
    return "\n---\n".join(formatted_stories)


@mcp.tool()
async def get_techcrunch_stories(
    feed_url: str = DEFAULT_TC_RSS_URL, count: int = 30
) -> str:
    """Get stories from TechCrunch.

    Args:
        feed_url: URL of the TechCrunch RSS feed to use
        count: Number of stories to return (default: 30)
    """
    # Fetch the content
    rss_content = await fetch_tc_rss(feed_url)
    if rss_content.startswith("Error"):
        return rss_content

    stories = parse_tc_rss(rss_content)

    # Check for errors in parsing
    if stories and "error" in stories[0]:
        return stories[0]["error"]

    # Limit to requested count
    stories = stories[: min(count, len(stories))]

    if not stories:
        return "No stories found."

    formatted_stories = [format_tc_story(story) for story in stories]
    return "\n---\n".join(formatted_stories)


@mcp.tool()
async def get_ainews_latest(feed_url: str = DEFAULT_AINEWS_RSS_URL) -> str:
    """Get the latest story from AI News.

    Args:
        feed_url: URL of the AI News RSS feed to use (default: AI News)
    """
    # Fetch the content
    rss_content = await fetch_ainews_rss(feed_url)
    if rss_content.startswith("Error"):
        return rss_content

    stories = parse_ainews_rss(rss_content)

    # Check for errors in parsing
    if stories and "error" in stories[0]:
        return stories[0]["error"]

    if not stories:
        return "No stories found."

    # Only format the latest story
    return format_ainews_story(stories[0])


@mcp.tool()
async def get_wired_stories(
    feed_url: str = DEFAULT_WIRED_RSS_URL, count: int = 30
) -> str:
    """Get AI stories from Wired.

    Args:
        feed_url: URL of the Wired RSS feed to use (default: Wired AI feed)
        count: Number of stories to return (default: 30)
    """
    # Fetch the content
    rss_content = await fetch_wired_rss(feed_url)
    if rss_content.startswith("Error"):
        return rss_content

    stories = parse_wired_rss(rss_content)

    # Check for errors in parsing
    if stories and "error" in stories[0]:
        return stories[0]["error"]

    # Limit to requested count
    stories = stories[: min(count, len(stories))]

    if not stories:
        return "No stories found."

    formatted_stories = [format_wired_story(story) for story in stories]
    return "\n---\n".join(formatted_stories)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
