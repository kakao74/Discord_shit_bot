"""
Discord Shit Tracker Bot
Content monitoring with AI-powered text improvement
Works in ALL Discord servers where the bot is added
"""

import discord
from discord.ext import commands
import logging
import os
import sys
import asyncio
import aiohttp
import json
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict, deque
import time

# Setup logging without emojis for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Add console handler without emojis
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

class OpenRouterTextImprover:
    """OpenRouter API integration for text improvement."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openrouter/auto"
    
    async def improve_text(self, original_text: str) -> Optional[str]:
        """Improve the flagged text using OpenRouter API."""
        try:
            if not original_text or original_text.strip() == "*No text content*":
                return None
            
            prompt = f"""Improve this inappropriate message to be more respectful and constructive:

Original: "{original_text}"

Provide only the improved text, no explanations."""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You improve text to be respectful and appropriate."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        improved_text = result['choices'][0]['message']['content'].strip()
                        improved_text = improved_text.strip('"').strip("'").strip()
                        logger.debug(f"AI improved text: {improved_text}")
                        return improved_text
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error improving text: {e}")
            return None

class ShitTrackerBot(commands.Bot):
    """Discord bot for content monitoring with AI text improvement."""
    
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.reactions = True
        intents.guilds = True
        intents.message_content = True
        
        super().__init__(
            command_prefix='!st ',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Configuration
        self.target_emoji = '💩'
        
        # Initialize AI text improver
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.text_improver = OpenRouterTextImprover(openrouter_key) if openrouter_key else None
        if not self.text_improver:
            logger.warning("OPENROUTER_API_KEY not set - AI text improvement disabled")
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: deque(maxlen=10))
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 5      # max reactions per window
    
    async def on_ready(self):
        """Bot ready event."""
        logger.info(f'Bot {self.user} connected to Discord!')
        logger.info(f'Monitoring {len(self.guilds)} guilds:')
        
        for guild in self.guilds:
            logger.info(f'   - {guild.name} (ID: {guild.id})')
        
        if self.text_improver:
            logger.info("OpenRouter AI text improvement enabled")
        else:
            logger.warning("AI text improvement disabled (no API key)")
        
        # Set presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{self.target_emoji} reactions in all servers"
            ),
            status=discord.Status.online
        )
        
        logger.info("Bot ready and monitoring ALL servers!")
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited."""
        now = time.time()
        user_actions = self.rate_limits[user_id]
        
        # Remove old actions outside the window
        while user_actions and now - user_actions[0] > self.rate_limit_window:
            user_actions.popleft()
        
        # Check if user exceeded limit
        if len(user_actions) >= self.rate_limit_max:
            return True
        
        # Add current action
        user_actions.append(now)
        return False
    
    async def on_reaction_add(self, reaction, user):
        """Handle reaction events - works in ALL servers."""
        try:
            # Skip bot reactions
            if user.bot:
                return
            
            # Check if it's the target emoji
            if str(reaction.emoji) != self.target_emoji:
                return
            
            # Skip DMs
            if not reaction.message.guild:
                logger.debug("Reaction in DM, ignoring")
                return
            
            # Rate limiting
            if self._check_rate_limit(user.id):
                logger.debug(f"Rate limited user {user.name}")
                return
            
            message = reaction.message
            
            # Log the reaction
            logger.info(f"Poop reaction by {user.name} in guild: {message.guild.name} (ID: {message.guild.id})")
            
            # Handle the incident
            await self._handle_incident(reaction, user)
            
        except Exception as e:
            logger.error(f"Error in on_reaction_add: {e}")
    
    async def _handle_incident(self, reaction, user):
        """Handle flagged content incident."""
        try:
            message = reaction.message
            
            # Create the flagged content embed
            embed = discord.Embed(
                title="💩 Content Flagged",
                color=0xFF6B35,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add message content
            content = message.content or "*No text content*"
            if len(content) > 1000:
                content = content[:997] + "..."
            
            embed.add_field(
                name="📝 Original Message",
                value=f"```{content}```",
                inline=False
            )
            
            embed.add_field(
                name="👤 Author",
                value=f"{message.author.mention}",
                inline=True
            )
            
            embed.add_field(
                name="😡 Flagged by",
                value=f"{user.mention}",
                inline=True
            )
            
            embed.add_field(
                name="📍 Server",
                value=f"{message.guild.name}",
                inline=True
            )
            
            embed.add_field(
                name="🔗 Jump to Message",
                value=f"[Click here]({message.jump_url})",
                inline=False
            )
            
            embed.set_footer(text=f"Message ID: {message.id}")
            
            # Send the flagged content embed
            try:
                await message.channel.send(embed=embed)
                logger.info(f"Flagged content logged in {message.guild.name}")
            except Exception as e:
                logger.error(f"Failed to send flagged embed: {e}")
            
            # Try to get AI improvement
            if self.text_improver and content != "*No text content*":
                logger.debug("Requesting AI text improvement...")
                improved_text = await self.text_improver.improve_text(content)
                
                if improved_text:
                    # Send AI improvement
                    improvement_embed = discord.Embed(
                        title="🤖 AI-Improved Version",
                        description="Here's how this message could be improved:",
                        color=0x00D4AA,
                        timestamp=datetime.now(timezone.utc)
                    )
                    
                    improvement_embed.add_field(
                        name="✨ Suggested Improvement",
                        value=f"```{improved_text}```",
                        inline=False
                    )
                    
                    improvement_embed.set_footer(text="Powered by OpenRouter AI • Use as guidance only")
                    
                    try:
                        await message.channel.send(embed=improvement_embed)
                        logger.info("AI improvement sent")
                    except Exception as e:
                        logger.error(f"Failed to send AI improvement: {e}")
                else:
                    # Send error message
                    error_embed = discord.Embed(
                        title="🤖 AI Improvement",
                        description="❌ Could not generate improved text for this message.",
                        color=0xFF4444
                    )
                    try:
                        await message.channel.send(embed=error_embed)
                    except Exception as e:
                        logger.error(f"Failed to send AI error: {e}")
            
        except Exception as e:
            logger.error(f"Error handling incident: {e}")
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information."""
        embed = discord.Embed(
            title="🤖 Shit Tracker Bot",
            description="Content monitoring bot with AI-powered text improvement",
            color=0x3498DB
        )
        
        embed.add_field(
            name="📋 Commands",
            value="`!st help` - Show this help\n"
                  "`!st ping` - Check bot status\n"
                  "`!st improve <text>` - Test AI text improvement",
            inline=False
        )
        
        embed.add_field(
            name="🎯 How it works",
            value=f"React with {self.target_emoji} to any message to flag it for review.\n"
                  "The bot will log the incident and provide an AI-improved version.",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value=f"• Works in: **All servers where bot is added**\n"
                  f"• AI Improvement: `{'Enabled' if self.text_improver else 'Disabled'}`\n"
                  f"• Rate Limit: 5 reactions per minute per user",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot status."""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        latency = round(self.latency * 1000, 2)
        response_time = round((end_time - start_time) * 1000, 2)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x2ECC71
        )
        
        embed.add_field(
            name="📡 WebSocket Latency",
            value=f"{latency}ms",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Response Time",
            value=f"{response_time}ms",
            inline=True
        )
        
        embed.add_field(
            name="🤖 AI Status",
            value="Enabled" if self.text_improver else "Disabled",
            inline=True
        )
        
        embed.add_field(
            name="🌐 Servers",
            value=f"{len(self.guilds)} servers",
            inline=True
        )
        
        await message.edit(content=None, embed=embed)
    
    @commands.command(name='improve')
    async def improve_text(self, ctx, *, text: str):
        """Test AI text improvement."""
        if not self.text_improver:
            await ctx.send("❌ AI text improvement is not available (no OpenRouter API key configured)")
            return
        
        if len(text) > 500:
            await ctx.send("❌ Text too long (max 500 characters)")
            return
        
        async with ctx.typing():
            improved = await self.text_improver.improve_text(text)
        
        if improved:
            embed = discord.Embed(
                title="🤖 Text Improvement Test",
                color=0x00D4AA
            )
            
            embed.add_field(
                name="📝 Original",
                value=f"```{text}```",
                inline=False
            )
            
            embed.add_field(
                name="✨ Improved",
                value=f"```{improved}```",
                inline=False
            )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to improve text. Please try again later.")

async def main():
    """Main function."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")
    
    # Check required environment variables
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        return
    
    # Create and run bot
    bot = ShitTrackerBot()
    
    try:
        logger.info("Starting Discord Shit Tracker Bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)