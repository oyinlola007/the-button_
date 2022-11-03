import discord, asyncio, webcolors, time

from pyfiglet import Figlet

import methods.config as config
import methods.utils as utils

client = discord.Client()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

global_message = None
reacted = []
in_progress = False
start_message_id = 0
pending = False
init_post_time = 0
start_time = 0


@client.event
async def on_reaction_add(reaction, user):
    global start_time
    global reacted
    try:
        if reaction.message.id == global_message.id and user.id != config.BOT_ID and in_progress and user.mention not in reacted:
            start_time = int(time.time())
            reacted.append(user.mention)
    except:
        pass

@client.event
async def on_message(message):
    global start_message_id
    global reacted
    global in_progress
    global pending
    global init_post_time
    if message.author.id == config.ADMIN_ID and str(message.channel.type) == 'private':
        if message.content == "!start":
            if not in_progress:
                reacted = []
                in_progress = True
                pending = True
                init_post_time = int(time.time())
                channel = client.get_channel(config.POST_CHANNEL)

                colour = int("0x" + webcolors.name_to_hex("purple").strip("#"), 16)
                embed=discord.Embed(description="```" + utils.render_text('the\n  button', 'slant') + "```\n\nA " + str(int(config.DURATION/60)) + "-minute countdown timer will start in " + str(config.DELAY) + " minutes time\n\nThe timer will restart whenever a user reacts to the timer with " + config.EMOJI + "\n\nEach user can only restart the timer once\n\nThe last user to react before the timer runs out wins the challenge\n\nGood luck!!!", color=colour)
                msg = await channel.send(embed=embed)
                start_message_id = msg.id

                await message.channel.send(">>> Challenge started")
            else:
                await message.channel.send(">>> Challenge currently in progress")


async def user_metrics_background_task():
    await client.wait_until_ready()
    while True:

        global pending
        global start_time
        global global_message
        global reacted
        global in_progress

        if pending:
            if int(time.time()) - init_post_time >= config.DELAY * 60:
                pending = False
                colour = int("0x" + webcolors.name_to_hex("green").strip("#"), 16)

                embed=discord.Embed(description=f"Last user to reset - None\n```{utils.convert_elapsed(config.DURATION)}```", color=colour)
                channel = client.get_channel(config.POST_CHANNEL)
                global_message = await channel.send(embed=embed)
                await global_message.add_reaction(config.EMOJI)
                start_time = int(time.time())

        elif not pending and in_progress:
            elapsed_time = int(time.time()) - start_time

            try:
                last_restart = reacted[-1]
            except:
                last_restart = "None"


            if elapsed_time <= config.DURATION:
                if elapsed_time < 45:
                    colour = "green"
                elif elapsed_time < 90:
                    colour = "yellow"
                elif elapsed_time < 135:
                    colour = "orange"
                else:
                    colour = "red"

                colour = int("0x" + webcolors.name_to_hex(colour).strip("#"), 16)
                embed=discord.Embed(description=f"Last user to reset - {last_restart}\n```{utils.convert_elapsed(elapsed_time)}```", color=colour)
                await global_message.edit(embed=embed)

            else:
                if last_restart == "None":
                    channel = client.get_channel(config.POST_CHANNEL)
                    colour = int("0x" + webcolors.name_to_hex("purple").strip("#"), 16)
                    embed=discord.Embed(description="Challenge over. There is no winner since the timer was never restarted", color=colour)
                    await channel.send(embed=embed)
                else:
                    channel = client.get_channel(config.POST_CHANNEL)
                    colour = int("0x" + webcolors.name_to_hex("purple").strip("#"), 16)
                    embed=discord.Embed(description=f"Challenge over. The winner of the challenge is {last_restart}", color=colour)
                    await channel.send(embed=embed)

                in_progress = False


        await asyncio.sleep(1)

client.loop.create_task(user_metrics_background_task())
client.run(config.DISCORD_TOKEN)



