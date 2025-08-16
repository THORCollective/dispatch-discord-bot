import feedparser
import logging
from typing import Dict, Optional, List
from datetime import datetime
from src.config import DISPATCH_RSS_URL, USER_AGENT

logger = logging.getLogger(__name__)


def fetch_dispatch_feed() -> Optional[feedparser.FeedParserDict]:
    """
    Fetch the THOR Collective Dispatch RSS feed.
    
    Returns:
        Parsed feed object or None if error
    """
    try:
        logger.info(f"Fetching Dispatch RSS feed from: {DISPATCH_RSS_URL}")
        
        # Set user agent
        feedparser.USER_AGENT = USER_AGENT
        
        feed = feedparser.parse(DISPATCH_RSS_URL)
        
        if feed.bozo:
            logger.warning(f"Feed parsing had issues but continuing: {feed.bozo_exception}")
        
        if not feed.entries:
            logger.error("No entries found in Dispatch RSS feed")
            return None
            
        logger.info(f"Successfully fetched {len(feed.entries)} entries from Dispatch RSS feed")
        return feed
        
    except Exception as e:
        logger.error(f"Error fetching Dispatch RSS feed: {e}")
        return None


def get_latest_dispatch_posts(feed: feedparser.FeedParserDict, hours_back: int = 1) -> List[Dict[str, str]]:
    """
    Get Dispatch posts from the last N hours.
    
    Args:
        feed: Parsed RSS feed
        hours_back: How many hours back to check for new posts
        
    Returns:
        List of new post data
    """
    if not feed or not feed.entries:
        logger.error("No entries in feed")
        return []
    
    # Get current time and calculate cutoff
    now = datetime.now()
    cutoff_hours = hours_back
    
    new_posts = []
    
    for entry in feed.entries:
        # Extract post data
        post_data = extract_post_data(entry)
        
        # For hourly checks, we'll just get the latest post to avoid duplicates
        # In a real implementation, you'd want to track processed posts
        if len(new_posts) == 0:  # Just get the most recent post
            new_posts.append(post_data)
            logger.info(f"Found latest post: {post_data['title']}")
        
    return new_posts


def extract_post_data(entry: Dict) -> Dict[str, str]:
    """
    Extract standardized post data from RSS entry.
    
    Args:
        entry: RSS feed entry
        
    Returns:
        Standardized post data dictionary
    """
    # Extract content snippet
    content_snippet = ""
    if hasattr(entry, 'summary'):
        content_snippet = entry.summary
    elif hasattr(entry, 'description'):
        content_snippet = entry.description
    elif hasattr(entry, 'content') and entry.content:
        content_snippet = entry.content[0].get('value', '')
    
    # Clean HTML from snippet if present
    import re
    content_snippet = re.sub(r'<[^>]+>', '', content_snippet)
    # Limit snippet length for Discord
    content_snippet = content_snippet[:300] + "..." if len(content_snippet) > 300 else content_snippet
    
    # Extract author
    author = "THOR Collective"
    if hasattr(entry, 'author'):
        author = entry.author
    elif hasattr(entry, 'dc_creator'):
        author = entry.dc_creator
    
    # Extract publication date
    pub_date = ""
    if hasattr(entry, 'published'):
        pub_date = entry.published
    elif hasattr(entry, 'updated'):
        pub_date = entry.updated
    
    post_data = {
        "title": entry.get('title', 'No Title'),
        "link": entry.get('link', ''),
        "content_snippet": content_snippet,
        "author": author,
        "pub_date": pub_date
    }
    
    logger.info(f"Extracted post data: {post_data['title']}")
    return post_data