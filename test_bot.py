#!/usr/bin/env python3
"""
Simple test script to verify the bot is working
"""

import os
import asyncio
import discord
from dotenv import load_dotenv

async def test_bot():
    """Test if the bot can connect to Discord."""
    load_dotenv()
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found in .env file")
        return False
    
    # Create a simple bot to test connection
    intents = discord.Intents.default()
    intents.reactions = True
    intents.guilds = True
    intents.message_content = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"✅ Bot connected as {client.user}")
        print(f"📊 Connected to {len(client.guilds)} guilds:")
        for guild in client.guilds:
            print(f"   - {guild.name} (ID: {guild.id})")
        
        # Close the connection after testing
        await client.close()
    
    try:
        await client.start(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Testing bot connection...")
    try:
        result = asyncio.run(test_bot())
        if result:
            print("✅ Bot test successful!")
        else:
            print("❌ Bot test failed!")
    except Exception as e:
        print(f"❌ Test error: {e}")