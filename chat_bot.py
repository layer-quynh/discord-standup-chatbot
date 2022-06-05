import asyncio
import datetime

from discord.ext import commands, tasks
from discord import Client, Status, Intents, Guild
import aiocron
from config import TOKEN, SERVER_ID, CHANNEL_ID
import requests
import json

intents = Intents.all()
bot = commands.Bot(command_prefix="#", intents=intents)


@aiocron.crontab('* * * * *')
async def cronjob1():
    for guild in bot.guilds:
        if guild.id == SERVER_ID:
            for mem in guild.members:
                if mem.bot:
                    continue
                channel = bot.get_user(mem.id)
                genesis_channel = bot.get_channel(CHANNEL_ID)

                url = 'http://127.0.0.1:8000/user-id?discord_user_id=' + str(mem.id)
                res = requests.get(url)
                res = json.loads(res.content)
                user_id = res.get('id', None)
                if user_id is not None:
                    get_today_post_url = 'http://127.0.0.1:8000/get-yesterday-post/' + str(user_id)
                    get_today_post_res = requests.get(get_today_post_url)
                    get_today_post_res = json.loads(get_today_post_res.content)
                    today = datetime.datetime.now().date().strftime('%d/%m/%Y')
                    mem_id = '<@' + str(mem.id) + '>'
                    if get_today_post_res.get('id', None) is not None:
                        print(get_today_post_res)
                        content = get_today_post_res.get('content', None)
                        if content is not None:
                            # report_content = mem_id + " posted an update for Daily Standup in " + \
                            #                  today + ' : \n' + content
                            await genesis_channel.send(content)
                    else:
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
                                # today = datetime.datetime.now().date().strftime('%d/%m/%Y')
                                # mem_id = '<@' + str(mem.id) + '>'
                                report_content = mem_id + " posted an update for Daily Standup in " + \
                                                 today + ' : \n' + 'What you did since yesterday: ' + did_message.content + '\n' + \
                                                 'What will you do today: ' + will_do_message.content
                                await channel.send("Yay! You sent the report")
                                report = await genesis_channel.send(report_content)
                                print(report)
                                # msg_id = 982489394877452400
                                # message = await genesis_channel.fetch_message(msg_id)
                                # print(message)
                                # await message.edit(content="Update")


@bot.event
async def on_ready():
    # print(bot.users)
    guilds = bot.guilds
    for guild in guilds:
        if guild.id == SERVER_ID:
            for mem in guild.members:
                print(mem.id)
                url = 'http://127.0.0.1:8000/user-id?discord_user_id=' + str(mem.id)
                res = requests.get(url)
                res = json.loads(res.content)
                if res.get('id', None) is None:
                    post_url = 'http://127.0.0.1:8000/user'
                    data = {'user_name': mem.name, 'discord_user_id': str(mem.id)}
                    requests.post(url=post_url, json=data)

            for channel in guild.channels:
                # print("Channel: ", channel)
                if channel.name == 'team-genesis':
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


@bot.command(pass_context=True)
async def td(ctx, *, arg):
    author = ctx.author
    channel = ctx.channel

    report_content = save_or_update_post(author, channel, arg, None)
    message = 'Yay! This is your report looks like for tomorrow: \n' + report_content

    await ctx.send(message)


@bot.command(pass_context=True)
async def twd(ctx, *, arg):
    author = ctx.author
    channel = ctx.channel
    report_content = save_or_update_post(author, channel, None, arg)
    message = 'Yay! This is your report looks like for tomorrow: \n' + report_content

    await ctx.send(message)


def save_or_update_post(author, channel, did_message, will_do_message):
    author_id = author.id
    url = 'http://127.0.0.1:8000/user-id?discord_user_id=' + str(author_id)
    res = requests.get(url)
    res = json.loads(res.content)
    print(res)
    user_id = res.get('id', None)

    if user_id is not None:
        tomorrow_post_url = 'http://127.0.0.1:8000/get-tomorrow-post/' + str(user_id)
        tomorrow_post_res = requests.get(url=tomorrow_post_url)
        tomorrow_post_res = json.loads(tomorrow_post_res.content)
        tomorrow_post_id = tomorrow_post_res.get('id', None)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow = tomorrow.strftime('%d/%m/%Y')
        mem_id = '<@' + str(author_id) + '>'
        # report_content = mem_id + " posted an update for Daily Standup in " + \
        #                  today + ' : \n' + 'What you did since yesterday: ' + did_message + '\n' + \
        #                  'What will you do today: ' + will_do_message

        if tomorrow_post_id is not None:
            update_post_url = 'http://127.0.0.1:8000/posts/' + str(tomorrow_post_id)
            data = {}
            if did_message is not None:
                data['do_yesterday'] = did_message
            else:
                did_message = tomorrow_post_res.get('do_yesterday', '')
            if will_do_message is not None:
                data['do_today'] = will_do_message
            else:
                will_do_message = tomorrow_post_res.get('do_today', '')

            report_content = mem_id + " posted an update for Daily Standup in " + \
                             tomorrow + ' : \n' + 'What you did since yesterday: ' + did_message + '\n' + \
                             'What will you do today: ' + will_do_message

            data['content'] = report_content
            requests.put(url=update_post_url, json=data)
        else:
            if did_message is None:
                did_message = ''

            if will_do_message is None:
                will_do_message = ''

            report_content = mem_id + " posted an update for Daily Standup in " + \
                             tomorrow + ' : \n' + 'What you did since yesterday: ' + did_message + '\n' + \
                             'What will you do today: ' + will_do_message

            data = {'user_id': user_id, 'status': 'for_tomorrow', 'id_channel': str(channel.id), 'do_yesterday': did_message,
                    'do_today': will_do_message, 'content': report_content, 'time_post': str(datetime.datetime.now())}
            post_url = 'http://127.0.0.1:8000/post'
            requests.post(url=post_url, json=data)

        return report_content

    return None


bot.run(TOKEN)
