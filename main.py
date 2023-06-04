import discord
import csv
import time
import threading
from dhooks import Webhook, Embed
import os
import asyncio
import websockets
from htmlbuilder import parsehtml
import re
import io
import requests
from sklearn.neural_network import MLPClassifier
import pickle
from PIL import Image, ImageOps
import numpy as np
from imagelib import imageRandomizer


# Opening miniscule text file as webhook link for security
webhook = Webhook(open('offboardwebhook','r').read())
# Opening miniscule text file as token for security
TOKEN = open('offboardtoken','r').read()

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# This will store preferences for the bot, the 'preferences' dictionary below is a temporary global list of settings
# It reads from config.csv at every start-up, and can be modified on the fly with commands
Preferences = {}


@client.event
async def on_ready():
    print(f"{client.user} connected.")
    def threadedwebsock():
        # websocket which gets called by localhost on port 8765 so that HTML page can send kick requests
        # Guess this could have been done with JavaScript / TypeScript on NodeJS or something, but this helps to keep
        # A log of what's going on in the discord bot
        async def websock(websocket):
            try:
                usersid = await websocket.recv()
                usertokick = await client.fetch_user(usersid)
                await discord.Guild.kick(self=await client.fetch_guild(int(Preferences['GuildID'])), user=usertokick)
                print(f"Kicked {usertokick.name}")
            except AttributeError:
                print("This user isn't in the server.")

        async def webrun():
            async with websockets.serve(websock, "localhost", 8765):
                await asyncio.Future()

        asyncio.create_task(webrun())
    t1 = threading.Thread(target=threadedwebsock)
    t1.run()

    # Establish settings with saved preferences in config.csv
    try:
        with open('config.csv', 'r') as configcsv:
            csvHeader = csv.reader(configcsv)
            for item in csvHeader:
                if item != ['Setting', 'Value']:    # Skipping over the headers
                    Preferences.update({item[0]: item[1]})
    except FileNotFoundError:
        print('# Config.csv not found, creating')
        with open('config.csv', 'w') as configcsv:
            # Write something so it at least has somewhere to look, PLEASE FILL THIS IN!!!
            configcsv.write('Setting,Value\nCommandSymbol,!\nStaffChannel,nil\nStaffRole,nil\nBotStaffChannel,nil\nOwnerRoleID,nil\nGuildID,nil\nMutedRole,nil\nAviTimer,15')
            print('# Config successfully created, appended command symbol to list, default c!')

        # Re-establishing the current session's preferences, since this can't be done from write-mode
        with open('config.csv','r') as configcsv:
            csvHeader = csv.reader(configcsv)
            for item in csvHeader:
                if item != ['Setting', 'Value']:
                    Preferences.update({item[0]: item[1]})

    if not os.path.exists("./users/"):
        os.makedirs(f"./users/")

    async def rebuildusers():
        for i in client.guilds:
            if i.id == int(Preferences["GuildID"]):
                for member in i.members:
                    if not os.path.exists(f"./users/{member.id}/"):
                        os.makedirs(f"./users/{member.id}/")
                        with open(f"./users/{member.id}/avatar.txt", 'w') as file:
                            file.write(member.avatar.key)
                        with open(f"./users/{member.id}/display.txt", 'w') as file:
                            file.write(member.display_avatar.key)

                        # This will need to be re-written IT WAS NOT GOOD!!!

                        # Do machine learning thing
                        # memberavireq = requests.get(member.avatar.url).content
                        # tempmemb = io.BytesIO(memberavireq)
                        # outim = imageRandomizer(tempmemb).reshape(1,-1)/255
                        # modelres = MLModel.predict(outim)
                        # if modelres[0] == 1:
                        #     await createhtmlofuser(member.id)
                        #     print(f"User {member.name} seems nazi pfp?")
                        # with Image.open(tempmemb) as imagefile:
                        #     imagefile = ImageOps.grayscale(imagefile)
                        #     imagefile = imagefile.resize((32,32))
                        #     img = np.asarray(imagefile.getdata()).reshape(1,-1) * 0.003921568627451
                        #     modelres = MLModel.predict_proba(img)
                        #     print(f"User {member.name} is class: {modelres}")

                    if os.path.exists(f"./users/{member.id}/avatar.txt"):
                        with open(f'./users/{member.id}/avatar.txt', 'r') as file:
                            line = file.read()
                            if line == str(member.avatar.key):
                                pass
                            else:
                                print(f"{member.name} updated avatar pic")
                                # Do the comparison machine learning thing
                                pass
                        with open(f"./users/{member.id}/display.txt", 'r') as file:
                            line = file.read()
                            if line == str(member.display_avatar.key):
                                pass
                            else:
                                print(f"{member.name} updated display pic")
                                # Do the comparison machine learning thing
                                pass
                    with open(f"./users/{member.id}/avatar.txt", 'w') as file:
                        file.write(member.avatar.key)
                    with open(f"./users/{member.id}/display.txt", 'w') as file:
                        file.write(member.display_avatar.key)
        return

    # Can't even begin to remember what this was for

    # async def sctn():
    #     while 1:
    #         await rebuildusers()
    #         # time.sleep(int(Preferences['AviTimer']))
    #         await asyncio.sleep(int(Preferences['AviTimer']))

    # await sctn()

    # def getmachine(useravi:discord.Member.avatar.):
    #     with Image.open(useravi)

@client.event
async def on_member_join(member):
    sendToStaff = client.get_channel(int(Preferences['StaffChannel']))
    # Checking new-joins if they have any slurs in their username
    with open('swearList.csv', 'r') as swearlist:
        header = csv.reader(swearlist)
        for item in header:
            if str(item[0]) in str(member).lower():
                await discord.Guild.ban(self= await client.fetch_guild(Preferences['GuildID']),user=member)
                await sendToStaff.send(f'User <@{member.id}> auto-banned, tried joining with off-limits name {member}. ID: {member.id}')
                # The embed and variables below just set up the webhook to post in staff channel
                image = 'https://cdn-icons-png.flaticon.com/128/2505/2505264.png'
                embed = Embed(timestamp='now')
                embed.set_thumbnail(url=image)
                embed.set_title(title=f'{client.user} has auto-banned:')
                embed.add_field(name=f'{member.name}', value=f'{member.id}')
                embed.add_field(name="Reason for ban: ", value=f"auto-ban for inappropriate name on join ({member.name})")
                webhook.send(embed=embed)
                # Breaking the for loop early if it finds something, just to be a little more efficient
                break

@client.event
async def on_member_update(before,after):
    sendToStaff = client.get_channel(int(Preferences['StaffChannel']))
    with open('swearList.csv', 'r') as swearlist:
        header = csv.reader(swearlist)
        for item in header:
            # This checks if the user has staff, this prevents malicious staff from using change nickname to kick/ban other
            # Staff members
            if str(item[0]) in str(after.name).lower() or str(item[0]) in str(after.display_name).lower() and str(Preferences['StaffRole']) not in str(before.roles):
                await sendToStaff.send(
                    f'User <@{before.id}> auto-kicked, tried changing nick/display name to "{after.display_name}". ID: {after.id}')
                # The embed and variables below just set up the webhook to post in staff channel
                image = 'https://cdn-icons-png.flaticon.com/128/1/1928.png'
                embed = Embed(timestamp='now')
                embed.set_thumbnail(url=image)
                embed.set_title(title=f'{client.user} has kicked:')
                embed.add_field(name=f'{before.name}', value=f'{before.id}')
                embed.add_field(name="Reason for kick: ", value=f"auto-kick for inappropriate name change ({after.display_name})")
                webhook.send(embed=embed)
                await discord.Guild.kick(self= await client.fetch_guild(int(Preferences['GuildID'])),user=after)
                break


@client.event
async def on_message(message):
    # Establishing Quality of Life variables from message functions
    username = str(message.author)
    user_message = str(message.content)
    channel_posted = str(message.channel.name)
    try:
        sendToStaff = client.get_channel(int(Preferences['StaffChannel']))
    except ValueError:
        # the config file is probably wrong, no spaces please!
        await message.channel.send('Someone updated staff channel incorrectly, use only numbers')
        Preferences['StaffChannel'] = 0
    now = int(time.time())
    try:
        message_embed = str(message.attachments[0].url)
    except IndexError:
        message_embed = 'no_embed'

    # This is an Auto-Deleter that removes any of the swears in the swearList.csv
    # You can expand upon this, it's quite inefficient as it goes through every word in a message
    # It has some words already in it, if you want to add a word that's typically used in the middle of other words
    # You can add a space to it in the swearList, the method below will check for the word + one space

    with open('swearList.csv', 'r') as swearlist:
        header = csv.reader(swearlist)
        if message.author != client.user:
            try:
                if (str(Preferences['StaffRole']) not in str(message.author.roles)):
                    for x in header:
                        for word in message.content.split():
                            if str(x[0]) in f"{str(word).lower()} ":
                                await sendToStaff.send(f'User <@{message.author.id}> posted restricted content: {user_message}')
                                await message.channel.purge(limit=1)
                                if str(Preferences['MutedRole']) not in str(message.author.roles):
                                    targetserver = await client.fetch_guild(int(Preferences['GuildID']))
                                    mutedrole = discord.Guild.get_role(targetserver,int(Preferences['MutedRole']))
                                    await message.author.add_roles(mutedrole)
                                    image = 'https://findicons.com/files/icons/770/token_dark/256/mute.png'
                                    embed = Embed(timestamp='now')
                                    embed.set_thumbnail(url=image)
                                    embed.set_title(title=f'{client.user} has muted:')
                                    embed.add_field(name=f'{message.author}', value=f'{message.author.id}')
                                    embed.add_field(name="Reason for mute: ",
                                                    value=f"Said: {message.content}")
                                    webhook.send(embed=embed)
                                break
            except AttributeError:
                pass



    # Storing messages for msg history in 'msgHistory.csv'
    # Try/Except block just checks if file exists and fills the CSV parameters
    try:
        with open('msgHistory.csv','r') as testmsg:
            pass
    except FileNotFoundError:
        print('# msgHistory not found, establishing real quick')
        with open('msgHistory.csv','w') as msghistory:
            msghistory.writelines('username,user_id,channel_posted,user_message,message_embed,unix_time\n')
    with open('msgHistory.csv', 'a') as msghistory:
        # protecting against intentional / unintentional csv injection
        usernamereplace = username.replace(",","").replace('"',' ')
        usermessagereplace = user_message.replace(","," ").replace('"',' ')
        msghistory.writelines(f'{usernamereplace},{message.author.id},{channel_posted},{usermessagereplace},{message_embed},{now}\n')

    # Print all messages sent, who sent them, and where they were sent, first checks for an embed link
    try:
        print(f"{username} posted in {channel_posted}: \n\t\"{user_message} \t{message_embed}\"")
    except IndexError:
        print(f"{username} posted in {channel_posted}: \n\t\"{user_message}")

    async def botCommand(usermessage,elevatedprivs=False):
        # This will check if the first two characters are equal to the defined command symbol
        commandchoice = str(usermessage.split(' ',1)[0]).split('c!')[1]

        # First checking if user calling command has the staff-role provided in Preferences
        if str(Preferences['StaffRole']) in str(message.author.roles):
            if commandchoice == 'kick':
                try:
                    # Separating command choice and the info provided to it
                    commandinfo = usermessage.split(' ', 1)[1]
                except IndexError:
                    await message.channel.send('User to kick must be provided')
                try:
                    # Getting the name, the translate will remove the <@> stuff surrounding an @ member call
                    parsename = int((commandinfo).split(" ")[0].translate({ord(i):None for i in '<@>'}))
                    try:
                        reason = str(commandinfo.split(" ",1)[1])
                    except IndexError:
                        reason = 'None'
                    # Setting up a few variables to keep track of where the calls are being made
                    target = await client.fetch_user(parsename)
                    targetserver = await client.fetch_guild(int(Preferences['GuildID']))
                    try:
                        currenttarget = await discord.Guild.fetch_member(targetserver,parsename)
                    except:
                        await message.channel.send("User not in server")
                        return
                    # Checking if person being kicked has staff-role
                    if str(Preferences['StaffRole']) not in str(currenttarget.roles):
                        await message.channel.purge(limit=1)
                        await discord.Guild.kick(self=targetserver,user=target,reason=reason)
                        await sendToStaff.send(f"{target} ID: {target.id}, kicked by {message.author} from {targetserver} at <t:{now}:f> for {reason}")
                        # The embed and variables below just set up the webhook to post in staff channel
                        image = 'https://cdn-icons-png.flaticon.com/128/1/1928.png'
                        embed = Embed(timestamp='now')
                        embed.set_thumbnail(url=image)
                        embed.set_title(title=f'{message.author} has kicked:')
                        embed.add_field(name=f'{target.name}',value=f'{target.id}')
                        embed.add_field(name="Reason for kick: ",value=f'{reason}')
                        webhook.send(embed=embed)
                    else:
                        await message.channel.send('User has staff-role')
                        return
                # UnboundLocalError catches error potentially caused by parsename not being able to reach commandinfo
                # This is caused if you don't give a user to kick, it won't be able to make a commandinfo, and will pass
                # on the entire command as to not cause a traceback
                except UnboundLocalError:
                    pass
                return
            if commandchoice == 'ban':
                try:
                    # Separating command choice and the info provided to it
                    commandinfo = usermessage.split(' ', 1)[1]
                except IndexError:
                    await message.channel.send('User to ban must be provided')
                try:
                    # Getting the name, the translation will remove the <@> stuff surrounding an @ member call
                    parsename = int((commandinfo).split(" ")[0].translate({ord(i):None for i in '<@>'}))
                    try:
                        reason = str(commandinfo.split(" ",1)[1])
                    except IndexError:
                        reason = 'None'
                    # Setting up a few variables to keep track of where the calls are being made
                    target = await client.fetch_user(parsename)
                    targetserver = await client.fetch_guild(int(Preferences['GuildID']))
                    try:
                        currenttarget = await discord.Guild.fetch_member(targetserver,parsename)
                    except:
                        await discord.Guild.ban(self=targetserver, user=target, reason=reason, delete_message_days=3)
                        await message.channel.send("User not in server, applied ban anyway")
                        image = 'https://cdn-icons-png.flaticon.com/128/2505/2505264.png'
                        embed = Embed(timestamp='now')
                        embed.set_thumbnail(url=image)
                        embed.set_title(title=f'{message.author} has banned:')
                        embed.add_field(name=f'{target.name}',value=f'{target.id}')
                        embed.add_field(name="Reason for ban: ",value=f'{reason}')
                        webhook.send(embed=embed)
                        return
                    # Checking if person being banned has staff-role
                    if str(Preferences['StaffRole']) not in str(currenttarget.roles):
                        await message.channel.purge(limit=1)
                        await discord.Guild.ban(self=targetserver,user=target,reason=reason,delete_message_days=3)
                        await sendToStaff.send(f"{target} ID: {target.id}, kicked by {message.author} from {targetserver} at <t:{now}:f> for {reason}")
                        # The embed and variables below just set up the webhook to post in staff channel
                        image = 'https://cdn-icons-png.flaticon.com/128/2505/2505264.png'
                        embed = Embed(timestamp='now')
                        embed.set_thumbnail(url=image)
                        embed.set_title(title=f'{message.author} has banned:')
                        embed.add_field(name=f'{target.name}',value=f'{target.id}')
                        embed.add_field(name="Reason for ban: ",value=f'{reason}')
                        webhook.send(embed=embed)
                    else:
                        await message.channel.send('User has staff-role')
                        return
                # UnboundLocalError catches error potentially caused by parsename not being able to reach commandinfo
                # This is caused if you don't give a user to kick, it won't be able to make a commandinfo, and will pass
                # on the entire command as to not cause a traceback
                except UnboundLocalError:
                    pass
                return


            # Simple mass message culler to remove a large amount of messages, i.e. when a raid happens
            if commandchoice == 'purge':
                try:
                    MessagesToCull = int(usermessage.split(' ', 1)[1]) + 1
                    if MessagesToCull > 150:
                        await message.channel.send('Thats a lot of messages, reduce to less than 150')
                        return
                except IndexError:
                    await message.channel.send('Need numerical value of messages to purge')
                except ValueError:
                    await message.channel.send('Value given was alphanumerical, must be a number (1,2,3)')
                # Catching error if above statements isolate messagetocull
                try:
                    await message.channel.purge(limit=MessagesToCull)
                except UnboundLocalError:
                    pass
                return
            if commandchoice == 'update' and elevatedprivs == True:
                try:
                    commandinfo = usermessage.split(' ', 1)[1]
                    if commandinfo.split(" ")[1].isupper() or commandinfo.split(" ")[1].islower():
                        await message.channel.send('Only numerical ID allowed')
                        return
                except IndexError:
                    await message.channel.send('You need to give a value to update')
                try:
                    Preferences[commandinfo.split(" ")[0]] = commandinfo.split(" ")[1]
                    with open('config.csv', 'w') as configcsv:
                        configcsv.writelines("Setting,Value\n")
                        for x,y in Preferences.items():
                            configcsv.writelines(f"{x},{y}\n")
                    newstaff = client.get_channel(id=int(commandinfo.split(" ")[1]))
                    await message.channel.send(f'{commandinfo.split(" ")[0]} updated to: {newstaff.name}')
                except UnboundLocalError:
                    pass
                return
            elif elevatedprivs == False:
                await message.channel.send('Insufficient Privileges')
                return
        elif str(Preferences['StaffRole']) not in str(message.author.roles):
            if commandchoice == "kick" or commandchoice == "purge":
                await message.channel.send('You need to be staff to do that')
                return

        # Role command will return all roles a given user has, this was helpful for development
        if commandchoice == 'role' or commandchoice == 'roles':
            try:
                commandinfo = usermessage.split(' ', 1)[1]
            except IndexError:
                await message.channel.send('User-id required')

            # This is the same concept as above, catching the error caused by not providing a user-id
            try:
                parsename = int((commandinfo).split(" ")[0].translate({ord(i): None for i in '<@>'}))
                targetserver = await client.fetch_guild(guild_id=int(Preferences['GuildID']))
                currenttarget = await discord.Guild.fetch_member(self=targetserver, member_id=parsename)
                await message.channel.send(str(currenttarget.roles).replace('@','').replace(',','%'))
            except UnboundLocalError:
                pass
            return

        async def createhtmlofuser(userid):
            for i in client.guilds:
                if i.id == int(Preferences['GuildID']):
                    alltheusermsg = []
                    for x in i.channels:
                        if type(x) == discord.channel.TextChannel:
                            # There HAS to be a better way to do this
                            messages = [[message.created_at,
                                         re.sub(",|\.|-|=|`|\[|\]|;|'|/|\{|\}|\\\\|\||:\"|>", "", message.content) or
                                         message.attachments[0].url] async for message in x.history(limit=50) if
                                        message.author.id == userid]
                            try:
                                alltheusermsg.extend(messages)
                                # print(str(messages[0][1]).replace("'","quote").replace('"',"quote"))
                            except IndexError as e:
                                print(e)
                    last50 = sorted(alltheusermsg, reverse=True)[:49]
                    last50formatted = []
                    userobject = client.get_user(userid)
                    for i in last50:
                        last50formatted.append([i[0].strftime("%m/%d/%Y, %H:%M:%S"), i[1]])
                    parsehtml(last50formatted, userid, userobject.name,
                              userobject.created_at.strftime("%m/%d/%Y, %H:%M:%S"), userobject.avatar.url)
                    print("Succesfully made html")

        if commandchoice == 'htmlall':
            for guild in client.guilds:
                if guild.id == int(Preferences['GuildID']):
                    for member in guild.members:
                        await createhtmlofuser(member.id)
                    await message.channel.send("Completed all HTML")

        else:
            await message.channel.send('Unfamiliar with command')
        return


    if message.content[0:2].lower() == Preferences['CommandSymbol']:
        # TODO: implement simple commands
        if str(Preferences['OwnerRoleID']) in str(message.author.roles):
            await botCommand(message.content, elevatedprivs=True)
        else:
            await botCommand(message.content)
        pass

client.run(TOKEN)
