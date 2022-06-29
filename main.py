from zlib import DEFLATED
import discord
from discord.ext import commands
import os
import random
import os.path
from decouple import config
import googletrans
import asyncpg

#getting variables
CAPY_IMAGES = config("CAPY_IMAGES") 
TOKEN = config("TOKEN")
PATH_IMAGEDATABASE = config("PATH_IMAGEDATABASE") 
PATH_PREFIX = config("PATH_PREFIX")
CAPY_BASE = config("DATABASE")
translator = googletrans.Translator()

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
] #almost all languages & some forms of rus and eng

DEFAULT_PREFIX = "!"

async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot,message)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
    if len(prefix) == 0:
        await bot.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2)", message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX
    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot, message)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(CAPY_BASE) #connecting to database
    print("Connected to database.")


bot = commands.Bot(command_prefix = get_prefix, help_command = None, activity = discord.Activity(type=discord.ActivityType.playing, name="!help"), status=discord.Status.idle)  #identity)


@bot.event
async def on_ready():
    print("{0.user} is fully operational.".format(bot)) #when the bot is loaded


@bot.command(aliases=["setpre"])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, new_prefix):
    await bot.db.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
    await ctx.send(f"The prefix was changed to: {new_prefix}")
    await ctx.guild.me.edit(nick = f"CapyBot [{new_prefix}]") 


@bot.command()
async def translate(ctx, sentence, arg1 = "", arg2 = ""): #this thing translates text to whatever you want (google translate) by any args
    if len(str(sentence)) != 0: 
        if arg1[:2] == "d=":
            dest = arg1[-2:]
            if arg2[:2] == "s=":
                src = arg2[-2:]
                translation = translator.translate(sentence, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(sentence, dest)
                await ctx.channel.send(f"{translation.text}")

        if arg1[:2] == "s=":
            src = arg1[-2:]
            if arg2[:2] == "d=":
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
async def language(ctx, lang = ""):
    if len(str(lang)) == 2:
        lang_code = googletrans.LANGUAGES[str(lang)]
        await ctx.channel.send(f"{lang}:  {lang_code}")

    elif len(str(lang)) > 2:
        lang_code = googletrans.LANGCODES[str(lang)]
        await ctx.channel.send(f"{lang}:  {lang_code}")



@bot.command()
async def treply(ctx, arg1 = "", arg2 = ""):
    if ctx.message.reference and (msg := ctx.message.reference.resolved) and isinstance(msg, discord.Message):
        if arg1[:2] == "d=":
            dest = arg1[-2:]
            if arg2[:2] == "s=":
                src = arg2[-2:]
                translation = translator.translate(msg.content, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(msg.content, dest)
                await ctx.channel.send(f"{translation.text}")

        if arg1[:2] == "s=":
            src = arg1[-2:]
            if arg2[:2] == "d=":
                dest = arg2[-2:]
                translation = translator.translate(msg.content, dest, src)
                await ctx.channel.send(f"{translation.text}")
            else:
                translation = translator.translate(msg.content, src)
                await ctx.channel.send(f"{translation.text}")

        if len(arg1) == 0 and len(arg2) == 0:
            translation = translator.translate(msg.content)
            await ctx.channel.send(f"{translation.text}")
    else:
        await ctx.send("You need to reply to an existing message.")



@bot.group(invoke_without_command = True)
async def help(ctx): # new help command
    capycolor = discord.Color.from_rgb(219, 188, 129)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "Help", description = f"Use {prefix}help <command> to get more information on a command.", color = capycolor)

    em.add_field(name = "Translation", value = "translate, treply,   language, languages_list")
    em.add_field(name = "Capybara", value = "Capybara")
    em.add_field(name = "Bot command", value = "changeprefix")

    await ctx.send(embed = em)


@help.command()
async def translate(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "translate", description = "Translates a word or a sentence.", color = capycolor)

    em.add_field(name = "Syntax", value = f"{prefix}translate <'sentence'> [s=(sourse language)] [d=(destination language)]")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a {prefix}help languages_list or use a {prefix}language to get a language code.")

    await ctx.send(embed = em)

@help.command()
async def language(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "languages", description = "Gives you a code to language or a language to a code.", color = capycolor)

    em.add_field(name = "Syntax", value = f"{prefix}languages <(|english| for code) or] (|en| for language)>")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a {prefix}help languages_list.")

    await ctx.send(embed = em)

@help.command()
async def languages_list(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)
    def supported_locales():
        return [l for l in googletrans.LANGUAGES.values()]

    em = discord.Embed(title = "languages_list", description = supported_locales(), color = capycolor)

    await ctx.send(embed = em)

@help.command()
async def treply(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "treply", description = "Translates message you replyed to.", color = capycolor)

    em.add_field(name = "Syntax", value = f"{prefix}treply [s=(sourse language)] [d=(destination language)]")
    em.add_field(name = "Additional info", value = f"You can get a list of all languages by calling a {prefix}help languages_list or use a {prefix}language to get a language code.")

    await ctx.send(embed = em)

@help.command()
async def capybara(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)

    em = discord.Embed(title = "capybara", description = "Sends you a random capybara pic.", color = capycolor)

    em.add_field(name = "Syntax", value = "Not a command, just type 'capybara' in any language (almost any language).")

    await ctx.send(embed = em)

@help.command()
async def changeprefix(ctx):
    capycolor = discord.Color.from_rgb(219, 188, 129)
    prefix = await bot.db.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", ctx.guild.id)
    prefix = prefix[0].get("prefix")

    em = discord.Embed(title = "changeprefix", description = "Changes your server prefix.", color = capycolor)

    em.add_field(name = "Syntax" , value = f"{prefix}changeprefix <new_prefix>")

    await ctx.send(embed = em)







@bot.event
async def on_message(message):
    msg = message.content

    if any(word.lower() in msg for word in capybara_words) or \
            any(word.upper() in msg for word in capybara_words) or \
            any(word in msg for word in capybara_words): #searches for words in lower, upper and Ca... - like words
        os.chdir(CAPY_IMAGES) #doesn't work without this, idk
        image = random.choice(os.listdir(PATH_IMAGEDATABASE)) #gets random image of capybara from the directory
        with open(image, 'rb') as f: # opens it
            picture = discord.File(f)
            await message.channel.send(file=picture) #sends it as a picture
         
    if "727" in msg:
        await message.channel.send("WYSI") #if sees 727 - sends WYSI

    await bot.process_commands(message)

bot.loop.run_until_complete(create_db_pool())
bot.run(TOKEN)