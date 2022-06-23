import discord
import os
import random
import os.path
from decouple import config
from googletrans import Translator

client = discord.Client()
translator = Translator()

TOKEN = config("TOKEN")


capybara_words = ["Capybara", "Capybaras", "Copybara", "Coconut Doggo",
                  "Capibara","Капибара", "Кокосовая Свинка", "Водосвинка",
                  "Кокосовая собачка",  "Водяная Собачка", "Капибары",
                  "Капибару", "Капибарой", "Капибаре", "Водная свинка",
                  "Водяная свинка", "Капибар", 'ካፕባራ', 'كابيبا',
                  'Капібара', 'ক্যাপিবারা','Campybara','Kapibara',
                  'Kapybara', 'კაპიბარა','Καπετάρι',
                  'ક capપીબરા','Cayrona', 'קפיברה', 'קפיברה', 'कैपीबारा',
                  'Calapóir','カピバラ', 'CapiSbara', 'ಬಿಲ್ಲೆ', 'Капибас',
                  '카피 바라','Капыбара','കാപ്പിബറ', 'Kopa', 'कॅपीबारा',
                  'Капбайбара', 'क्याप्बेरा', 'କ୍ୟାପିବାଡା |', 'کیپیرارا',
                  'کپیوبارا','ਕੈਪੀਬੋਰਰਾ','Цапибара', 'Campiybara', 'Capbara',
                  'ڪيپيبرا','Casybati','Капайарара', 'கேபிபரா', 'కాపిబారా',
                  'Капібара', 'کیپیبرا', 'Kapabaa', 'Nghapybara', 'קאַפּייבאַראַ',
                   'Fapu', 'Ikhonsaba'
]


@client.event
async def on_ready():
    print('{0.user} is connected'.format(client))


@client.event
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return

    if "727" in msg:
        await message.channel.send("WYSI")

    if msg.startswith("!capy Radiance"):
        await message.channel.send(
        "Radiance, blinding horizon \n The brilliant sunrise \n Thier horizons, where they seize "
        "this life \n Our children... \n Painters, they are...\n They are, the change... \n Painters..."
        )

    if any(word.lower() in msg for word in capybara_words) or \
            any(word.upper() in msg for word in capybara_words) or \
            any(word in msg for word in capybara_words):
        path = config("PATH_BASE")
        os.chdir(path)
        image = random.choice(os.listdir(path))
        with open(image, 'rb') as f:
            picture = discord.File(f)
            await message.channel.send(file=picture)



client.run(TOKEN)
