from discord.ext import commands
import discord
from helpers import globe
import datetime as dt
import sqlite3 as sql
import pytz
import asyncio


def ord(n):
    return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


class Bday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sql.connect("data/bday.db")
        self.c = self.conn.cursor()

    @commands.group(aliases=["bdays"])
    async def bday(self, ctx):
        """
        Tell the bot your birthday and party!
        """  # this is an example of how not to code
        # all commands using the @bday.group decorator will be prefixed with "bday", e.g. "bday date"
        pass

    @bday.group(aliases=["add", "update", "change", "set"])
    async def date(self, ctx, *, date):
        """
        Save your birthdate into the bot
        You can only set this 3 times
        """
        # convert the date string into a datetime object
        formats = ["%d %B", "%d %b", "%B %d", "%b %d"]

        time = None
        for i in formats:
            try:
                time = dt.datetime.strptime(date, i)
            except ValueError:
                pass

        if not time:
            await ctx.send(f"{globe.errorx} The inputted date is in an invalid format\n"
                           f"Format it as something like `12 october` or `12 oct`")
            return

        # check if entry in db
        fetch = self.c.execute("SELECT * FROM bdays WHERE ID=?", (ctx.author.id,))
        fetch = fetch.fetchone()

        data = (ctx.author.display_name, ctx.author.id, time.isoformat(), None)

        if not fetch:  # no db entry
            self.c.execute("INSERT INTO bdays (Username, ID, Datetime, Timezone, Changes) VALUES (?, ?, ?, ?, 2)", data)
            await ctx.send("🍰 Added your birthday to the database")
        else:  # there is a db entry
            if fetch[4] > 0:
                self.c.execute("UPDATE bdays SET Username=?, Datetime=?,"
                               " Changes=? WHERE ID=?", (data[0], data[2], fetch[4] - 1, data[1]))
                await ctx.send("🍰 Updated your birthday in the database")
            else:
                await ctx.send(f"{globe.errorx} You have changed your birthdate too much, to prevent abuse of the "
                               f"bot, contact a moderator to get it changed again")
                return
        self.conn.commit()

    @bday.group(aliases=["tz"])
    async def timezone(self, ctx, *, timezone):
        """
        Save your timezone for the birthday command
        Use the tzsearch command to find your timezone
        """
        if timezone not in pytz.all_timezones:
            await ctx.send(
                f"{globe.errorx} That is not a valid timezone, use the `tzsearch` command to find a timezone\n"
                "This link may help: http://kevalbhatt.github.io/timezone-picker/ Select your location on the map and"
                " run this command again with the Country/City or Continent/City value from the site")
            return

        # check if entry in db
        fetch = self.c.execute("SELECT * FROM bdays WHERE ID=?", (ctx.author.id,))
        fetch = fetch.fetchone()

        data = (ctx.author.display_name, ctx.author.id)

        if not fetch:  # no db entry
            await ctx.send(f"{globe.errorx} You haven't set up a birth date yet, use the `bday add` command")
        else:  # there is a db entry
            self.c.execute("UPDATE bdays SET Username=?, Timezone=? WHERE ID=?", (data[0], timezone, data[1]))
            self.conn.commit()
            await ctx.send("🗃 Updated your database entry")

    @bday.group(aliases=["bday", "mine", "entry"])
    async def list(self, ctx, member: discord.Member = None):
        """
        Show what birthdate and timezone the bot has stored for you
        If a member is specified, it will show their birthday
        """
        if not member:
            target = ctx.author
        else:
            target = member

        fetch = self.c.execute("SELECT * FROM bdays WHERE ID=?", (target.id,))
        fetch = fetch.fetchone()

        if not fetch and not member:  # no db entry
            await ctx.send("You haven't yet set your birthday. Use the `bday add` command!")
        elif not fetch and member:
            await ctx.send(f"{member.display_name} hasn't yet set their birthday yet")
        else:  # there is a db entry
            date = dt.datetime.strptime(fetch[2], "%Y-%m-%dT%H:%M:%S")
            month = date.strftime("%B")
            day = date.day
            date = f"{month} {ord(day)}"
            if member:
                output = f"🗓 {member.display_name}'s birthday is on {date}"
            else:
                output = f"🗓 Your birthday is on {date}"
            if fetch[3]:
                output += f" in timezone {fetch[3]}"
            await ctx.send(output)

    @bday.group()
    @commands.is_owner()
    async def announce(self, ctx, user: discord.Member):
        """
        Just a POC at the moment, dont use
        """
        colour = [0xe60000, 0xe67300, 0xe6e600, 0x39e600, 0x00e6e6, 0x7300e6, 0xe600e6] * 3
        embed = discord.Embed()
        embed.set_author(name=f"🎉🎉 Its {user.display_name}'s birthday!!! 🎉🎉", icon_url=user.avatar_url)
        embed.colour = colour[0]
        msg = await ctx.send(embed=embed)

        for i in colour[1:]:
            await asyncio.sleep(1)
            embed.colour = i
            await msg.edit(embed=embed)

    @bday.group()
    @commands.check(globe.check_mod)
    async def force(self, ctx, member: discord.Member, *, date):
        """
        Bypass the 3 changes limit
        """
        # convert the date string into a datetime object
        formats = ["%d %B", "%d %b", "%B %d", "%b %d"]

        time = None
        for i in formats:
            try:
                time = dt.datetime.strptime(date, i)
            except ValueError:
                pass

        if not time:
            await ctx.send(f"{globe.errorx} The inputted date is in an invalid format\n"
                           f"Format it as something like `12 october` or `12 oct`")
            return

        # check if entry in db
        fetch = self.c.execute("SELECT * FROM bdays WHERE ID=?", (member.id,))
        fetch = fetch.fetchone()

        data = (member.display_name, member.id, time.isoformat(), None)

        if not fetch:  # no db entry
            await ctx.send(f"{globe.errorx} That user has never inputted a birthday")
        else:  # there is a db entry
            self.c.execute("UPDATE bdays SET Username=?, Datetime=?"
                           " WHERE ID=?", (data[0], data[2], data[1]))
            self.conn.commit()
            await ctx.send(f"🍰 Updated {member.display_name}'s birthday in the database")

    @bday.group(aliases=["redeem", "celebrate", "today", "role", "now"])
    async def party(self, ctx):
        """
        Get given the birthday role!
        """
        # TODO: rename command -> doesnt sound intuitive eek
        fetch = self.c.execute("SELECT * FROM bdays WHERE ID=?", (ctx.author.id,))
        fetch = fetch.fetchone()

        if not fetch:
            await ctx.send(f"{globe.errorx} You haven't told me your birthday so we can't party just yet")
            return

        tz = fetch[3]
        if not tz:
            p = self.bot.command_prefix
            await ctx.send(f"❕ You will need to set your timezone first! {p}bday tz [timezone]")
            return
        tz = pytz.timezone(tz)
        date = fetch[2]
        date = tz.localize(dt.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"))
        timein = dt.datetime.now(tz).replace(year=1900)

        if timein.date() == date.date():
            server = self.bot.get_guild(globe.serv_id)
            role = server.get_role(globe.bday_id)
            await ctx.author.add_roles(role)

            await ctx.send(f"🎉🎉 Happy birthday {ctx.author.mention}!! 🎉🎉")

            if ctx.channel.id != globe.main_id:
                await server.get_channel(globe.main_id).send(f"🎉🎉 Happy birthday {ctx.author.mention}!! 🎉🎉")

            next_day = tz.localize(dt.datetime(date.year, date.month, date.day))
            time_diff = next_day - timein
            time_diff = time_diff.seconds

            event = [ctx.author.display_name, ctx.author.id, "bday remove",
                     (dt.datetime.now() + dt.timedelta(seconds=time_diff)).isoformat()]
            globe.pending_events.append(event)

            await asyncio.sleep(time_diff)
            await ctx.author.remove_roles(role)
            globe.pending_events.remove(event)
        else:
            await ctx.send("🗓 Today isn't your birthday")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):  # if the command handles the error on its own
            return

        error = getattr(error, 'original', error)  # idk found on github

        if isinstance(error, commands.CommandNotFound):  # noone cares lel
            return
        elif isinstance(error, commands.CheckFailure):  # supresssss
            return
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} {error.args[0]}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} Your command is missing an argument, consult the help command")
        else:
            raise error

    @bday.command(aliases=["next", "soon", "future", "coming"])
    async def upcoming(self, ctx):
        """
        Shows the next 10 birthdays
        """
        fetch = self.c.execute("SELECT * FROM bdays ORDER BY Datetime ASC")  # get all rows sorted by date

        past = []
        future = []
        members = [x.id for x in ctx.guild.members]
        for i in list(fetch):  # get all rows in list
            if i[1] in members:
                if i[3]:
                    tz = pytz.timezone(i[3])  # set timezone if set by user
                else:
                    tz = pytz.utc  # make timezone UTC

                date = tz.localize(dt.datetime.strptime(i[2], "%Y-%m-%dT%H:%M:%S"))  # get bday as tz aware
                current = dt.datetime.now(tz).replace(year=1900)  # get now as tz aware
                if current.date() > date.date():  # if the date is in the past
                    # years should be the same btw
                    past.append(i)
                else:
                    future.append(i)

        bdays = future + past
        bdays = bdays[:10]
        output = ""

        for i in bdays:
            date = dt.datetime.strptime(i[2], "%Y-%m-%dT%H:%M:%S")
            day = ord(date.day)
            month = date.strftime("%b")
            user = ctx.guild.get_member(i[1])
            output += f"{month} {day}\t{user.display_name}\n"

        output = f"**Upcoming birthdays in {ctx.guild.name}:**\n{output}"

        await ctx.send(output)


def setup(bot):
    bot.add_cog(Bday(bot))
