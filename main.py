import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CLICK_TO_VERIFY_ID = int(os.getenv("CLICK_TO_VERIFY_ID"))
VERIFICATION_CATEGORY_ID = int(os.getenv("VERIFICATION_CATEGORY_ID"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))
UNVERIFIED_ROLE_ID = int(os.getenv("UNVERIFIED_ROLE_ID"))

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

temp_channels = {}

@bot.event
async def on_ready():
    print(f"{bot.user} is connected.")

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    staff_role = guild.get_role(STAFF_ROLE_ID)

    # User joins "Click to Verify"
    if after.channel and after.channel.id == CLICK_TO_VERIFY_ID:
        if UNVERIFIED_ROLE_ID in [role.id for role in member.roles]:
            # Delete old temp channel if exists
            if member.id in temp_channels:
                old_channel = guild.get_channel(temp_channels[member.id])
                if old_channel:
                    await old_channel.delete()

            # Create new private voice channel
            category = guild.get_channel(VERIFICATION_CATEGORY_ID)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
                staff_role: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
            }

            channel = await guild.create_voice_channel(
                name="🔎・Verification :",
                category=category,
                overwrites=overwrites
            )

            await member.move_to(channel)
            temp_channels[member.id] = channel.id

    # User leaves any voice channel
    if before.channel and member.id in temp_channels:
        temp_channel = guild.get_channel(temp_channels[member.id])
        if temp_channel:
            # Check if there's any unverified user left
            still_unverified = any(
                UNVERIFIED_ROLE_ID in [role.id for role in m.roles]
                for m in temp_channel.members
            )
            if not still_unverified:
                await temp_channel.delete()
                del temp_channels[member.id]

bot.run(TOKEN)