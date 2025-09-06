import os
import discord
from discord.ext import commands
import aiohttp
import json
from dotenv import load_dotenv
from collections import deque

load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# API configuration
API_URL = "https://ai.pentogang.com/api/chat/completions"
API_KEY = os.getenv('API_KEY', None)

# Message history
message_history = deque(maxlen=100)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="mentions"))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

last_processed_message = None

@bot.tree.command(name="clear_context", description="Clears the conversation context.")
async def clear_context(interaction: discord.Interaction):
    """Clears the conversation context."""
    message_history.clear()
    await interaction.response.send_message("Conversation context has been cleared.")

@bot.event
async def on_message(message):
    global last_processed_message
    
    if message.author == bot.user:
        return
    
    if message.id == last_processed_message:
        return
        
    if bot.user in message.mentions:
        last_processed_message = message.id
        
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()

        # Check if the message is a reply
        if message.reference and message.reference.message_id:
            try:
                # Fetch the replied-to message
                replied_to_message = await message.channel.fetch_message(message.reference.message_id)
                
                # Prepend the replied-to message's content to the current message
                content = f"Replying to '{replied_to_message.author.name}': '{replied_to_message.content}'\n\n{content}"
            except discord.NotFound:
                pass
        
        if not content:
            await message.reply("Whaaa?")
            return
            
        async with message.channel.typing():
            try:
                print(f"Processing message: {content}")
                
                # Add user message to history
                message_history.append({"role": "user", "name": message.author.name, "content": content})
                
                headers = {
                    'Content-Type': 'application/json',
                }
                
                if API_KEY:
                    headers['Authorization'] = f'Bearer {API_KEY}'
                
                # Construct messages payload from history
                messages_payload = list(message_history)
                
                payload = {
                    "model": "discord-bot:120b",
                    "messages": messages_payload,
                    "max_tokens": 500
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(API_URL, json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            reply = data['choices'][0]['message']['content']
                            
                            # Add bot reply to history
                            message_history.append({"role": "assistant", "name": bot.user.name, "content": reply})
                            
                            await message.reply(reply)
                        else:
                            error_text = await response.text()
                            await message.reply(f"Sorry, I encountered an error: {response.status} - {error_text}")
            except Exception as e:
                await message.reply(f"Sorry, I encountered an error: {str(e)}")
if __name__ == "__main__":
    # Run the bot with the token from environment variables
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))