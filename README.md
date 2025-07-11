# Discord Shit Tracker Bot — Universal Multi-Server Bot

This bot monitors Discord messages for 💩 reactions and provides AI-powered text improvement suggestions using OpenRouter. **The bot works in ANY Discord server where it's added** - no configuration required!

## ✅ Features

- **Universal Multi-Server Support** - Works in all servers where the bot is added
- **AI-Powered Text Improvement** - Uses OpenRouter to suggest better alternatives
- **Rate Limiting** - Prevents spam (5 reactions per minute per user)
- **Real-time Logging** - Shows which server each reaction comes from
- **Simple Setup** - Just add bot token and run!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key_here  # Optional
```

### 3. Run the Bot
```bash
python run.py
```
or
```bash
python bot.py
```

### 4. Test the Bot
```bash
python test_bot.py
```

## 📋 Commands

- `!st help` — Show help information and bot status
- `!st ping` — Check bot latency and server count
- `!st improve <text>` — Test AI text improvement on any text

## 🎯 How It Works

1. **Add the bot to any Discord server**
2. **React with 💩 to any message** to flag it for review
3. **The bot logs the incident** in the same channel where the reaction occurred
4. **AI suggests an improved version** of the flagged message (if OpenRouter API key is provided)
5. **Works across all servers** where the bot is present

## 📊 Example Output

When someone reacts with 💩 to a message:

```
💩 Content Flagged
📝 Original Message: "This is stupid and you're an idiot"
👤 Author: @username
😡 Flagged by: @moderator
📍 Server: My Discord Server
🔗 Jump to Message: [Click here](link)
```

```
🤖 AI-Improved Version
Here's how this message could be improved:
✨ Suggested Improvement: "I disagree with this approach and would like to discuss alternative solutions."
```

## ⚙️ Configuration

### Required
- `DISCORD_BOT_TOKEN` - Your Discord bot token

### Optional
- `OPENROUTER_API_KEY` - For AI text improvement features
- `LOG_LEVEL` - Logging level (default: INFO)
- `COMMAND_PREFIX` - Bot command prefix (default: !st)

## 🔧 Bot Permissions Required

When adding the bot to a server, ensure it has these permissions:
- Read Messages
- Send Messages
- Add Reactions
- Read Message History
- Embed Links

## 🌐 Multi-Server Operation

The bot automatically works in **ALL servers** where it's added:
- ✅ No server-specific configuration needed
- ✅ Monitors all servers simultaneously
- ✅ Logs show which server each reaction comes from
- ✅ Rate limiting works across all servers
- ✅ Commands work in all servers

## 🛠️ Troubleshooting

### Bot Not Responding
1. Check if `DISCORD_BOT_TOKEN` is correct in `.env`
2. Verify bot has proper permissions in the Discord server
3. Ensure bot is online (check Discord developer portal)
4. Run `python test_bot.py` to test connection

### AI Not Working
1. Verify `OPENROUTER_API_KEY` is set correctly
2. Check your OpenRouter API credits
3. Test with `!st improve test message`

### Rate Limiting
- Users are limited to 5 💩 reactions per minute
- This prevents spam and abuse
- Rate limits apply across all servers

## 📝 Logs

The bot provides detailed logging:
```
🤖 Bot connected as YourBot#1234
📊 Monitoring 3 guilds:
   - Server One (ID: 123456789)
   - Server Two (ID: 987654321)
   - Server Three (ID: 555666777)
🚀 Bot ready and monitoring ALL servers!

💩 Reaction by username in guild: Server One (ID: 123456789)
✅ Flagged content logged in Server One
✅ AI improvement sent
```

## 🔒 Privacy & Security

- Bot only responds to 💩 reactions
- No message content is stored permanently
- AI processing is done via OpenRouter API
- Rate limiting prevents abuse
- All operations are logged for transparency

## 📞 Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all environment variables are set correctly
3. Ensure the bot has proper Discord permissions
4. Test your OpenRouter API key with `!st improve test message`
5. Run `python test_bot.py` to verify bot connectivity

---

**Ready to deploy!** The bot will work immediately in any Discord server where you add it. No additional configuration required!