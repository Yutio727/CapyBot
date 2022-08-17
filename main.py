from typing_extensions import Required
import discord
import discord.utils    
from discord import Member, option, OptionChoice, User
from discord.ext import commands
import os
import random
import os.path
from decouple import config
import googletrans
import asyncpg
import asyncio
import mysql.connector
from humanfriendly import parse_timespan
from datetime import timedelta

#getting variables
CAPY_IMAGES = config("CAPY_IMAGES") 
TOKEN = config("TOKEN")
HOST = config("HOST")
USER = config("USER")
PASSWORD = config("PASSWORD")
DATABASE = config("DATABASE")

translator = googletrans.Translator() #googletrans lib

intents = discord.Intents.default() #discord intents
intents.members = True #doesn't work without it
intents.message_content = True #doesn't work without it

capydb = mysql.connector.connect( #database connection
  host = HOST,
  user = USER,
  password = PASSWORD,
  database = DATABASE
)



capybara_words = [
    "Capybara", "Capybaras", "Copybara", "Capypic", "Capypics" "Coconut doggo",
    "Capibara", "Capybro", "Capybr", "Капибара", 
    "Cpbr", "Кокосовая Свинка", "Водосвинка",
    "Кокосовая собачка",  "Водяная Собачка", "Капибары",
    "Капибару", "Капибарой", "Капибаре", "Водная свинка",
    "Водяная свинка", "Капибар", 'ካፕባራ', 'كابيبا',
    'Капібара', 'ক্যাপিবারা','Campybara','Kapibara',
    'Kapybara', 'კაპიბარა','Καπετάρι','ક capપીબરા',
    'Cayrona', 'קפיברה', 'קפיברה', 'कैपीबारा',
    'Calapóir','カピバラ', 'CapiSbara', 'ಬಿಲ್ಲೆ', 'Капибас',
    '카피 바라','Капыбара','കാപ്പിബറ', 'Kopa', 'कॅपीबारा',
    'Капбайбара', 'क्याप्बेरा', 'କ୍ୟାପିବାଡା |', 'کیپیرارا',
    'کپیوبارا','ਕੈਪੀਬੋਰਰਾ','Цапибара', 'Campiybara', 'Capbara',
    'ڪيپيبرا','Casybati','Капайарара', 'கேபிபரா', 'కాపిబారా',
    'Капібара', 'کیپیبرا', 'Kapabaa', 'Nghapybara', 'קאַפּייבאַראַ',
    'Fapu', 'Ikhonsaba', "水豚", "Capy"
] #almost all languages & some forms of rus and eng from googletrans

capycolor = discord.Color.from_rgb(219, 188, 129) #unique color for embeds 


message_on_cooldown = [] #used in on_message
lang_list = [] #used in {prefix}help languages_list

DEFAULT_PREFIX = "!"
DEFAULT_TOGGLE = "1"


async def get_prefix(bot, message): #getting prefix from database
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot,message)

    cursor = capydb.cursor() #openning the cursor to do something with db

    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {message.guild.id}") #executing sql request
    data = cursor.fetchone() #fetching that request

    if data == None:
        
        cursor.execute("INSERT INTO guilds(guild_id, prefix) VALUES (%s, %s)", [message.guild.id, DEFAULT_PREFIX]) #cexecuting sql request
        prefix = DEFAULT_PREFIX
        capydb.commit() #commiting the change to db
    else:
        prefix = data[1]
        capydb.commit() #commiting the change to db


    toggle = cursor.execute("SELECT * FROM capypics WHERE guild_id = (%s)", [message.guild.id])
    data1 = cursor.fetchone()

    if data1 == None:

        cursor.execute("INSERT INTO capypics(guild_id, toggle) VALUES (%s, %s)", [message.guild.id, DEFAULT_TOGGLE])
        toggle = DEFAULT_TOGGLE
        capydb.commit()
    else:
        toggle = data1[1]
        capydb.commit()

    cursor.close() #closing the cursor (important)
    return commands.when_mentioned_or(prefix)(bot, message)


# async def create_db_pool(): #connecting to database
#     print("Connected to database.".format(bot))


#bot command
bot = commands.Bot(command_prefix = get_prefix, intents=intents, help_command = None, activity = discord.Activity(type=discord.ActivityType.playing, name="!help"),\
    status=discord.Status.idle, debug_guilds=[815928209786011678,990336510895222795,1002519224046075904])


@bot.event
async def on_ready(): #when bot is ready
    if (capydb.is_connected()):
        print("Connected to a database.")
    else:
        print("Connection to database is not established.")

    print("{0.user} is fully operational.".format(bot)) #when the bot is loaded
    print("Please wait atleast 1 minute before using slash commands if test_guilds are not set in debug_guilds.")
    # for guild in bot.guilds:
    #     print(guild.id)



@bot.event
async def on_command_error(ctx, error): #handling errors
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Command is on a cooldown.",description=f"Try again in {error.retry_after:.2f}s.", color=capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.MissingPermissions):
        em = discord.Embed(title=f"You're missing some permissions.", color=capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.CommandInvokeError):
        em = discord.Embed(title=f"Something went wrong.", color=capycolor)
        await ctx.send(embed = em, delete_after = 15)
        raise error

    elif isinstance(error, commands.MissingRequiredArgument):
        em = discord.Embed(title=f"You haven't entered all required arguments.", color=capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"This command doesn't exist.", color=capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.NoPrivateMessage):
        em = discord.Embed(title = "This command cannot be used in private messages.")
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.UserNotFound):
        em = discord.Embed(title = "Couldn't find this user.", color = capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.BadArgument):
        em = discord.Embed(title = "You entered the wrong argument.", color = capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.BotMissingPermissions):
        em = discord.Embed(title = f"Bot is missing needed permissions: {error}.")
        await ctx.send(embed = em, delete_after = 15)
    else:
       raise error #raises the error if it's not already listed in isinstanse


@bot.event
async def on_application_command_error(ctx, error): #slash commands handler
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Command is on a cooldown.",description=f"Try again in {error.retry_after:.2f}s.", color=capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.MissingPermissions):
        em = discord.Embed(title=f"You're missing some permissions.", color=capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.CommandInvokeError):
        em = discord.Embed(title=f"Something went wrong.", color=capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.MissingRequiredArgument):
        em = discord.Embed(title=f"You haven't entered all required arguments.", color=capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"This command doesn't exist.", color=capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.NoPrivateMessage):
        em = discord.Embed(title = "This command cannot be used in private messages.")
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.UserNotFound):
        em = discord.Embed(title = "Couldn't find this user.", color = capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.BadArgument):
        em = discord.Embed(title = "You entered the wrong argument.", color = capycolor)
        await ctx.respond(embed = em, delete_after = 15)

    elif isinstance(error, commands.BotMissingPermissions):
        em = discord.Embed(title = f"Bot is missing needed permissions: {error}.")
        await ctx.respond(embed = em, delete_after = 15)

    else:
       raise error #raises the error if it's not already listed in isinstanse


# @bot.slash_command(name = "pingy", description="Sends the bot's latency.") # this decorator makes a slash command
# @commands.has_permissions(administrator = True)
# @commands.bot_has_permissions(change_nickname = True, send_messages = True, read_messages = True)
# @commands.cooldown(1, 5, type=commands.BucketType.user)
# async def pingy(ctx): # a slash command will be created with the name "ping"
#     await ctx.respond(f"Pong! Latency is {bot.latency}")


@bot.command(aliases=["setpre"])
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(change_nickname = True, send_messages = True, read_messages = True)
@commands.cooldown(1, 5, type=commands.BucketType.guild)
async def prefix(ctx, new_prefix = ""):#changes the prefix
    cursor = capydb.cursor()
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        cursor.execute(f"UPDATE guilds SET prefix = '{new_prefix}' WHERE guild_id = {ctx.guild.id}")

        await ctx.send(embed = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor))
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]") #changes nickname with current guild prefix
        capydb.commit()

    elif len(new_prefix) == 0:
        await ctx.send(embed = discord.Embed(title = "You didn't enter the prefix", color = capycolor))

    else:
        await ctx.send(embed = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor))
    cursor.close()



@bot.command()
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def capybara(ctx):
    cursor = capydb.cursor()
    toggle = cursor.execute("SELECT * FROM capypics WHERE guild_id = (%s)", [ctx.guild.id])
    data = cursor.fetchone()
    toggle = str(data[1])

    if  toggle == "1":
        cursor.execute(f"UPDATE capypics SET toggle = '0' WHERE guild_id = {ctx.guild.id}")
        await ctx.channel.send(embed = discord.Embed(title = "Capybara pics are off.", color = capycolor))
        capydb.commit()

    if toggle == "0":
        cursor.execute(f"UPDATE capypics SET toggle = '1' WHERE guild_id = {ctx.guild.id}")
        await ctx.channel.send(embed = discord.Embed(title = "Capybara pics are on.", color = capycolor))
        capydb.commit()
    cursor.close()

@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def translate(ctx, sentence, destination = "", source = ""): #this thing translates text to whatever you want (google translate) by any args
    if len(str(sentence)) > 0:
        if len(destination) == 2:
            if len(source) == 2:
                translation = translator.translate(sentence, destination, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, from **{source}** to **{destination}**.", color = capycolor)
                await ctx.channel.send(embed = em)

            if len(source) == 0:
                translation = translator.translate(sentence, destination)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, to **{destination}**.", color = capycolor)
                await ctx.channel.send(embed = em)

        if len(destination) == 0 and len(source) == 0:
            translation = translator.translate(sentence)
            em = discord.Embed(title = f"{translation.text}", description = f" Translated **{sentence}**.", color = capycolor)
            await ctx.channel.send(embed = em)
    else: 
        await ctx.channel.send(embed = discord.Embed(title = "You didn't enter any text to translate.", color = capycolor))


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def treply(ctx, destination = "", source = ""):
    if ctx.message.reference and (msg := ctx.message.reference.resolved) and isinstance(msg, discord.Message): #checks if you had replyed and used the command
        if len(destination) == 2:
            if len(source) == 2:
                translation = translator.translate(msg.content, destination, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{msg.content}**, from **{source}** to **{destination}**.", color = capycolor)
                await ctx.channel.send(embed = em)

            if len(source) == 0:
                translation = translator.translate(msg.content, destination)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{msg.content}**, to **{destination}**.", color = capycolor)
                await ctx.channel.send(embed = em)

        if len(destination) == 0 and len(source) == 0:
            translation = translator.translate(msg.content)
            em = discord.Embed(title = f"{translation.text}", description = f" Translated **{msg.content}**.", color = capycolor)
            await ctx.channel.send(embed = em)
    else: 
        await ctx.channel.send(embed = discord.Embed(title = "You need to reply to an existing message.", color = capycolor))


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def language(ctx, language = ""): #you enter the language or the language code - it gives you the language code or language
    if len(language) == 2:
        lang_code = googletrans.LANGUAGES[str(language)]
        await ctx.channel.send(embed = discord.Embed(title = f"**{lang_code}** is  **{language}**", color = capycolor))

    elif len(language) > 2:
        lang_code = googletrans.LANGCODES[str(language)]
        await ctx.channel.send(embed = discord.Embed(title = f"**{language}** is  **{lang_code}**", color = capycolor))

    else:
        await ctx.channel.send(embed = discord.Embed(title = "Your language isn't on the list.", color = capycolor))

    
@bot.command()
@commands.cooldown(1, 30, type=commands.BucketType.user)
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_messages = True)
async def clear(ctx, amount=10): #deletes messages
    if amount <= 50:
        await ctx.channel.purge(limit=amount)
        await ctx.send(embed = discord.Embed(title = f"{amount} messages are deleted.", color = capycolor), delete_after = 5)

    else:
        await ctx.channel.send(embed = discord.Embed(title = "Clear limit is 50.", color = capycolor), delete_after = 5)


@bot.command(description = "Ghost ping a user.")
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ping(ctx, user:discord.User = None): #pings the user and immediately deletes the message
    if user is not None:
        await ctx.respond(f'{user.mention}', delete_after=0)
        await ctx.message.delete()
    else:
        await ctx.respond(embed = discord.Embed(title = "You didn't enter the nickname.", color = capycolor))


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(ban_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
async def ban(ctx,  member:discord.Member = None, reason: str = "one good reason"):
    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor))
        return

    if member == ctx.message.author:
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban yourself.", color = capycolor))
        return

    if member == bot.user:  
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban this bot using this bots command, lol.", color = capycolor))
        return

    await ctx.guild.ban(member, reason = reason)

    em_m = discord.Embed(title = f"You have been banned from {ctx.guild.name}.", color = capycolor)
    em_m.add_field(name = "Reason", value = f"**{reason}**")
    await member.send(embed = em_m)

    em = discord.Embed(title = f"{member} is terminated.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await ctx.channel.send(embed = em)


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(ban_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
async def unban(ctx, member = None):
    if member != None:
        member_name, member_discriminator = member.split("#")
        async for ban_entry in ctx.guild.bans(limit = 150):
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(embed = discord.Embed(title = f"Unbanned {member}", color = capycolor))
                return

            else:
                await ctx.send(embed = discord.Embed(title = f"{member} isn't banned.", color = capycolor))
                return

    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user.", color = capycolor))
        return 


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
async def mute(ctx, member: discord.Member = None, time = None, reason = "one good reason"):
    perms = discord.Permissions(speak = False, send_messages = False, read_message_history = False, read_messages = False)
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")
    
    if not muted_role:
        muted_role = await ctx.guild.create_role(name = "Muted")
    
    await muted_role.edit(permissions = perms)

    if member is None:
        await ctx.send(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))
        
    elif  member is not None:
        await member.add_roles(muted_role, reason = reason)
        if time is not None:
            time_u = parse_timespan(time)

            em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")
            em_m.add_field(name = "Time", value = f"{time}")

            await member.send(embed = em_m)

            em = discord.Embed(title = f"Muted {member}.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            em.add_field(name = "Time", value = f"{time}")

            await ctx.send(embed = em)

            await asyncio.sleep(time_u)
            await member.remove_roles(muted_role)

        elif time is None:
            em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")

            await member.send(embed = em_m)

            em = discord.Embed(title = f"Muted {member}.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            await ctx.send(embed = em)

    elif muted_role in member.roles:
        await ctx.send(embed = discord.Embed(title = f"{member} is already muted.", color = capycolor))



@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
async def unmute(ctx, member: discord.Member = None):
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")

    if member is not None:
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(embed = discord.Embed(title = f"{member} is unmuted.", color = capycolor))

        elif muted_role not in member.roles:
            await ctx.send(embed = discord.Embed(title = f"{member} is not muted.", color = capycolor))

    elif member is None:
        await ctx.send(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author

        em = discord.Embed(color = capycolor)
        em.set_image(url = member.avatar.url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.channel.send(embed = em)

    elif member is not None:
        em = discord.Embed(color = capycolor)
        em.set_image(url=member.avatar.url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.channel.send(embed = em)


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(moderate_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_permissions = True)
async def timeout(ctx, user: discord.Member = None, time = None, reason = "one good reason"):
    if user is not None:
        if time is not None:
            time_u = parse_timespan(time)

            await user.timeout(until = discord.utils.utcnow() + timedelta(seconds = time_u), reason = reason)

            em_m = discord.Embed(title = f"You've been timed out on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")
            em_m.add_field(name = "Time", value = f"{time}")

            await user.send(em_m)

            em = discord.Embed(title = f"{user} is timed out.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            em.add_field(name = "Time", value = f"{time}")

            await ctx.send(embed = em)

        if time is None:
            await ctx.send(embed = discord.Embed(title = "You need to enter time as argument.", color = capycolor))

    if user is None:
        await ctx.send(embed = discord.Embed(title = "You need to enter the username as argument.", color = capycolor))


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(kick_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, kick_members = True)
async def kick(ctx,  member:discord.Member = None, *, reason: str = "one good reason"):
    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor))
        return

    if member == ctx.message.author:
        await ctx.channel.send(embed = discord.Embed(title = "You can't kick yourself.", color = capycolor))
        return

    if member == bot.user:  
        await ctx.channel.send(embed = discord.Embed(title = "You can't kick this bot using this bots command, lol.", color = capycolor))
        return

    await ctx.guild.kick(member)

    em_m = discord.Embed(title = f"You have been kicked from {ctx.guild.name}.", color = capycolor)
    em_m.add_field(name = "Reason", value = f"**{reason}**")
    await member.send(embed = em_m)

    em = discord.Embed(title = f"{member} is kicked.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await ctx.channel.send(embed = em)


#help command for prefix use
@bot.group(invoke_without_command = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def help(ctx): # new help command
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "Help", description = f"Use **{prefix}help <command>** to get more information on a command.", color = capycolor)

    em.add_field(name = "Translation", value = "**translate, treply, language, languages_list**")
    em.add_field(name = "Capybara and tools", value = "**capybara, avatar**")
    em.add_field(name = "Bot commands", value = "**prefix, clear, ping, ban, unban, mute, unmute**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def translate(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}translate <'sentence'> [s='(sourse language)'] [d='(destination language)']**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def language(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}languages <('english' for code) or] ('en' for language)>**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list**.")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def languages_list(ctx):
    for l in googletrans.LANGUAGES.values():
        lang_list.append(l)
    em = discord.Embed(title = "languages_list", description = "\n".join(lang_list), color = capycolor)

    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def treply(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}treply [d='(destination language)'] [s='(sourse language)']**")
    em.add_field(name = "Default languages", value = "The defaults are:\n • Auto source language \n • English as a destination language")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def capybara(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "capybara", description = "Toogles On and Off on your capybara pics dispenser.", color = capycolor)

    em.add_field(name = "Syntax", value = f"{prefix}capybara")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def prefix(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "prefix", description = "Changes your server prefix.", color = capycolor)

    em.add_field(name = "Syntax" , value = f"**{prefix}prefix '<new_prefix>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def clear(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ping(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ping '<user (without #(discriminator))>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ban(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ban '<user (can be without #(discriminator))>' '<reason>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def unban(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unban '<user (with #(discriminator))>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def mute(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "mute", description = "Mutes a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}mute '[user]' '[time]' '<reason>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def unmute(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "unmute", description = "Unmutes a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unmute '[user]'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def avatar(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "avatar", description = "Gets avatar from user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}avatar '<user>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def timeout(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    em = discord.Embed(title = "avatar", description = "Gets avatar from user.", color = capycolor)
    em.add_field(name = "Syntax", value = f"**{prefix}timeout '[user]' '[time]' '<reason>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def kick(ctx):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()
    em = discord.Embed(title = "kick", description = "Kicks the user from the server.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}kick '[user]'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)



#slash commands
@bot.slash_command(name = "prefix", description="Changes the prefix on your server.")
@option(
    "prefix", 
    description = "Changes the prefix on your server.",
    required = True,
    default = '',
    input_type = str,
)
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_guild_permissions(change_nickname = True, send_messages = True, read_messages = True)
async def prefix(ctx, new_prefix:str = ""):#changes the prefix
    cursor = capydb.cursor()
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        cursor.execute(f"UPDATE guilds SET prefix = '{new_prefix}' WHERE guild_id = {ctx.guild.id}")

        await ctx.respond(embed = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor))
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]") #changes nickname with current guild prefix
        capydb.commit()

    elif len(new_prefix) == 0 or new_prefix is None:
        await ctx.respond(embed = discord.Embed(title = "You didn't enter the prefix", color = capycolor), delete_after = 5)

    else:
        await ctx.respond(embed = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor), delete_after = 5)
    cursor.close()



@bot.slash_command(name = "capybara", description="Toogles the capybara pics sending.")
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_guild_permissions(send_messages = True, read_messages = True)
async def capybara(ctx):
    cursor = capydb.cursor()
    toggle = cursor.execute("SELECT * FROM capypics WHERE guild_id = (%s)", [ctx.guild.id])
    data = cursor.fetchone()
    toggle = str(data[1])

    if  toggle == "1":
        cursor.execute(f"UPDATE capypics SET toggle = '0' WHERE guild_id = {ctx.guild.id}")
        await ctx.respond(embed = discord.Embed(title = "Capybara pics are off.", color = capycolor))
        capydb.commit()

    if toggle == "0":
        cursor.execute(f"UPDATE capypics SET toggle = '1' WHERE guild_id = {ctx.guild.id}")
        await ctx.respond(embed = discord.Embed(title = "Capybara pics are on.", color = capycolor))
        capydb.commit()
    cursor.close()

@bot.slash_command(name = "translate", description="Translates a word or a sentence.")
@option(
    "sentence", 
    description = "Your sentence.",
    required = True,
    default = None,
    input_type = str,
)
@option(
    "source",
    description = "The language you want to translate from.",
    required = False,
    default = None,
    input_type = str,
)
@option(
    "destination",
    description = "The language you want to translate to.",
    required = False,
    default = None,
    input_type = str,
)
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.bot_has_guild_permissions(send_messages = True, read_messages = True)
async def translate(ctx, sentence:str = None, source:str = None, destination:str = None): #this thing translates text to whatever you want (google translate) by any args
    if sentence is not None: #when sentence is existing
            if destination is not None and source is not None: #if first argument is destination language
                translation = translator.translate(sentence, destination, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, from **{source}** to **{destination}**.", color = capycolor)
                await ctx.respond(embed = em)

            elif source is not None and destination is None:
                translation = translator.translate(sentence, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, from **{source}**.", color = capycolor)
                await ctx.respond(embed = em)

            elif destination is not None and source is None:
                translation = translator.translate(sentence, destination)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}** to **{destination}**.", color = capycolor)
                await ctx.respond(embed = em)

            elif destination is None and source is None:
                translation = translator.translate(sentence)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**.", color = capycolor)
                await ctx.respond(embed = em)
    elif sentence is None:
        await ctx.respond(embed = discord.Embed(title = "You didn't enter any text to translate.", color = capycolor), delete_after = 5)   


@bot.slash_command(name = "language", description = "Gives you language code or a full language name of the language code.")
@option(
    "language",
    description = "Language you want to see.",
    required = False,
    default = None,
    input_type = str,
)
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.bot_has_guild_permissions(send_messages = True, read_messages = True)
async def language(ctx, language:str = None):
    if language is not None:
        if len(str(language)) == 2:
            lang_code = googletrans.LANGUAGES[str(language)]
            await ctx.respond(embed = discord.Embed(title = f"{lang_code} is  **{language}**", color = capycolor))  

        elif len(str(language)) > 2:
            lang_code = googletrans.LANGCODES[str(language)]
            await ctx.respond(embed = discord.Embed(title = f"{language} is  **{lang_code}**", color = capycolor))  

    elif language is None:
        await ctx.respond(embed = discord.Embed(title = "You need to enter the language.", color = capycolor), delete_after = 5)

    else:
        await ctx.respond(embed = discord.Embed(title = "Your language isn't on the list.", color = capycolor), delete_after = 5)

@bot.slash_command(name = "ping", description = "Pings a user and deletes a message.")
@option(
    "user",
    description = "User your want to ping.",
    required = True,
    default = None,
    input_type = User,
)
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_guild_permissions(send_messages = True, read_messages = True)
async def ping(ctx, user:discord.User = None): #pings the user and immediately deletes the message
    if user is not None:    
        await ctx.respond(f'{user.mention}', delete_after=0)

    elif user is None:
        await ctx.respond(embed = discord.Embed(title = "You didn't enter the nickname.", color = capycolor), delete_after = 5)

@bot.slash_command(name = "clear", description = "Deletes messages by amount. (10 by default).")
@option(
    "amount",
    description = "The amount of messages you want to delete.",
    required = False,
    default = 10,
    input_type = int,
)
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_messages = True)
async def clear(ctx, amount:int = 10): #deletes messages
    if amount == 10:
        await ctx.channel.purge(limit=10)
        await ctx.respond(embed = discord.Embed(title = "10 messages are deleted.", color = capycolor), delete_after = 5)

    elif (amount >= 1) and (amount <= 50):
        await ctx.channel.purge(limit=amount)
        await ctx.respond(embed = discord.Embed(title = f"{amount} messages are deleted.", color = capycolor), delete_after = 5)

    elif amount > 50:
        await ctx.respond(embed = discord.Embed(title = "Message clear limit is 50.", color = capycolor), delete_after = 5)

@bot.slash_command(name = "ban", description = "Bans a user.")
@option(
    "member",
    description = "User you want to ban.", 
    required = True,
    default = None,
    input_type = User,
)
@option(
    "reason",
    description = "Ban reason.", 
    required = True,
    default = None,
    input_type = str,
)
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
async def ban(ctx,  member:discord.Member = None, reason: str = "one good reason"):
    if member == None:
        await ctx.respond(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor), delete_after = 5)
        return

    if member == ctx.author:
        await ctx.respond(embed = discord.Embed(title = "You can't ban yourself.", color = capycolor), delete_after = 5)
        return

    if member == bot.user:  
        await ctx.respond(embed = discord.Embed(title = "You can't ban this bot using this bots command, lol.", color = capycolor), delete_after = 5)
        return

    await ctx.guild.ban(member, reason = reason)

    em = discord.Embed(title = f"{member} is terminated.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await ctx.respond(embed = em)

    em_m = discord.Embed(title = f"You have been banned from {ctx.guild.name}", color = capycolor)
    em_m.add_field(name = "Reason", value = f"**{reason}**")
    await member.send(embed = em_m)



@bot.slash_command(name = "unban", description = "Unbans a user.")
@option(
    "member",
    description = "User you want to unban.(with #discriminator).",
    required = True,
    default = None 
)
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
async def unban(ctx, member:str = None):
    if member != None:
        member_name, member_discriminator = member.split("#")
        async for ban_entry in ctx.guild.bans(limit = 150):
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.respond(embed = discord.Embed(title = f"Unbanned {member}", color = capycolor))
                return

            else:
                await ctx.respond(embed = discord.Embed(title = f"{member} isn't banned.", color = capycolor))
                return

    if member == None:
        await ctx.channel.respond(embed = discord.Embed(title = "You didn't select a user.", color = capycolor))
        return 


@bot.slash_command(name = "mute", description = "Mutes a user.")
@option(
    "member",
    description = "User you want to mute.", 
    required = True,
    default = None,
    input_type = User,
)
@option(
    "time",
    description = "Time you want to set the mute in format: 1s, 2m, 3h, 4d.", 
    required = False,
    default = None,
    input_type = str,
)
@option(
    "reason",
    description = "Reason of the mute.", 
    required = False,
    default = None,
    input_type = str,
)
@commands.cooldown(1,5, commands.BucketType.user)
@commands.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
async def mute(ctx, member: discord.Member = None, time = None, reason: str = "one good reason"):
    perms = discord.Permissions(speak = False, send_messages = False, read_message_history = False, read_messages = False)
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")
    
    if not muted_role:
        muted_role = await ctx.guild.create_role(name = "Muted")

    if member == ctx.message.author:
        await ctx.channel.send(embed = discord.Embed(title = "You can't mute yourself.", color = capycolor))
        return

    if member == bot.user:  
        await ctx.channel.send(embed = discord.Embed(title = "You can't mute this bot using this bots command, lol.", color = capycolor))
        return
    
    await muted_role.edit(permissions = perms)

    if member is None:
        await ctx.respond(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))
        
    elif  member is not None:
        await member.add_roles(muted_role, reason = reason)
        if time is not None:
            time_u = parse_timespan(time)

            em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")
            em_m.add_field(name = "Time", value = f"{time}")

            await member.send(embed = em_m)

            em = discord.Embed(title = f"Muted {member}.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            em.add_field(name = "Time", value = f"{time}")

            await ctx.respond(embed = em)

            await asyncio.sleep(time_u)
            await member.remove_roles(muted_role)

        elif time is None:
            em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")

            await member.send(embed = em_m)

            em = discord.Embed(title = f"Muted {member}.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")

            await ctx.respond(embed = em)


    elif muted_role in member.roles:
        await ctx.respond(embed = discord.Embed(title = f"{member} is already muted.", color = capycolor))


@bot.slash_command(name = "unmute", description = "Unmutes a user.")
@option(
    "member",
    description = "User you want to unmute.", 
    required = True,
    default = None,
    input_type = User,
)
@commands.cooldown(1,5, commands.BucketType.user)
@commands.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
async def unmute(ctx, member: discord.Member = None):
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")
    
    if member is not None:
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.respond(embed = discord.Embed(title = f"{member} is unmuted.", color = capycolor))

        elif muted_role not in member.roles:
            await ctx.respond(embed = discord.Embed(title = f"{member} is not muted.", color = capycolor))


    if member is None:
        await ctx.respond(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))


@bot.slash_command(name = "avatar", description = "Gets avatar from user.")
@option(
    "member",
    description = "User you want to get an avatar from.", 
    required = True,
    input_type = User,
    default = None
)
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

        em = discord.Embed(color = capycolor)
        em.set_image(url = member.avatar.url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.respond(embed = em)

    elif member is not None:
        em = discord.Embed(color = capycolor)
        em.set_image(url = member.avatar.url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.respond(embed = em)


@bot.slash_command(name = "timeout", description = "Timeouts the")
@option(
    "user",
    description = "User you want to timeout.",
    required = True,
    input_type = User,
    default = None,
)
@option(
    "time",
    description = "Time you want to timeout the user for.",
    required = True,
    input_type = str,
    default = None,
)
@option(
    "reason",
    description = "Reason of the timeout.", 
    required = False,
    default = None,
    input_type = str,
)
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(moderate_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_permissions = True)
async def timeout(ctx, user: discord.Member = None, time = None, reason = "one good reason"):
    if user == ctx.message.author:
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban yourself.", color = capycolor))
        return

    if user == bot.user:  
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban this bot using this bots command, lol.", color = capycolor))
        return

    if user is not None:
        if time is not None:
            time_u = parse_timespan(time)
            
            await user.timeout(until = discord.utils.utcnow() + timedelta(seconds = time_u), reason = reason)

            em_m = discord.Embed(title = f"You've been timed out on {ctx.guild.name}.", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")
            em_m.add_field(name = "Time", value = f"{time}")

            await user.send(em_m)

            em = discord.Embed(title = f"{user} is timed out.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            em.add_field(name = "Time", value = f"{time}")

            await ctx.respond(embed = em)

        if time is None:
            await ctx.respond(embed = discord.Embed(title = "You need to enter time as argument.", color = capycolor))

    if user is None:
        await ctx.respond(embed = discord.Embed(title = "You need to enter the username as argument.", color = capycolor))

@bot.slash_command(name = "kick", description = "Kicks user from the server.")
@option(
    "user",
    description = "User you want to timeout.",
    required = True,
    input_type = User,
    default = None,
)
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(kick_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, kick_members = True)
async def kick(ctx,  user:discord.Member = None, *, reason: str = "one good reason"):
    if user == None:
        await ctx.respond(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor))
        return

    if user == ctx.author:
        await ctx.respond(embed = discord.Embed(title = "You can't kick yourself.", color = capycolor))
        return

    if user == bot.user:  
        await ctx.respond(embed = discord.Embed(title = "You can't kick this bot using this bots command, lol.", color = capycolor))
        return

    await ctx.guild.kick(user)

    em_m = discord.Embed(title = f"You have been kicked from {ctx.guild.name}.", color = capycolor)
    em_m.add_field(name = "Reason", value = f"**{reason}**")
    await user.send(embed = em_m)

    em = discord.Embed(title = f"{user} is kicked.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await ctx.respond(embed = em)



@bot.slash_command(name = "help", description = "List of all commands.")
@option(
    "command",
    description = "Choose command to get information about it.", 
    required = False,
    default = None,
    input_type = str,
    choices=[
                OptionChoice("translate", "translate"),
                OptionChoice("language", "language"),
                OptionChoice("languages_list", "languages_list"),
                OptionChoice("treply", "treply"),
                OptionChoice("capybara", "capybara"),
                OptionChoice("prefix", "prefix"),
                OptionChoice("clear", "clear"),
                OptionChoice("ping", "ping"),
                OptionChoice("ban", "ban"),
                OptionChoice("unban", "unban"),
                OptionChoice("mute", "mute"),
                OptionChoice("unmute", "unmute"),
                OptionChoice("avatar", "avatar"),
            ],
)
@commands.cooldown(1, 5, commands.BucketType.guild)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def help(ctx, command: str = None):
    cursor = capydb.cursor()
    prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {ctx.guild.id}")
    data = cursor.fetchone()
    prefix = data[1]
    cursor.close()

    if command == None:
        em = discord.Embed(title = "Help", description = f"Use **{prefix}help <command>** to get more information on a command. ", color = capycolor)

        em.add_field(name = "Translation", value = "**translate, treply, language, languages_list**")
        em.add_field(name = "Capybara and tools", value = "**capybara, avatar**")
        em.add_field(name = "Bot commands", value = "**prefix, clear, ping, ban, unban, mute, unmute**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "translate":
        em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}translate ['sentence'] <'(sourse language>'] <'(destination language)'>**")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "language":
        em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}languages <('english' for code) or ('en' for language)>**")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list**.")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "languages_list":
        for l in googletrans.LANGUAGES.values():
            lang_list.append(l)

        em = discord.Embed(title = "languages_list", description = "\n".join(lang_list), color = capycolor)

        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)
    
    elif command == "treply":
        em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}treply <d='(destination language)'> <s='(sourse language)'>**")
        em.add_field(name = "Default languages", value = "The defaults are:\n • Auto source language \n • English as a destination language")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")

        await ctx.respond(embed = em)

    elif command == "capybara":
        em = discord.Embed(title = "capybara", description = "Toogles On and Off on your capybara pics dispenser.", color = capycolor)

        em.add_field(name = "Syntax", value = f"{prefix}capybara")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)
    
    elif command == "prefix":
        em = discord.Embed(title = "prefix", description = "Changes your server prefix.", color = capycolor)
            
        em.add_field(name = "Syntax" , value = f"**{prefix}prefix '[new_prefix]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
            
        await ctx.respond(embed = em)

    elif command == "clear":
        em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)
            
        em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
            
        await ctx.respond(embed = em)
    
    elif command == "ping":
        em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}ping '[user (without #(discriminator))]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await ctx.respond(embed = em)

    elif command == "ban":
        em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}ban '[user (can be without #(discriminator))]' '<reason>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await ctx.respond(embed = em)
    
    elif command == "unban":
        em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}unban '[user (with #(discriminator))]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "mute":
        em = discord.Embed(title = "mute", description = "Mutes a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}mute '[user]' '<reason>' '<time>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "unmute":
        em = discord.Embed(title = "unmute", description = "Unmutes a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}unmute '[user]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await ctx.respond(embed = em)

    elif command == "avatar":
        em = discord.Embed(title = "avatar", description = "Gets avatar from user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}avatar '[user]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)

    elif command == "timeout":
        em = discord.Embed(title = "timeout", description = "Timeouts the user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}timeout '[user]' '[time]' '<reason>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)
    
    elif command == "kick":
        em = discord.Embed(title = "kick", description = "Kicks the user from the server.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}kick '[user]' **")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await ctx.respond(embed = em)
    
    else:
        await ctx.respond(embed = discord.Embed(title = f"There's no {prefix}help for this command.", color = capycolor))


# #on_message use
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    msg = message.content

    if message.author == bot.user:
        return
    
    if (any(word.lower() in msg for word in capybara_words) or \
            any(word.upper() in msg for word in capybara_words) or \
            any(word in msg for word in capybara_words)): #searches for words in lower, upper and Ca... - like words

            cursor = capydb.cursor()

            prefix = cursor.execute(f"SELECT * FROM guilds WHERE guild_id = {message.guild.id}")
            data = cursor.fetchone()
            prefix = data[1]

            if  msg.startswith(prefix):
                return
            else:
                toggle = cursor.execute("SELECT * FROM capypics WHERE guild_id = (%s)", [message.guild.id])
                data1 = cursor.fetchone()
                toggle = str(data1[1])

                if not message.guild.id in message_on_cooldown and toggle == "1":
                    os.chdir(CAPY_IMAGES) #changes main directory, doesn't work without it
                    image = random.choice(os.listdir(CAPY_IMAGES)) #gets random image of capybara from the directory

                    with open(image, 'rb') as f: # opens it
                        picture = discord.File(f)
                        await message.channel.send(file=picture) #sends it as a picture

                    message_on_cooldown.append(message.guild.id) #add guild to cooldown
                    await asyncio.sleep(5) # time in seconds
                    message_on_cooldown.remove(message.guild.id) #remove guild from cooldown

                if message.guild.id in message_on_cooldown:
                    em = discord.Embed(title = "Your server is on cooldown.", color = capycolor)
                    await message.channel.send(embed =  em, delete_after = 3)

                if toggle == "0" and not message.guild.id in message_on_cooldown:
                    em = discord.Embed(title = "Your capypics are off.", color = capycolor)
                    await message.channel.send(embed = em, delete_after = 3)
                    
                    message_on_cooldown.append(message.guild.id) #add guild to cooldown
                    await asyncio.sleep(30) # time in seconds
                    message_on_cooldown.remove(message.guild.id) #remove guild from cooldown

            cursor.close()

bot.run(TOKEN)
