# THOR Collective Dispatch Discord Bot

A GitHub Actions bot that monitors the THOR Collective Dispatch RSS feed and posts new articles to Discord.

## Features

- 🔄 **Hourly Monitoring**: Checks for new Dispatch posts every hour
- 📰 **RSS Feed Integration**: Monitors https://dispatch.thorcollective.com/feed
- 💬 **Discord Integration**: Posts formatted updates to Discord channel
- 🤖 **Bot API**: Uses Discord bot instead of webhooks for reliable posting
- 🛡️ **Error Handling**: Comprehensive error handling with Discord notifications

## Setup

### Prerequisites

- GitHub repository with Actions enabled
- Discord bot with access to target channel

### GitHub Secrets Configuration

Add these secrets to your GitHub repository:

1. **DISCORD_BOT_TOKEN**: Your Discord bot token
   - Create bot at: https://discord.com/developers/applications
   - Generate token in Bot section

2. **DISPATCH_CHANNEL_ID**: Your Discord channel ID (optional)
   - Right-click channel → Copy Channel ID
   - Default: Uses the channel from original n8n workflow

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dispatch-discord-bot.git
cd dispatch-discord-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DISCORD_BOT_TOKEN="your_bot_token"
export DISCORD_CHANNEL_ID="your_channel_id"
```

4. Run in dry-run mode:
```bash
DRY_RUN=true python -m src.main
```

## Usage

### Automatic Hourly Runs

The bot runs automatically every hour via GitHub Actions.

### Manual Trigger

You can manually trigger the workflow:
1. Go to Actions tab in your GitHub repository
2. Select "THOR Collective Dispatch Monitor" workflow
3. Click "Run workflow"
4. Optionally enable dry-run mode

## Message Format

Posts are formatted to match the original n8n workflow:

```
**New THOR Collective Dispatch Post!** 🚀

[Article Title](https://dispatch.thorcollective.com/post-url)

Article preview content...
```

## Project Structure

```
dispatch-discord-bot/
├── .github/
│   └── workflows/
│       └── dispatch-monitor.yml       # GitHub Actions workflow
├── src/
│   ├── main.py                        # Main orchestrator
│   ├── config.py                      # Configuration
│   ├── rss_handler.py                 # RSS feed processing
│   └── discord_poster.py              # Discord bot integration
├── requirements.txt                   # Dependencies
├── .gitignore                         # Git ignore rules
└── README.md                          # Documentation
```

## Configuration

### RSS Feed URL
Default: `https://dispatch.thorcollective.com/feed`

To change the feed, edit `DISPATCH_RSS_URL` in `src/config.py`.

### Check Frequency
Default: Every hour

To change frequency, edit the cron expression in `.github/workflows/dispatch-monitor.yml`:
```yaml
schedule:
  - cron: '0 * * * *'  # Every hour at minute 0
```

### Discord Channel
The bot will post to the channel specified in `DISCORD_CHANNEL_ID` environment variable.

## Troubleshooting

### Bot Not Running
- Check GitHub Actions is enabled
- Verify bot token is configured
- Review workflow logs for errors

### Discord Not Posting
- Verify bot token is valid and bot is in server
- Check bot has permission to send messages in target channel
- Ensure channel ID is correct

### No Posts Detected
- Verify the Dispatch RSS feed is accessible
- Check if new posts are available in the feed
- Review logs for RSS parsing errors

## Migration from n8n

This bot replicates the functionality of the n8n "Dispatch -> Discord" workflow:

- ✅ Hourly RSS feed monitoring
- ✅ Same Discord message format
- ✅ Same target channel (configurable)
- ✅ Error handling and notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details