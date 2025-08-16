#!/usr/bin/env python3
import logging
import sys
from src.config import LOG_FORMAT, LOG_LEVEL, DRY_RUN
from src.rss_handler import fetch_dispatch_feed, get_latest_dispatch_posts
from src.discord_poster import DispatchDiscordPoster

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dispatch_monitor.log')
    ]
)

logger = logging.getLogger(__name__)


def handle_error(error: Exception, context: str) -> None:
    """
    Handle errors with logging and Discord notification.
    
    Args:
        error: The exception that occurred
        context: Context about where the error occurred
    """
    error_msg = f"Error in {context}: {str(error)}"
    logger.error(error_msg, exc_info=True)
    
    # Send Discord notification for critical errors
    try:
        discord = DispatchDiscordPoster()
        discord.send_error_notification(error_msg)
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")


def monitor_dispatch() -> bool:
    """
    Main function to monitor THOR Collective Dispatch feed.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("=" * 50)
    logger.info("Starting THOR Collective Dispatch Monitor")
    logger.info(f"Dry run mode: {DRY_RUN}")
    logger.info("=" * 50)
    
    try:
        # Step 1: Fetch Dispatch RSS feed
        logger.info("Fetching THOR Collective Dispatch RSS feed")
        feed = fetch_dispatch_feed()
        if not feed:
            raise Exception("Failed to fetch Dispatch RSS feed")
        
        # Step 2: Get latest posts (checking last hour)
        logger.info("Checking for new Dispatch posts")
        new_posts = get_latest_dispatch_posts(feed, hours_back=1)
        
        if not new_posts:
            logger.info("No new Dispatch posts found")
            return True
        
        # Step 3: Post each new update to Discord
        discord_poster = DispatchDiscordPoster()
        success_count = 0
        
        for post in new_posts:
            logger.info(f"Processing post: {post['title']}")
            
            success = discord_poster.post_to_discord(
                title=post['title'],
                link=post['link'],
                content_snippet=post['content_snippet']
            )
            
            if success:
                success_count += 1
                logger.info(f"Successfully posted: {post['title']}")
            else:
                logger.error(f"Failed to post: {post['title']}")
        
        # Summary
        logger.info("=" * 50)
        logger.info("Dispatch Monitor completed")
        logger.info(f"New posts found: {len(new_posts)}")
        logger.info(f"Successfully posted: {success_count}")
        logger.info("=" * 50)
        
        return success_count == len(new_posts)
        
    except Exception as e:
        handle_error(e, "dispatch monitoring")
        return False


def main() -> None:
    """
    Main entry point for the Dispatch monitor.
    """
    try:
        # Test connections if in dry run mode
        if DRY_RUN:
            logger.info("Running in DRY RUN mode - no actual posts will be made")
        
        # Run main monitoring
        success = monitor_dispatch()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user")
        sys.exit(0)
    except Exception as e:
        handle_error(e, "main")
        sys.exit(1)


if __name__ == "__main__":
    main()