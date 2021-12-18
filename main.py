from settings import *
import discord
import asyncio
import json
from scripts import *
from discord.ext import commands
from discord import File
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import requests
from easy_pil import Editor, Canvas, load_image_async, Font

intent = discord.Intents(messages=True, members=True, guilds=True)
client = discord.Client(intents=intent)


with open("ethaddresses.json", "r") as outfile:
    EthAddresses = json.load(outfile)

with open("invite_tracker.json", "r") as outfile:
    Invite_Tracker = json.load(outfile)

with open("activity_tracker.json", "r") as outfile:
    Activity_Tracker = json.load(outfile)

with open("commands.json", "r") as outfile:
    Commands = json.load(outfile)

RANK_ROLES = ["Guardsman", "Iron Priest", "Hearthguard Sgt",
              "Templar General", "Cardinals", "Arbitrator"]

WHITELIST_ROLES = ["The First Order", "Founding Marine", "Shroomz Marine", "Marine of Wars",
                   "House of Marines", "Event 2069 Survivor", "OG Expeditor", "Certified Marine Bro"]


WHITELIST_CAP = [1000]
WHITELIST_COUNT = [0]
for i in EthAddresses:
    WHITELIST_COUNT[0] += 1


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    await track_activities(Activity_Tracker)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):

        user_roles = message.author.roles
        splits = message.content.split(" ", 1)
        command = splits[0]

        # ****************************************************
        #      !enlist - Store Eth address of user           *
        # ****************************************************
        if command == ("!enlist"):
            if not is_correct_channel(Commands, command, message.channel.id):
                return
            enlist_command = message.content.split(" ", 1)
            if(len(enlist_command) == 1):
                embed = discord.Embed(
                    description="!enlist command Format: ***[!enlist]*** ***[0x00000000000]***", color=discord.Color.blue())
                await message.channel.send(embed=embed)
                return
            if(not is_whitelist_eligible(message, Activity_Tracker, Invite_Tracker)):
                if(not whitelist_roles(user_roles, WHITELIST_ROLES)):
                    embed = discord.Embed(title="Not eligible yet",
                                          description="You'll need the minimum requirements to qualify for whitelisting. Use ***!stats*** to find out the task(s) needed to be done.", color=discord.Color.blue())
                    await message.channel.send(embed=embed)
                    return
            if(message.author.name not in EthAddresses) and (int(WHITELIST_COUNT[0]) >= int(WHITELIST_CAP[0])):
                embed = discord.Embed(
                    description="Enlistment is full.", color=discord.Color.blue())
                await message.channel.send(embed=embed)
                return
            EthAddresses[message.author.name] = enlist_command[1]
            update_eth_address(EthAddresses)
            WHITELIST_COUNT[0] += 1
            embed = discord.Embed(
                description=f"{message.author.name} has been enlisted.", color=discord.Color.blue())
            await message.channel.send(embed=embed)
            return
        # ****************************************************
        #      !stats - Check user stats                     *
        # ****************************************************
        if command == ("!stats"):
            if not is_correct_channel(Commands, command, message.channel.id):
                return
            eligible = is_whitelist_eligible(
                message, Activity_Tracker, Invite_Tracker)
            await stats(message, eligible)
            return
        # ****************************************************
        #      !rank - returns the user's status card        *
        # ****************************************************
        if command == ("!rank"):
            if not is_correct_channel(Commands, command, message.channel.id):
                return
            await card(message)
            return
        # ****************************************************
        #      !set - set command channel.                   *
        # ****************************************************
        if command.startswith("!set"):
            t = command.split("!set", 1)
            cmd = "!" + t[1]
            if is_Admin(user_roles):
                if cmd not in Commands:
                    return
                Commands[cmd] = message.channel.id
                update_commands(Commands)
                await message.channel.send(
                    f"The {command} command has been set to this channel!"
                )
            return
        # ****************************************************
        #      !trackinvites - Adds a new keyword message.   *
        # ****************************************************
        if command == ("!trackinvites"):
            if is_Admin(user_roles):
                await track_invites(message.guild, message, Invite_Tracker)
                await message.channel.send("Invite Tracker Initiated.")
            return
        # ****************************************************
        #      !rbcommands - List recruitment bot commands.  *
        # ****************************************************
        if command == "!rbcommands":
            return_list = ""
            for i in Commands:
                return_list = return_list + i + "\n"
            await message.channel.send(return_list)
            return
        # ****************************************************
        #      !totalwhitelist -                             *
        # ****************************************************
        if command == "!totalwhitelist":
            if is_Admin(user_roles):

                if len(splits) == 1:
                    embed = discord.Embed(
                        description="!enlist command Format: ***[!totalwhilelist]*** ***[integer]***", color=discord.Color.blue())
                    await message.channel.send(embed=embed)
                    return
                else:
                    try:
                        wcmd = isinstance(int(splits[1]), int)
                    except:
                        embed = discord.Embed(
                            description="Please enter a valid integer", color=discord.Color.blue())
                        await message.channel.send(embed=embed)
                        return
                    WHITELIST_CAP[0] = int(splits[1])
                    embed = discord.Embed(
                        description=f"Whitelist limit changed to {WHITELIST_CAP[0]}", color=discord.Color.blue())
                    await message.channel.send(embed=embed)
                    return
        # ****************************************************
        #      !totalwhitelist -                             *
        # ****************************************************
        if command == "!getwhitelist":
            if is_Admin(user_roles):
                # try:
                eth_addresses = ""
                for key, value in EthAddresses.items():
                    eth_addresses = eth_addresses + f"{key},{value}\n"
                await message.channel.send(eth_addresses)
                return

    else:
        if check_channel(message.channel.name):
            if message.author.name not in Activity_Tracker:
                Activity_Tracker[message.author.name] = 100
            else:
                Activity_Tracker[message.author.name] = Activity_Tracker[message.author.name] + 1
                guild_roles = message.guild.roles
                if(Activity_Tracker[message.author.name] == 500):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[0])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[0]}")
                elif(Activity_Tracker[message.author.name] == 1000):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[1])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[1]}")
                elif(Activity_Tracker[message.author.name] == 1500):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[2])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[2]}")
                elif(Activity_Tracker[message.author.name] == 2000):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[3])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[3]}")
                elif(Activity_Tracker[message.author.name] == 2500):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[4])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[4]}")
                elif(Activity_Tracker[message.author.name] == 3000):
                    _rank_role = get_rank_role(guild_roles, RANK_ROLES[5])
                    await message.author.add_roles(_rank_role)
                    await message.channel.send(f"{message.author.name} has been promoted to {RANK_ROLES[5]}")


async def track_invites(guild, message, INVITE_TRACKER):
    while True:
        invite_list = await guild.invites()
        for i in invite_list:  # Looping through list of invites
            if i.inviter.name not in Invite_Tracker:  # Add user if not exists
                Invite_Tracker[i.inviter.name] = {i.url: {"count": i.uses}}
            # Add url if not exist
            elif i.url not in Invite_Tracker[i.inviter.name]:
                Invite_Tracker[i.inviter.name][i.url] = {"count": i.uses}
            else:  # At this point, Invite_Tracker has the inviter and that invite url, so we assume it also has count.
                # Update uses
                Invite_Tracker[i.inviter.name][i.url]["count"] = i.uses
        update_invite_tracker(Invite_Tracker)
        # Get founding marine role
        for i in guild.roles:
            if i.name == "Founding Marine":
                _role = i

        for k, v in INVITE_TRACKER.items():
            sum = invite_sum(INVITE_TRACKER[k])
            if sum >= 10:
                for member in guild.members:
                    if member.name == k:
                        _member = member
                # get member
                # check if member has role
                        if _role not in _member.roles:
                            await member.add_roles(_role)
                            await message.channel.send(f"{member.name} is now a {_role.name}")
                # if not give role
        await asyncio.sleep(360)  # Change to sleep for 12-24 hours


async def track_activities(activity):
    while True:
        update_activity_tracker(Activity_Tracker)
        await asyncio.sleep(360)  # Change to sleep for 12-24 hours


async def card(message):
    if message.author.name not in Activity_Tracker:
        Activity_Tracker[message.author.name] = 100
        update_activity_tracker(Activity_Tracker)
    role = ""
    if(Activity_Tracker[message.author.name] >= 500):
        role = RANK_ROLES[0]
    if(Activity_Tracker[message.author.name] >= 1000):
        role = RANK_ROLES[1]
    if(Activity_Tracker[message.author.name] >= 1500):
        role = RANK_ROLES[2]
    if(Activity_Tracker[message.author.name] >= 2000):
        role = RANK_ROLES[3]
    if(Activity_Tracker[message.author.name] >= 2500):
        role = RANK_ROLES[4]
    if(Activity_Tracker[message.author.name] >= 3000):
        role = RANK_ROLES[5]
    xp_need = 100
    xp_have = Activity_Tracker[message.author.name]
    rank = get_rank(Activity_Tracker, message)
    if xp_need > xp_have:
        level = 1
    else:
        level = int(xp_have / xp_need)
        if level > 30:
            level = 30
    remaining_xp = xp_have % xp_need
    if level == 30:
        remaining_xp = 100
    percentage = remaining_xp / xp_need * 100
    background = Editor("./BG1.png")
    user_avatar_url = str(message.author.avatar_url_as(format="png"))
    profile = await load_image_async(
        user_avatar_url)
    profile = Editor(profile).resize((150, 150)).circle_image()

    square = Canvas((500, 500), "#06FFBF")
    square = Editor(square)
    square.rotate(30, expand=True)

    background.paste(square.image, (600, -250))
    background.paste(profile.image, (30, 45))
    poppins = Font.poppins(size=40)
    poppins_small = Font.poppins(size=30)
    background.rectangle((30, 220), width=650,
                         height=40, fill="white", radius=20)

    background.text((200, 55), f"{role} {message.author.name}",
                    color="white", font=poppins)

    background.rectangle((200, 100), width=350, height=2, fill="#17F3F6")
    background.text(
        (200, 130),
        f"Level : {level}",
        color="white",
        font=poppins
    )

    background.text(
        (450, 130),
        f"Rank: #{rank}",
        color="white",
        font=poppins
    )

    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill="#FF56B2",
        radius=20,
    )
    if level < 30:
        background.text(
            (690, 220),
            f"- {remaining_xp}/100xp",
            color="white",
            font=poppins
        )

    file = File(fp=background.image_bytes, filename="card.png")

    await message.channel.send(file=file)


async def stats(message, isQualified):

    if isQualified:
        desc = f"```ini\n[{message.author.name} is qualified for whitelisting]\n```"
    else:
        desc = f"```css\n[{message.author.name} is not qualified for whitelisting]\n```"
    if(whitelist_roles(message.author.roles, WHITELIST_ROLES)):
        desc = f"```ini\n[{message.author.name} is qualified for whitelisting]\n```"
    activity_bar = ""
    invite_bar = ""
    activity_count = 0
    invite_count = 0

    if message.author.name not in Activity_Tracker:
        Activity_Tracker[message.author.name] = 100
        update_activity_tracker(Activity_Tracker)
    else:
        activity_count = Activity_Tracker[message.author.name] % 100
    activity_level = int(Activity_Tracker[message.author.name]/100)
    if activity_level > 30:
        activity_level = 30
    if message.author.name in Invite_Tracker:
        invite_count = invite_sum(Invite_Tracker[message.author.name])

    # Activity Bar
    a_percentage = activity_level / 10
    if activity_level > 10:
        a_percentage = 1
    a_green_blocks = int(a_percentage * 20)
    a_black_blocks = int(20 - a_green_blocks)
    for i in range(a_green_blocks):
        activity_bar = activity_bar + ":green_square:"
    for i in range(a_black_blocks):
        activity_bar = activity_bar + ":black_large_square:"
    # Invite Bar
    i_percentage = invite_count / 10
    if invite_count > 10:
        i_percentage = 1
    i_green_blocks = int(i_percentage * 20)
    i_black_blocks = int(20 - i_green_blocks)
    for i in range(i_green_blocks):
        invite_bar = invite_bar + ":green_square:"
    for i in range(i_black_blocks):
        invite_bar = invite_bar + ":black_large_square:"

    embed = discord.Embed(title=f"Stats for: {message.author.name}",
                          description=desc, color=discord.Color.blue())
    embed.add_field(name="Chat Activity",
                    value=f"{activity_bar}" + f" - {activity_level}/10\n{activity_count}/100", inline=False)
    embed.add_field(name="Invite Amount",
                    value=f"{invite_bar}" + f" - {invite_count}/10", inline=False)

    await message.channel.send(embed=embed)


client.run(os.getenv("MARINEBOT"))
