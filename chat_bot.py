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

# Making html
import webbrowser
import os


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

    # if message.content == '#edit-td':

    if message.content == 'bye':
        string = 'Goodbye ' + message.author.name
        await message.channel.send(string)

    if message.content.startswith('edit_did'):
        content = message.content.split(' ', 1)
        msg_content, msg_id = save_or_update_post(message.author, message.channel, content[1], None, post_type='get-reported-post-today')
        genesis_channel = bot.get_channel(CHANNEL_ID)
        msg = await genesis_channel.fetch_message(int(msg_id))
        await msg.edit(content=msg_content)
        await message.channel.send('Updated')

    if message.content.startswith('edit_will'):
        content = message.content.split(' ', 1)
        msg_content, msg_id = save_or_update_post(message.author, message.channel, None, content[1], post_type='get-reported-post-today')
        genesis_channel = bot.get_channel(CHANNEL_ID)
        msg = await genesis_channel.fetch_message(int(msg_id))
        await msg.edit(content=msg_content)
        await message.channel.send('Updated')

    if message.content == 'edit td -ui':
        await editPost(str(message.author.id))

    if message.content == 'edit tm -ui':
        await editTomorrowPost(str(message.author.id))

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

    report_content , _= save_or_update_post(author, channel, arg, None)
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

async def editPost(author_id):
    f = open('edit-post.html', 'w')
    # the html code which will go in the file GFG.html

    backend_url = 'http://127.0.0.1:8000'
    action_url = backend_url + '/update'
# search de tra ve user_id
    res1 = requests.get(backend_url+'/user-id/'+str(author_id))
    res1 = json.loads(res1.content)
    userID = res1.get('id')

    print(author_id)
    res= requests.get(backend_url+'/get-reported-post-today/'+str(userID))
    res = json.loads(res.content)

    message_id= res.get('message_id',None)
    do_yesterday = res.get('do_yesterday',None)
    do_today = res.get('do_today',None)

    html_template = """
          <style>
          * {
            box-sizing: border-box;
            margin: 0px;
          }
          .outside-container {
            width: 500px;
            margin: auto;
            /* border: 1px red solid; */
            padding: 10px;
            background-color: rgb(147, 186, 231);
            border: 5px solid #d3e2f4;
            border-radius: 5%;
          }
          h1 {
            /* background-color: rgb(171, 131, 235); */
            margin-top: 10px;
            margin-bottom: 5px;
            text-align: center;
          }
          p {
            padding: 15px 0 15px 0;
          }
          .textarea-container {
            padding: 0 5px;
          }
          textarea {
            width: 100%;
            border: 0px;
            padding: 10px;
            border-radius: 10px;
          }
          input[type="submit"] {
            display: block;
            margin: auto;
            margin-bottom: 15px;
            width: 200px;
            height: 50px;
            border: rgb(255, 224, 168) 3px solid;
            background-color: orange;
            border-radius: 10px;
            color: rgb(68, 3, 3);
            font-weight: 900;
          }
        </style>
                """ + f"""
        <div class="outside-container">
          <h1>Author ID #{author_id}</h1>
          <h1>Edit Post #{message_id}</h1>
          <form action="{action_url}" method="post">
            <input
              type="hidden"
              name="message_id"
              id="inputMessageID"
              value="{message_id}"
            />
            <p>What did you do yesterday?</p>
            <div class="textarea-container">
              <textarea name="do_yesterday" id="inputYesterday" rows="6">{do_yesterday}</textarea>
            </div>

            <p>What will you do today?</p>

            <div class="textarea-container">
              <textarea name="do_today" id="inputToday" rows="6">{do_today}</textarea
              >
            </div>

            <br />
            <br />
            <input
              type="submit"
              value="Confirm Edit"
              style="width: 200px; height: 50px"
            />
          </form>
        </div>
        """
    # writing the code into the file
    f.write(html_template)
    # close the file
    f.close()
    # 1st method how to open html files in chrome using
    filename = 'file:///' + os.getcwd() + '/' + 'edit-post.html'
    # webbrowser.open_new_tab(filename)
    webbrowser.open(filename,new=2,autoraise=True)
    return None

async def editTomorrowPost(author_id):
    f = open('edit-tomorrow-post.html', 'w')
    # the html code which will go in the file GFG.html

    backend_url = 'http://127.0.0.1:8000'
    action_url = backend_url + '/update'
# search de tra ve user_id
    res1 = requests.get(backend_url+'/user-id/'+str(author_id))
    res1 = json.loads(res1.content)
    userID = res1.get('id')

    print(author_id)
    res= requests.get(backend_url+'/get-tomorrow-post/'+str(userID))
    res = json.loads(res.content)

    message_id= res.get('message_id',None)
    do_yesterday = res.get('do_yesterday',None)
    do_today = res.get('do_today',None)

    if message_id is None:
        print('No tomorrow standup post')
        # user_to_level_up = bot.fetch_user(author_id)  # since your user variable is an ID
        # dm_channel = user_to_level_up.dm_channel
        # if dm_channel is None:
        #     await user_to_level_up.create_dm()
        #     dm_channel = user_to_level_up.dm_channel
        # await dm_channel.send('You have not create standup for tomorrow')
        return None

    html_template = """
          <style>
          * {
            box-sizing: border-box;
            margin: 0px;
          }
          .outside-container {
            width: 500px;
            margin: auto;
            /* border: 1px red solid; */
            padding: 10px;
            background-color: rgb(147, 186, 231);
            border: 5px solid #d3e2f4;
            border-radius: 5%;
          }
          h1 {
            /* background-color: rgb(171, 131, 235); */
            margin-top: 10px;
            margin-bottom: 5px;
            text-align: center;
          }
          p {
            padding: 15px 0 15px 0;
          }
          .textarea-container {
            padding: 0 5px;
          }
          textarea {
            width: 100%;
            border: 0px;
            padding: 10px;
            border-radius: 10px;
          }
          input[type="submit"] {
            display: block;
            margin: auto;
            margin-bottom: 15px;
            width: 200px;
            height: 50px;
            border: rgb(255, 224, 168) 3px solid;
            background-color: orange;
            border-radius: 10px;
            color: rgb(68, 3, 3);
            font-weight: 900;
          }
        </style>
                """ + f"""
        <div class="outside-container">
          <h1>Author ID #{author_id}</h1>
          <h1>Edit Post #{message_id}</h1>
          <form action="{action_url}" method="post">
            <input
              type="hidden"
              name="message_id"
              id="inputMessageID"
              value="{message_id}"
            />
            <p>What will be finished today?</p>
            <div class="textarea-container">
              <textarea name="do_yesterday" id="inputYesterday" rows="6">{do_yesterday}</textarea>
            </div>

            <p>What will you do tomorrow?</p>

            <div class="textarea-container">
              <textarea name="do_today" id="inputToday" rows="6">{do_today}</textarea
              >
            </div>

            <br />
            <br />
            <input
              type="submit"
              value="Confirm Edit"
              style="width: 200px; height: 50px"
            />
          </form>
        </div>
        """
    # writing the code into the file
    f.write(html_template)
    # close the file
    f.close()
    # 1st method how to open html files in chrome using
    filename = 'file:///' + os.getcwd() + '/' + 'edit-tomorrow-post.html'
    webbrowser.open(filename,new=2,autoraise=True)
    return None


bot.run(TOKEN)
