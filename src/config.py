import os

# THOR Collective Dispatch RSS feed
DISPATCH_RSS_URL = "https://dispatch.thorcollective.com/feed"

# Environment variables
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "1367529936729935983")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# HTTP headers for RSS requests
USER_AGENT = "Mozilla/5.0 (compatible; THOR-Dispatch-Bot/1.0)"