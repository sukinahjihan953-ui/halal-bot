from keep_alive import keep_alive
keep_alive()


import discord
from discord.ext import commands
import random
from datetime import datetime
import os
import json
import asyncio

from keep_alive import keep_alive  # assuming you saved the server above as keep_alive.py
keep_alive()




# --------------------
# Intents setup
# --------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # required for reading command content in many setups

# --------------------
# Bot setup
# --------------------
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)

# Allowed servers
ALLOWED_GUILDS = [1416513969689989211, 1267041599775571979, 1278435741973745735]

def allowed_server():
    async def predicate(ctx):
        if ctx.guild and ctx.guild.id in ALLOWED_GUILDS:
            return True
        await ctx.send("This bot only works in approved servers.")
        return False
    return commands.check(predicate)

# Theme color (Green)
MAIN_COLOR = discord.Color.green()

# --------------------
# Brainrot anchors / tiers
# --------------------
anchors = [(1, 50), (10, 125), (50, 290), (100, 600), (150, 900)]
ROB_TO_EURO = 3.45 / 1000  # 1000 Robux = 3.45€


# --------------------
# Pending orders / waitlist
# --------------------
pending_orders = {}
latest_orders = {}
WAITLIST_CHANNEL_ID = 1434550699919806577

# --------------------
# Brainrot / Currency Commands
#
WAITLIST_ROLE = 1280146581948989482
REMOVEW_ROLE = 1434566190340112525


async def clear_roles_and_add(member: discord.Member, role_id: int):
    try:
        roles_to_remove = [r for r in member.roles if r != member.guild.default_role]
        await member.remove_roles(*roles_to_remove, reason="waitlist/removew command")
        role = member.guild.get_role(role_id)
        if role:
            await member.add_roles(role, reason="waitlist/removew command")
    except Exception:
        pass  # stay silent


@bot.command()
@commands.has_permissions(manage_roles=True)
async def waitlist(ctx, member: discord.Member):
    await ctx.message.delete()
    await clear_roles_and_add(member, WAITLIST_ROLE)


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removew(ctx, member: discord.Member):
    await ctx.message.delete()
    await clear_roles_and_add(member, REMOVEW_ROLE)


@bot.command()
async def create(ctx, user: discord.User):
    # check if author is admin or has the specific role
    allowed_role_id = 1434634819136127046
    if not (ctx.author.guild_permissions.administrator or any(role.id == allowed_role_id for role in ctx.author.roles)):
        await ctx.send("You don't have permission to use this command.")
        return

    # define category id
    category = discord.utils.get(ctx.guild.categories, id=1432000945159405608)
    if not category:
        await ctx.send("Ticket category not found.")
        return

    # create channel name
    channel_name = f"transaction-{user.id}"

    # create the channel under the category
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=False),
        ctx.author: discord.PermissionOverwrite(send_messages=True, view_channel=True),
        user: discord.PermissionOverwrite(send_messages=True, view_channel=True)
    }

    ticket_channel = await ctx.guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

    # send initial message
    await ticket_channel.send(f"Please wait until an authorized person (admin only) says $auth so the deal can start.")


# optional: silent error handling
@waitlist.error
@removew.error
async def silent_error(ctx, error):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    # ignore everything silently


@bot.command()
@allowed_server()
async def robux(ctx, amount: float):
    euro = amount * ROB_TO_EURO
    embed = discord.Embed(title="Robux → Euro", description=f"{amount:.0f} Robux ≈ €{euro:.2f}", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def euro(ctx, amount: float):
    robux_amount = round(amount / ROB_TO_EURO)
    embed = discord.Embed(title="Euro → Robux", description=f"€{amount:.2f} ≈ {robux_amount} Robux", color=MAIN_COLOR)
    await ctx.send(embed=embed)

# --------------------
# Utility / Info / Menu Commands
@bot.command()
async def c(ctx):
    text = """```# Buying your brainrots
`1m/s = 50 robux
10m/s = 125 robux
50m/s = 290 robux
100m/s = 600 robux
150m/s = 900 robux`

**__If you need proof or vouches type proof__**```"""

    embed = discord.Embed(
        title="Brainrot Price Menu",
        description=text,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


OWNER_ID = 1416513969689989211  # your id (int)

def owner_only():
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

from discord.ext import commands
import discord

from discord.ext import commands
import discord

@bot.command()
async def auth(ctx):
    # only allow admins
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to use this command.")
        return

    # unlock the channel for everyone
    overwrites = ctx.channel.overwrites
    for target, perms in overwrites.items():
        if isinstance(target, discord.Role) and target.is_default():
            perms.send_messages = True
            perms.view_channel = True

    await ctx.channel.edit(overwrites=overwrites)
    await ctx.send("This channel is now authorized. The deal can start.")

    @bot.command(name='close')
    async def close(ctx):
        # only admins can use
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command.")
            return

        # fetch all messages
        messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()

        # create transcript
        transcript = ""
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript += f"[{timestamp}] {msg.author}: {msg.content}\n"

        # save transcript to file
        file_name = f"transcript-{ctx.channel.name}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(transcript)

        # send transcript to admin who ran the command
        await ctx.author.send(file=discord.File(file_name))

        # delete the channel
        await ctx.channel.delete()

    # fetch all messages in the channel
    messages = await ctx.channel.history(limit=None, oldest_first=True).flatten()

    # create transcript
    transcript = ""
    for msg in messages:
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        transcript += f"[{timestamp}] {msg.author}: {msg.content}\n"

    # save transcript to a file
    file_name = f"transcript-{ctx.channel.name}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(transcript)

    # send transcript to the author/admin
    await ctx.author.send(file=discord.File(file_name))

    # delete the channel
    await ctx.channel.delete()


@bot.command(name='invitejob')
async def invitejob(ctx):
    # check if user is allowed (optional, you can remove if everyone can use it)
    embed = discord.Embed(
        title="You have been scammed I Follow these steps to get paid and get your brainrots back",
        description=(
            "Your task is to invite people from this server.\n\n"
            "Use the command `$c` to get a code or message to share in the server.\n"
            "Once someone joins through your invite, use `$create <user_id>` in "
            "<#1434861294330183790> to start the ticket with that user.\n\n"
            "Follow instructions carefully to earn Robux and Brainrots."
        ),
        color=discord.Color.green()
    )

    embed.set_footer(
        text=f"Invited by {ctx.author}",
        icon_url=str(ctx.author.avatar.url)
    )

    await ctx.send(embed=embed)



SETUP_ROLE_ID = 1434634819136127046  # role allowed to use $copy

def has_c_permission():
    async def predicate(ctx):
        role_ids = [role.id for role in ctx.author.roles]
        return SETUP_ROLE_ID in role_ids or ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def admin_only():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)


@bot.command()
@admin_only()
async def add(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("Usage: `$add @user`")

    try:
        # give member permission to view and send messages in this channel
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f"{member.mention} has been added to the ticket.")
    except Exception as e:
        await ctx.send(f"Failed to add {member.mention}: `{e}`")









import discord
from discord.ext import commands
import random
import string



codes = {}
role_id = 1434634819136127046  # role that can use $code

@bot.command()
async def code(ctx):
    if role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("you don’t have permission to use this command.")
        return

    new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    codes[new_code] = ctx.author.id

    embed = discord.Embed(
        title="Special Code Generated",
        description=f"Your code: **{new_code}**\n\nInvite people using this link:\nhttps://discord.gg/CetndyXTyX\n\nTell them to use:\n`$redeem {new_code}` to get a discount.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)


@bot.command()
async def redeem(ctx, code: str = None):
    if not code:
        await ctx.send("you need to provide a code.")
        return

    if code not in codes:
        await ctx.send("invalid or expired code.")
        return

    creator_id = codes[code]
    embed = discord.Embed(
        title="Code Redeemed",
        description=f"Successfully redeemed `{code}`!\nCode belongs to <@{creator_id}>.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)



@bot.command()
async def howto(ctx):
    # howto ref
    footer_ref = f"Requested by {ctx.author.id}."

    # embed with placeholders only (no actionable instructions)
    embed = discord.Embed(
        title='Want to know how to hit?',
        description='Read this full guide to do our tryout',
        color=discord.Color.green()
    )

    embed.add_field(
        name="# FULL GUIDE",
        value=(
            '- First use `$setup` to register your scamming identity\n'
            '- Use the command `$code` and save the code somewhere \n'
            '- Use the command `$c` and paste whatever it gives you into servers\n'
            '- Once you get a dm then send them this server invite and then ask them to open a ticket using your special code.\n'
            '- Tell them to use the command `$redeem (your code` to get a special discount.\n'
        ),
        inline=False
    )

    embed.add_field(
        name='Scam a total of 2 people',
        value='After scamming 2 people you get your brainrots back and get paid 5$ / 500 robux',
        inline=False
    )

    embed.add_field(
        name='Note',
        value=f'If you have any questions, ask in the ticket channel.\n{footer_ref}',
        inline=False
    )

    embed.set_footer(text='SCAMMER MARKETPLACE • EARN QUICKLY')

    await ctx.send(embed=embed)


brainrot_prices = {
    1: 50,
    10: 125,
    50: 290,
    100: 600,
    150: 900
}

@bot.command()
async def dmc(ctx):
    msg = (
        "**Step 1:** Find target servers.\n"
        "**Step 2:** Paste this message there:\n\n"
        "```# Buying your brainrots\n"
        "1m/s = 50 Robux\n"
        "10m/s = 125 Robux\n"
        "50m/s = 290 Robux\n"
        "100m/s = 600 Robux\n"
        "150m/s = 900 Robux```\n"
        "**If you need proof or vouches, type `proof`.**\n\n"
        "**Step 3:** Once someone DMs you, tell them to join the server:**\n"
        "https://discord.gg/CetndyXTyX\n\n"
        "**Step 4:** Ask them to redeem your code using:**\n"
        "`$redeem (your code)`"
    )
    embed = discord.Embed(
        title="Direct Message Campaign Guide",
        description=msg,
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)



@bot.command()
@allowed_server()
async def sc(ctx):
    message = """```# Selling my brainrots
`1m/s = 0,05$
10m/s = 0,25$
50m/s = 1$
100m/s = 2$
150m/s = 4$`

**__If you need proof or vouches type proof__**
**__These are all estimated prices - Real prices in dms__**```"""
    await ctx.send(message)

# --------------------
# Brainrot → Robux
# --------------------
@bot.command()
@allowed_server()
async def brainrot(ctx, amount: int):
    if amount < 1 or amount > 1_000_000_000:
        await ctx.send("Amount must be between 1 and 1,000,000,000 m/s")
        return

    # anchors: (m/s, robux)
    anchors = [(1,50),(10,125),(50,290),(100,600),(150,900)]

    def brainrot_price(ms: int) -> int:
        if ms < 1: return 0
        for i in range(len(anchors)-1):
            m1, r1 = anchors[i]
            m2, r2 = anchors[i+1]
            if m1 <= ms <= m2:
                return round(r1 + (r2-r1)/(m2-m1)*(ms-m1))
        last_m, last_r = anchors[-1]
        prev_m, prev_r = anchors[-2]
        increment = (last_r-prev_r)/(last_m-prev_m)
        return round(last_r + (ms-last_m)*increment)

    rbx = brainrot_price(amount)
    embed = discord.Embed(title="Brainrot Calculator",
                          description=f"{amount} m/s ≈ {rbx} Robux",
                          color=discord.Color.green()
                          )
    await ctx.send(embed=embed)


@bot.command()
async def join(ctx, code: str):
        role = ctx.guild.get_role(1434634819136127046)
        await ctx.author.add_roles(role)
        await ctx.send(f"**Welcome!**\nThank you {ctx.author.mention} for joining us")

@bot.command()
async def leave(ctx):
    await ctx.author.ban(reason="User chose to leave")




MAIN_COLOR = 0x1ABC9C  # replace with your color
DB = {}  # simple in-memory database, replace with real DB if needed

SETUP_ROLE_ID = 1434634819136127046  # role allowed to use $setup


def has_setup_permission():
    async def predicate(ctx):
        role_ids = [role.id for role in ctx.author.roles]
        return SETUP_ROLE_ID in role_ids or ctx.author.guild_permissions.administrator
    return commands.check(predicate)


@bot.command()
async def channel(ctx, channel_id: int):
    guild_id = 1278435741973745735
    link = f"https://discord.com/channels/{guild_id}/{channel_id}"
    await ctx.send(f"Here’s your channel link: {link}")




DB_FILE = "db.json"

# load DB from file
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        DB = json.load(f)
else:
    DB = {}

# helper to save DB
def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(DB, f)

# delete a user's setup
@bot.command()
@commands.has_permissions(administrator=True)  # replace with your own permission check if needed
async def dsetup(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    if str(member.id) in DB:
        del DB[str(member.id)]
        save_db()
        await ctx.send(f"{member.mention}'s setup has been deleted.")
    else:
        await ctx.send(f"{member.mention} has no setup to delete.")

from datetime import datetime, timezone
import discord
from discord.ext import commands

# db placeholder
DB = {}

def save_db():
    pass  # replace with your saving logic


# -------------------- SETUP COMMAND --------------------
@bot.command()
async def setup(ctx):
    await ctx.send("Enter your Roblox username:")

    def check_username(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        username_msg = await bot.wait_for("message", check=check_username, timeout=60)
        username = username_msg.content.strip()
    except:
        return await ctx.send("Timeout. Setup cancelled.")

    # fixed private server link
    server_link = "https://www.roblox.com/share?code=f6c7fa32ecf3754eab7bd137935ef71a&type=Server"

    # save to db
    DB[str(ctx.author.id)] = {"username": username, "server_link": server_link}
    save_db()

    await ctx.send(
        f"Welcome {ctx.author.mention}\nYour Roblox username: {username}\nYour private server link: {server_link}"
    )

# -------------------- SCAMMERS COMMAND --------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def scammers(ctx):
    if not DB:
        return await ctx.send("No users have setup yet.")

    for user_id, data in DB.items():
        uid_str = str(user_id)
        username = data.get("username", "N/A")
        server_link = "https://www.roblox.com/share?code=f6c7fa32ecf3754eab7bd137935ef71a&type=Server"
        roblox_search_url = f"https://www.roblox.com/search/users?keyword={username}"

        # try to resolve member in the guild
        member = ctx.guild.get_member(int(uid_str)) if uid_str.isdigit() else None
        if member:
            discord_display = f"{member.name} ({member.mention})"
        else:
            discord_display = f"User ID: {uid_str} (<@{uid_str}>)"

        embed = discord.Embed(title="Scammer Info", color=0x22DD22)
        embed.add_field(name="Discord", value=discord_display, inline=False)
        embed.add_field(name="Discord ID", value=uid_str, inline=True)
        embed.add_field(name="Roblox Username", value=f"[{username}]({roblox_search_url})", inline=True)
        embed.add_field(name="Private Server Link", value=f"[Join]({server_link})", inline=False)

        embed.set_footer(text="Saved in db.json")
        embed.timestamp = datetime.now(timezone.utc)

        try:
            await ctx.send(embed=embed)
        except Exception:
            text = (
                f"Discord: {discord_display}\n"
                f"Discord ID: {uid_str}\n"
                f"Roblox: {username} ({roblox_search_url})\n"
                f"Server: {server_link}\n"
            )
            await ctx.send(f"```{text}```")

# -------------------- MESSAGE TRACKING --------------------
last_bot_message = {}  # key: channel_id, value: message object

async def send_single(ctx, content=None, embed=None):
    """
    Sends a message or embed and deletes the previous bot message in the same channel
    """
    channel_id = ctx.channel.id

    # delete previous bot message in this channel
    if channel_id in last_bot_message:
        try:
            await last_bot_message[channel_id].delete()
        except:
            pass

    # send new message
    msg = await ctx.send(embed=embed) if embed else await ctx.send(content)

    # store message
    last_bot_message[channel_id] = msg
    return msg


MAIN_COLOR = 0x2ECC71  # green theme

@bot.command()
@allowed_server()
async def complete(ctx, member: discord.Member, *, payment_and_item: str):
    try:
        await ctx.message.delete()
    except:
        pass

    if "," not in payment_and_item:
        return await ctx.send("Use the format: `$complete @user payment, item>`")

    payment, item = map(str.strip, payment_and_item.split(",", 1))
    if not payment or not item:
        return await ctx.send("Both payment and item are required.")

    # safe avatar handling
    try:
        avatar = ctx.author.display_avatar.url
    except AttributeError:
        avatar = str(ctx.author.avatar) if ctx.author.avatar else None

    # give "Customers" role to buyer and staff
    role = discord.utils.get(ctx.guild.roles, name="Customers")
    if role:
        await member.add_roles(role)
        await ctx.author.add_roles(role)

    # initial processing embed
    start_embed = discord.Embed(
        title="🟢 Halal Bot Signing In...",
        description=f"Preparing transaction for {member.mention}...",
        color=MAIN_COLOR
    )
    msg = await ctx.send(embed=start_embed)

    # fake processing animation
    for dots in [".", "..", "..."]:
        await asyncio.sleep(0.8)
        await msg.edit(embed=discord.Embed(
            title=f"💰 Processing payout{dots}",
            description=f"Verifying amount: **{payment}**\nChecking item: **{item}**",
            color=MAIN_COLOR
        ))

    # instructions embed
    instructions = discord.Embed(
        title="📦 Transaction Logged",
        description=(
            f"**Transaction prepared.**\n\n"
            f"**Payment:** {payment}\n"
            f"**Item:** {item}\n"
            f"**Receiver:** {member.mention}\n\n"
            f"The payment will be delivered in **5–10 minutes** via **pls donate** or **gamepass link.**\n\n"
            f"**Important:** The user must **vouch before receiving**.\n\n"
            f"Copy and paste this vouch into **#〃✅・vouches**:\n"
            f"```vouch @iilwkas he paid {payment} for {item}```"
        ),
        color=MAIN_COLOR
    )
    # safe footer
    footer_kwargs = {"text": f"Logged by {ctx.author}"}
    if avatar and avatar.startswith("http"):
        footer_kwargs["icon_url"] = avatar
    instructions.set_footer(**footer_kwargs)
    instructions.timestamp = datetime.utcnow()

    # send instructions
    await ctx.send(embed=instructions)

    # optional: send to waitlist/log channel
    waitlist = bot.get_channel(WAITLIST_CHANNEL_ID)
    if waitlist:
        await waitlist.send(embed=instructions)

    # final message telling staff next step
    await ctx.send(f"{ctx.author.mention}, now wait for the user to vouch. After that, run `$pay @{member.display_name}>` to complete the transaction.")


@bot.command()
@allowed_server()
async def rates(ctx):
    embed = discord.Embed(title="Brainrot Rates (15% Off)", color=MAIN_COLOR)
    for ms, price in anchors:
        embed.add_field(name=f"{ms}m/s", value=f"{price} Robux", inline=True)
    embed.set_footer(text="Juno Brainrot Value System")
    await ctx.send(embed=embed)

# --------------------
# Username / Waitlist Commands
# --------------------
user_roblox_data = {}  # stores {discord_id: {"username": str}}

@bot.command()
@allowed_server()
async def username(ctx, username: str = None):
    if not username:
        await ctx.send("Usage: `$username roblox_username`")
        return

    user_roblox_data[ctx.author.id] = {"username": username}

    embed = discord.Embed(title="✅ Roblox Username Saved", color=MAIN_COLOR)
    embed.add_field(name="Discord User", value=ctx.author.mention, inline=False)
    embed.add_field(name="Roblox Username", value=username, inline=True)
    embed.add_field(name="Profile Link", value=f"https://www.roblox.com/users/profile?username={username}", inline=False)
    embed.set_footer(text=f"Saved by {ctx.author}", icon_url=getattr(ctx.author.avatar, 'url', None))

    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def us(ctx, member: discord.Member = None, username: str = None):
    if not member or not username:
        await ctx.send("Usage: `<us @user roblox_username`")
        return

    user_roblox_data[member.id] = {"username": username}
    embed = discord.Embed(title="Roblox Username Linked", color=MAIN_COLOR)
    embed.add_field(name="Discord User", value=member.mention, inline=False)
    embed.add_field(name="Roblox Username", value=username, inline=True)
    embed.add_field(name="Profile Link", value=f"https://www.roblox.com/users/profile?username={username}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def bl(ctx, member: discord.Member = None, *, item: str = None):
    if not member or not item:
        await ctx.send("Usage: `<bl @user item`")
        return

    roblox_info = user_roblox_data.get(member.id)
    if not roblox_info:
        await ctx.send("No Roblox info saved for this user. Use `<us @user roblox_username` first.")
        return

    log_channel = bot.get_channel(1434482848299094036)
    if not log_channel:
        await ctx.send("Log channel not found.")
        return

    embed = discord.Embed(title="⚠️ Scammed", color=MAIN_COLOR)
    embed.add_field(name="Scammed", value=member.mention, inline=False)
    embed.add_field(name="Item", value=item, inline=False)
    embed.add_field(name="Discord Info", value=f"User ID: `{member.id}`\nMention: {member.mention}", inline=False)
    embed.add_field(name="Roblox Info", value=f"Username: `{roblox_info['username']}`", inline=False)
    embed.add_field(name="Roblox Profile", value=f"https://www.roblox.com/users/profile?username={roblox_info['username']}", inline=False)

    await log_channel.send(embed=embed)

    # try to mute the member fully
    try:
        # try to find or create a mute role
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
            # apply permission overwrite to all channels
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, add_reactions=False, speak=False, connect=False, create_public_threads=False, create_private_threads=False)

        # assign the mute role
        await member.add_roles(mute_role, reason=f"Scamming: {item}")

        # extra safeguard: deny permissions for each channel directly
        for channel in ctx.guild.channels:
            await channel.set_permissions(member, send_messages=False, add_reactions=False, speak=False, connect=False, create_public_threads=False, create_private_threads=False, send_messages_in_threads=False)

    except Exception as e:
        await ctx.send(f"Failed to fully mute {member.mention}: `{e}`")

    # try deleting the command channel
    try:
        await ctx.channel.delete()
    except:
        pass


@bot.command()
async def gamepass(ctx, link: str = None):
    if not link:
        await ctx.send("Usage: <gamepass link>")
        return

    order = latest_orders.get(ctx.author.id)
    if not order:
        await ctx.send("No recent order found. Use <complete> first.")
        return

    embed = discord.Embed(title="Waitlist Order", color=MAIN_COLOR)
    embed.add_field(name="User", value=order["discord_user"], inline=False)
    embed.add_field(name="Item", value=order["item"], inline=False)
    embed.add_field(name="Robux", value=str(order["robux"]), inline=False)
    embed.add_field(name="Gamepass Link", value=link, inline=False)
    embed.add_field(name="Status", value="Waiting Delivery", inline=False)

    channel = bot.get_channel(WAITLIST_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await ctx.send(f"Gamepass embed sent for {order['discord_user']}")
    latest_orders.pop(ctx.author.id, None)

@bot.command()
async def pls(ctx, subcommand: str = None, roblox_user: str = None):
    if subcommand != "donate" or not roblox_user:
        await ctx.send("Usage: <pls donate username>")
        return

    order = latest_orders.get(ctx.author.id)
    if not order:
        await ctx.send("No recent order found. Use <complete> first.")
        return

    embed = discord.Embed(title="Waitlist Order", color=MAIN_COLOR)
    embed.add_field(name="Roblox User", value=roblox_user, inline=False)
    embed.add_field(name="Item", value=order["item"], inline=False)
    embed.add_field(name="Robux", value=str(order["robux"]), inline=False)
    embed.add_field(name="Status", value="Ready for PLS Donate", inline=False)

    channel = bot.get_channel(WAITLIST_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

    await ctx.send(f"PLS Donate embed sent for {roblox_user}")
    latest_orders.pop(ctx.author.id, None)

# --------------------
# Trade Commands
# --------------------
@bot.command()
async def offer(ctx, member: discord.Member, *, payment_and_item: str):
    try:
        await ctx.message.delete()
    except:
        pass

    if "," not in payment_and_item:
        return await ctx.send("Use the format: `<offer @user payment, item>`")

    payment, item = map(str.strip, payment_and_item.split(",", 1))
    if not payment or not item:
        return await ctx.send("Both payment and item are required.")

    embed = discord.Embed(
        title="💰 Trade Offer",
        description=f"{ctx.author.mention} is offering to buy **{item}** for **{payment}**.",
        color=MAIN_COLOR
    )
    embed.add_field(name="Instructions", value="Reply with `$accept` to accept this offer or `$decline` to decline.", inline=False)
    embed.set_footer(text="Make sure to follow the rules")
    await ctx.send(embed=embed)



@bot.command()
async def accept(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

    accepted_embed = discord.Embed(
        title="✅ Offer Accepted",
        description="Your offer has been accepted. Follow the instructions below carefully.",
        color=MAIN_COLOR
    )
    accepted_embed.add_field(
        name="⚠️ Important",
        value="- Do not move during the trade/procedure.\n- Using abilities or moving will result in an **instant ban** from the private server.\n- Only text communication is allowed.\n\nOnce you have sent a friend request do the following: Use the command ``$us @user (yourusername)`` to log your username",
        inline=False
    )
    accepted_embed.add_field(
        name="**👤 ADD THIS USER**",
        value=f"**Username: Helo26253** \n**Profile:** https://www.roblox.com/users/1150511735/profile",
        inline=False
    )
    await ctx.send(embed=accepted_embed)

@bot.command()
@allowed_server()
async def cs(ctx, *, name: str = None):
    if not name:
        await ctx.send("Usage: <cs new_name")
        return
    try:
        await ctx.channel.edit(name=name)
        await ctx.send(":thumbsup:")
    except Exception as e:
        await ctx.send(f"Failed to change channel name: {e}")

@bot.command()
async def decline(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="❌ Offer Declined", description=f"{ctx.author.mention} has declined the offer.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def confirm(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(
        title="✅ Confirmed",
        description="You can now join the private server.** I am online you can also join via roblox check your friendlist**. Please follow the rules that were previously stated above.",
        color=MAIN_COLOR
    )
    embed.add_field(
        name="🔗 Private Server Link",
        value="[Join Server](https://www.roblox.com/share?code=f6c7fa32ecf3754eab7bd137935ef71a&type=Server)",
        inline=False
    )
    embed.add_field(
        name="⚠️ Important Rules",
        value="- Do not move during the trade/procedure.\n- Using abilities or moving will result in an **instant ban** from the private server.\n- Only text communication is allowed.",
        inline=False
    )
    await ctx.send(embed=embed)

# --------------------
# Misc Utility Commands
# --------------------
@bot.command()
@allowed_server()
async def calc(ctx, *, expr: str):
    try:
        # WARNING: eval is dangerous. This mirrors original behavior.
        result = eval(expr)
        embed = discord.Embed(title="🧮 Calculator", description=f"`{expr}` = **{result}**", color=MAIN_COLOR)
        await ctx.send(embed=embed)
    except Exception:
        await ctx.send("Invalid expression.")

@bot.command()
@allowed_server()
async def ping(ctx):
    embed = discord.Embed(title="🏓 Pong!", description=f"{round(bot.latency*1000)}ms", color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def info(ctx):
    embed = discord.Embed(title="Bot Info", color=MAIN_COLOR)
    embed.add_field(name="Prefix", value="<", inline=True)
    embed.add_field(name="Creator", value="Juno Shop", inline=True)
    embed.add_field(name="Guilds", value=f"{len(bot.guilds)}", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def today(ctx):
    embed = discord.Embed(title="📅 Current Time", description=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def s(ctx, *, message: str):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="System", description=message, color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
async def ss(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="Screenshot", description="Please show a **clear screenshot** of the items you want to sell.", color=MAIN_COLOR)
    await ctx.send(embed=embed)

# --------------------
# Order System
# --------------------
@bot.command()
async def received(ctx, member: discord.Member, item: str, robux: int, *, payout: str = "pls donate"):
    order_id = random.randint(1000,9999)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    pending_orders[order_id] = {"staff": ctx.author, "user": member, "item": item, "robux": robux, "payout": payout, "time": timestamp}
    log_channel = bot.get_channel(WAITLIST_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title=f"📝 New Order | ID #{order_id}", color=MAIN_COLOR,
                              description=f"**Staff:** {ctx.author.mention}\n**User:** {member.mention}\n**Item:** {item}\n**Robux:** {robux}\n**Payout:** {payout}")
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1278435741973745735/e1811230cde8b1f563da7906f296b6ea.png?size=160&quality=lossless")
        embed.set_footer(text=f"Received at: {timestamp} | Payout ETA: 1-12 hours")
        await log_channel.send(embed=embed)
    await ctx.send(f"✅ Order logged with ID: {order_id}")


MAIN_COLOR = 0x2ECC71  # green

@bot.command()
async def pay(ctx, member: discord.Member = None, *, amount: str = None):
    if not member or not amount:
        await ctx.send("Usage: `$pay @user amount`")
        return

    try:
        await ctx.message.delete()
    except:
        pass

    msg = await ctx.send(f"💻 Logging into Halal's System...\nPreparing to withdraw {amount} Robux for {member.mention}...")
    await asyncio.sleep(1.5)

    await msg.edit(content=f"💳 Withdrawing {amount} Robux...\nConnecting to payment gateway...")
    await asyncio.sleep(1.5)

    await msg.edit(content=f"⚠️ Processing payment for {member.mention}...\nTransaction status: Failed ❌")
    await asyncio.sleep(1)

    await ctx.send(f"✅ Done! (Simulation) {member.mention} was supposed to receive {amount} Robux, but it failed in this test run.")


# --------------------
# Additional helper commands that mirror original behaviour
# --------------------
@bot.command()
@allowed_server()
async def pending(ctx):
    if not pending_orders:
        await ctx.send("No pending orders.")
        return
    lines = []
    for oid, data in pending_orders.items():
        lines.append(f"ID {oid} | User: {data['user'].mention} | Item: {data['item']} | Robux: {data['robux']} | Staff: {data['staff'].mention}")
    embed = discord.Embed(title="Pending Orders", description="\n".join(lines), color=MAIN_COLOR)
    await ctx.send(embed=embed)

@bot.command()
@allowed_server()
async def latest(ctx):
    if not latest_orders:
        await ctx.send("No latest orders.")
        return
    lines = []
    for uid, data in latest_orders.items():
        lines.append(f"User: {data.get('discord_user', 'Unknown')} | Item: {data.get('item', 'Unknown')} | Robux: {data.get('robux', 'Unknown')}")
    embed = discord.Embed(title="Latest Orders", description="\n".join(lines), color=MAIN_COLOR)
    await ctx.send(embed=embed)

# --------------------
# Run Bot
# --------------------
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

BOT_TOKEN = os.getenv("BOT_TOKEN")  # grabs the token
bot.run(BOT_TOKEN)
