
# Discord Shit Tracker Bot — Usage Guide

This bot monitors Discord messages for 💩 reactions and provides AI-powered text improvement suggestions using OpenRouter.

## Usage

### Running the Bot

```bash
python run.py
```

### Commands

- `!st help` — Show help information and bot configuration
- `!st ping` — Check bot status, latency, and AI availability
- `!st improve <text>` — Test AI text improvement on any text

### How It Works

1. React to any message with 💩 to flag it for review.
2. The bot logs the original message to your configured log channel.
3. The bot uses OpenRouter AI to suggest a more respectful, constructive version of the flagged message.
4. Moderators see both the original and improved text for reference.

### Example

**Original flagged message:**
> "This is stupid and you're an idiot"

**AI-improved version:**
> "I disagree with this approach and would like to discuss alternative solutions."

### Example Log Output

```
💩 Content Flagged
📝 Original Message: "This sucks and you're dumb"
👤 Author: @username
😡 Reactor: @moderator
📍 Location: #general
```

```
🤖 AI-Improved Version
✨ Suggested Improvement: "I'm not satisfied with this and would like to discuss concerns."
💡 How to use:
• Copy the improved text above
• Share with the user as a suggestion
• Use as a reference for moderation
```

## Troubleshooting

- **Bot Not Responding:**
  - Check if your bot token is correct
  - Verify bot permissions
  - Check if TARGET_GUILD_ID is correct
- **AI Not Working:**
  - Verify OPENROUTER_API_KEY is set correctly
  - Check your OpenRouter API credits
- **Rate Limiting:**
  - Bot limits users to 5 reactions per minute
  - OpenRouter has its own rate limits (see their docs)

## Support

If you encounter issues:
2. Verify all configuration values
3. Ensure the bot has proper Discord permissions
4. Test your OpenRouter API key with `!st improve test message`
5. Check OpenRouter API status and credits