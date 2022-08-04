import discord
import discord.utils
from discord import Member
from discord.ext import commands
import re
import os
import random
import os.path
from decouple import config
import googletrans
import asyncpg
import asyncio
import dislash
from dislash import InteractionClient, Option, OptionType, ContextMenuInteraction, application_commands, OptionChoice, SlashInteraction

#getting variables
CAPY_IMAGES = config("CAPY_IMAGES") 
TOKEN = config("TOKEN")
PATH_IMAGEDATABASE = config("PATH_IMAGEDATABASE") 
PATH_PREFIX = config("PATH_PREFIX")
CAPY_BASE = config("DATABASE")

translator = googletrans.Translator() #googletrans lib

intents = discord.Intents.default() #discord intents
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

capycolor = discord.Color.from_rgb(219, 188, 129) #unique color for embeds 

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?") #regex for mute command
time_dict = {"h":3600, "s":1, "m":60, "d":86400} #time in seconds to convert in mute command

message_on_cooldown = [] #used in on_message
lang_list = [] #used in {prefix}help languages_list

DEFAULT_PREFIX = "!"
DEFAULT_TOGGLE = "On"



class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
                time += time_dict[k]*float(v)
        return time

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

inter_client = InteractionClient(bot, test_guilds = [815928209786011678,990336510895222795,1002519224046075904]) #delete test_guilds to get it to production


@bot.event
async def on_ready(): #when bot is ready
    print("{0.user} is fully operational.".format(bot)) #when the bot is loaded
    print("Please wait atleast 1 minute before using slash commands if test_guilds are not set in inter_client.")
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
async def on_slash_command_error(inter: ContextMenuInteraction, error):
    if isinstance(error, application_commands.errors.CommandOnCooldown):
        em = discord.Embed(title=f"Command is on a cooldown.", description=f"Try again in {error.retry_after:.2f}s.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)

    elif isinstance(error, application_commands.errors.MissingPermissions):
        em = discord.Embed(title=f"You're missing some permissions.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)
        
    elif isinstance(error, KeyError):
        em = discord.Embed(title=f"You entered in wrong argument.", color=capycolor)
        await inter.respond(embed = em, ephemeral = True)
    else:
        raise error #raises the error if it's not already listed in isinstanse


@bot.command(aliases=["setpre"])
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(change_nickname = True, send_messages = True, read_messages = True)
@commands.cooldown(1, 5, type=commands.BucketType.guild)
async def prefix(ctx, new_prefix = ""):#changes the prefix
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        await ctx.send(embed = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor))
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]") #changes nickname with current guild prefix

    elif len(new_prefix) == 0:
        await ctx.send(embed = discord.Embed(title = "You didn't enter the prefix", color = capycolor))

    else:
        await ctx.send(embed = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor))




@bot.command()
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
async def capybara(ctx):
    toggle = await bot.db.fetch("SELECT toggle FROM capypics WHERE guild_id = $1", ctx.guild.id)
    toggle = toggle[0].get("toggle")

    if  toggle == "On":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "Off", ctx.guild.id)
        await ctx.channel.send(embed = discord.Embed(title = "Capybara pics are off.", color = capycolor))

    if toggle == "Off":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "On", ctx.guild.id)
        await ctx.channel.send(embed = discord.Embed(title = "Capybara pics are on.", color = capycolor))

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
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.has_permissions(manage_messages = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_messages = True)
async def clear(ctx, amount=10): #deletes messages
    if amount <= 50:
        await ctx.channel.purge(limit=amount)

    else:
        await ctx.channel.send(embed = discord.Embed(title = "Clear limit is 50.", color = capycolor))


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
@commands.has_permissions(administrator = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ping(ctx, user:discord.User = None): #pings the user and immediately deletes the message
    if user is not None:
        await ctx.send(f'{user.mention}', delete_after=0)
        await ctx.message.delete()
    else:
        await ctx.send(embed = discord.Embed(title = "You didn't enter the nickname.", color = capycolor))


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

    em = discord.Embed(title = f"{member.mention} is terminated.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await ctx.channel.send(embed = em)


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(ban_members = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
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


@bot.command()
@commands.cooldown(1,5, type=commands.BucketType.user)
@commands.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@commands.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
async def mute(ctx, member: discord.Member = None, reason: str = "", time:TimeConverter = None):
    perms = discord.Permissions(speak = False, send_messages = False, read_message_history = False, read_messages = False)
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")

    if not muted_role:
        muted_role = await ctx.guild.create_role(name = "Muted")
    
    await muted_role.edit(permissions = perms)

    if member is None:
        await ctx.send(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))
        
    elif  member is not None:
        await member.add_roles(muted_role, reason = reason)
        if len(reason) != 0:
            if time is not None:
                em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
                em_m.add_field(name = "Reason", value = f"{reason}")
                em_m.add_field(name = "Time", value = f"{round(time)}s")

                await member.send(embed = em_m)

                em = discord.Embed(title = f"Muted {member}.", color = capycolor)
                em.add_field(name = "Reason", value = f"{reason}")
                em.add_field(name = "Time", value = f"{round(time)}s")

                await ctx.send(embed = em)

                await asyncio.sleep(time)
                await member.remove_roles(muted_role)

            elif time is None:
                em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
                em_m.add_field(name = "Reason", value = f"{reason}")

                await member.send(embed = em_m)

                em = discord.Embed(title = f"Muted {member}.", color = capycolor)
                em.add_field(name = "Reason", value = f"{reason}")

                await ctx.send(embed = em)

        elif len(reason) == 0:
            reason = "one good reason"
            if time is not None:
                em_m = discord.Embed(title = f"You have been muted on {ctx.guild.name}.", color = capycolor)
                em_m.add_field(name = "Reason", value = f"{reason}")
                em_m.add_field(name = "Time", value = f"{round(time)}s")

                await member.send(embed = em_m)

                em = discord.Embed(title = f"Muted {member}.", color = capycolor)
                em.add_field(name = "Reason", value = f"{reason}")
                em.add_field(name = "Time", value = f"{round(time)}s")

                await ctx.send(embed = em)

                await asyncio.sleep(time)
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
        em.set_image(url = member.avatar_url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.channel.send(embed = em)

    elif member is not None:
        em = discord.Embed(color = capycolor)
        em.set_image(url=member.avatar_url)
        em.set_footer(text = f"Avatar from {member}")

        await ctx.channel.send(embed = em)


#help command for prefix use
@bot.group(invoke_without_command = True)
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def help(ctx): # new help command
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

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
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}translate <'sentence'> [s='(sourse language)'] [d='(destination language)']**")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def language(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

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
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

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
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "capybara", description = "Toogles On and Off on your capybara pics dispenser.", color = capycolor)

    em.add_field(name = "Syntax", value = f"{prefix}capybara")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def prefix(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "prefix", description = "Changes your server prefix.", color = capycolor)

    em.add_field(name = "Syntax" , value = f"**{prefix}prefix '<new_prefix>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def clear(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ping(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ping '<user (without #(discriminator))>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def ban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}ban '<user (can be without #(discriminator))>' '<reason>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def unban(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unban '<user (with #(discriminator))>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def mute(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "mute", description = "Mutes a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}mute '<user>' '<reason>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def unmute(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "unmute", description = "Unmutes a user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}unmute '<user>'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

@help.command()
@commands.cooldown(1, 5, type=commands.BucketType.channel)
@commands.bot_has_permissions(send_messages = True, read_messages = True)
async def avatar(ctx):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "avatar", description = "Gets avatar from user.", color = capycolor)

    em.add_field(name = "Syntax", value = f"**{prefix}avatar '[user]'**")
    em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

    await ctx.send(embed = em)

#regular slash commands
@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@dislash.bot_has_guild_permissions(change_nickname = True, send_messages = True, read_messages = True)
@inter_client.slash_command(
    description="Changes the prefix on your server.",
    options=[
        Option("new_prefix", "Prefix you want to use on your server.", OptionType.STRING),
    ]
)
async def prefix(ctx, new_prefix = ""):#changes the prefix
    if len(new_prefix) > 0 and len(new_prefix) <= 3:
        await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        await ctx.send(embed = discord.Embed(title = f"Prefix was changed to: {new_prefix}", color = capycolor))
        await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]")

    elif len(new_prefix) == 0:
        await ctx.send(embed = discord.Embed(title = "You didn't enter the prefix", color = capycolor))

    else:
        await ctx.send(embed = discord.Embed(title = "Your prefix is way too long, try shorter one.", color = capycolor))


@dislash.cooldown(1, 30, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@dislash.bot_has_guild_permissions(send_messages = True, read_messages = True)
@inter_client.slash_command(
    description="Toogles the capybara pics sending."
)
async def capybara(ctx):
    toggle = await bot.db.fetch("SELECT toggle FROM capypics     WHERE guild_id = $1", ctx.guild.id)
    toggle = toggle[0].get("toggle")

    if  toggle == "On":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "Off", ctx.guild.id)
        await ctx.respond(embed = discord.Embed(title = "Capybara pics are off.", color = capycolor))

    if toggle == "Off":
        await bot.db.execute("UPDATE capypics SET toggle = $1 WHERE guild_id = $2", "On", ctx.guild.id)
        await ctx.respond(embed = discord.Embed(title = "Capybara pics are on.", color = capycolor))


@dislash.cooldown(1,5, type=commands.BucketType.user)
@dislash.bot_has_guild_permissions(send_messages = True, read_messages = True)
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
        await inter.respond(embed = discord.Embed(title = "You didn't enter any text to translate.", color = capycolor))   


@dislash.cooldown(1,5, type=commands.BucketType.user)
@dislash.bot_has_guild_permissions(send_messages = True, read_messages = True)
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
            await inter.respond(embed = discord.Embed(title = f"{lang_code} is  **{language}**", color = capycolor))  

        elif len(str(language)) > 2:
            lang_code = googletrans.LANGCODES[str(language)]
            await inter.respond(embed = discord.Embed(title = f"{language} is  **{lang_code}**", color = capycolor))  

    elif language is None:
        await inter.respond(embed = discord.Embed(title = "You need to enter the language.", color = capycolor))

    else:
        await inter.respond(embed = discord.Embed(title = "Your language isn't on the list.", color = capycolor))


@dislash.cooldown(1, 30, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@dislash.bot_has_guild_permissions(send_messages = True, read_messages = True)
@inter_client.slash_command(
    description="Pings a user and deletes a message.",
    options=[
        Option("user", "User your want to ping.", OptionType.USER),
    ]
)
async def ping(inter, user:discord.User = None): #pings the user and immediately deletes the message
    if user is not None:
        await inter.send(f'{user.mention}', delete_after=0)

    else:
        await inter.respond(embed = discord.Embed(title = "You didn't enter the nickname.", color = capycolor))


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(administrator = True)
@dislash.bot_has_permissions(send_messages = True, read_messages = True, manage_messages = True)
@inter_client.slash_command(
    description="Deletes messages by amount. (10 by default)",
    options=[
        Option("amount", "The amount of messages you want to delete.", OptionType.INTEGER),
    ]
)
async def clear(ctx, amount = 10): #deletes messages
    if amount == 10:
        await ctx.channel.purge(limit=10)
        await ctx.send(embed = discord.Embed(title = "10 messages are deleted.", color = capycolor))

    elif (amount >= 1) and (amount <= 50):
        await ctx.channel.purge(limit=amount)
        await ctx.send(embed = discord.Embed(title = f"{amount} messages are deleted.", color = capycolor))

    elif amount > 50:
        await ctx.send(embed = discord.Embed(title = "Message clear limit is 50.", color = capycolor))


@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(ban_members=True)
@dislash.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
@inter_client.slash_command(
    description="Bans a user.",
    options=[
        Option("member", "User you want to ban.", OptionType.USER),
        Option("reason", "Ban reason.", OptionType.STRING)
    ]
)
async def ban(inter: ContextMenuInteraction,  member:discord.Member = None, reason: str = "one good reason"):
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

    em_m = discord.Embed(title = f"You have been banned from {inter.guild.name}", color = capycolor)
    em_m.add_field(name = "Reason", value = f"**{reason}**")
    await member.send(embed = em_m)

    em = discord.Embed(title = f"{member.mention} is terminated.", color = capycolor)
    em.add_field(name = "Reason", value = f"**{reason}**")
    await inter.respond(embed = em)



@dislash.cooldown(1, 5, commands.BucketType.user)
@dislash.has_permissions(ban_members=True)
@dislash.bot_has_permissions(send_messages = True, read_messages = True, ban_members = True)
@inter_client.slash_command(
    description="Unbans a user.",
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


@dislash.cooldown(1,5, commands.BucketType.user)
@dislash.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@dislash.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
@inter_client.slash_command(
    description="Mutes a user.",
    options=[
        Option("member", "User you want to mute.", OptionType.USER),
        Option("reason", "Reason of the mute.", OptionType.STRING),
        Option("time", "Time you want to set the mute in format: 1s, 2m, 3h, 4d.", OptionType.STRING),
    ]
)
async def mute(ctx, member: discord.Member = None, reason: str = "one good reason", time = None):
    perms = discord.Permissions(speak = False, send_messages = False, read_message_history = False, read_messages = False)
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")

    if not muted_role:
        muted_role = await ctx.guild.create_role(name = "Muted")
    
    await muted_role.edit(permissions = perms)

    if member is None:
        await ctx.send(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))
        
    elif  member is not None:
        if time is not None:
            args = time.lower()
            matches = re.findall(time_regex, args)
            time = 0
            for v, k in matches:
                time += time_dict[k]*float(v)

            em_m = discord.Embed(title = f"You were muted from {ctx.guild.name}", color = capycolor)
            em_m.add_field(name = "Reason", value = f"{reason}")
            em_m.add_field(name = "Time", value = f"{round(time)}s")

            await member.send(embed = em_m)

            em = discord.Embed(title = f"Muted {member}.", color = capycolor)
            em.add_field(name = "Reason", value = f"{reason}")
            em.add_field(name = "Time", value = f"{round(time)}s")

            await ctx.send(embed = em)

            await asyncio.sleep(time)
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

@dislash.cooldown(1,5, commands.BucketType.user)
@dislash.has_permissions(manage_roles = True, ban_members = True, manage_permissions = True)
@dislash.bot_has_permissions(send_messages = True, read_messages = True, manage_roles = True, manage_messages = True, manage_permissions = True)
@inter_client.slash_command(
    description="Unmutes a user.",
    options=[
        Option("member", "User you want to mute.", OptionType.USER),
    ]
)
async def unmute(ctx, member: discord.Member = None):
    muted_role = discord.utils.get(ctx.guild.roles, name  = "Muted")
    
    if member is not None:
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(embed = discord.Embed(title = f"{member} is unmuted.", color = capycolor))

        elif muted_role not in member.roles:
            await ctx.send(embed = discord.Embed(title = f"{member} is not muted.", color = capycolor))


    if member is None:
        await ctx.send(embed = discord.Embed(title = f"You need to enter the username as argument.", color = capycolor))


@dislash.cooldown(1,5, commands.BucketType.user)
@dislash.bot_has_permissions(send_messages = True, read_messages = True)
@inter_client.slash_command(
    description="Sends avatar of user",
    options=[
        Option("member", "User you want to get an avatar from.", OptionType.USER),
    ]
)
async def avatar(inter, member: discord.Member = None):
    if member is None:
        member = inter.author

        em = discord.Embed(color = capycolor)
        em.set_image(url = member.avatar_url)
        em.set_footer(text = f"Avatar from {member}")

        await inter.respond(embed = em)

    elif member is not None:
        em = discord.Embed(color = capycolor)
        em.set_image(url = member.avatar_url)
        em.set_footer(text = f"Avatar from {member}")

        await inter.respond(embed = em)

#help slash command
@dislash.cooldown(1, 5, commands.BucketType.guild)
@dislash.bot_has_permissions(send_messages = True, read_messages = True)
@inter_client.slash_command(
    description="Has subcommands",
    options=[
        Option(
            "command",
            description="Choose command to get information about it.",
            type=OptionType.STRING,
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
    ]
)
async def help(inter: SlashInteraction, command: str = None):
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", inter.guild.id)
    prefix = prefix[0].get("prefix")

    if command == None:
        em = discord.Embed(title = "Help", description = f"Use **{prefix}help <command>** to get more information on a command. ", color = capycolor)

        em.add_field(name = "Translation", value = "**translate, treply, language, languages_list**")
        em.add_field(name = "Capybara and tools", value = "**capybara, avatar**")
        em.add_field(name = "Bot commands", value = "**prefix, clear, ping, ban, unban, mute, unmute**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "translate":
        em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}translate <'sentence'> ['(sourse language)'] ['(destination language)']**")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "language":
        em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}languages <('english' for code) or] ('en' for language)>**")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list**.")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "languages_list":
        for l in googletrans.LANGUAGES.values():
            lang_list.append(l)

        em = discord.Embed(title = "languages_list", description = "\n".join(lang_list), color = capycolor)

        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)
    
    elif command == "treply":
        em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}treply [d='(destination language)'] [s='(sourse language)']**")
        em.add_field(name = "Default languages", value = "The defaults are:\n • Auto source language \n • English as a destination language")
        em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a **{prefix}help languages_list** or use a **{prefix}language** to get a language code.")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "capybara":
        em = discord.Embed(title = "capybara", description = "Toogles On and Off on your capybara pics dispenser.", color = capycolor)

        em.add_field(name = "Syntax", value = f"{prefix}capybara")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)
    
    elif command == "prefix":
        em = discord.Embed(title = "prefix", description = "Changes your server prefix.", color = capycolor)
            
        em.add_field(name = "Syntax" , value = f"**{prefix}prefix '<new_prefix>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
            
        await inter.respond(embed = em)

    elif command == "clear":
        em = discord.Embed(title = "clear", description = "Deletes messages. Standart amount is **10**, but you can set up to **50**.", color = capycolor)
            
        em.add_field(name = "Syntax", value = f"**{prefix}clear [amount]**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
            
        await inter.respond(embed = em)
    
    elif command == "ping":
        em = discord.Embed(title = "ping", description = "Pings a user and deletes the messages after, making it a ghost ping.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}ping '<user (without #(discriminator))>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await inter.respond(embed = em)

    elif command == "ban":
        em = discord.Embed(title = "ban", description = "Bans a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}ban '<user (can be without #(discriminator))>' '<reason>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await inter.respond(embed = em)
    
    elif command == "unban":
        em = discord.Embed(title = "unban", description = "Unbans a user.", color = capycolor)

        em.add_field(name = "Syntax", value = f"**{prefix}unban '<user (with #(discriminator))>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "mute":
        em = discord.Embed(title = "mute", description = "Mutes a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}mute '<user>' '<reason>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)

    elif command == "unmute":
        em = discord.Embed(title = "unmute", description = "Unmutes a user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}unmute '<user>'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")
        
        await inter.respond(embed = em)

    elif command == "avatar":
        em = discord.Embed(title = "avatar", description = "Gets avatar from user.", color = capycolor)
        
        em.add_field(name = "Syntax", value = f"**{prefix}avatar '[user]'**")
        em.add_field(name = "Slash", value = "You can use slash alternative of that command.")

        await inter.respond(embed = em)
    
    else:
        await inter.respond(embed = discord.Embed(title = f"There's no {prefix}help for this command.", color = capycolor))


#on_message use
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

bot.loop.run_until_complete(create_db_pool()) #database requests in loop
bot.run(TOKEN)
