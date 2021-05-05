import json
import os
import discord
import aiohttp
import asyncio
import keep_alive
import datetime
from discord import Guild, TextChannel
from discord.ext import commands
from datetime import datetime
from colorama import Fore

ownercolor = 0xff0000
usercolor = 0x03989b
announcecolor = 0xe1ff00
commandcolor = 0x08c42e
botinvite = f"https://discord.com/oauth2/authorize?client_id=839093901713080320&scope=bot&permissions=-1"
bot = commands.Bot(command_prefix="?", intents=discord.Intents.all(), case_insensitive=True, help_command=None)

@bot.event
async def on_command_error(message, error):
    embed = discord.Embed(
        title=f"Globalbot Errormessage: \n",
        description=f"{error}\n"
                    f"\n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})", color=commandcolor)

    embed.set_author(name=f"{message.author.name}", icon_url=f"{emojiurl}")
    embed.set_thumbnail(url=f"{message.author.avatar_url}")
    embed.set_footer(text=f"User ID: {message.author.id} | Sent from: {message.guild.name}", icon_url=f"{message.author.avatar_url}")
    embed.timestamp = datetime.utcnow()
    await message.send(embed=embed)
    await message.message.delete()


@bot.event
async def on_ready():
    print(f"{Fore.GREEN}Globalbot is ready for use!")
    await bot.change_presence(activity=discord.Streaming(name=f" {prefix}help",url=twitchurl))
    print("Something went wrong")

with open('config.json') as f:
    config = json.load(f)
prefix = config.get("Prefix")
clientid = config.get("ClientID")
githuburl = config.get("Githuburl")
ranks = config.get("OwnerID")
supportinvite = config.get("Supportserver")
emojiurl = config.get("Emojiurl")
twitchurl = config.get("Twitchurl")


if os.path.isfile("servers.json"):
    with open("servers.json", encoding="utf-8") as file:
        servers = json.load(file)

else:
    servers = {"servers": []}
    with open("servers.json", "w") as file:
        json.dump(servers, file, indent=4)

# ----------------------------------------------------------------- #

def guild_exists(guildid):
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guildid):
            return True
    return False


def get_globalchat(guildid, channelid):
    globalchat = None
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guildid):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    globalchat = server

            else:
                globalchat = server
    return globalchat


def get_globalchat_id(guildid):
    globalchat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guildid):
            globalchat = i
        i += 1
    return globalchat

# ----------------------------------------------------------------- #

@bot.command()
async def announce(ctx, *, text):
    if str(ctx.author.id) not in ranks:
        embed = discord.Embed(
            title=f"Globalbot Errormessage: \n",
            description="You are missing Botowner permission(s) to run this command.\n"
                        f"\n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})",
            color=commandcolor)

        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{emojiurl}")
        embed.set_thumbnail(url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=f"User ID: {ctx.author.id} | Sent from: {ctx.guild.name}",
                         icon_url=f"{ctx.author.avatar_url}")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
        await ctx.message.delete()
        pass
    else:
        embed = discord.Embed(
            title="➜ Important Announcement!",
            description=f"{text} \n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})",
            color=announcecolor
        )
        embed.set_thumbnail(url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=f"User ID: {ctx.author.id} | Sent from: {ctx.guild.name}", icon_url=f"{ctx.author.avatar_url}")
        embed.timestamp = datetime.utcnow()


        for server in servers["servers"]:
            guild: Guild = bot.get_guild(int(server["guildid"]))
            if guild:
                channel: TextChannel = guild.get_channel(int(server["channelid"]))
                if channel:
                    await channel.send(embed=embed)
        await ctx.message.delete()


@bot.command()
@commands.has_permissions(administrator=True)
async def addglobal(ctx):
    if not guild_exists(ctx.guild.id):
        server = {
            "guildid": ctx.guild.id,
            "channelid": ctx.channel.id,
            "invite": f'{(await ctx.channel.create_invite()).url}'
        }
        servers["servers"].append(server)
        with open('servers.json', 'w') as f:
            json.dump(servers, f, indent=4)

        embed = discord.Embed(
            description=f"Sucesfully added Globalchat in Channel {ctx.channel.mention}.",
            color=0x1abc9c
        )

        await ctx.send(embed=embed)
        await ctx.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def removeglobal(ctx):
    if guild_exists(ctx.guild.id):
        globalid = get_globalchat_id(ctx.guild.id)
        if globalid != -1:
            servers["servers"].pop(globalid)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)

        embed = discord.Embed(
            description=f"Sucessfully removed Globalchat from Channel: {ctx.channel.mention}.",
            color=0xc0392b
        )

        await ctx.send(embed=embed)
        await ctx.message.delete()

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title=f"Command List: \n",
        description=f"{prefix}help => Shows this Message\n"
                    f"{prefix}announce => Sending a Announcement though all Servers (Botowner only)\n"
                    f"{prefix}addglobal => Setup Globalchat in a Channel\n"
                    f"{prefix}removeglobal => Removes GlobalChat from a channel\n"
                    f"{prefix}serverlist => Shows Servernames where im in\n"
                    f"{prefix}joke => Generating a random joke using a API\n"
                  
                    f"\n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})", color=commandcolor)

    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{emojiurl}")
    embed.set_thumbnail(url=f"{ctx.author.avatar_url}")
    embed.set_footer(text=f"User ID: {ctx.author.id} | Sent from: {ctx.guild.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
async def serverlist(ctx):
    serverlist = [server.name for server in bot.guilds]

    embed = discord.Embed(
        title=f"All Servers im curretly in: ({len(serverlist)})",
        description=f" \n".join(serverlist),
        color=commandcolor
    )
    embed.set_thumbnail(url=f"{ctx.guild.icon_url}")
    embed.set_footer(text=f"Requested by: {ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)
    await ctx.message.delete()


@bot.command()
async def joke(ctx):
    await ctx.message.delete()
    headers = {
        "Accept": "application/json"
    }
    async with aiohttp.ClientSession()as session:
        async with session.get("https://icanhazdadjoke.com", headers=headers) as req:
            r = await req.json()
    embed = discord.Embed(title="Random Generated Dadjoke: ", description=r["joke"], color=commandcolor)
    embed.set_thumbnail(url="https://media.tenor.com/images/99338a98580194539b4ecbcbc1ade726/tenor.gif")
    embed.set_footer(text=f"User ID: {ctx.author.id} | Sent from: {ctx.guild.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

# ----------------------------------------------------------------- #

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.content.startswith("?"):
        if get_globalchat(message.guild.id, message.channel.id):
            await sendAll(message, message.author)
    await bot.process_commands(message)


async def sendAll(message, member):
    global word
    bad_words = ["Hurensohn", "ficke", "Ficker", "Wichser", "bitch",".gg",".ly",".de",".com","kek","Kek","KEk","KEK","KeK","kekw","KEkw","KEKw","KEKW","KeKw","kEkW"," https://discord.gg/","https://discordapp.com"]
    bad_word_detection = []

    for word in message.content.split():
        if word not in bad_words:
            bad_word_detection.append(False)
        else:
            bad_word_detection.append(True)

    if True in bad_word_detection:
        embed = discord.Embed(
            title=f"Blacklisted Word Detected! \n",
            description=f"I have detected that you used **{word}** what is blacklisted. Please stop doing that!\n"
                        f"\n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})",
            color=commandcolor)

        embed.set_author(name=f"{message.author.name}", icon_url=f"{emojiurl}")
        embed.set_thumbnail(url=f"{message.author.avatar_url}")
        embed.set_footer(text=f"User ID: {message.author.id} | Sent from: {message.guild.name}",
                         icon_url=f"{message.author.avatar_url}")
        embed.timestamp = datetime.utcnow()
        await message.channel.send(embed=embed)
        await message.delete()

    else:
        # Wenn UserID  nicht in ranks variable: #
        if not str(message.author.id) in ranks:
            embed = discord.Embed(
                title="",
                description=f"{message.content} \n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})",
                color=usercolor
            )

            embed.set_author(name=f"GlobalChat: {member.name}",
                             icon_url=f"{emojiurl}")
            embed.set_thumbnail(url=f"{message.author.avatar_url}")
            embed.set_footer(text=f"User ID: {message.author.id} | Sent from: {message.guild.name}", icon_url=f"{message.author.avatar_url}")
            embed.timestamp = datetime.utcnow()

            for server in servers["servers"]:
                guild: Guild = bot.get_guild(int(server["guildid"]))
                if guild:
                    channel: TextChannel = guild.get_channel(int(server["channelid"]))
                    if channel:
                        await channel.send(embed=embed)
            await message.delete()

        # Wenn UserID in ranks variable: #
        if str(message.author.id) in ranks:
            embed = discord.Embed(
                title="",
                description=f"{message.content} \n\n[Support-Server]({supportinvite}) | [Bot-Invite]({botinvite}) | [GitHub]({githuburl})",
                color=ownercolor
            )

            embed.set_author(name=f"Bot Developer: {member.name}",
                        icon_url=f"https://emoji.gg/assets/emoji/1180-staff.gif")
            embed.set_thumbnail(url=f"{message.author.avatar_url}")
            embed.set_footer(text=f"User ID: {message.author.id} | Sent from: {message.guild.name}", icon_url=f"{message.author.avatar_url}")
            embed.timestamp = datetime.utcnow()

            for server in servers["servers"]:
                guild: Guild = bot.get_guild(int(server["guildid"]))
                if guild:
                    channel: TextChannel = guild.get_channel(int(server["channelid"]))
                    if channel:
                        await channel.send(embed=embed)
            await message.delete()

# ----------------------------------------------------------------- #

# ----------------------------------------------------------------- #
keep_alive.keep_alive()
bot.run("ODM5MDkzOTAxNzEzMDgwMzIw.YJEpFw.Bw9CJp1-j1IoFcXht3ajM4e7rQI")
