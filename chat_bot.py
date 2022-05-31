import asyncio
import datetime

from discord.ext import commands, tasks
from discord import Client, Status, Intents, Guild
import aiocron
from config import TOKEN, SERVER_ID, CHANNEL_ID

intents = Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@aiocron.crontab('* * * * *')
async def cornjob1():
    for guild in bot.guilds:
        if guild.id == SERVER_ID:
            for mem in guild.members:
                # print(mem)
                channel = bot.get_user(mem.id)
                genesis_channel = bot.get_channel(CHANNEL_ID)
                # await bot.change_presence(status=Status.idle)
                await channel.send('Hi! What you did since yesterday?')

                try:
                    did_message = await bot.wait_for('message', timeout=60)
                    # print('Did: ', did_message)
                except asyncio.TimeoutError:
                    # await channel.send('You ran out of time to answer!')
                    return
                if did_message.author.id == mem.id:
                    await channel.send('What will you do today?')

                    try:
                        will_do_message = await bot.wait_for('message', timeout=60)
                    except Exception as ex:
                        print(ex)
                        return

                    if will_do_message.author.id == mem.id:
                        today = datetime.datetime.now().date().strftime('%d/%m/%Y')
                        report_content = will_do_message.author.name + " posted an update for Daily Standup in " + \
                                         today + ' : \n' + 'What you did since yesterday: ' + did_message.content + '\n' + \
                                         'What will you do today: ' + will_do_message.content
                        await channel.send(report_content)
                        await genesis_channel.send(report_content)


@bot.event
async def on_ready():
    # print(bot.users)
    guilds = bot.guilds
    for guild in guilds:
        if guild.id == SERVER_ID:
            for mem in guild.members:
                print(mem)
            for channel in guild.channels:
                # print("Channel: ", channel)
                if channel.name == 'channel-test':
                    print(channel.id)
                    await channel.send('Hello channel')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == 'hello':
        string = 'Hi ' + message.author.name
        await message.channel.send(string)

    if message.content == 'bye':
        string = 'Goodbye ' + message.author.name
        await message.channel.send(string)

    await bot.process_commands(message)


@bot.command()
async def square(ctx, arg):
    print(arg)
    await ctx.send(int(arg) ** 2)


bot.run(TOKEN)
