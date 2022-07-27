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
import asyncio
import functools
import dislash
from dislash import InteractionClient, Option, OptionType, ContextMenuInteraction, application_commands

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

capycolor = discord.Color.from_rgb(219, 188, 129)

guilds_list = []
message_on_cooldown = [] 
lang_list = []
DEFAULT_PREFIX = "!"
DEFAULT_TOGGLE = "On"


async def get_prefix(bot, message): #getting prefix from database
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot,message)

    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
    toggle = await bot.db.fetch("SELECT toggle FROM capypics WHERE guild_id = $1", message.guild.id)
    
    if len(prefix) == 0:
        await bot.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)", message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX
    else:
        prefix = prefix[0].get("prefix")

    if len(toggle) == 0:
        await bot.db.execute("INSERT INTO capypics(guild_id, toggle) VALUES ($1, $2)", message.guild.id, DEFAULT_TOGGLE)
        toggle = DEFAULT_TOGGLE
    else:
        toggle = toggle[0].get("toggle")
    #   print(toggle)
    return commands.when_mentioned_or(prefix)(bot, message)


async def create_db_pool(): #connecting to database
    bot.db = await asyncpg.create_pool(CAPY_BASE) 
    print("Connected to database.".format(bot))


#bot command
bot = commands.Bot(command_prefix = get_prefix, intents=intents, help_command = None, activity = discord.Activity(type=discord.ActivityType.playing, name="!help"), status=discord.Status.idle)

inter_client = InteractionClient(bot)


@bot.event
async def on_ready(): #when bot is ready
    print("{0.user} is fully operational.".format(bot)) #when the bot is loaded
    print("Please wait atleast 20 seconds before using slash commands.")



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
        em = discord.Embed(title = "You put in wrong argument.", color = capycolor)
        await ctx.send(embed = em, delete_after = 15)

    elif isinstance(error, commands.BotMissingPermissions):
        em = discord.Embed(title = f"Bot is missing needed permissions: {error}.")
        await ctx.send(embed = em, delete_after = 15)
    else:
       raise error

@bot.event
async def on_slash_command_error(inter: ContextMenuInteraction, error):
    if isinstance(error, application_commands.errors.CommandOnCooldown):
        em = discord.Embed(title=f"Command is on a cooldown.", description=f"Try again in {error.retry_after:.2f}s.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)

    elif isinstance(error, application_commands.errors.MissingPermissions):
        em = discord.Embed(title=f"You're missing some permissions.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)
        
    elif isinstance(error, KeyError):
        em = discord.Embed(title=f"You put in wrong argument.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)
    else:
        raise error


@bot.command(aliases=["setpre"])
@commands.has_permissions(administrator = True)
@commands.cooldown(1, 5, type=commands.BucketType.guild)
async def prefix(ctx, new_prefix):#changes the prefix
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        em = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor)
        await ctx.send(embed = em)
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]")
    else:
        em = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor)
        await ctx.send(embed = em)




@bot.command()
@commands.has_permissions(administrator = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def capybara(ctx):
    toggle = await bot.db.fetch("SELECT toggle FROM capypics     WHERE guild_id = $1", ctx.guild.id)
    toggle = toggle[0].get("toggle")
    if  toggle == "On":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "Off", ctx.guild.id)
        em = discord.Embed(title = "Capybara pics are off.", color = capycolor)
        await ctx.channel.send(embed = em)
    if toggle == "Off":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "On", ctx.guild.id)
        em = discord.Embed(title = "Capybara pics are on.", color = capycolor)
        await ctx.channel.send(embed = em)

@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
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
        em = discord.Embed(title = "You didn't put any text to translate.", color = capycolor)
        await ctx.channel.send(embed = em, delete_after = 15)


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
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
        em = discord.Embed(title = "You need to reply to an existing message.", color = capycolor)
        await ctx.channel.send(embed = em, delete_after = 15)


@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
async def language(ctx, language = ""): #you put the language or the language code - it gives you the language code or language
    if len(language) == 2:
        lang_code = googletrans.LANGUAGES[str(language)]
        em = discord.Embed(title = f"**{lang_code}** is  **{language}**", color = capycolor)
        await ctx.channel.send(embed = em)

    elif len(language) > 2:
        lang_code = googletrans.LANGCODES[str(language)]
        em = discord.Embed(title = f"**{language}** is  **{lang_code}**", color = capycolor)
        await ctx.channel.send(embed = em)
    else:
        em = discord.Embed(title = "Your language isn't on the list.", color = capycolor)
        await ctx.channel.send(embed = em)

    
@bot.command()
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def clear(ctx, amount=10): #deletes messages
    if amount <= 50:
        await ctx.channel.purge(limit=amount)
    else:
        await ctx.channel.send("Message deleting limit is 50.")


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def ping(ctx, user:discord.User): #pings the user and immediately deletes the message
    await ctx.send(f'{user.mention}', delete_after=0)
    await ctx.message.delete()


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def ban(ctx,  member:discord.Member = None, reason = "one good reason"):
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
    await member.send(embed = discord.Embed(title = f"You have been banned from {ctx.guild.name} for {reason}", color = capycolor))

    await ctx.channel.send(embed = discord.Embed(title = f"{member} is terminated."), color = capycolor)
async def unban(inter: ContextMenuInteraction, member = None):
    if member != None:
        banned_users = await inter.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await inter.guild.unban(user)
                await inter.respond(embed = discord.Embed(title = f"Unbanned {member}", color = capycolor))
                return
            else:
                await inter.respond(embed = discord.Embed(title = f"{member} isn't banned.", color = capycolor))
                return
    if member == None:
        await inter.respond(embed = discord.Embed(title = "You didn't select a user.", color = capycolor))
        return 


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
                await ctx.send(embed = discord.Embed(title = f"Unbanned {member}", color = capycolor))
                return
            else:
                await ctx.send(embed = discord.Embed(title = f"{member} isn't banned.", color = capycolor))
                return
    if member == None:
        await ctx.channel.send(embed = discord.Embed(title = "You didn't select a user.", color = capycolor))
        return 



@dislash.cooldown(1,5, type=commands.BucketType.user)
@inter_client.command(
    description="Translates a word or a sentence",
    options=[
        Option("sentence", "Your sentence.", OptionType.STRING),
        Option("source", "The language you want to translate from.", OptionType.STRING),
        Option("destination", "The language you want to translate to.", OptionType.STRING)
    ]
)
async def translate(inter, sentence = None, source = None, destination = None): #this thing translates text to whatever you want (google translate) by any args
    if sentence is not None: #when sentence is existing
            if destination is not None and source is not None: #if first argument is destination language
                translation = translator.translate(sentence, destination, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, from **{source}** to **{destination}**.", color = capycolor)
                await inter.respond(embed = em)
            if source is not None and destination is None:
                translation = translator.translate(sentence, source)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**, from **{source}**.", color = capycolor)
                await inter.respond(embed = em)
            if destination is not None and source is None:
                translation = translator.translate(sentence, destination)
                em = discord.Embed(title = f"{translation.text}", description = f"Translated **{sentence}**.", color = capycolor)
                await inter.respond(embed = em)
    else:
        em = discord.Embed(title = "You didn't put any text to translate.", color = capycolor)
        await inter.respond(embed = em)   


@dislash.cooldown(1,5, type=commands.BucketType.user)
@inter_client.slash_command(
    description="Translates a word or a sentence",
    options=[
        Option("language", "Language you want to see.", OptionType.STRING),
    ]
)
async def language(inter, language = None):
    if language is not None:
        if len(str(language)) == 2:
            lang_code = googletrans.LANGUAGES[str(language)]
            em = discord.Embed(title = f"{lang_code} is  **{language}**", color = capycolor)
            await inter.respond(embed = em)  
        elif len(str(language)) > 2:
            lang_code = googletrans.LANGCODES[str(language)]
            em = discord.Embed(title = f"{language} is  **{lang_code}**", color = capycolor)
            await inter.respond(embed = em)  
    elif language is None:
        em = discord.Embed(title = "You need to enter the language.", color = capycolor)
        await inter.respond(embed = em) 
    else:
        em = discord.Embed(title = "Your language isn't on the list.", color = capycolor)
        await inter.respond(embed = em)


@dislash.cooldown(1, 30, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@inter_client.slash_command(
    description="Pings a user and deletes a message.",
    options=[
        Option("user", "User your want to ping.", OptionType.USER),
    ]
)
async def ping(inter, user:discord.User): #pings the user and immediately deletes the message
    await inter.send(f'{user.mention}', delete_after=0)


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@inter_client.slash_command(
    description="Changes the prefix on your server.",
    options=[
        Option("new_prefix", "Prefix you want to use on your server.", OptionType.STRING),
    ]
)
async def prefix(ctx, new_prefix):#changes the prefix
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        em = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor)
        await ctx.send(embed = em)
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]")
    else:
        em = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor)
        await ctx.send(embed = em)


@dislash.cooldown(1, 30, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@inter_client.slash_command(
    description="Toogles the capybara pics sending."
)
async def capybara(ctx):
    toggle = await bot.db.fetch("SELECT toggle FROM capypics     WHERE guild_id = $1", ctx.guild.id)
    toggle = toggle[0].get("toggle")
    if  toggle == "On":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "Off", ctx.guild.id)
        em = discord.Embed(title = "Capybara pics are off.", color = capycolor)
        await ctx.respond(embed = em)
    if toggle == "Off":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "On", ctx.guild.id)
        em = discord.Embed(title = "Capybara pics are on.", color = capycolor)
        await ctx.respond(embed = em)


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@inter_client.slash_command(
    description="Deletes messages by amount. (10 by default)",
    options=[
        Option("amount", "The amount of messages you want to delete.", OptionType.INTEGER),
    ]
)
async def clear(ctx, amount = 10): #deletes messages
    if amount == 10:
        await ctx.channel.purge(limit=10)
        em = discord.Embed(title = "10 messages are deleted.", color = capycolor)
        await ctx.send(embed = em)
    elif (amount >= 1) and (amount <= 50):
        await ctx.channel.purge(limit=amount)
        em = discord.Embed(title = f"{amount} messages are deleted.", color = capycolor)
        await ctx.send(embed = em)
    elif amount > 50:
        em = discord.Embed(title = "Message deleting limit is 50.", color = capycolor)
        await ctx.send(embed = em)


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(ban_members=True)
@inter_client.slash_command(
    description="Bans a user",
    options=[
        Option("member", "User you want to ban.", OptionType.USER),
        Option("reason", "Ban reason.", OptionType.STRING)
    ]
)
async def ban(inter: ContextMenuInteraction,  member:discord.Member = None, reason = "one good reason."):
    if member == None:
        await inter.respond(embed = discord.Embed(title = "You didn't select a user or user not found.", color = capycolor))
        return
    if member == inter.author:
        await inter.respond(embed = discord.Embed(title = "You can't ban yourself.", color = capycolor))
        return
    if member == bot.user:  
        await inter.respond(embed = discord.Embed(title = "You can't ban this bot using this bots command, lol.", color = capycolor))
        return

    await inter.guild.ban(member, reason = reason)
    await member.send(embed = discord.Embed(title = f"You have been banned from {inter.guild.name} for {reason}", color = capycolor))

    await inter.respond(embed = discord.Embed(title = f"{member} is terminated.", color = capycolor))


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(ban_members=True)
@inter_client.slash_command(
    description="Unbans a user",
    options=[
        Option("member", "User you want to unban.(with #discriminator)", OptionType.STRING),
    ]
)
async def unban(inter: ContextMenuInteraction, member = None):
    if member != None:
        banned_users = await inter.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await inter.guild.unban(user)
                await inter.respond(embed = discord.Embed(title = f"Unbanned {member}", color = capycolor))
                return
            elif (user.name, user.discriminator) != (member_name, member_discriminator):
                await inter.respond(embed = discord.Embed(title = f"{member} isn't banned.", color = capycolor))
                return
    if member == None:
        await inter.respond(embed = discord.Embed(title = "You didn't select a user.", color = capycolor))
        return 

@bot.group(invoke_without_command = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def help(ctx): # new help command
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "Help", description = f"Use **{prefix}help <command>** to get more information on a command.", color = capycolor)

    em.add_field(name = "Translation", value = "**translate, treply, language, languages_list**")
    em.add_field(name = "Capybara", value = "**capybara**")
    em.add_field(name = "Bot commands", value = "**prefix, clear, ping, ban, unban**")

    await ctx.send(embed = em)


@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def translate(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}translate <'sentence'> [s='(sourse language)'] [d='(destination language)']**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def language(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}languages <('english' for code) or] ('en' for language)>**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list**.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def languages_list(ctx):
    for l in googletrans.LANGUAGES.values():
        lang_list.append(l)
    em = discord.Embed(title = "languages_list", description = "\n".join(lang_list), color = capycolor)

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def treply(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}treply [d='(destination language)'] [s='(sourse language)']**")
    em.add_field(name = "Default languages", value = "The defaults are:\n • Auto source language \n • English as a destination language")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def capybara(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "capybara", description = "Toogles On and Off on your capybara pics dispenser.", color = capycolor)

    em.add_field(name = "Syntax", value = "f{prefix}capybara")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def prefix(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "prefix", description = "Changes your server prefix.", color = capycolor)

    em.add_field(name = "Syntax" , value = f"**{prefix}prefix '<new_prefix>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def clear(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def ping(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ping '<user (without #(discriminator))>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def ban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ban '<user (can be without #(discriminator))>' '<reason>'**")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def unban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unban '<user (with #(discriminator))>'**")

    await ctx.send(embed = em)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    msg = message.content

    if message.author == bot.user:
        return
    
    
    if (any(word.lower() in msg for word in capybara_words) or \
            any(word.upper() in msg for word in capybara_words) or \
            any(word in msg for word in capybara_words)): #searches for words in lower, upper and Ca... - like words
            prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
            prefix = prefix[0].get("prefix")
            toggle = await bot.db.fetch("SELECT toggle FROM capypics WHERE guild_id = $1", message.guild.id)
            toggle = toggle[0].get("toggle")
            if not message.guild.id in message_on_cooldown and toggle == "On" and not msg.startswith(prefix):
                os.chdir(CAPY_IMAGES) #changes main directory, doesn't work without it
                image = random.choice(os.listdir(PATH_IMAGEDATABASE)) #gets random image of capybara from the directory
                with open(image, 'rb') as f: # opens it
                    picture = discord.File(f)
                    await message.channel.send(file=picture) #sends it as a picture
                message_on_cooldown.append(message.guild.id) #add guild to cooldown
                await asyncio.sleep(5) # time in seconds
                message_on_cooldown.remove(message.guild.id) #remove guild from cooldown
            if message.guild.id in message_on_cooldown:
                em = discord.Embed(title = "Your server is on cooldown.", color = capycolor)
                await message.channel.send(embed =  em, delete_after = 3)
            if toggle == "Off" and not message.guild.id in message_on_cooldown:
                em = discord.Embed(title = "Your capypics are off.", color = capycolor)
                await message.channel.send(embed = em, delete_after = 3)
                message_on_cooldown.append(message.guild.id) #add guild to cooldown
                await asyncio.sleep(30) # time in seconds
                message_on_cooldown.remove(message.guild.id) #remove guild from cooldown

bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)
