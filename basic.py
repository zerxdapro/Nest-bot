import inspect
from discord.ext import commands
import discord
import re
import globe
import asyncio
import datetime as dt
import requests
import image_handler
import csv
from threading import enumerate as threadlist
from PIL import Image, ImageFont, ImageDraw
from image_handler import mask_circle_transparent

num_emoji = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

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
    {"ID":632753058190852096, "roles": {"🏳️‍🌈": 632752022411673600}}
]


# async def timer_loop(time, message, caller):
#     embed = message.embeds[0]
#     loops = int(time / 60)
#     if time % 60:
#         loops += 1
#     for i in range(loops):
#         # print(time)
#         await asyncio.sleep(60)
#         time -= 60
#         if time > 0:
#             delta = dt.timedelta(seconds=time)
#             desc = f"{delta.days} days, {delta.seconds // 3600 % 24} hours, {delta.seconds // 60 % 60} minutes remaining"
#             if desc == "0 days, 0 hours, 0 minutes remaining":
#                 desc = "<1 minute remaining"
#             new_embed = discord.Embed(title=embed.title, colour=embed.colour, description=desc)
#             try:
#                 await message.edit(embed=new_embed)
#             except (discord.NotFound, discord.HTTPException):
#                 await caller.send(f"Your `{embed.title[2:-6]}` timer got deleted")
#                 return
#         else:
#             new_embed = discord.Embed(title=embed.title, colour=embed.colour, description="Timer is up!")
#             try:
#                 await message.edit(embed=new_embed)
#             except (discord.NotFound, discord.HTTPException):
#                 pass
#             await caller.send(f"Your `{embed.title[2:-6]}` timer is finished!")
#             return


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliases=["countdown"])
    # @commands.check(globe.check_mod)
    # async def timer(self, ctx, *, time):
    #     match = r"(([0-9]+) ?(days?|d))?( ?([0-9]+) ?(hours?|hrs?|h))?( ?([0-9]+) ?(minutes?|mins?|m))?"
    #     match = re.match(match, time, re.IGNORECASE)
    #     if match:
    #         time = [None, None, None]
    #         time[0] = match.group(2)
    #         time[1] = match.group(5)
    #         time[2] = match.group(8)
    #
    #         order = ["days", "hours", "minutes"]
    #         raw = ""
    #         for i in range(len(time)):
    #             if not time[i]:
    #                 time[i] = 0
    #             else:
    #                 time[i] = int(time[i])
    #             raw += f"{str(time[i])} {order[i]}, "
    #         raw = raw[:-2]
    #
    #         time[0] = time[0] * 86400
    #         time[1] = time[1] * 3600
    #         time[2] = time[2] * 60
    #         time = sum(time)
    #
    #         result = dt.datetime.now() + dt.timedelta(seconds=time)
    #
    #         embed = discord.Embed(title=f"⏱ {raw} timer", colour=0xe45898, description=raw + " remaining")
    #         message = await ctx.send(embed=embed)
    #
    #         self.bot.loop.create_task(timer_loop(time, message, ctx.author))
    #         with open('data/timers.csv', 'a') as fd:
    #             writer = csv.writer(fd)
    #             writer.writerow([ctx.author.id, message.id, ctx.channel.id, result])
    #     else:
    #         raise commands.MissingRequiredArgument

    # @timer.error
    # async def do_repeat_handler(self, ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send(f"{globe.errorx} Your command was formatted incorrectly")
    #     else:
    #         print("other error")
    #         # await self.bot.owner.send(f"`{ctx.content}`\n\nCaused:\n\n```\n{error}\n```")
    #         raise error

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # msg = f"Hey! Welcome to the feemagers discord server {member.display_name}. You have access to the
        # introductions channel, so why don't you tell us a bit about yourself over there? The other channels will be
        # unlocked for you in 15 minutes - this is to reduce spam/raiders. We can't wait to meet you!" msg_pub =
        # f"Hey! Welcome to the feemagers discord server {member.mention}. You have access to this channel currently,
        # so tell us a bit about yourself if you'd like. The other channels will be unlocked for you in 15 minutes -
        # this is to reduce spam/raiders. We can't wait to meet you!" try: await member.send(msg) except
        # discord.Forbidden: server = self.bot.get_guild(globe.fserv_id) channel = server.get_channel(globe.intro_id)
        # await channel.send(msg_pub)
        if member.guild.id != globe.fserv_id:
            return
        cnl = member.guild.get_channel(globe.welcome_id)
        image_handler.make_welcome("welcome", member)
        await cnl.send(str(member.mention), file=discord.File("image.png"))
        # await asyncio.sleep(15 * 60)
        # try:
        #     await member.add_roles(member.guild.get_role(globe.reg_id))
        #     await member.send("You have been given the regular role and can now see all of the channels!")
        # except (discord.HTTPException, discord.Forbidden):
        #     pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != globe.fserv_id:
            return
        cnl = member.guild.get_channel(globe.welcome_id)
        image_handler.make_welcome("leave", member)
        await cnl.send(str(member.mention), file=discord.File("image.png"))

    @commands.command(aliases=["announce"])
    @commands.check(globe.check_mod)
    async def say(self, ctx, channel: discord.TextChannel, *, message):
        try:
            await channel.send(message)
        except discord.HTTPException:
            await ctx.send(f"{globe.errorx} I can't find that channel")

    @say.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"<:redcross:608943524075012117> {error.args[0]}")

    @commands.command()
    @commands.check(globe.check_mod)
    async def addrole(self, ctx, user: discord.Member, role):
        role = [x for x in ctx.guild.roles if x.name.lower() == role or str(x.id) == role][0]
        await user.add_roles(role)
        await ctx.send("<:greentick:608943523823222785> Added role")

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        elif ctx.guild is None:
            me = self.bot.owner_id
            me = self.bot.get_user(me)
            emb = discord.Embed(description=str(ctx.content))
            emb.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            if ctx.attachments != []:
                emb.set_image(url=ctx.attachments[0].url)
            emb.set_footer(text=ctx.created_at.strftime("%H:%M%p, %-d %b %Y"))

            await me.send("Dm from user", embed=emb)

        elif ctx.channel.id == globe.mod_suggest_id:
            await ctx.add_reaction(globe.upvote)
            await ctx.add_reaction(globe.downvote)

    @commands.command(aliases=["rl"])
    @commands.is_owner()
    async def reload(self, ctx, arg):
        self.bot.reload_extension(arg)
        if arg == "invites":
            await self.bot.get_cog("Invites").setup()
        print(f"---------- RELOADED COG '{arg}' ----------")
        await ctx.send("✅")

    # @reload.error
    # async def do_repeat_handler(self, ctx, error):
    #     if isinstance(error, commands.ExtensionNotLoaded):
    #         await ctx.send(f"{globe.errorx} That cog isn't loaded")
    #     elif isinstance(error, commands.ExtensionNotFound):
    #         await ctx.send(f"{globe.errorx} That cog doesn't exist")
    #     elif isinstance(error, commands.ExtensionFailed):
    #         await ctx.send(f"{globe.errorx} An error occured while loading that cog")
    #     else:
    #         raise error

    @commands.command(aliases=["exec", "code", "eval"])
    @commands.is_owner()
    async def run(self, ctx, *, command):
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

        out = ""
        for i in command.split("\n"):
            out += ">>> " + i + "\n"
        output = "```python\n{}\n{}```".format(out, "{}")

        env.update(globals())

        try:
            result = eval(command, env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send(type(e).__name__ + ': ' + str(e))
            return
        if len(output.format(result)) > 2000:
            await ctx.send(f"{globe.errorx} The output could not be sent- too long?")
            return
        await ctx.send(output.format(result))

    @run.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, discord.HTTPException):
            await ctx.send(f"{globe.errorx} The output could not be sent- too long?")

    @commands.command()
    @commands.is_owner()
    async def add_cog(self, ctx, name):
        self.bot.extension(name)
        print(f"---------- ADDED COG '{name}' ----------")
        await ctx.send("✅")

    @commands.command()
    async def poll(self, ctx, question, *answers):
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
            server = self.bot.get_guild(globe.fserv_id)
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
            server = self.bot.get_guild(globe.fserv_id)
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
            # print(payload.emoji)
            # print(user_reacts)
            if not user_reacts:
                print("Poll reaction: no reaction added")
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

    @commands.command(aliases=["color"])
    async def colour(self, ctx, hexcol):
        rex = re.match(r"#([0-9a-f]{6})", hexcol, re.IGNORECASE)
        if rex:
            await ctx.trigger_typing()
            image = Image.new("RGB", (256, 256), hexcol)
            image.save("image.png")
            await ctx.send(f"🖌 Colour: {hexcol}", file=discord.File("image.png"))
        else:
            await ctx.send(f"{globe.errorx} That input is not a hexadecimal colour")

    @commands.command()
    async def testcol(self, ctx, hexcol):
        rex = re.match(r"#([0-9a-f]{6})", hexcol, re.IGNORECASE)
        if rex:
            await ctx.trigger_typing()
            font_path = "images/Whitney Medium.ttf"
            padding = 20
            pfp = Image.open(requests.get(ctx.author.avatar_url_as(format="png", size=128), stream=True).raw)
            pfp = mask_circle_transparent(pfp)
            font = ImageFont.truetype(font_path, 39)
            width = padding * 3 + font.getsize("M" * 32)[0] + 128
            height = 128 + padding * 2
            image = Image.new("RGBA", (width, height), "#36393f")
            image.paste(pfp, (padding, padding, 128 + padding, 128 + padding), pfp)

            font = ImageFont.truetype(font_path, 42)
            draw = ImageDraw.Draw(image)
            draw.text((128 + padding * 2, padding), ctx.author.display_name, font=font, fill=hexcol)
            draw.text((128 + padding * 2 + 1, padding), ctx.author.display_name, font=font, fill=hexcol)
            height = font.getsize(ctx.author.display_name)[1]
            font = ImageFont.truetype(font_path, 39)
            draw.text((128 + padding * 2, padding * 1.5 + height), f"{ctx.guild.name}", font=font,
                      fill="#dcddde")
            image.save("image.png")
            await ctx.send(f"🖌 Colour: {hexcol}", file=discord.File("image.png"))
        else:
            await ctx.send(f"{globe.errorx} That input is not a hexadecimal colour")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
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
