import discord
import asyncio
import logging
from typing import Optional
from src.config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, DRY_RUN

logger = logging.getLogger(__name__)


class DispatchDiscordPoster:
    def __init__(self):
        """Initialize Discord bot client."""
        self.bot_token = DISCORD_BOT_TOKEN
        self.channel_id = DISCORD_CHANNEL_ID
        
        if not self.bot_token:
            logger.warning("Discord bot token not configured")
            self.client = None
        else:
            # Configure intents for the bot
            intents = discord.Intents.default()
            intents.message_content = True
            self.client = discord.Client(intents=intents)
            logger.info("Discord client initialized")
    
    def format_dispatch_message(self, title: str, link: str, content_snippet: str) -> str:
        """
        Format message for Discord (matching the n8n workflow format).
        
        Args:
            title: Post title
            link: Post URL
            content_snippet: Post content preview
            
        Returns:
            Formatted Discord message
        """
        # Clean up title and content to remove any problematic characters
        clean_title = title.strip()
        clean_content = content_snippet.strip()
        
        # Ensure URL is properly formatted
        if not link.startswith('http'):
            link = f"https://{link}"
        
        # Format message with better structure
        message = f"**New THOR Collective Dispatch Post!** 🚀\n\n{clean_title}\n\n{clean_content}\n\n[Read more]({link})"
        
        # Ensure message doesn't exceed Discord limit (2000 chars)
        if len(message) > 2000:
            # Trim content snippet to fit
            base_message = f"**New THOR Collective Dispatch Post!** 🚀\n\n{clean_title}\n\n"
            footer = f"\n\n[Read more]({link})"
            available_space = 2000 - len(base_message) - len(footer) - 3  # 3 for "..."
            if available_space > 50:
                clean_content = clean_content[:available_space] + "..."
                message = base_message + clean_content + footer
        
        logger.debug(f"Formatted Discord message: {message}")
        return message
    
    def post_multiple_to_discord(self, posts: list) -> int:
        """
        Post multiple Dispatch updates to Discord in a single session.
        
        Args:
            posts: List of post dictionaries with title, link, content_snippet, author
            
        Returns:
            Number of successfully posted messages
        """
        if not self.bot_token or DRY_RUN:
            logger.info(f"Skipping Discord posts (dry_run={DRY_RUN}, token={bool(self.bot_token)})")
            if DRY_RUN:
                for post in posts:
                    message = self.format_dispatch_message(post['title'], post['link'], post['content_snippet'])
                    logger.info(f"[DRY RUN] Would post to Discord:\n{message}")
            return len(posts)
        
        # Prepare all embeds
        embeds_to_send = []
        for post in posts:
            link = post['link']
            if not link.startswith('http'):
                link = f"https://{link}"
            
            embed_data = {
                'title': post['title'].strip(),
                'description': post['content_snippet'].strip()[:500],
                'url': link,
                'author': post.get('author') or 'Ask-a-Thrunter',
                'author_url': 'https://dispatch.thorcollective.com',
                'thumbnail': 'https://pbs.twimg.com/profile_images/1719421917473927168/Aaifurr1_400x400.jpg',
                'footer': 'THOR Collective Dispatch'
            }
            embeds_to_send.append(embed_data)
        
        # Run the async posting function with a single client
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            client = discord.Client(intents=intents)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._post_multiple_messages_with_client(client, embeds_to_send))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running async Discord posts: {e}")
            return 0
    
    def post_to_discord(self, title: str, link: str, content_snippet: str, author: str = None) -> bool:
        """
        Post Dispatch update to Discord.
        
        Args:
            title: Post title
            link: Post URL
            content_snippet: Post content preview
            author: Optional author name
            
        Returns:
            True if posted successfully, False otherwise
        """
        if not self.bot_token or DRY_RUN:
            logger.info(f"Skipping Discord post (dry_run={DRY_RUN}, token={bool(self.bot_token)})")
            if DRY_RUN:
                message = self.format_dispatch_message(title, link, content_snippet)
                logger.info(f"[DRY RUN] Would post to Discord:\n{message}")
            return True
        
        # Ensure URL is properly formatted
        if not link.startswith('http'):
            link = f"https://{link}"
        
        # Create embed data for rich formatting with all the necessary fields
        embed_data = {
            'title': title.strip(),
            'description': content_snippet.strip()[:500],  # Discord embed description limit
            'url': link,
            'author': author or 'Ask-a-Thrunter',  # Use provided author or default
            'author_url': 'https://dispatch.thorcollective.com',  # Author URL
            'thumbnail': 'https://pbs.twimg.com/profile_images/1719421917473927168/Aaifurr1_400x400.jpg',  # THOR Collective logo
            'footer': 'THOR Collective Dispatch'
        }
        
        # Main message
        message = "**New THOR Collective Dispatch Post!** 🚀"
        
        # Run the async posting function with a fresh client
        try:
            # Create a new client for this message
            intents = discord.Intents.default()
            intents.message_content = True
            client = discord.Client(intents=intents)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._post_message_with_client(client, message, embed_data))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error running async Discord post: {e}")
            return False
    
    async def _post_multiple_messages_with_client(self, client: discord.Client, embeds_to_send: list) -> int:
        """
        Async function to post multiple messages to Discord with a single client.
        
        Args:
            client: Discord client instance
            embeds_to_send: List of embed data dictionaries
            
        Returns:
            Number of successfully posted messages
        """
        try:
            if not self.channel_id:
                logger.error("Discord channel ID not configured")
                return 0
                
            try:
                channel_id_int = int(self.channel_id)
            except ValueError:
                logger.error(f"Invalid channel ID format: {self.channel_id}")
                return 0
            
            ready_event = asyncio.Event()
            messages_sent = 0
            
            @client.event
            async def on_ready():
                nonlocal messages_sent
                logger.info(f"Bot connected as: {client.user}")
                
                channel = client.get_channel(channel_id_int)
                if not channel:
                    logger.error(f"Could not find channel with ID: {self.channel_id}")
                    logger.info("Available channels:")
                    for guild in client.guilds:
                        for ch in guild.text_channels:
                            logger.info(f"  - {ch.name} (ID: {ch.id})")
                else:
                    logger.info(f"Found channel: {channel.name} in {channel.guild.name}")
                    
                    # Send all embeds with rate limit handling
                    for i, embed_data in enumerate(embeds_to_send):
                        try:
                            embed = discord.Embed(
                                title=embed_data.get('title', ''),
                                description=embed_data.get('description', ''),
                                url=embed_data.get('url', ''),
                                color=0x0099ff
                            )
                            
                            if embed_data.get('author'):
                                embed.set_author(
                                    name=embed_data.get('author'),
                                    url=embed_data.get('author_url', '')
                                )
                            
                            if embed_data.get('thumbnail'):
                                embed.set_thumbnail(url=embed_data.get('thumbnail'))
                            
                            if embed_data.get('footer'):
                                embed.set_footer(text=embed_data.get('footer'))
                            
                            embed.timestamp = discord.utils.utcnow()
                            
                            logger.info(f"Sending embed {i+1}/{len(embeds_to_send)}: {embed.title}")
                            
                            message = "**New THOR Collective Dispatch Post!** 🚀"
                            sent_message = await channel.send(content=message, embed=embed)
                            logger.info(f"Message sent with ID: {sent_message.id}")
                            messages_sent += 1
                            
                            # Add delay between messages to avoid rate limiting
                            if i < len(embeds_to_send) - 1:
                                await asyncio.sleep(2)  # 2 second delay between posts
                                
                        except discord.HTTPException as e:
                            logger.error(f"Failed to send embed {i+1}: {e}")
                            if "rate limited" in str(e).lower():
                                logger.info("Rate limited, waiting 5 seconds...")
                                await asyncio.sleep(5)
                                # Try again
                                try:
                                    sent_message = await channel.send(content=message, embed=embed)
                                    messages_sent += 1
                                except:
                                    logger.error(f"Failed to retry embed {i+1}")
                    
                    logger.info(f"Successfully posted {messages_sent}/{len(embeds_to_send)} messages to Discord")
                
                await asyncio.sleep(1)
                ready_event.set()
                await client.close()
            
            logger.info("Connecting to Discord...")
            await client.start(self.bot_token)
            
            await ready_event.wait()
            return messages_sent
            
        except discord.LoginFailure:
            logger.error("Discord login failed - check bot token")
            return 0
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to send messages in this channel")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error posting to Discord: {e}")
            return 0
        finally:
            if client and not client.is_closed():
                await client.close()
    
    async def _post_message_with_client(self, client: discord.Client, message: str, embed_data: Optional[dict] = None) -> bool:
        """
        Async function to post message to Discord with a specific client.
        
        Args:
            client: Discord client instance
            message: Formatted message to post
            embed_data: Optional embed data for rich formatting
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            # Get the channel ID
            if not self.channel_id:
                logger.error("Discord channel ID not configured")
                return False
                
            try:
                channel_id_int = int(self.channel_id)
            except ValueError:
                logger.error(f"Invalid channel ID format: {self.channel_id}")
                return False
            
            # Create event for when bot is ready
            ready_event = asyncio.Event()
            message_sent = False
            
            @client.event
            async def on_ready():
                nonlocal message_sent
                logger.info(f"Bot connected as: {client.user}")
                
                # Get the channel
                channel = client.get_channel(channel_id_int)
                if not channel:
                    logger.error(f"Could not find channel with ID: {self.channel_id}")
                    # List available channels for debugging
                    logger.info("Available channels:")
                    for guild in client.guilds:
                        for ch in guild.text_channels:
                            logger.info(f"  - {ch.name} (ID: {ch.id})")
                else:
                    logger.info(f"Found channel: {channel.name} in {channel.guild.name}")
                    
                    # Send with embed if provided
                    if embed_data:
                        embed = discord.Embed(
                            title=embed_data.get('title', ''),
                            description=embed_data.get('description', ''),
                            url=embed_data.get('url', ''),
                            color=0x0099ff  # Use hex color instead of discord.Color
                        )
                        
                        # Add author information
                        if embed_data.get('author'):
                            embed.set_author(
                                name=embed_data.get('author'),
                                url=embed_data.get('author_url', '')
                            )
                        
                        # Add thumbnail  
                        if embed_data.get('thumbnail'):
                            embed.set_thumbnail(url=embed_data.get('thumbnail'))
                        
                        # Add footer
                        if embed_data.get('footer'):
                            embed.set_footer(text=embed_data.get('footer'))
                        
                        # Add timestamp
                        embed.timestamp = discord.utils.utcnow()
                        
                        # Log embed details for debugging
                        logger.info(f"Sending embed with title: {embed.title}")
                        logger.info(f"Embed URL: {embed.url}")
                        logger.info(f"Embed author: {embed.author.name if embed.author else 'None'}")
                        logger.info(f"Embed thumbnail: {embed.thumbnail.url if embed.thumbnail else 'None'}")
                        
                        # Send the message with embed
                        sent_message = await channel.send(content=message, embed=embed)
                        logger.info(f"Message sent with ID: {sent_message.id}")
                    else:
                        await channel.send(message)
                    
                    logger.info("Successfully posted to Discord")
                    message_sent = True
                
                # Wait a moment to ensure message is fully sent
                await asyncio.sleep(1)
                ready_event.set()
                await client.close()
            
            # Start the client
            logger.info("Connecting to Discord...")
            await client.start(self.bot_token)
            
            # Wait for ready event
            await ready_event.wait()
            return message_sent
            
        except discord.LoginFailure:
            logger.error("Discord login failed - check bot token")
            return False
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to send messages in this channel")
            return False
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting to Discord: {e}")
            return False
        finally:
            if client and not client.is_closed():
                await client.close()
    
    async def _post_message_async(self, message: str, embed_data: Optional[dict] = None) -> bool:
        """
        Async function to post message to Discord.
        
        Args:
            message: Formatted message to post
            embed_data: Optional embed data for rich formatting
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            # Get the channel ID
            if not self.channel_id:
                logger.error("Discord channel ID not configured")
                return False
                
            try:
                channel_id_int = int(self.channel_id)
            except ValueError:
                logger.error(f"Invalid channel ID format: {self.channel_id}")
                return False
            
            # Create event for when bot is ready
            ready_event = asyncio.Event()
            message_sent = False
            
            @self.client.event
            async def on_ready():
                nonlocal message_sent
                logger.info(f"Bot connected as: {self.client.user}")
                
                # Get the channel
                channel = self.client.get_channel(channel_id_int)
                if not channel:
                    logger.error(f"Could not find channel with ID: {self.channel_id}")
                    # List available channels for debugging
                    logger.info("Available channels:")
                    for guild in self.client.guilds:
                        for ch in guild.text_channels:
                            logger.info(f"  - {ch.name} (ID: {ch.id})")
                else:
                    logger.info(f"Found channel: {channel.name} in {channel.guild.name}")
                    
                    # Send with embed if provided
                    if embed_data:
                        embed = discord.Embed(
                            title=embed_data.get('title', ''),
                            description=embed_data.get('description', ''),
                            url=embed_data.get('url', ''),
                            color=0x0099ff  # Use hex color instead of discord.Color
                        )
                        
                        # Add author information
                        if embed_data.get('author'):
                            embed.set_author(
                                name=embed_data.get('author'),
                                url=embed_data.get('author_url', '')
                            )
                        
                        # Add thumbnail  
                        if embed_data.get('thumbnail'):
                            embed.set_thumbnail(url=embed_data.get('thumbnail'))
                        
                        # Add footer
                        if embed_data.get('footer'):
                            embed.set_footer(text=embed_data.get('footer'))
                        
                        # Add timestamp
                        embed.timestamp = discord.utils.utcnow()
                        
                        # Log embed details for debugging
                        logger.info(f"Sending embed with title: {embed.title}")
                        logger.info(f"Embed URL: {embed.url}")
                        logger.info(f"Embed author: {embed.author.name if embed.author else 'None'}")
                        logger.info(f"Embed thumbnail: {embed.thumbnail.url if embed.thumbnail else 'None'}")
                        
                        # Send the message with embed
                        sent_message = await channel.send(content=message, embed=embed)
                        logger.info(f"Message sent with ID: {sent_message.id}")
                    else:
                        await channel.send(message)
                    
                    logger.info("Successfully posted to Discord")
                    message_sent = True
                
                # Wait a moment to ensure message is fully sent
                await asyncio.sleep(1)
                ready_event.set()
                await self.client.close()
            
            # Start the client
            logger.info("Connecting to Discord...")
            await self.client.start(self.bot_token)
            
            # Wait for ready event
            await ready_event.wait()
            return message_sent
            
        except discord.LoginFailure:
            logger.error("Discord login failed - check bot token")
            return False
        except discord.Forbidden:
            logger.error("Bot doesn't have permission to send messages in this channel")
            return False
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting to Discord: {e}")
            return False
        finally:
            if self.client and not self.client.is_closed():
                await self.client.close()
    
    def send_error_notification(self, error_msg: str) -> bool:
        """
        Send error notification to Discord.
        
        Args:
            error_msg: Error message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.bot_token or DRY_RUN:
            logger.info(f"Skipping error notification (dry_run={DRY_RUN}, token={bool(self.bot_token)})")
            return True
        
        error_message = f"⚠️ **Dispatch Monitor Error** ⚠️\n\n{error_msg}"
        
        try:
            # Create a new client for this message
            intents = discord.Intents.default()
            intents.message_content = True
            client = discord.Client(intents=intents)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._post_message_with_client(client, error_message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False