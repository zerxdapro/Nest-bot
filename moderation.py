from discord.ext import commands
import discord
import re
from globe import serv_id, cmd_id, check_mod
import globe
import asyncio
import csv
import datetime as dt


mute_ignore = [625112497497833514, 628560677153538088, 624784883251675137]
server_whitelist = [globe.serv_id, 571462276930863117]


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["yeet"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kicks the specified user and dms the reason if provided
        """
        if member.roles[-1] >= ctx.guild.get_member(self.bot.user.id).roles[-1]:
            await ctx.send(f"{globe.errorx} I don't have permissions to kick that user")
            return
        msg = "You have been kicked from The Nest"
        if reason:
            msg += f" for `{reason}`"

        try:
            await member.send(msg)
        except discord.Forbidden:
            await ctx.send("❗ I can't dm that user")

        await ctx.send(
            f"**{globe.tick} User {member.mention} has been kicked by {ctx.author.mention}**")
        await member.kick(reason=reason)

    @kick.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't give me someone to kick")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{globe.errorx} I don't have permissions to kick that user")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"{globe.errorx} {error.args[0]}")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.check(globe.check_mod)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        """
        Ban the specified user from the server and tells them the reason if provided
        """
        if user.id == ctx.author.id:  # @jelly
            await ctx.send(f"{globe.errorx}  You can't ban yourself")
            return

        if user in ctx.guild.members:  # if user is in the server
            target = ctx.guild.get_member(user.id)  # set the member object
        else:  # if not in the server, ban
            msg = f"**{globe.tick} User {user.mention} has been banned from the server by {ctx.author.mention}**"
            await ctx.send(msg)
            await ctx.guild.ban(user, reason=reason)
            return

        # check if bot has permissions to ban that user
        if target.roles[-1] >= ctx.guild.get_member(self.bot.user.id).roles[-1]:
            await ctx.send(f"{globe.errorx} I don't have permissions to ban that user")
        else:
            msg = "You have been banned from The Nest"
            if reason:
                msg += f" for `{reason}`"
            try:
                await target.send(msg)
            except discord.Forbidden:
                await ctx.send("❗ I can't dm that user")

            msg = f"**{globe.errorx} User {target.mention} has been banned from the server by {ctx.author.mention}**"
            await ctx.send(msg)
            await ctx.guild.ban(target, reason=reason)

    @ban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You didn't give me someone to ban")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permissions to ban that user")
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"{globe.errorx} {error.args[0]}")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user):
        """
        Unban a user from the server
        """
        bans = await ctx.guild.bans()
        for entry in bans:
            current = entry.user
            if user in [current.name.lower(), str(current.id)]:
                await ctx.send(f"{current.mention} has been unbanned by {ctx.author.mention}")
                await ctx.guild.unban(current)
                return
        await ctx.send(f"{globe.errorx} Member '{user}' not found")

    @unban.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{globe.errorx} I don't have permissions to unban that user")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.check(check_mod)
    async def mute(self, ctx, member: discord.Member, *, time_and_reason=""):
        """
        Stop a user from typing and reacting in all channels
        """
        # time_and_reason is a dodgy way to handle it?
        # i think dicord.py can do this better
        # TODO: one day

        if member.id == ctx.author.id:
            await ctx.send(f"{globe.errorx} You can't mute yourself")
            return
        dm = True

        # Format the message all pretty and stuff
        match = r"(([0-9]+) ?(hours?|hrs?|minutes?|mins?|m\b|h\b)? ?)?(.*)?"
        time_and_reason = time_and_reason.lower()
        match = re.match(match, time_and_reason)
        time = match.group(2)
        unit = match.group(3)
        reason = match.group(4)
        msg = "You have been muted in The Nest"
        output = f"User {member.mention} has been muted by {ctx.author.mention}"
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
                await member.send(msg)
        except discord.Forbidden:
            await ctx.send("❗ I can't dm that user")

        server = self.bot.get_guild(globe.serv_id)
        muted = server.get_role(globe.muted)

        try:
            await member.add_roles(muted)
        except discord.Forbidden:
            await ctx.send(f"{globe.errorx} I am not able to add the muted role")

        if not dm:
            output += "\n`[User was not messaged]`"
        await ctx.send(output)

        for channel in ctx.guild.channels:
            try:
                if channel.category_id not in mute_ignore:  # ignore mod channels
                    await channel.set_permissions(muted, send_messages=False, add_reactions=False)
            except discord.Forbidden:
                pass

        if time:
            # user name, id, event type, time to remove
            # so idk if this will work but we will go with it
            event = [member.display_name, member.id, "unmute", (dt.datetime.now()+dt.timedelta(seconds=time)).isoformat()]
            globe.pending_events.append(event)
            # the rest of this does actually work
            await asyncio.sleep(time)
            await member.remove_roles(muted)

    @mute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't give me someone to mute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{globe.errorx} I don't have permissions to mute that user")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.check(check_mod)
    async def unmute(self, ctx, member: discord.Member):
        """
        Unmute a user
        """
        server = self.bot.get_guild(globe.serv_id)
        muted = server.get_role(globe.muted)
        await member.remove_roles(muted)
        await ctx.send(f"User {member.mention} has been unmuted by {ctx.author.mention}")

    @unmute.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't give me someone to unmute")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{globe.errorx} I don't have permissions to unmute that user")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    async def purge(self, ctx, number: int):
        """
        Deletes the last x number of messages from the server
        """
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.channel.purge(limit=number + 1)

        if not ctx.guild.id == globe.serv_id:
            return
        desc = f"**{number + 1} messages were deleted in {ctx.channel.mention} by {ctx.author.mention}**"
        embed = discord.Embed(colour=0xe45858, description=desc)
        server = self.bot.get_guild(globe.serv_id)
        channel = server.get_channel(globe.audit_id)
        await channel.send(embed=embed)

    @commands.command()
    @commands.check(check_mod)
    async def warnings(self, ctx, *, user: discord.User = None):
        """
        Get the warnings from a specific user. If no user is provided, ALL warnings will be shown
        """
        server = self.bot.get_guild(serv_id)
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
                server = self.bot.get_guild(serv_id)
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
                    return (not self.bot.user == user) and reaction.emoji == "👍" and reaction.message.id == confirmation.id

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
            await ctx.send(f"{globe.errorx}  That user isn't in the server")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command()
    @commands.check(check_mod)
    async def warn(self, ctx, member: discord.Member, *, reason):
        """
        Add a warning to the database for that user. The user will also be DMed the reason
        """
        with open('data/warnings.csv', 'a') as fd:
            writer = csv.writer(fd)
            # Mod name, Mod ID, User name, User ID, Reason, Time
            time = dt.datetime.now().strftime("%-d %B %y")
            writer.writerow([ctx.author.display_name, ctx.author.id, member.display_name, member.id, reason, time])
        await ctx.send(f"**{globe.tick} {member.mention} has been warned**")
        await member.send(f"You were warned in {ctx.guild.name} for '{reason}'")

    @warn.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"{globe.errorx}  I can't find that user")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command(aliases=["dewarn"])
    @commands.check(check_mod)
    async def unwarn(self, ctx, member: discord.Member, *, snippet):
        """
        Remove a warning from a user
        """
        if ctx.author.id == member.id:
            await ctx.send(f"{globe.errorx}You can't remove a warning to yourself")
            return
        with open("data/warnings.csv", "r") as file:
            header = ["Mod name", "Mod ID", "User name", "User ID", "Reason", "Time"]
            reader = csv.reader(file, delimiter=",")
            reader = list(reader)

            found = False
            for i in reader[1:]:
                if snippet.lower() in i[4].lower() and member.id == int(i[3]):
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
            await ctx.send(f"{globe.errorx} No warnings were found with that user or reason")

    @unwarn.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_message(self, ctx):
        msg = ctx.content.lower()
        try:  # ngl dont know why this is here
            if ctx.author.bot:
                return
        except AttributeError:
            pass

        # unfortunetely this regex is dummy thicc but i think its as tiny as i can get it :/
        inv = r"\b(https?://)?(www\.)?(discord\.gg|discordapp\.com/invite)/([a-zA-Z0-9]{5,7})\b"
        blacklist = r"\b(fag(got)?s?|niggers?|retard(ed|s)?)\b"

        if re.search(blacklist, msg) and not ctx.author.bot:
            await ctx.delete()
            server = self.bot.get_guild(serv_id)
            channel = server.get_channel(cmd_id)
            title = f"**Autodeleted message by {ctx.author.mention} ({ctx.author.id}) in {ctx.channel.mention}**\n"
            embed = discord.Embed(description=title + msg, colour=0xFF0000)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=ctx.author.created_at.strftime("%-I:%M%p, %-d %b %Y"))
            await channel.send(embed=embed)

        elif re.search(inv, msg) and not check_mod(ctx):  # enforce rule 8
            search = re.search(inv, ctx.content, re.IGNORECASE)
            invite = search.group(0)
            try:
                invite = await self.bot.fetch_invite(invite)
                inv_id = invite.guild.id

                rule_34 = "https://discordapp.com/channels/624784883251675136/624784883251675138/625251053713096704"

                if inv_id in server_whitelist:  # dont delete nest and team
                    return

                server = self.bot.get_guild(serv_id)

                channel = server.get_channel(cmd_id)
                title = f"**Discord server link posted by {ctx.author.mention} ({ctx.author.id}) in {ctx.channel.mention}**\n"
                embed = discord.Embed(description=title + msg, colour=0xFF0000)
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.set_footer(text=ctx.author.created_at.strftime("%-I:%M%p, %-d %b %Y"))
                await channel.send(embed=embed)

                await ctx.delete()

                desc = f"[Please observe rule 8]({rule_34})"
                embed = discord.Embed(description=desc, color=0xff0000)
                await ctx.channel.send(str(ctx.author.mention), embed=embed, delete_after=8)

            except discord.NotFound:
                # if it cant find the invite just ignore it since there is no issue as it likely doesnt exist
                pass


def setup(bot):
    bot.add_cog(Moderation(bot))
