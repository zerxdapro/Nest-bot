import inspect
from discord.ext import commands
import discord
import re
from helpers import globe, image_handler
import importlib

#  :zero: :one: :two: etc
num_emoji = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷",
             "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

react_roles = [
    {"ID": 626340756315045899, "roles": {"❔": 626340292811030542}},
    {"ID": 626994531409068042, "roles": {"📲": 626993822324359168}},
    {"ID": 627743686826131456, "roles": {
        f"{3}\N{COMBINING ENCLOSING KEYCAP}": 627743939658645532,
        f"{4}\N{COMBINING ENCLOSING KEYCAP}": 627744050841387008,
        f"{5}\N{COMBINING ENCLOSING KEYCAP}": 627744064946569256,
        f"{6}\N{COMBINING ENCLOSING KEYCAP}": 627744070537838602,
        f"{7}\N{COMBINING ENCLOSING KEYCAP}": 627744098245148683,
        f"{8}\N{COMBINING ENCLOSING KEYCAP}": 627744108227854367,
        f"{9}\N{COMBINING ENCLOSING KEYCAP}": 627744138963582986,
        f"{0}\N{COMBINING ENCLOSING KEYCAP}": 627744171347935252
    }},
    {"ID": 627746527749734430, "roles": {
        "🚺": 627747612853927956,
        "🚹": 627747557463949322,
        "👤": 627747582483103744,
        "🚻": 627747640645386250
    }},
    {"ID": 627978987179868170, "roles": {
        "🌍": 627979732465745975,
        "🌎": 627979419692171294,
        "🌏": 627979487266603019,
        "🏝": 627979525241962536,
        "🏰": 627979557189713931,
        "🇺🇸": 631748587143036929
    }},
    {"ID": 632753058190852096, "roles": {"🏳️‍🌈": 632752022411673600}}
]

"""
async def timer_loop(time, message, caller):
    embed = message.embeds[0]
    loops = int(time / 60)
    if time % 60:
        loops += 1
    for i in range(loops):
        # print(time)
        await asyncio.sleep(60)
        time -= 60
        if time > 0:
            delta = dt.timedelta(seconds=time)
            desc = f"{delta.days} days, {delta.seconds // 3600 % 24} hours, {delta.seconds // 60 % 60} minutes remaining"
            if desc == "0 days, 0 hours, 0 minutes remaining":
                desc = "<1 minute remaining"
            new_embed = discord.Embed(title=embed.title, colour=embed.colour, description=desc)
            try:
                await message.edit(embed=new_embed)
            except (discord.NotFound, discord.HTTPException):
                await caller.send(f"Your `{embed.title[2:-6]}` timer got deleted")
                return
        else:
            new_embed = discord.Embed(title=embed.title, colour=embed.colour, description="Timer is up!")
            try:
                await message.edit(embed=new_embed)
            except (discord.NotFound, discord.HTTPException):
                pass
            await caller.send(f"Your `{embed.title[2:-6]}` timer is finished!")
            return
"""


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    @commands.command(aliases=["countdown"])
    @commands.check(globe.check_mod)
    async def timer(self, ctx, *, time):
        match = r"(([0-9]+) ?(days?|d))?( ?([0-9]+) ?(hours?|hrs?|h))?( ?([0-9]+) ?(minutes?|mins?|m))?"
        match = re.match(match, time, re.IGNORECASE)
        if match:
            time = [None, None, None]
            time[0] = match.group(2)
            time[1] = match.group(5)
            time[2] = match.group(8)
    
            order = ["days", "hours", "minutes"]
            raw = ""
            for i in range(len(time)):
                if not time[i]:
                    time[i] = 0
                else:
                    time[i] = int(time[i])
                raw += f"{str(time[i])} {order[i]}, "
            raw = raw[:-2]
    
            time[0] = time[0] * 86400
            time[1] = time[1] * 3600
            time[2] = time[2] * 60
            time = sum(time)
    
            result = dt.datetime.now() + dt.timedelta(seconds=time)
    
            embed = discord.Embed(title=f"⏱ {raw} timer", colour=0xe45898, description=raw + " remaining")
            message = await ctx.send(embed=embed)
    
            self.bot.loop.create_task(timer_loop(time, message, ctx.author))
            with open('data/timers.csv', 'a') as fd:
                writer = csv.writer(fd)
                writer.writerow([ctx.author.id, message.id, ctx.channel.id, result])
        else:
            raise commands.MissingRequiredArgument

    @timer.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} Your command was formatted incorrectly")
        else:
            print("other error")
            # await self.bot.owner.send(f"`{ctx.content}`\n\nCaused:\n\n```\n{error}\n```")
            raise error
    """

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_member_join(self, member):
        # Send the welcome image when people join
        cnl = member.guild.get_channel(globe.welcome_id)
        image_handler.make_welcome("welcome", member)  # saves image to image.png
        await cnl.send(str(member.mention), file=discord.File("image.png"))

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_member_remove(self, member):
        # Send the goodbye message when someone leaves
        cnl = member.guild.get_channel(globe.welcome_id)
        image_handler.make_welcome("leave", member)  # image saved to image.png
        await cnl.send(str(member.mention), file=discord.File("image.png"))

    @commands.command(aliases=["announce"])
    @commands.check(globe.check_mod)
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        """
        Send a message with the bot in that channel
        """
        await channel.send(message)

    @say.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"{globe.errorx} {error.args[0]}")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{globe.errorx} I'm not allowed to send messages there")
        else:
            raise error

    @commands.command()
    @commands.check(globe.check_mod)
    async def addrole(self, ctx, member: discord.Member, role):
        """
        Adds a the specified role to the member given
        """
        # I dont use the role converter here since it is case sensitive
        role = [x for x in ctx.guild.roles if x.name.lower() == role.lower() or str(x.id) == role][0]
        await member.add_roles(role)
        await ctx.send(f"{globe.tick} Added role")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        # elif ctx.guild is None:
        #     # I totally don't receive all dms to the bot
        #     me = self.bot.owner_id
        #     me = self.bot.get_user(me)
        #     emb = discord.Embed(description=str(ctx.content))
        #     emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        #     if ctx.attachments:
        #         emb.set_image(url=ctx.attachments[0].url)
        #     emb.set_footer(text=ctx.created_at.strftime("%H:%M%p, %-d %b %Y"))
        #     await me.send("Dm from user", embed=emb)

        elif ctx.channel.id == globe.suggest_id:
            # React with the upvotes for the suggestion channel
            await ctx.add_reaction(globe.upvote)
            await ctx.add_reaction(globe.downvote)

    @commands.command(aliases=["rl"])
    @commands.is_owner()
    async def reload(self, ctx, cog):
        """
        Reloads a cog and updates changes to it
        """
        try:
            self.bot.reload_extension("cogs." + cog)
        except Exception as error:
            await ctx.send(f"{globe.errorx} `{error}`")

        if cog == "invites":
            await self.bot.get_cog("Invites").setup()
        print(f"---------- RELOADED COG '{cog}' ----------")
        await ctx.send("✅")

    @commands.command(aliases=["exec", "code", "eval"])
    @commands.is_owner()
    async def run(self, ctx, *, code):
        """
        Runs eval() on python code
        """
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'commands': commands,
            'discord': discord,
            'guild': ctx.message.guild,
            'globe': globe,
        }

        out = ">>> " + code + "\n"
        output = "```python\n{}\n{}```".format(out, "{}")

        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(type(e).__name__ + ': ' + str(e))
            return

        if len(output.format(result)) > 2000:
            await ctx.send(f"{globe.errorx} The output is too long?")
        else:
            await ctx.send(output.format(result))

    @run.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            await ctx.send(f"{globe.errorx} The output is too long?")

    @commands.command()
    @commands.is_owner()
    async def add_cog(self, ctx, name):
        """
        Install a cog into the bot (idk if it works)
        """
        self.bot.load_extension(name)
        print(f"---------- ADDED COG '{name}' ----------")
        await ctx.send("✅")

    @commands.command()
    @commands.check(globe.check_mod)
    async def poll(self, ctx, question, *answers):
        """
        QOTD poll
        """
        if ctx.channel.id == globe.qotd_id:
            embed = discord.Embed(colour=ctx.guild.get_member(self.bot.user.id).colour)
            body = ""
            if len(answers) > len(num_emoji):
                await ctx.author.send(f"{globe.errorx} Too many arguments in poll")
                return
            for i in range(len(answers)):
                body += f"{num_emoji[i]} {answers[i].capitalize()}\n"

            embed.description = body
            msg = await ctx.send(f"**Poll: {question.capitalize()}**", embed=embed)
            for i in range(len(answers)):
                await msg.add_reaction(f"{num_emoji[i]}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        id = payload.message_id
        user = payload.user_id
        guild = payload.guild_id
        emoji = str(payload.emoji)
        channel = payload.channel_id

        if channel == globe.react_id:
            guild = self.bot.get_guild(guild)
            for i in react_roles:
                if i["ID"] == id:
                    member = guild.get_member(user)
                    channel = guild.get_channel(channel)
                    message = await channel.fetch_message(id)
                    if emoji in i["roles"]:
                        role = guild.get_role(i["roles"][emoji])
                        await member.add_roles(role)
                        return
                    else:
                        await message.remove_reaction(emoji, member)

        elif str(payload.emoji) == "📊" and payload.channel_id == globe.qotd_id:
            message_id = payload.message_id
            server = self.bot.get_guild(globe.serv_id)
            channel = server.get_channel(globe.qotd_id)
            message = await channel.fetch_message(message_id)
            author = server.get_member(payload.user_id)

            if globe.check_mod(author) and "Poll: " in message.content:
                if "🔒" not in message.content:  # not locked
                    title = '📊 Results for: "' + message.clean_content[8:-2] + '"'
                    msg = message.embeds[0].description
                    answers = msg.split("\n")
                    answers = [x.split(" ", 1)[1] for x in answers]

                    votes = sum([len(await x.users().flatten()) - 1 for x in message.reactions])
                    embed = discord.Embed(title=title, colour=server.get_member(self.bot.user.id).colour)
                    for i in range(len(answers)):
                        emote = num_emoji[i]
                        reactions = [x for x in message.reactions if x.emoji == emote]
                        count = len(await reactions[0].users().flatten()) - 1
                        percent = str(int(count / votes * 100)) + "%"
                        embed.add_field(name=answers[i] + ":", value=str(percent), inline=False)
                    await channel.send(embed=embed)
                    await message.edit(content=("🔒" + message.content), embed=message.embeds[0])
                    await message.clear_reactions()
                else:
                    await author.send("❗ That poll has already been finished")
            await message.remove_reaction("📊", author)

        elif payload.channel_id == globe.qotd_id and not payload.user_id == self.bot.user.id:  # only 1 reaction for poll
            message_id = payload.message_id
            server = self.bot.get_guild(globe.serv_id)
            channel = server.get_channel(globe.qotd_id)
            message = await channel.fetch_message(message_id)

            if not "Poll: " in message.content:  # tfw non nested if statement
                return

            reactions = message.reactions
            user_reacts = []
            for i in reactions:
                users = [x.id for x in await i.users().flatten()]
                if payload.user_id in users:
                    user_reacts.append(i.emoji)

            if not user_reacts:
                # this shouldn't occur but i don't trust my code
                # > reaction added  > no reaction added   yeah.. .. . .
                print("Poll reaction: no reaction added???")
            elif not len(user_reacts) == [payload.emoji]:  # more than one emote since more than one instance
                user = server.get_member(payload.user_id)
                try:
                    if str(payload.emoji) in num_emoji:
                        user_reacts.remove(str(payload.emoji))
                        for i in user_reacts:
                            if str(i) in num_emoji:
                                await message.remove_reaction(i, user)
                except ValueError:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # remove react role
        id = payload.message_id
        user = payload.user_id
        guild = payload.guild_id
        emoji = str(payload.emoji)
        channel = payload.channel_id

        if channel == globe.react_id:
            guild = self.bot.get_guild(guild)
            for i in react_roles:
                if i["ID"] == id:
                    if emoji in i["roles"]:
                        role = guild.get_role(i["roles"][emoji])
                        member = guild.get_member(user)
                        await member.remove_roles(role)
                        return


def setup(bot):
    bot.add_cog(Basic(bot))
