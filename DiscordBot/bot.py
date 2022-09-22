# Import the necessary modules for this file
import discord
import itertools
import random
import requests
import pickle

from discord.ext import tasks
from discord.ext import commands

import keep_alive
import secrets

intents = discord.Intents.all()  # Declare all intents
intents.members = True  # Allow the bot to view server members
bot = commands.Bot(command_prefix='', intents=intents)  # Create an instance of the discord client

# These are the different options for the bot status
status = itertools.cycle(['with Python 🐍', 'League 😎', 'with my food 😋', 'with Java ☕', 'with robots 🤖'])

# List of emojis to be used for the !poll command
emojis = ["\N{REGIONAL INDICATOR SYMBOL LETTER A}", "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER C}", "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER E}", "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER G}", "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER I}", "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER K}", "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER M}", "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER O}", "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER Q}", "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
          "\N{REGIONAL INDICATOR SYMBOL LETTER S}", "\N{REGIONAL INDICATOR SYMBOL LETTER T}"]


# Save an object to a local file using the pickle module
def save_data(data, filename):
    with open(filename, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


# Load a locally saved object using the pickle module
def load_object(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


# Keep track of how many messages everyone has sent
total_messages = load_object("data.pickle")


# Display a confirmation message when the bot is ready
@bot.event
async def on_ready():
    change_status.start()
    print("Your bot is ready :)")


# Every 30 seconds, change the status of the bot
@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


# Respond to specific commands here
@bot.event
async def on_message(message):
    username = str(message.author).split("#")[0]  # Extract the author's username from the message
    guild = message.guild.name

    # If the message in question was sent by this bot, ignore the message
    if message.author == bot.user:
        return

    if guild not in total_messages:
        total_messages[guild] = {}

    if username in total_messages[guild]:
        total_messages[guild][username] += 1
    else:
        total_messages[guild][username] = 1
    save_data(total_messages, "data.pickle")

    if message.content.startswith("!help"):  # Help Command #
        embed = discord.Embed(title=f"List of Possible Commands:", color=0x7289DA, timestamp=message.created_at)
        embed.add_field(name='!help', value="Produces a list of possible commands", inline=False)
        embed.add_field(name='!hello', value="AnthonyBot will respond by saying hello!", inline=False)
        embed.add_field(name='!bye', value="AnthonyBot will respond by saying goodbye!", inline=False)
        embed.add_field(name='!sunchip', value="Sends an image of a random sunchip flavor", inline=False)
        embed.add_field(name='!choose', value="Selects a random server member and pings them!", inline=False)
        embed.add_field(name='!selfdestruct', value="This command 'initiates the self destruct sequence' 😂",
                        inline=False)
        embed.add_field(name='!weather {city}', value="Sends a weather report for the specified city", inline=False)
        embed.add_field(name='!poll "{question}" "{choice 1}" "{choice 2}"...',
                        value="Creates a poll with the specified question and answer choices", inline=False)
        embed.set_footer(text=f"Requested by {message.author.name}")
        await message.channel.send(embed=embed)
    elif message.content.startswith("!stats"):
        await message.channel.send(f'{username} has sent a total of {total_messages[guild][username]} messages')
    elif message.content.startswith("!hello"):  # Hello Command #
        await message.channel.send(f'Hello {username}!')
    elif message.content.startswith("!bye"):  # Bye Command #
        await message.channel.send(f'Goodbye {username}!')
    elif message.content.startswith("!sunchip"):  # SunChip Command #
        choice = random.randint(1, 5)
        await message.channel.send(file=discord.File(f"SunchipImages/sunchips{choice}.png"))
    elif message.content.startswith("!choose"):  # Choose Command #
        random_member = random.choice(message.channel.guild.members)
        await message.channel.send(f'{random_member.mention}, I choose you!')
    elif message.content.startswith("!selfdestruct"):  # SelfDestruct Command #
        await message.channel.send('Initiating self-destruct sequence in')
        await message.channel.send('THREE...')
        await message.channel.send('TWO...')
        await message.channel.send('ONE...')
        await message.channel.send('💥')
    elif message.content.startswith("!weather"):  # Weather Command #
        city_name = str(message.content).split('weather ')[1]  # Extract the requested city name from the message
        complete_url = secrets.weather_base_url + "appid=" + secrets.weather_api_key + "&q=" + city_name
        response = requests.get(complete_url)  # Request the weather data from the full url
        x = response.json()  # Save the json response as variable 'x'
        if x["cod"] != "404":
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_fahrenheit = str(round((current_temperature - 273.15) * 1.8 + 32))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            embed = discord.Embed(
                title=f"Weather forecast - {city_name}",
                color=0x7289DA,
                timestamp=message.created_at,
            )
            embed.add_field(
                name="Description",
                value=f"**{weather_description}**",
                inline=False)
            embed.add_field(
                name="Temperature(F)",
                value=f"**{current_temperature_fahrenheit}°F**",
                inline=False)
            embed.add_field(
                name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(
                name="Atmospheric Pressure(hPa)",
                value=f"**{current_pressure}hPa**",
                inline=False)
            embed.set_footer(text=f"Requested by {message.author.name}")
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(
                f"Sorry, no results were found for the city {city_name}!")
    elif message.content.startswith("!poll"):  # Poll Command #
        message_parts = message.content.split(' "')
        question = message_parts[1]
        embed = discord.Embed(title=f"Poll - {question[:-1]}", color=0x7289DA, timestamp=message.created_at)
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
        iteration = 2
        while iteration < len(message_parts):
            letter = alphabet[iteration - 2]
            embed.add_field(name=f"{letter}) {message_parts[iteration][:-1]}",
                            value=f"vote for this option by reacting with {letter}", inline=False)
            iteration += 1
        embed.set_footer(text=f"Requested by {message.author.name}")
        embed_message = await message.channel.send(embed=embed)
        iteration = 2
        while iteration < len(message_parts):
            await embed_message.add_reaction(emojis[iteration - 2])
            iteration += 1

keep_alive.keep_alive()  # Keep the bot alive 24/7!
bot.run(secrets.bot_token)  # Activate the bot!
