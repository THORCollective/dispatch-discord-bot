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
    cutoff_time = now.timestamp() - (hours_back * 3600)  # Convert hours to seconds
    
    new_posts = []
    
    for entry in feed.entries:
        # Parse the publication date
        entry_time = None
        
        # Try to get publication time from various fields
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            import time
            entry_time = time.mktime(entry.published_parsed)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            import time
            entry_time = time.mktime(entry.updated_parsed)
        elif hasattr(entry, 'published'):
            try:
                from dateutil import parser
                parsed_date = parser.parse(entry.published)
                entry_time = parsed_date.timestamp()
            except:
                logger.warning(f"Could not parse date: {entry.published}")
        
        # If we can't determine the time, skip this entry
        if entry_time is None:
            logger.warning(f"Could not determine publication time for: {entry.get('title', 'Unknown')}")
            continue
        
        # Check if this post is within our time window
        if entry_time >= cutoff_time:
            post_data = extract_post_data(entry)
            new_posts.append(post_data)
            if hours_back > 24:
                days = hours_back // 24
                logger.info(f"Found post within {days} days: {post_data['title']}")
            else:
                logger.info(f"Found post within {hours_back} hours: {post_data['title']}")
        else:
            # Since RSS feeds are typically ordered by date (newest first), 
            # we can break early once we hit an old post
            logger.debug(f"Post too old: {entry.get('title', 'Unknown')}")
            break
    
    if not new_posts:
        if hours_back > 24:
            days = hours_back // 24
            logger.info(f"No new posts found in the last {days} days")
        else:
            logger.info(f"No new posts found in the last {hours_back} hours")
    
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
    import html
    content_snippet = re.sub(r'<[^>]+>', '', content_snippet)
    # Decode HTML entities
    content_snippet = html.unescape(content_snippet)
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
        "title": html.unescape(entry.get('title', 'No Title')),
        "link": entry.get('link', ''),
        "content_snippet": content_snippet,
        "author": author,
        "pub_date": pub_date
    }
    
    logger.info(f"Extracted post data: {post_data['title']}")
    return post_data