from discord.ext import commands
import discord
import re
from globe import fserv_id, cmd_id, check_mod
import globe
import asyncio
import csv
import datetime as dt


mute_ignore = [625112497497833514, 628560677153538088, 624784883251675137]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yeet"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, target: discord.Member, *, reason=None):
        if target.roles[-1] >= ctx.guild.get_member(self.bot.user.id).roles[-1]:
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to kick that user")
            return
        msg = "You have been kicked from The Nest"
        if reason:
            msg += f" for `{reason}`"

        try:
            await target.send(msg)
        except discord.Forbidden:
            await ctx.send("❗ I can't dm that user")

        await ctx.send(
            f"**<:greentick:608943523823222785> User {target.mention} has been kicked by {ctx.author.mention}**")
        await target.kick(reason=reason)

    @kick.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("<:redcross:608943524075012117> You didn't give me someone to kick")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to kick that user")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"<:redcross:608943524075012117> {error.args[0]}")
        else:
            raise error

    @commands.command()
    @commands.check(globe.check_mod)
    async def ban(self, ctx, target: discord.User, *, reason=None):
        if target.id == ctx.author.id:
            await ctx.send(f"{globe.errorx}  You can't ban yourself")
            return

        if target in ctx.guild.members:  # if user is in the server
            target = ctx.guild.get_member(target.id)  # set the member object
        else:  # if not, ban
            await ctx.send(
                f"**<:greentick:608943523823222785> User {target.mention} has been banned from the server by {ctx.author.mention}**")
            await ctx.guild.ban(target, reason=reason)
            return
        if target.roles[-1] >= ctx.guild.get_member(self.bot.user.id).roles[-1]:  # check if bot has permissions to ban that user
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to ban that user")
        else:
            msg = "You have been banned from The Nest"
            if reason:
                msg += f" for `{reason}`"
            try:
                await target.send(msg)
            except discord.Forbidden:
                await ctx.send("❗ I can't dm that user")
            await ctx.send(
                f"**<:greentick:608943523823222785> User {target.mention} has been banned from the server by {ctx.author.mention}**")
            await ctx.guild.ban(target, reason=reason)


    @ban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to ban")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to ban that user")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"<:redcross:608943524075012117> {error.args[0]}")
        else:
            raise error

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, target: discord.User):
        await ctx.send(f"<:greentick:608943523823222785> {ctx.author.mention} has unbanned {target.mention}")
        await ctx.guild.unban(target)

    @ban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to ban")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to ban that user")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"<:redcross:608943524075012117> {error.args[0]}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, target):
        bans = await ctx.guild.bans()
        for entry in bans:
            current = entry.user
            if target in [current.name.lower(), str(current.id)]:
                await ctx.send(f"{current.mention} has been unbanned by {ctx.author.mention}")
                await ctx.guild.unban(current)
                return
        await ctx.send(f"<:redcross:608943524075012117> Member '{target}' not found")

    @unban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to unban that user")

    @commands.command()
    @commands.check(check_mod)
    async def mute(self, ctx, user: discord.Member, *, time_and_reason=""):
        if user.id == ctx.author.id:
            await ctx.send(f"{globe.errorx} You can't mute yourself")
            return
        dm = True

        match = r"(([0-9]+) ?(hours?|hrs?|minutes?|mins?|m\b|h\b)? ?)?(.*)?"
        time_and_reason = time_and_reason.lower()
        match = re.match(match, time_and_reason)
        time = match.group(2)
        unit = match.group(3)
        reason = match.group(4)
        msg = "You have been muted in The Nest"
        output = "User {} has been muted by {}".format(user.mention, ctx.author.mention)
        if not reason:
            reason = None
        elif reason == "nodm":
            dm = False
        else:
            msg += f" for `{reason}`"
            output += f" for `{reason}`"
        if not time:
            time = None
        else:
            if not unit:
                unit = "minutes"
            if unit in ["hrs", "hr", "hour", "hours", "h"]:
                unit = "hours"
                msg += f". You will be unmuted in {time} {unit}"
                output += f". They will be unmuted in {time} {unit}"
                time = int(time) * 3600
            elif unit in ["min", "mins", "minutes", "minute", "m"]:
                unit = "minutes"
                msg += f". You will be unmuted in {time} {unit}"
                output += f". They will be unmuted in {time} {unit}"
                time = int(time) * 60

        try:
            if dm:
                await user.send(msg)
        except discord.Forbidden:
            await ctx.send("❗ I can't dm that user")

        server_roles = ctx.guild.roles
        server_roles = (x.name for x in server_roles)
        if "Muted" not in server_roles:
            muted = await ctx.guild.create_role(name="Muted")
        else:
            muted = [x for x in ctx.guild.roles if x.name == "Muted"]
            muted = muted[0]

        await user.add_roles(muted)

        if not dm:
            output += "\n`[User was not messaged]`"
        await ctx.send(output)

        for channel in ctx.guild.channels:
            try:
                if channel.category.id not in mute_ignore:  # ignore mod channels
                    await channel.set_permissions(muted, send_messages=False, add_reactions=False)
            except discord.Forbidden:
                pass

        if time:
            # user name, id, event type, time to remove
            # so idk if this will work but we will go with it
            event = [user.display_name, user.id, "unmute", (dt.datetime.now()+dt.timedelta(seconds=time)).isoformat()]
            globe.pending_events.append(event)
            # the rest of this does actually work
            await asyncio.sleep(time)
            await user.remove_roles(muted)

    @mute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("<:redcross:608943524075012117> You didn't give me someone to mute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to mute that user")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("<:redcross:608943524075012117> I can't find that user")
        else:
            raise error

    @commands.command()
    @commands.check(check_mod)
    async def unmute(self, ctx, user: discord.Member):
        muted = [x for x in ctx.guild.roles if x.name == "Muted"]
        muted = muted[0]
        await user.remove_roles(muted)
        await ctx.send("User {} has been unmuted by {}".format(user.mention, ctx.author.mention))

    @unmute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("<:redcross:608943524075012117> You didn't give me someone to unmute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("<:redcross:608943524075012117> I don't have permissions to mute that user")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("<:redcross:608943524075012117> I can't find that user")
        else:
            raise error

    @commands.command()
    async def purge(self, ctx, amount: int):
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.channel.purge(limit=amount + 1)

        if not ctx.guild.id == globe.fserv_id:
            return
        desc = f"**{amount + 1} messages were deleted in {ctx.channel.mention} by {ctx.author.mention}**"
        embed = discord.Embed(colour=0xe45858, description=desc)
        server = self.bot.get_guild(globe.fserv_id)
        channel = server.get_channel(globe.audit_id)
        await channel.send(embed=embed)

    @commands.command()
    @commands.check(check_mod)
    async def warnings(self, ctx, *, user: discord.User = None):
        server = self.bot.get_guild(fserv_id)
        if user:
            if server.get_member(user.id):
                user = server.get_member(user.id)
        with open("data/warnings.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            reader = list(reader)

            msg = ""
            count = 0
            for i in reader[1:]:
                if user:
                    if user.id != int(i[3]):
                        continue
                server = self.bot.get_guild(fserv_id)
                mod_nick = server.get_member(int(i[1]))
                if not mod_nick:
                    mod_nick = i[0]
                else:
                    mod_nick = mod_nick.display_name

                user_nick = server.get_member(int(i[3]))
                if not user_nick:
                    user_nick = i[2]
                else:
                    user_nick = user_nick.display_name
                count += 1

                msg += f"{user_nick} ({i[3]}): Warned by {mod_nick} on {i[5]}\n\t{i[4]}\n"
            if msg == "" and user:
                msg = f"{user.display_name} has no warnings yet"
            elif msg == "":
                msg = f"There are no warnings currently"
            else:
                msg = f"{count} warnings\n\n\n" + msg

            if len(msg) > 2000:
                count = (len(msg) // 2000) + 1
                confirmation = await ctx.send(
                    f"❗ The warnings need to be split up into ~{count} messages, send them all? (👍)")
                await confirmation.add_reaction("👍")

                def check(reaction, user):
                    return (
                               not self.bot.user == user) and reaction.emoji == "👍" and reaction.message.id == confirmation.id

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("Waiting for the reaction timed out")
                    await confirmation.remove_reaction("👍", self.bot.user)
                else:
                    for chunk in [msg[i:i + 1994] for i in range(0, len(msg), 2000)]:
                        await ctx.send(f"```{chunk}```")
                        await asyncio.sleep(0.5)
            else:
                await ctx.send(f"```{msg}```")

    @warnings.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("<:redcross:608943524075012117>  That user isn't in the server")

    @commands.command()
    @commands.check(check_mod)
    async def warn(self, ctx, target: discord.Member, *, reason):
        with open('data/warnings.csv', 'a') as fd:
            writer = csv.writer(fd)
            # Mod name, Mod ID, User name, User ID, Reason, Time
            time = dt.datetime.now().strftime("%-d %B %y")
            writer.writerow([ctx.author.display_name, ctx.author.id, target.display_name, target.id, reason, time])
        await ctx.send(f"**<:greentick:608943523823222785> {target} has been warned**")
        await target.send(f"You were warned in {ctx.guild.name} for '{reason}'")

    @warn.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("<:redcross:608943524075012117>  I can't find that user")

    @commands.command(aliases=["dewarn"])
    @commands.check(check_mod)
    async def unwarn(self, ctx, target: discord.Member, *, snippet):
        if ctx.author.id == target.id:
            await ctx.send("<:redcross:608943524075012117> You can't remove a warning to yourself")
            return
        with open("data/warnings.csv", "r") as file:
            header = ["Mod name", "Mod ID", "User name", "User ID", "Reason", "Time"]
            reader = csv.reader(file, delimiter=",")
            reader = list(reader)

            found = False
            for i in reader[1:]:
                if snippet.lower() in i[4].lower() and target.id == int(i[3]):
                    reader.remove(i)
                    found = True
                    break
        if found:
            with open('data/warnings.csv', 'wt') as f:
                csv_writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                csv_writer.writerow(header)  # write header
                csv_writer.writerows(reader[1:])
            await ctx.send("Warning removed")
        else:
            await ctx.send("<:redcross:608943524075012117> No warnings were found with that user or reason")

    @unwarn.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("<:redcross:608943524075012117> I can't find that user")
        else:
            raise error

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_message(self, ctx):
        msg = ctx.content.lower()
        try:
            if ctx.author.bot:
                return
        except AttributeError:
            pass
        # if re.search(r"\bnigger\b", msg):
        #     server = self.bot.get_guild(fserv_id)
        #     channel = server.get_channel(cmd_id)
        #     try:
        #         await ctx.author.send(
        #             "You have been auto-banned from the r/feemagers discord server for saying the n word")
        #     except discord.Forbidden:
        #         pass
        #     await ctx.author.ban(reason="Autoban- 'Nigger'")
        #     title = f"**Autobanned user {ctx.author.mention} ({ctx.author.id}) for saying the n word**\n"
        #     embed = discord.Embed(description=title + msg, colour=0xFF0000)
        #     embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        #     embed.set_footer(text=ctx.author.created_at.strftime("%-I:%M%p, %-d %b %Y"))
        #     await channel.send(embed=embed)
        #     try:
        #         await ctx.delete()
        #     except discord.NotFound:
        #         pass

        if re.search(r"\b(fag|faggot|fags|nigger|niggers)\b", msg) and not ctx.author.bot:
            await ctx.delete()
            server = self.bot.get_guild(fserv_id)
            channel = server.get_channel(cmd_id)
            title = f"**Autodeleted message by {ctx.author.mention} ({ctx.author.id})**\n"
            embed = discord.Embed(description=title + msg, colour=0xFF0000)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=ctx.author.created_at.strftime("%-I:%M%p, %-d %b %Y"))
            await channel.send(embed=embed)
        elif re.search(r"\bretard(ed|s)?\b", msg) and not ctx.author.bot:
            await ctx.delete()
            server = self.bot.get_guild(fserv_id)
            channel = server.get_channel(cmd_id)
            title = f"**Autodeleted message by {ctx.author.mention} ({ctx.author.id})**\n"
            embed = discord.Embed(description=title + msg, colour=0xFF0000)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=ctx.author.created_at.strftime("%-I:%M%p, %-d %b %Y"))
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
