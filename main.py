import requests, random
import discord, os
from discord.utils import get
from discord.ext import commands
from discord import Member
from discord.ext.commands import has_permissions

ranks = {
    "Ascended": "ascended_uhc",
    "Divine": "divine_uhc",
    "Celestial": "celestial_uhc",
    "Godlike": "godlike_uhc",
    "Grandmaster": "grandmaster_uhc",
    "Legend": "legend_uhc",
    "Master": "master_uhc",
    "Diamond": "diamond_uhc",
    "Gold": "gold_uhc",
}

apikey = "<ANTISNIPER-API-KEY>"

def createEmbed(title, description, fields, color):
  embed=discord.Embed(title=title, description=description, color=color)
  embed.set_author(name="UHC Scrims Bot", url="https://github.com/CraftYun83/UHC-Scrims-Bot", icon_url="https://i.ibb.co/dW0DnF0/maxresdefault.jpg")
  embed.set_thumbnail(url="https://i.ibb.co/dW0DnF0/maxresdefault.jpg")
  embed.set_footer(text="https://uhcscrims.herokuapp.com/")
  for field in fields:
    embed.add_field(name=field[0], value=field[1], inline=True)
  return embed

def removeName(name):
    with open("userdata.txt", "r+") as file:
        content = file.read()
        for user in content.split("\n"):
            if len(user.split("||")) == 3:
                username = user.split("||")[1]
                if username == name:
                    content = content.replace(user+"\n", "")
        file.close()

    with open("userdata.txt", "w+") as file:
        file.write(content)
        file.close()

def getInfo(name):
    data = requests.get("https://api.slothpixel.me/api/players/"+name).json()
    try:
        return 0, [data["error"]]
    except KeyError:
        rank = "Unranked"
        packages = data["stats"]["Duels"]["general"]["packages"]
        for prop in ranks.keys():
            if ranks[prop] in packages:
                rank = prop
                break
        
        discord = data["links"]["DISCORD"]
        if discord == None:
            return 0, ["DISCORD_NOT_LINKED"]
        else:
            return 1, [rank, discord]

bot = commands.Bot(command_prefix="!", description="UHC Scrims Bot")

@bot.event
async def on_ready():
    print("The UHC Scrims Bot is now up and running!")

@bot.command(name="verify")
async def verify(ctx, arg1):
  print("detected")
  users = []
  with open("userdata.txt", "r") as file:
    content = file.read()
    print(content)
    content = content.split("\n")
    users = content
  tags = []
  for user in users:
    user = user.split("||")
    print(user)
    if len(user) == 3:
      tags.append(user[1])
  print(tags)
  if str(ctx.author) in tags:
    await ctx.send(embed=createEmbed("Error", "Sorry, you are already verified! Try unverifying using `!unverify` before running this command again!", [], color=0xFF0000))
  else:
    success, data = getInfo(str(arg1))
    if success == 0:
      await ctx.send(embed=createEmbed("Error", f"Sorry, {arg1}'s profile isn't linked to any Discord account!", [], color=0xFF0000))
    else:
      if str(data[1]).lower() == str(ctx.author).lower():
        division = data[0]
        role = get(ctx.guild.roles, name=division)
        await ctx.author.add_roles(role)
        with open("userdata.txt", "a") as file:
          file.write(str(arg1)+"||"+str(data[1])+"||"+str(data[0]))
          file.write("\n")
          file.close()
        await ctx.send(embed=createEmbed("Role Given", "Congratulations! You just verified your Minecraft account! You can unverify using `!unverify` and update your role using `!update`", [["Given Role: ", division], ["IGN: ", str(arg1)], ["Discord Tag: ", str(ctx.author)]], color=0x44ff00))
      else:
        await ctx.send(embed=createEmbed("Error", f"Sorry, {arg1}'s profile is linked to a different Discord account!", [], color=0xFF0000))

@verify.error
async def verify_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(embed=createEmbed("Invalid Syntax", "Correct Syntax: !verify <IGN>", [], color=0xFF0000))

@bot.command(name="update")
async def update(ctx):
  users = []
  with open("userdata.txt") as file:
    content = file.read()
    content = content.split("\n")
    for c in content:
      users.append(c.split("||"))

  for user in users:
    print(user)
    if len(user) == 3:
      if user[1].lower() == str(ctx.author).lower():
        role = get(ctx.guild.roles, name=user[2].replace("\n", ""))
        print(role)
        await ctx.author.remove_roles(role)
        success, data = getInfo(str(user[0]))
        print(success)
        print(data)
        if success == 1:
          role = get(ctx.guild.roles, name=data[0])
          print(data[0])
          print(role)
          await ctx.author.add_roles(role)
          await ctx.send(embed=createEmbed("Role Updated", "Succesfully updated your role!", [["Previous Role: ", user[2].replace("\n", "")], ["New Role: ", data[0]], ["IGN: ", str(user[0])]], color=role.color))
          return True
        else:
          print(data[0])
          await ctx.send(embed=createEmbed("Error", "Sorry, there was a problem trying to get your new statistics, please try again later.", [], color=0xFF0000))
  await ctx.send(embed=createEmbed("Error", "Sorry, you are not currently verified! Try verifying using `!verify <IGN>` before running this command again!", [], color=0xFF0000))

@bot.command(name="unverify")
async def unverify(ctx):
  users = []
  with open("userdata.txt") as file:
    content = file.read()
    content = content.split("\n")
    for c in content:
      users.append(c.split("||"))

  for user in users:
    print(user)
    if len(user) == 3:
      if user[1].lower() == str(ctx.author).lower():
        role = get(ctx.guild.roles, name=user[2].replace("\n", ""))
        await ctx.author.remove_roles(role)
        removeName(str(ctx.author))
        await ctx.send(embed=createEmbed("Unverified", "Succesfully unverified you!", [["Old Role: ", user[2].replace("\n", "")], ["IGN: ", user[0]], ["Discord Tag: ", str(user[1])]], color=0x44ff00))
        return True
  await ctx.send(embed=createEmbed("Error", "Sorry, you are not currently verified! Try verifying using `!verify <IGN>` before running this command again!", [], color=0xFF0000))

@bot.command(name="unverifyuser")
@has_permissions(manage_roles=True, ban_members=True)
async def unverifyuser(ctx, member: Member):
  users = []
  with open("userdata.txt") as file:
    content = file.read()
    content = content.split("\n")
    for c in content:
      users.append(c.split("||"))

  for user in users:
    if len(user) == 3:
      if user[1].lower() == str(member).lower():
        role = get(ctx.guild.roles, name=user[2].replace("\n", ""))
        await ctx.author.remove_roles(role)
        removeName(str(member))
        await ctx.send(embed=createEmbed("Unverified", f"Succesfully unverified {str(member)}!", [["Old Role: ", user[2].replace("\n", "")], ["IGN: ", user[0]], ["Discord Tag: ", str(user[1])]], color=0x44ff00))
        return True
  await ctx.send(embed=createEmbed("Error", "Sorry, this player is not currently verified! Try making the user verify using `!verify <IGN>` before running this command again!", [], color=0xFF0000))

@unverifyuser.error
async def unverifyuser_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(embed=createEmbed("Invalid Syntax", "Correct Syntax: !unverifyuser @<user>", [], color=0xFF0000))
  if isinstance(error, commands.MissingPermissions):
    await ctx.send(embed=createEmbed("Error", "You do not have permission to unverify other users!", [], color=0xFF0000))

def getRealName(nick):
    data = requests.get(f"https://api.antisniper.net/denick?key={apikey}&nick={nick}").json()
    if data["success"] == False:
        if data["cause"] == "Invalid API key":
            return 0, ["API-KEY-ERROR"]
        if data["cause"] == "Malformed nick":
            return 0, ["INVALID-NICK"]
        else:
            return 0, [data["cause"]]
    else:
        if "data" in list(data.keys()):
            if data["data"] == None:
                return 0, ["NOONE-NICKED"]
        if "player" in data.keys():
            if data["player"] != None:
                return 1, [data["player"]["ign"], data["player"]["uuid"]]

def getNick(name):
    data = requests.get(f"https://api.antisniper.net/findnick?key={apikey}&name={name}").json()
    if data["success"] == False:
        if data["cause"] == "Invalid API key":
            return 0, ["API-KEY-ERROR"]
        if data["cause"] == "Malformed name":
            return 0, ["INVALID-NAME"]
        else:
            return 0, [data["cause"]]
    else:
        if "data" in list(data.keys()):
            if data["data"] == None:
                return 0, ["NICK-NOT-FOUND"]
        if "player" in data.keys():
            if data["player"] != None:
                return 1, [data["player"]["nick"]]

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command(name="denick")
async def denick(ctx, arg1):
    nick = str(arg1)
    success, data = getRealName(nick)
    if success == 1:
        await ctx.send(embed=createEmbed("Name Grabbed!", f"Succesfully denicked {nick}!", [["Nick: ", nick], ["Actual IGN: ", data[0]], ["UUID: ", data[1]]], color=0x44ff00))
    else:
        if data[0] == "NOONE-NICKED" or "INVALID-NICK":
            await ctx.send(embed=createEmbed("Nick Not Found!", f"I couldn't find anyone nicked {nick}, sorry!", [], color=0xFF0000))
        else:
            print(data[0])

@denick.error
async def denick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=createEmbed("Invalid Syntax", "Correct Syntax: !denick <NICK>", [], color=0xFF0000))
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=createEmbed("Cooldown!", f"To stop rate limit, I capped this command at once every 5 seconds. You can try again in {error.retry_after:.2f}s.", [], color=0xFF0000))
    else:
        print(error)

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command(name="getnick")
async def getnick(ctx, arg1):
    name = str(arg1)
    success, data = getNick(name)
    if success == 1:
        await ctx.send(embed=createEmbed("Nick Grabbed!", f"Succesfully grabbed nick of {name}!", [["Nick: ", data[0]]], color=0x44ff00))
    else:
        if data[0] == "NICK-NOT-FOUND":
            await ctx.send(embed=createEmbed("Nick Not Found!", f"I couldn't find the nick of {name}, sorry!", [], color=0xFF0000))
        if data[0] == "INVALID-NAME":
            await ctx.send(embed=createEmbed("Nick Not Found!", f"I couldn't find the nick of {name} because they apparently don't exist, sorry!", [], color=0xFF0000))
        print(data[0])

@getnick.error
async def getnick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=createEmbed("Invalid Syntax", "Correct Syntax: !getnick <name>", [], color=0xFF0000))
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=createEmbed("Cooldown!", f"To stop rate limit, I capped this command at once every 5 seconds. You can try again in {error.retry_after:.2f}s.", [], color=0xFF0000))
    else:
        print(error)

bot.run("<DC-BOT-TOKEN>")
