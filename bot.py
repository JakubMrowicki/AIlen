import os
import discord
from discord.ext import commands
import aiohttp
from dotenv import load_dotenv
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()

# Bot setup
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', None)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# API configuration
API_URL = os.getenv('API_URL', None)  # base URL
API_KEY = os.getenv('API_KEY', None)
MODEL = os.getenv('MODEL', None)
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 500))
MAX_HISTORY_LENGTH = int(os.getenv('MAX_HISTORY_LENGTH', 100))

# Message history
message_history = deque(maxlen=MAX_HISTORY_LENGTH)

# Global variable to store fetched tools
available_tools = []

async def fetch_model_tools():
    """
    Fetches the model info, checks for tools, and if present, fetches the tools dynamically without hardcoding IDs.
    """
    global available_tools
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        if API_KEY:
            headers['Authorization'] = f'Bearer {API_KEY}'
        
        # Fetch model info to get toolIds
        async with aiohttp.ClientSession() as session:
            model_url = f"{API_URL}/api/v1/models/model?id={MODEL}"
            async with session.get(model_url, headers=headers) as response:
                if response.status == 200:
                    model_data = await response.json()
                    tool_ids = model_data.get('meta', {}).get('toolIds', [])
                    if not tool_ids:
                        logging.info("No tools associated with this model.")
                        available_tools = []
                        return
                    available_tools = [tool for tool in tool_ids]
                    logging.info(f"Total tools fetched: {len(available_tools)}")
                else:
                    logging.error(f"Failed to fetch model info: {response.status} - {await response.text()}")
                    available_tools = []
    except Exception as e:
        logging.error(f"Error fetching model or tools: {str(e)}")
        available_tools = []

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="mentions"))
    
    # Fetch tools dynamically at startup
    await fetch_model_tools()
    logging.info(f"Available tools: {available_tools}")
    
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

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
                logging.info(f"Processing message: {content}")
                
                # Add user message to history
                message_history.append({"role": "user", "name": message.author.name, "content": content})
                
                headers = {
                    'Content-Type': 'application/json',
                }
                
                if API_KEY:
                    headers['Authorization'] = f'Bearer {API_KEY}'
                
                # Construct messages payload from history
                messages_payload = list(message_history)
                
                # Prepare the payload with tools if available
                payload = {
                    "model": MODEL,
                    "messages": messages_payload,
                    "max_tokens": MAX_TOKENS
                }
                
                if available_tools:
                    payload["tool_ids"] = available_tools
                    payload["tool_choice"] = "auto"  # Let the model decide when to use tools
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{API_URL}/api/chat/completions", json=payload, headers=headers) as response:
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
    bot.run(DISCORD_BOT_TOKEN)
