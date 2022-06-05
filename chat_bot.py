import asyncio
import datetime

import pyautogui
import pyperclip
from discord.ext import commands, tasks
from discord import Client, Status, Intents, Guild
import aiocron
from config import TOKEN, SERVER_ID, CHANNEL_ID, DISCORD_USER_ID
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

                if mem.id != DISCORD_USER_ID:
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
                        content = get_today_post_res.get('content', None)
                        do_today = get_today_post_res.get('do_today', '')
                        do_yesterday = get_today_post_res.get('do_yesterday', '')

                        if content is not None:
                            # report_content = mem_id + " posted an update for Daily Standup in " + \
                            #                  today + ' : \n' + content
                            message = await genesis_channel.send(content)

                            save_new_report(user_id, channel, do_yesterday, do_today, content, message)
                    else:
                        # await bot.change_presence(status=Status.idle)
                        await channel.send('Hi! What you did since yesterday?')

                        def check(m):
                            return m.content not in ['#edit did', '#edit will', 'edit_did', 'edit_will']

                        try:
                            did_message = await bot.wait_for('message', timeout=60, check=check)
                            # print('Did: ', did_message)
                        except asyncio.TimeoutError:
                            # await channel.send('You ran out of time to answer!')
                            return
                        if did_message.author.id == mem.id:
                            await channel.send('What will you do today?')

                            try:
                                will_do_message = await bot.wait_for('message', timeout=60, check=check)
                            except Exception as ex:
                                print(ex)
                                return

                            if will_do_message.author.id == mem.id:
                                report_content = mem_id + " posted an update for Daily Standup in " + \
                                                 today + ' : \n' + 'What you did since yesterday: ' + did_message.content + '\n' + \
                                                 'What will you do today: ' + will_do_message.content
                                message = await genesis_channel.send(report_content)
                                print(message)
                                await channel.send("Yay! You sent the report")
                                save_new_report(user_id, channel, did_message, will_do_message, report_content, message)


def save_new_report(user_id, channel, did_message, will_do_message, report_content, report):
    print('Report id: ', report.id)
    data = {'user_id': user_id, 'status': 'done', 'id_channel': str(channel.id),
            'do_yesterday': did_message,
            'do_today': will_do_message, 'content': report_content,
            'message_id': str(report.id),
            'time_post': str(datetime.datetime.now())}
    post_url = 'http://127.0.0.1:8000/post'
    requests.post(url=post_url, json=data)


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

    if message.content == '#standup':
        # 0. Test command - da thanh cong
        mes = 'Da nhan duoc command standup. Co len'
        pyperclip.copy(mes)
        pyperclip.paste()
        pyautogui.hotkey('ctrl', 'v')
        # 1. Gui thong bao What you did since yesterday:
        # 2. Xu ly input cua client cho did since yesterday
        # 3. Gui thong bao What will you do today:
        # 4. Xu ly input cua client cho do today
        # 5. Xu ly logic cua content => luu db

    if message.content.startswith('edit_did'):
        content = message.content.split(' ', 1)
        msg_content, msg_id = save_or_update_post(message.author, message.channel, content[1], None,
                                                  post_type='get-reported-post-today')
        genesis_channel = bot.get_channel(CHANNEL_ID)
        msg = await genesis_channel.fetch_message(int(msg_id))
        await msg.edit(content=msg_content)
        await message.channel.send('Updated')

    if message.content.startswith('edit_will'):
        content = message.content.split(' ', 1)
        msg_content, msg_id = save_or_update_post(message.author, message.channel, None, content[1],
                                                  post_type='get-reported-post-today')
        genesis_channel = bot.get_channel(CHANNEL_ID)
        msg = await genesis_channel.fetch_message(int(msg_id))
        await msg.edit(content=msg_content)
        await message.channel.send('Updated')

    await bot.process_commands(message)


@bot.command(pass_context=True)
async def edit(ctx, *, arg):
    author = ctx.author
    channel = ctx.channel

    author_id = author.id
    url = 'http://127.0.0.1:8000/user-id?discord_user_id=' + str(author_id)
    res = requests.get(url)
    res = json.loads(res.content)
    user_id = res.get('id', None)
    do_yesterday = ''
    do_today = ''

    if user_id is not None:
        reported_url = 'http://127.0.0.1:8000/get-reported-post-today/' + str(user_id)
        reported_res = requests.get(url=reported_url)
        reported_res = json.loads(reported_res.content)
        print(reported_res)
        do_yesterday = reported_res.get('do_yesterday', '')
        do_today = reported_res.get('do_today', '')
    if arg == 'did':
        mes = 'edit_did ' + do_yesterday
        pyperclip.copy(mes)
        pyperclip.paste()
        pyautogui.hotkey('ctrl', 'v')

    if arg == 'will':
        mes = 'edit_will ' + do_today
        pyperclip.copy(mes)
        pyperclip.paste()
        pyautogui.hotkey('ctrl', 'v')


@bot.command(pass_context=True)
async def td(ctx, *, arg):
    author = ctx.author
    channel = ctx.channel

    report_content, _ = save_or_update_post(author, channel, arg, None)
    message = 'Yay! This is your report looks like for tomorrow: \n' + report_content

    await ctx.send(message)


@bot.command(pass_context=True)
async def twd(ctx, *, arg):
    author = ctx.author
    channel = ctx.channel
    report_content, _ = save_or_update_post(author, channel, None, arg)
    message = 'Yay! This is your report looks like for tomorrow: \n' + report_content

    await ctx.send(message)


def save_or_update_post(author, channel, did_message, will_do_message, post_type='get-tomorrow-post'):
    author_id = author.id
    url = 'http://127.0.0.1:8000/user-id?discord_user_id=' + str(author_id)
    res = requests.get(url)
    res = json.loads(res.content)
    print(res)
    user_id = res.get('id', None)

    if user_id is not None:
        tomorrow_post_url = 'http://127.0.0.1:8000/' + post_type + '/' + str(user_id)
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

            message_id = tomorrow_post_res.get('message_id')

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

            data = {'user_id': user_id, 'status': 'for_tomorrow', 'id_channel': str(channel.id),
                    'do_yesterday': did_message,
                    'do_today': will_do_message, 'content': report_content, 'time_post': str(datetime.datetime.now())}
            post_url = 'http://127.0.0.1:8000/post'
            post_res = requests.post(url=post_url, json=data)
            post_res = json.loads(post_res.content)
            message_id = post_res.get('message_id')

        return report_content, message_id

    return None


bot.run(TOKEN)
