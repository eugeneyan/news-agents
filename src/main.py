from mcp.server.fastmcp import FastMCP

from hackernews import DEFAULT_HN_RSS_URL, fetch_hn_rss, format_hn_story, parse_hn_rss
from wsj import DEFAULT_WSJ_RSS_URL, fetch_wsj_rss, format_wsj_story, parse_wsj_rss

# Initialize FastMCP server
mcp = FastMCP("my-mcp")


@mcp.tool()
async def get_hn_stories(feed_url: str = DEFAULT_HN_RSS_URL, count: int = 30) -> str:
    """Get top stories from Hacker News or similar RSS feeds.

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
async def get_wsj_stories(feed_url: str = DEFAULT_WSJ_RSS_URL, count: int = 30) -> str:
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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
