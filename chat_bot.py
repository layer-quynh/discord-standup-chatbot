import asyncio
import datetime

from discord.ext import commands, tasks
from discord import Client, Status, Intents, Guild
import aiocron
from config import TOKEN, SERVER_ID, CHANNEL_ID
import _thread
import threading

intents = Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@aiocron.crontab('* * * * *')
async def cronjob1():
    for guild in bot.guilds:
        if guild.id == SERVER_ID:
            for mem in guild.members:
                if mem.bot:
                    continue
                channel = bot.get_user(mem.id)
                genesis_channel = bot.get_channel(CHANNEL_ID)
                # loop = asyncio.get_event_loop()
                # loop.create_task(send_message(channel, genesis_channel, mem))

                loop = asyncio.get_event_loop()
                t = threading.Thread(target=loop_function, args=(loop, channel, genesis_channel, mem, ))
                t.start()

                # await bot.change_presence(status=Status.idle)
                # await channel.send('Hi! What you did since yesterday?')
                #
                # try:
                #     did_message = await bot.wait_for('message', timeout=60)
                #     # print('Did: ', did_message)
                # except asyncio.TimeoutError:
                #     # await channel.send('You ran out of time to answer!')
                #     return
                # if did_message.author.id == mem.id:
                #     await channel.send('What will you do today?')
                #
                #     try:
                #         will_do_message = await bot.wait_for('message', timeout=60)
                #     except Exception as ex:
                #         print(ex)
                #         return
                #
                #     if will_do_message.author.id == mem.id:
                #         today = datetime.datetime.now().date().strftime('%d/%m/%Y')
                #         mem_id = '<@' + str(mem.id) + '>'
                #         report_content = mem_id + " posted an update for Daily Standup in " + \
                #                          today + ' : \n' + 'What you did since yesterday: ' + did_message.content + '\n' + \
                #                          'What will you do today: ' + will_do_message.content
                #         await channel.send("Yay! You sent the report")
                #         report = await genesis_channel.send(report_content)
                #         print(report.report_content)


def loop_function(loop, channel, genesis_channel, mem):
    loop.create_task(send_message(channel, genesis_channel, mem))
    # loop = asyncio.new_event_loop()
    # loop.create_task(send_message(channel, genesis_channel, mem))


async def send_message(channel, genesis_channel, mem):
    await channel.send('Hi! What you did since yesterday?')

    try:
        did_message = await bot.wait_for('message', timeout=60)
        # print('Did: ', did_message)
    except asyncio.TimeoutError:
        # await channel.send('You ran out of time to answer!')
        return
    if did_message.author.id != bot.user.id:
        if did_message.author == bot.user:
            return
        await channel.send('What will you do today?')

        try:
            will_do_message = await bot.wait_for('message', timeout=60)
        except Exception as ex:
            print(ex)
            return

        # if will_do_message.author.id == mem.id:
        today = datetime.datetime.now().date().strftime('%d/%m/%Y')
        mem_id = '<@' + str(mem.id) + '>'
        report_content = mem_id + " posted an update for Daily Standup in " + \
                         today + ' : \n' + 'What you did since yesterday: ' + did_message.content + '\n' + \
                         'What will you do today: ' + will_do_message.content
        await channel.send("Yay! You sent the report")
        report = await genesis_channel.send(report_content)
        # print(report.report_content)


def between_callback(channel, genesis_channel, mem):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(send_message(channel, genesis_channel, mem))
    loop.close()


def printt():
    print('Hello world')


@bot.event
async def on_ready():
    # print(bot.users)
    guilds = bot.guilds
    for guild in guilds:
        if guild.id == SERVER_ID:
            # for mem in guild.members:
            #     print(mem.id)
            for channel in guild.channels:
                # print("Channel: ", channel)
                if channel.name == 'channel-test':
                    print(channel.id)
                    await channel.send('Hello channel')

                # t1 = threading.Thread(target=cronjob1, args=())
                # # t2 = threading.Thread(target=printt, args=())
                # #
                # # starting thread 1
                # t1.start()
                # # starting thread 2
                # # t2.start()
                #
                # # wait until thread 1 is completely executed
                # t1.join()
                # # wait until thread 2 is completely executed
                # # t2.join()


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#
#     if message.content == 'hello':
#         string = 'Hi ' + message.author.name
#         await message.channel.send(string)
#
#     if message.content == 'bye':
#         string = 'Goodbye ' + message.author.name
#         await message.channel.send(string)
#
#     await bot.process_commands(message)


@bot.command()
async def square(ctx, arg):
    print(arg)
    await ctx.send(int(arg) ** 2)


bot.run(TOKEN)
