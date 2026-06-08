import os
import discord
import pytz

from datetime import datetime
from discord.ext import tasks
from discord import app_commands
from dotenv import load_dotenv

from pintland_calendar import format_message

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Eastern Time zone
EASTERN = pytz.timezone("US/Eastern")


# -----------------------------
# Slash command
# -----------------------------
@tree.command(
    name="pintland-date",
    description="Show the current Pintland date"
)
async def pintland_date(interaction: discord.Interaction):
    await interaction.response.send_message(format_message())


# -----------------------------
# Scheduler (runs every minute, checks time)
# -----------------------------
@tasks.loop(seconds=60)
async def scheduler_loop():
    now = datetime.now(EASTERN)

    # Only trigger at 8:30 AM Eastern
    if now.hour == 8 and now.minute == 30:
        channel = client.get_channel(CHANNEL_ID)

        if channel:
            await channel.send(format_message())


# -----------------------------
# Startup
# -----------------------------
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    try:
        await tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Command sync error:", e)

    if not scheduler_loop.is_running():
        scheduler_loop.start()


client.run(TOKEN)