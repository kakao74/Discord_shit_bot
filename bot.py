"""
Discord Shit Tracker Bot
Content monitoring with AI-powered text improvement
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime, timezone
import os
import sys
from typing import Optional, Dict
from dataclasses import dataclass
import time
from collections import defaultdict, deque
import aiohttp
import json

# Configure logging
class ColoredFormatter(logging.Formatter):
    """Colored log formatter for better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level))
    
    logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

logger = setup_logging()

@dataclass
class IncidentData:
    """Simple incident data structure."""
    message_id: str
    channel_id: str
    guild_id: str
    message_author_id: str
    message_author_name: str
    reactor_id: str
    reactor_name: str
    message_content: str
    timestamp: datetime
    message_url: str
    channel_name: str
    guild_name: str
    
    def __post_init__(self):
        """Clean and validate data."""
        # Ensure timestamp is timezone-aware
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
        
        # Truncate long content
        if len(self.message_content) > 1000:
            self.message_content = self.message_content[:997] + "..."
        
        # Clean usernames
        self.message_author_name = self.message_author_name.strip()
        self.reactor_name = self.reactor_name.strip()

class OpenRouterTextImprover:
    """OpenRouter API integration for text improvement."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Use a widely available model on OpenRouter (update as needed)
        # You can check https://openrouter.ai/docs for more free/available models
        self.model = "openrouter/auto"
    
    async def improve_text(self, original_text: str) -> Optional[str]:
        """Improve the flagged text using OpenRouter API."""
        try:
            if not original_text or original_text.strip() == "*No text content*":
                return None
            
            # Create the prompt
            prompt = f"""
You are a helpful assistant that improves inappropriate or problematic text messages to make them more respectful and constructive.

Original message: "{original_text}"

Please provide an improved version that:
1. Maintains the core intent/meaning if possible
2. Uses respectful and appropriate language
3. Is constructive rather than destructive
4. Follows community guidelines
5. Is concise (under 200 characters)

If the message cannot be improved while maintaining any meaningful intent, suggest a completely different constructive message on a similar topic.

Respond with only the improved text, no explanations or quotes.
"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/discord-shit-bot",  # Optional: for OpenRouter
                "X-Title": "Discord Shit Tracker Bot"  # Optional: for OpenRouter
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that improves text to be more respectful and appropriate."},
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
                        
                        # Clean up the response
                        improved_text = improved_text.strip('"').strip("'").strip()
                        
                        logger.debug(f"OpenRouter improved text: {improved_text}")
                        return improved_text
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error improving text with OpenRouter: {e}")
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
            command_prefix=self._get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        # Configuration
        self.target_guild_id = self._get_env_int('TARGET_GUILD_ID')
        self.target_emoji = '💩'
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.text_improver = OpenRouterTextImprover(openrouter_key) if openrouter_key else None
        if not self.text_improver:
            logger.warning("OPENROUTER_API_KEY not set - text improvement disabled")
        # Simple rate limiting
        self.rate_limits = defaultdict(lambda: deque(maxlen=10))
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 5      # max reactions per window
    
    def _get_prefix(self, bot, message):
        """Get command prefix."""
        return commands.when_mentioned_or(
            os.getenv('COMMAND_PREFIX', '!st ')
        )(bot, message)
    
    def _get_env_int(self, key: str) -> Optional[int]:
        value = os.getenv(key)
        if value and value.strip():
            try:
                return int(value.strip())
            except ValueError:
                logger.error(f"Invalid {key}: {value}")
        return None
    
    async def on_ready(self):
        """Bot ready event."""
        logger.info(f'🤖 {self.user} connected to Discord!')
        logger.info(f'📊 Monitoring {len(self.guilds)} guilds')
        
        # Check OpenRouter status
        if self.text_improver:
            logger.info("🤖 OpenRouter text improvement enabled")
        else:
            logger.warning("⚠️ OpenRouter text improvement disabled (no API key)")
        
        # Set presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{self.target_emoji} reactions"
            ),
            status=discord.Status.online
        )
        
        logger.info("🚀 Bot ready!")
    
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
        """Handle reaction events."""
        try:
            # Quick checks
            if user.bot or str(reaction.emoji) != self.target_emoji:
                return
            
            # Rate limiting
            if self._check_rate_limit(user.id):
                logger.debug(f"Rate limited user {user.name}")
                return
            
            message = reaction.message
            
            # Check if in target guild
            if not message.guild or not self.target_guild_id:
                return
                
            if message.guild.id != self.target_guild_id:
                logger.debug(f"Reaction in non-target guild: {message.guild.name}")
                return
            
            # Handle the incident
            await self._handle_incident(reaction, user)
            
        except Exception as e:
            logger.error(f"Error in on_reaction_add: {e}")
    
    async def _handle_incident(self, reaction, user):
        """Handle flagged content incident."""
        try:
            message = reaction.message
            
            # Create incident data
            incident_data = IncidentData(
                message_id=str(message.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id),
                message_author_id=str(message.author.id),
                message_author_name=f"{message.author.name}#{message.author.discriminator}",
                reactor_id=str(user.id),
                reactor_name=f"{user.name}#{user.discriminator}",
                message_content=message.content or "*No text content*",
                timestamp=datetime.now(timezone.utc),
                message_url=message.jump_url,
                channel_name=message.channel.name,
                guild_name=message.guild.name
            )
            
            # Send to log channel
            await self._send_to_log_channel(incident_data, message, user)
            
            logger.info(f"✅ Incident logged: {user.name} → {message.author.name}")
            
        except Exception as e:
            logger.error(f"Error handling incident: {e}")
    
    async def _send_to_log_channel(self, incident_data: IncidentData, message, reactor):
        """Send log message and AI improvement only to the original message's channel."""
        try:
            embed = discord.Embed(
                title="💩 Content Flagged",
                color=0xFF6B35,
                timestamp=incident_data.timestamp
            )
            embed.add_field(
                name="📝 Original Message",
                value=f"```{incident_data.message_content}```",
                inline=False
            )
            embed.add_field(
                name="👤 Author",
                value=f"{message.author.mention}\n`{incident_data.message_author_name}`",
                inline=True
            )
            embed.add_field(
                name="😡 Reactor",
                value=f"{reactor.mention}\n`{incident_data.reactor_name}`",
                inline=True
            )
            embed.add_field(
                name="📍 Location",
                value=f"#{incident_data.channel_name}\n[Jump to Message]({incident_data.message_url})",
                inline=True
            )
            embed.set_footer(text=f"ID: {incident_data.message_id}")

            try:
                await message.channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send flagged embed to origin channel: {e}")

            if self.text_improver and incident_data.message_content != "*No text content*":
                logger.debug("Requesting AI text improvement...")
                improved_text = await self.text_improver.improve_text(incident_data.message_content)
                if improved_text:
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
                    improvement_embed.set_footer(text="Powered by OpenRouter • Use as guidance only")
                    try:
                        await message.channel.send(embed=improvement_embed)
                    except Exception as e:
                        logger.error(f"Failed to send AI improvement embed to origin channel: {e}")
                    logger.debug("AI improvement sent successfully")
                else:
                    error_embed = discord.Embed(
                        title="🤖 AI Improvement",
                        description="❌ Could not generate improved text for this message.",
                        color=0xFF4444,
                        timestamp=datetime.now(timezone.utc)
                    )
                    try:
                        await message.channel.send(embed=error_embed)
                    except Exception as e:
                        logger.error(f"Failed to send AI error embed to origin channel: {e}")
        except discord.HTTPException as e:
            logger.error(f"Discord API error: {e}")
        except Exception as e:
            logger.error(f"Error sending log: {e}")

# Commands
class BotCommands(commands.Cog):
    """Bot command handlers."""
    
    def __init__(self, bot):
        self.bot = bot
    
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
            value=f"React with {self.bot.target_emoji} to any message to flag it for review.\n"
                  "The bot will log the incident and provide an AI-improved version.",
            inline=False
        )
        
        embed.add_field(
            name="🤖 AI Features",
            value="• Automatic text improvement suggestions\n"
                  "• Respectful language alternatives\n"
                  "• Constructive communication examples",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value=f"• Target Server: `{ctx.bot.target_guild_id or 'Not set'}`\n"
                  f"• AI Improvement: `{'Enabled' if ctx.bot.text_improver else 'Disabled'}`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='improve')
    async def improve_text(self, ctx, *, text: str):
        """Test AI text improvement."""
        if not self.bot.text_improver:
            await ctx.send("❌ AI text improvement is not available (no OpenRouter API key configured)")
            return
        
        if len(text) > 500:
            await ctx.send("❌ Text too long (max 500 characters)")
            return
        
        async with ctx.typing():
            improved = await self.bot.text_improver.improve_text(text)
        
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
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot status."""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        latency = round(self.bot.latency * 1000, 2)
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
            value="Enabled" if self.bot.text_improver else "Disabled",
            inline=True
        )
        
        await message.edit(content=None, embed=embed)

# Main execution
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
    
    # Create bot
    bot = ShitTrackerBot()
    
    # Add commands
    await bot.add_cog(BotCommands(bot))
    
    # Run bot
    try:
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
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)