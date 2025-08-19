#!/usr/bin/env python3
"""Test Discord embed functionality."""
import discord
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')


async def test_embed():
    """Test sending an embed to Discord."""
    # Configure intents
    intents = discord.Intents.default()
    intents.message_content = True
    
    # Create client
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"Bot connected as: {client.user}")
        
        # Get channel
        channel = client.get_channel(int(DISCORD_CHANNEL_ID))
        if not channel:
            print(f"Could not find channel with ID: {DISCORD_CHANNEL_ID}")
            await client.close()
            return
            
        print(f"Found channel: {channel.name}")
        
        # Test 1: Simple message
        await channel.send("Test 1: Simple message")
        
        # Test 2: Message with embed
        embed = discord.Embed(
            title="Test Dispatch Post",
            description="This is a test description for the dispatch post to see if embeds work correctly.",
            url="https://dispatch.thorcollective.com/test",
            color=discord.Color.blue()
        )
        embed.add_field(name="Author", value="THOR Collective", inline=False)
        embed.set_footer(text="THOR Collective Dispatch")
        
        await channel.send(content="Test 2: Message with embed", embed=embed)
        
        # Test 3: Just embed without message
        embed2 = discord.Embed(
            title="My First DEFCON: A Noob's Chronicle",
            description="Day One &#8211; Line Con and Noob Village",
            url="https://dispatch.thorcollective.com/my-first-defcon-a-noobs-chronicle-of-chaos-coffee-and-crypto-stickers/",
            color=0x0080ff
        )
        await channel.send(embed=embed2)
        
        # Test 4: Using the exact format from our bot
        embed3 = discord.Embed(
            title="My First DEFCON: A Noob's Chronicle of Chaos, Coffee, and Crypto Stickers",
            description="Day One &#8211; Line Con and Noob Village",
            url="https://dispatch.thorcollective.com/my-first-defcon-a-noobs-chronicle-of-chaos-coffee-and-crypto-stickers/",
            color=discord.Color.blue()
        )
        await channel.send(content="**New THOR Collective Dispatch Post!** 🚀", embed=embed3)
        
        print("All tests sent successfully!")
        await client.close()
    
    # Start the client
    await client.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(test_embed())