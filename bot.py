import discord
from discord.ext import commands
from transformers import pipeline
import os

# Set up the bot with appropriate intents
intents = discord.Intents.default()
intents.message_content = True  # Ensure this intent is enabled
bot = commands.Bot(command_prefix='', intents=intents)

# Memory dictionary to hold conversation history for each user
memory = {}

# Load GPT-J model using Hugging Face's transformers library
generator = pipeline('text-generation', model='EleutherAI/gpt-j-6B')

@bot.event
async def on_ready():
    # Log basic bot information
    print(f'Logged in as: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('Bot is online and ready!')

    # Optional: Log the guilds (servers) the bot is connected to
    guilds = [guild.name for guild in bot.guilds]
    print(f'Connected to guilds: {", ".join(guilds)}')

@bot.event
async def on_message(message):
    # Log received message
    print(f"Received message from {message.author}: {message.content}")

    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the message mentions the bot
    if bot.user.mentioned_in(message):
        print(f"Bot mentioned in message: {message.content}")

        user_id = message.author.id

        # Initialize memory for the user if not already present
        if user_id not in memory:
            memory[user_id] = []

        # Add the new message to the user's memory
        memory[user_id].append(message.content)

        # Limit memory to the last 10 messages
        if len(memory[user_id]) > 10:
            memory[user_id] = memory[user_id][-10:]

        # Generate a response considering the conversation history
        conversation = " ".join(memory[user_id])
        response = generator(conversation, max_length=50, num_return_sequences=1, truncation=True)[0]['generated_text']

        # Clean up response to remove unwanted artifacts
        response = response.strip()
        response = response[len(conversation):]

        # Log the response before sending
        print(f"Sending response: {response}")

        # Send the response
        await message.channel.send(response)

    # Process commands if present
    await bot.process_commands(message)

# Run the bot with your token from environment variables
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
