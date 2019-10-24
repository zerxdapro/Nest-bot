import discord
from discord.ext import commands
from helpers import globe
from keys import BOT_TOKEN

# import gs_handler as gsh

bot = commands.Bot(command_prefix="/", case_insensitive=True, owner_id=349070664684142592)

cogs = ["basic", "moderation", "rules", "audit", "member", "pin", "invites", "public", "help", "users", "temp", "bday",
        "tickets"]


@bot.event
async def on_ready():
    startup = bot.user.name + " is running"
    print(startup)
    print("-"*len(startup))

    # Set activity for member count
    count = len([x for x in bot.get_guild(globe.serv_id).members if not x.bot])
    status = f"{count} members!"
    await bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))

    # Import all the commands
    bot.remove_command('help')
    for i in cogs:
        print("Loading extension: " + i)
        bot.load_extension("cogs." + i)

    # Grab the invites for logging
    invites = bot.get_cog("Invites")
    if not invites:
        print("-------error loading invites---------")
    else:
        await invites.setup()

    """
    gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])

    # resume timers

    with open("timers.csv", "r") as file:
        reader = csv.reader(file, delimiter=",")
        reader = list(reader)
        for i in reader[1:]:
            server = bot.get_guild(serv_id)
            channel = server.get_channel(int(i[2]))
            try:
                message = await channel.fetch_message(int(i[1]))
                author = server.get_member(int(i[0]))
                inp_time = dt.strptime(i[3], '%Y-%m-%d %H:%M:%S.%f')
                time = (inp_time - dt.now()).total_seconds()
                if time <= 0:
                    reader.remove(i)
                    embed = message.embeds[0]
                    new_embed = discord.Embed(title=embed.title, colour=embed.colour, description="Timer is up!")
                    await message.edit(embed=new_embed)
                else:
                    bot.loop.create_task(timer_loop(time, message, author))
            except discord.NotFound:
                pass

    header = ['Author', 'Message', 'Channel', 'Time']
    with open('timers.csv', 'wt') as f:
        csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        csv_writer.writerow(header)  # write header
        csv_writer.writerows(reader[1:])

    # end timers
    """


@bot.command()
@commands.is_owner()
async def kidnap(ctx, user: discord.Member):
    """
    Don't ask
    """
    server = bot.get_guild(globe.serv_id)
    muted = server.get_role(globe.muted)
    channel = 625608405528215552
    channel = server.get_channel(channel)
    await user.add_roles(muted)
    await channel.set_permissions(user, read_messages=True, read_message_history=False)
    await ctx.send(f"🔫 👿 \nGet in the van kiddo {user.mention}")
    await channel.send(str(user.mention))


@bot.command()
@commands.is_owner()
async def edit(ctx, message, *, content):
    """
    Edit a message from the bot
    """
    msg = await ctx.channel.fetch_message(int(message))
    await msg.edit(content=content)


bot.run(BOT_TOKEN)
