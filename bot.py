from discord import app_commands
import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Load data from JSON file for a specific guild
def load_data(guild_id):

    file_path = f'user_name_changes_{guild_id}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

# Save data to JSON file for a specific guild
def save_data(guild_id, data):

    file_path = f'user_name_changes_{guild_id}.json'
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_guild_join(guild):
    user_name_changes = load_data(guild.id)
    for member in guild.members:
        # if str(member.id) not in user_name_changes:
        if member.nick != None:
            user_name_changes[str(member.id)] = [member.nick]
        else:
            user_name_changes[str(member.id)] = [member.display_name]
    save_data(guild.id, user_name_changes)


@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(e)


@bot.event
async def on_member_update(before, after):

    user_name_changes = load_data(after.guild.id)

    if after.nick == None:
        if str(before.id) not in user_name_changes:
                user_name_changes[str(before.id)] = [after.display_name] 
        if after.display_name not in user_name_changes[str(before.id)]:
            user_name_changes[str(before.id)].append(after.display_name)

    elif before.nick != after.nick:
        if str(before.id) not in user_name_changes:
                user_name_changes[str(before.id)] = [after.nick] 
        if after.nick not in user_name_changes[str(after.id)]:
            user_name_changes[str(before.id)].append(after.nick)

    
    save_data(after.guild.id, user_name_changes)

@bot.tree.command(
    name="names", 
    description="Get the list of name changes for a user"
)
async def name_changes(ctx, user: discord.User = None):

    if user is None:
        user = ctx.user

    user_name_changes = load_data(ctx.guild.id)
    if str(user.id) in user_name_changes:
        changes = user_name_changes[str(user.id)]
        if len(changes) - 1 <= 1:
            await ctx.response.send_message(f'{user.display_name} has not changed their username.')
        else:
            await ctx.response.send_message(f'{user.display_name} has changed their username {len(changes)} times:\n{", ".join(changes)}')
    else:
        await ctx.response.send_message(f'Something went wrong')
     

id = os.environ.get('/key')
bot.run(id)
