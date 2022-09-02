from TwitchApi import TwitchApi
from discord.ext import tasks
import discord

TOKEN = 'your token'
CHANNEL_ID = 'your channel_id'
SERVER_ID = 'your server_id'

Bot = discord.Client(intents=discord.Intents.all())
live_info = TwitchApi()

@Bot.event
async def on_ready():
    print("Ready")
    stream_notice.start()
    game = discord.Game("Namchun Bot")
    await Bot.change_presence(status=discord.Status.online, activity=game)



@tasks.loop(minutes=1)
async def stream_notice():
    channel = Bot.get_channel(CHANNEL_ID)
    live_streamer, off_streamer = live_info.run()
    print(live_streamer, off_streamer)

    if live_streamer:
        for streamer in live_streamer:
            await channel.send("@everyone")
            await channel.send("```" + streamer + " 뱅온```")
    
    if off_streamer:
        for streamer in off_streamer:
            await channel.send("```" + streamer + " 뱅종```")



@Bot.event
async def on_message(message):
    if message.content.startswith('/hello'):
        await message.channel.send('hello')



Bot.run(TOKEN)
