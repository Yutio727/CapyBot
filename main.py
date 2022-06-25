from http import client
import discord
from discord.ext import commands
import os
import random
import json
import os.path
from decouple import config


CAPY_IMAGES = config("CAPY_IMAGES") 
TOKEN = config("TOKEN")
PATH_IMAGEDATABASE = config("PATH_IMAGEDATABASE") 
PATH_PREFIX = config("PATH_PREFIX")
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
    'Fapu', 'Ikhonsaba'
] #all languages & some forms of rus and eng

def get_prefix(bot, message): #getting a prefix from the f's below
    with open(PATH_PREFIX, "r") as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)] #command prefix

bot = commands.Bot(command_prefix = get_prefix) #main command

@bot.event
async def on_ready():
    print("Bot is ready") #when the bot is loaded

async def on_guild_join(guild):
    with open(PATH_PREFIX, "r") as f: #reading the prefixes to load in for the first time
        prefixes = json.load(f)

    prefixes[str(guild.id)] = "." #standart prefix to a bot

    with open(PATH_PREFIX, "w") as f:
        json.dump(prefixes, f, indent = 4) #writing a standart prefix
@bot.event
async def on_guild_remove(guild):
    with open(PATH_PREFIX, "r") as f: #deleting the prefix after bot leaves the guild
        prefixes = json.load(f)

    prefixes.pop(str(guild.id)) #deleting the prefix and id

    with open(PATH_PREFIX, "w") as f:
        json.dump(prefixes, f, indent = 4) #writing literally nothing


@bot.command()
@commands.has_permissions(administrator = True) #only admin can change the prefix
async def changeprefix(ctx, prefix): #command to change a prefix
    with open(PATH_PREFIX, "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix #changes the prefix on your guild to a prefix you've choose

    with open(PATH_PREFIX, "w") as f: #writes down the change of the prefix
        json.dump(prefixes, f, indent = 4)

    await ctx.send(f"The prefix was changed to {prefix}")

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

    #if msg.startswith("capy Radiance"):
        #await message.channel.send(
        #"Radiance, blinding horizon \n The brilliant sunrise \n Thier horizons, where they seize "
        #"this life \n Our children... \n Painters, they are...\n They are, the change... \n Painters..."
        #)
    await bot.process_commands(message)


bot.run(TOKEN)


