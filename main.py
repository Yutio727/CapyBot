from zlib import DEFLATED
import discord
import discord.utils
from discord import Member
from discord.ext import commands
import os
import random
import os.path
from decouple import config
import googletrans
import asyncpg
import discord.utils
import asyncio

#getting variables
CAPY_IMAGES = config("CAPY_IMAGES") 
TOKEN = config("TOKEN")
PATH_IMAGEDATABASE = config("PATH_IMAGEDATABASE") 
PATH_PREFIX = config("PATH_PREFIX")
CAPY_BASE = config("DATABASE")

translator = googletrans.Translator()

intents = discord.Intents.default()
intents.members = True

capybara_words = [
    "Capybara", "Capybaras", "Copybara", "Coconut Doggo",
    "Capibara","Капибара", "Кокосовая Свинка", "Водосвинка",
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
    'Fapu', 'Ikhonsaba', "水豚"
] #almost all languages & some forms of rus and eng from googletrans

capycolor = discord.Color.from_rgb(219, 188, 129)

message_on_cooldown = [] 
lang_list = []

DEFAULT_PREFIX = "!"


async def get_prefix(bot, message): #getting prefix from database
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot,message)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
    if len(prefix) == 0:
        await bot.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)", message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX
    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot, message)


async def create_db_pool(): #connecting to database
    bot.db = await asyncpg.create_pool(CAPY_BASE) 
    print("Connected to database.".format(bot))

#bot command
bot = commands.Bot(command_prefix = get_prefix, intents=intents, help_command = None, activity = discord.Activity(type=discord.ActivityType.playing, name="!help"), status=discord.Status.idle)

@bot.event
async def on_ready(): #when bot is ready
    print("{0.user} is fully operational.".format(bot)) #when the bot is loaded

@bot.event
async def on_command_error(ctx, error): #handling errors
    if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title=f"Command is on a cooldown.",description=f"Try again in {error.retry_after:.2f}s.", color=capycolor)
            await ctx.send(embed = em)
    elif isinstance(error, commands.MissingPermissions):
        em = discord.Embed(title=f"You're missing some permissions.", color=capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.CommandInvokeError):
        em = discord.Embed(title=f"Something went wrong.", color=capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        em = discord.Embed(title=f"You haven't entered all required arguments.", color=capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"This command doesn't exist.", color=capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.NoPrivateMessage):
        em = discord.Embed(title = "This command cannot be used in private messages.")
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.UserNotFound):
        em = discord.Embed(title = "Couldn't find this user.", color = capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.BadArgument):
        em = discord.Embed(title = "You put in wrong argument.", color = capycolor)
        await ctx.send(embed = em)
        print(error)
    elif isinstance(error, commands.BotMissingPermissions):
        em = discord.Embed(title = f"Bot is missing needed permissions: {error}.")
        await ctx.send(embed = em)
        print(error)
    else:
        print(error)



@bot.command(aliases=["setpre"])
@commands.has_permissions(administrator = True)
@commands.cooldown(1, 60, type=commands.BucketType.user)
async def changeprefix(ctx, new_prefix):#changes the prefix
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        await ctx.send(f"Prefix was changed to: {new_prefix}")
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]")
    else:
        await ctx.send("Your prefix is way too long, try shorter one.")



@bot.command()
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def translate(ctx, sentence, arg1 = "", arg2 = ""): #this thing translates text to whatever you want (google translate) by any args
    if len(str(sentence)) > 0: #when sentence is existing
        if arg1[:2] == "d=": #if first argument is destination language
            dest = arg1[-2:]
            if arg2[:2] == "s=":#if second argument is source language
                src = arg2[-2:]
                translation = translator.translate(sentence, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(sentence, dest)
                await ctx.channel.send(f"{translation.text}")

        if arg1[:2] == "s=":#if first argument is destination language
            src = arg1[-2:]
            if arg2[:2] == "d=":#if second argument is destination language
                dest = arg2[-2:]
                translation = translator.translate(sentence, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(sentence, src)
                await ctx.channel.send(f"{translation.text}")

        if len(arg1) == 0 and len(arg2) == 0:
            translation = translator.translate(sentence)
            await ctx.channel.send(f"{translation.text}")
    else: 
        await ctx.channel.send("You didn't put any text to translate.")

@bot.command()
@commands.cooldown(1, 10, type=commands.BucketType.user)
async def treply(ctx, arg1 = "", arg2 = ""):
    if ctx.message.reference and (msg := ctx.message.reference.resolved) and isinstance(msg, discord.Message): #checks if you had replyed and used the command
        if arg1[:2] == "d=": #if first argument is destination language
            dest = arg1[-2:]
            if arg2[:2] == "s=": #if second argument is source language
                src = arg2[-2:]
                translation = translator.translate(msg.content, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(msg.content, dest)
                await ctx.channel.send(f"{translation.text}")

        if arg1[:2] == "s=": #if first argument is source language
            src = arg1[-2:]
            if arg2[:2] == "d=": #if first argument is destination language
                dest = arg2[-2:]
                translation = translator.translate(msg.content, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(msg.content, src)
                await ctx.channel.send(f"{translation.text}")

        if len(arg1) == 0 and len(arg2) == 0: #if no arguments put
            translation = translator.translate(msg.content)
            await ctx.channel.send(f"{translation.text}")
    else:
        await ctx.send("You need to reply to an existing message.")


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def language(ctx, lang = ""): #you're putting the language or the language code - it gives you the language code or language
    if len(str(lang)) == 2:
        lang_code = googletrans.LANGUAGES[str(lang)]
        await ctx.channel.send(f"{lang}:  {lang_code}")

    if len(str(lang)) > 2:
        lang_code = googletrans.LANGCODES[str(lang)]
        await ctx.channel.send(f"{lang}:  {lang_code}")
    else:
        await ctx.channel.send("Your language isn't on the list.")

    
@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def clear(ctx, amount=10): #deletes messages
    if amount <= 50:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.channel.send("Message deleting limit is 50.")

@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def ban(ctx,  member:discord.Member = None, reason = None):
    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor))
        return
    if reason == None:
        reason == "One good reason."
    if member == ctx.message.author:
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban yourself.", color = capycolor))
        return
    if member == bot.user:  
        await ctx.channel.send(embed = discord.Embed(title = "You can't ban this bot using this bots command, lol.", color = capycolor))
        return

    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await member.send(message)

    await ctx.guild.ban(member, reason = reason)
    await ctx.channel.send(embed = discord.Embed(title = f"{member} is terminated."))

@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def unban(ctx, member = None):
    if member != None:
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(embed = discord.Embed(title = f"Unbanned {member}"))
                return
            else:
                await ctx.send(embed = discord.Embed(title = f"{member} isn't banned."))
                return
    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user or user not found."))
        return 




@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def ping(ctx, user:discord.User): #pings the user and immediately deletes the message
    await ctx.send(f'{user.mention}', delete_after=0)
    await ctx.message.delete()
    


@bot.group(invoke_without_command = True)
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def help(ctx): # new help command
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "Help", description = f"Use **{prefix}help <command>** to get more information on a command.", color = capycolor)

    em.add_field(name = "Translation", value = "**translate, treply, language, languages_list**")
    em.add_field(name = "Capybara", value = "**capybara**")
    em.add_field(name = "Bot commands", value = "**changeprefix, clear, ping, ban, unban**")

    await ctx.send(embed = em)


@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def translate(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}translate <'sentence'> [s='(sourse language)'] [d='(destination language)']**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def language(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}languages <('english' for code) or] ('en' for language)>**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list**.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def languages_list(ctx):
    for l in googletrans.LANGUAGES.values():
        lang_list.append(l)
    em = discord.Embed(title = "languages_list", description = "\n".join(lang_list), color = capycolor)

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def treply(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}treply [s='(sourse language)'] [d='(destination language)']**")
    em.add_field(name = "Default languages", value = "The defaults are:\n • Auto source language \n • English as a destination language")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def capybara(ctx):

    em = discord.Embed(title = "capybara", description = "Sends you a random capybara pic.", color = capycolor)

    em.add_field(name = "Syntax", value = "Not a command, just type **capybara** in any language (almost any language).")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def changeprefix(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "changeprefix", description = "Changes your server prefix.", color = capycolor)

    em.add_field(name = "Syntax" , value = f"**{prefix}changeprefix '<new_prefix>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def clear(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def ping(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ping '<user (without #(discriminator))>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def ban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ban '<user (can be without #(discriminator))>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def unban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unban '<user (with #(discriminator))>'**")

    await ctx.send(embed = em)

@bot.event
async def on_message(message):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
    prefix = prefix[0].get("prefix")
    msg = message.content

    if message.author == bot.user:
        return
    

    if (any(word.lower() in msg for word in capybara_words) or \
            any(word.upper() in msg for word in capybara_words) or \
            any(word in msg for word in capybara_words))\
            and not msg.startswith(prefix): #searches for words in lower, upper and Ca... - like words
        if not message.author.id in message_on_cooldown:

            os.chdir(CAPY_IMAGES) #changes main directory, doesn't work without it
            image = random.choice(os.listdir(PATH_IMAGEDATABASE)) #gets random image of capybara from the directory

            with open(image, 'rb') as f: # opens it
                picture = discord.File(f)
                await message.channel.send(file=picture) #sends it as a picture
            message_on_cooldown.append(message.author.id) #add users to cooldown
            await asyncio.sleep(60) # time in seconds
            message_on_cooldown.remove(message.author.id) #remove users from cooldown
        else:
            await message.delete()

          
    if "727" in msg:
        await message.channel.send("WYSI") #if sees 727 - sends WYSI

    await bot.process_commands(message)

bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)