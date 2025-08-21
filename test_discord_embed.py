#!/usr/bin/env python3
"""Test script to debug Discord embed posting."""

import discord
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

async def test_embed():
    """Test sending an embed to Discord."""
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f'Bot connected as {client.user}')
        
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Could not find channel {CHANNEL_ID}")
            await client.close()
            return
            
        print(f"Found channel: {channel.name}")
        
        # Test 1: Simple message
        await channel.send("Test 1: Simple text message")
        
        # Test 2: Message with basic embed
        embed = discord.Embed(
            title="Test 2: Basic Embed",
            description="This is a basic embed test",
            color=discord.Color.blue()
        )
        await channel.send("Message with basic embed:", embed=embed)
        
        # Test 3: Full embed like our dispatch posts
        full_embed = discord.Embed(
            title="Ask-a-Thrunter: July 2025 Recap",
            description="Mainly ramblings. And maybe some wisdom.",
            url="https://dispatch.thorcollective.com/test",
            color=discord.Color.blue()
        )
        full_embed.set_author(
            name="Ask-a-Thrunter",
            url="https://dispatch.thorcollective.com"
        )
        full_embed.set_thumbnail(url="https://dispatch.thorcollective.com/favicon.ico")
        full_embed.set_footer(text="THOR Collective Dispatch")
        full_embed.timestamp = discord.utils.utcnow()
        
        await channel.send("**New THOR Collective Dispatch Post!** 🚀", embed=full_embed)
        
        print("All tests sent successfully!")
        await asyncio.sleep(2)
        await client.close()
    
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(test_embed())