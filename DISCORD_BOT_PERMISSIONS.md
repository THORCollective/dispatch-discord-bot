# Discord Bot Permissions Required

## Essential Permissions

The bot needs the following permissions in the Discord server/channel:

### Required Permissions:
- **View Channels** - To see the channel
- **Send Messages** - To post messages
- **Embed Links** - To send rich embeds (THIS IS CRITICAL!)
- **Read Message History** - To verify messages were sent

### Optional but Recommended:
- **Attach Files** - If you want to send images directly
- **Use External Emojis** - For custom emoji support
- **Add Reactions** - If you want the bot to react to messages

## How to Set Permissions

### Method 1: When Adding Bot to Server
1. Use this permission calculator: https://discordapi.com/permissions.html
2. Select these permissions:
   - View Channels
   - Send Messages
   - Embed Links
   - Read Message History
3. This generates permission integer: `84992` (minimum required)
4. Add to your bot invite URL: 
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=84992&scope=bot
   ```

### Method 2: In Discord Server Settings
1. Go to Server Settings → Roles
2. Find your bot's role
3. Enable these permissions:
   - View Channels
   - Send Messages
   - Embed Links
   - Read Message History

### Method 3: Channel-Specific Permissions
1. Right-click the channel → Edit Channel
2. Go to Permissions
3. Add your bot role or bot user
4. Enable:
   - View Channel
   - Send Messages
   - Embed Links
   - Read Message History

## Common Issues

### Embeds Not Showing?
1. **Missing "Embed Links" permission** - Most common cause!
2. **Bot role is below @everyone** - Move bot role higher in role hierarchy
3. **Channel overrides** - Check channel-specific permission overrides
4. **Discord settings** - Users can disable embeds in their personal settings

### How to Debug:
1. Check bot permissions in the specific channel:
   - Type: `/permissions @YourBot #channel-name`
2. Verify the bot role position:
   - Server Settings → Roles → Drag bot role higher
3. Test with admin permissions temporarily:
   - Give bot Administrator permission
   - If it works, it's definitely a permission issue
   - Remove admin and add specific permissions

## Permission Integer Calculator

Common permission combinations:
- `84992` - Basic (View, Send, Embed, History)
- `379904` - Basic + Files + Reactions
- `8` - Administrator (use only for testing!)

## Checking Current Bot Permissions

You can check what permissions your bot has by:
1. Right-click the bot user in Discord
2. Select "Roles" to see assigned roles
3. Check each role's permissions in Server Settings

## Important Notes

- **Embed Links is REQUIRED** for Discord embeds to display
- Without this permission, only plain text will show
- The bot needs permissions in BOTH the server AND the specific channel
- Channel permissions can override server permissions