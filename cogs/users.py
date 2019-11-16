from discord.ext import commands
import discord
from helpers import globe
import sqlite3 as sql
import datetime as dt
import random
from copy import deepcopy
from math import ceil

blacklist = [624785558102605824, 627985907013910538]

exponent = (1893.0 / 4500.0)
coef = 0.31


def xp_to_level(xp):
    return int(coef * xp ** exponent)


def root(base, value):
    return value ** (1. / base)


def level_to_xp(level):
    return int(root(exponent, level / coef))


def make_bar(num, den, size):
    progress = int(num / den * size)
    remain = int(size - progress)
    return "**{}{}**".format("▰" * progress, "▱" * remain)


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sql.connect("data/users.db")
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if random.randint(0, 2) > 0 or ctx.author.bot:
            return
        elif ctx.channel.id in blacklist and ctx.content.lower().startswith("owo"):
            return
        elif globe.member_role not in [x.id for x in ctx.author.roles]:
            return

        user = ctx.author
        id = user.id

        fetch = self.conn.execute("SELECT Name,ID,Level,XP,xp_time,month_xp FROM users WHERE ID=?", (id,))
        fetch = deepcopy(fetch.fetchone())
        if not fetch:  # no user entry
            data = (user.display_name, id, 1, 0, '2019-01-04T16:41:24.647172', 0)  # template data
            self.conn.execute("INSERT INTO users (Name,ID,Level,XP,xp_time,month_xp) VALUES (?,?,?,?,?,?)")  # save
            self.conn.commit()
            fetch = data

        fetch = list(fetch)
        now = dt.datetime.now()
        last_xp = dt.datetime.strptime(fetch[4], "%Y-%m-%dT%H:%M:%S.%f")

        if last_xp.month + 1 == now.month:
            print("New month, resetting")
            # a month's difference, move month xp to global xp and reset month xp
            self.conn.execute("""UPDATE users SET month_xp= 0""")
            self.conn.execute("""UPDATE users SET xp_time=?""", (now.isoformat(), ))
            self.conn.commit()
            fetch[5] = 0

        if now >= last_xp + dt.timedelta(minutes=2):  # if its been 2 min since last got xp
            rand_xp = random.randint(15, 25)
            fetch[5] += rand_xp
            fetch[3] += rand_xp

            if fetch[3] >= level_to_xp(fetch[2]):  # if enough xp to level up
                fetch[3] -= level_to_xp(fetch[2])
                fetch[2] += 1

                server = self.bot.get_guild(globe.serv_id)
                bot_2 = server.get_channel(globe.bot_2_id)

                embed = discord.Embed(title=f"You've reached level {fetch[2]}!", color=0x3ac797)
                embed.set_author(name=user.display_name, icon_url=user.avatar_url)

                await bot_2.send(user.mention, embed=embed)

            data = (fetch[2], fetch[3], now.isoformat(), fetch[5], id)
            self.conn.execute("UPDATE users SET Level=?, XP=?, xp_time=?, month_xp=? WHERE ID=?", data)
            self.conn.commit()

    @commands.command(aliases=["xp"])
    async def level(self, ctx, member: discord.Member = None):
        """
        Shows you your xp and levels
        If a user is specified, it will show their xp/levels
        """
        if not member:
            member = ctx.author

        search = self.c.execute("SELECT XP, Level, month_xp FROM users WHERE ID=?", (member.id,))
        fetch = deepcopy(search.fetchone())
        if not fetch:
            await ctx.send("That user has no xp")

        embed = discord.Embed(color=member.color)
        if str(embed.colour) == "#000000":
            embed.colour = 0xffffff

        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Level", value=fetch[1])
        bar = make_bar(fetch[0], level_to_xp(fetch[1]), 15)
        embed.add_field(name="Total XP", value=bar + f" {fetch[0]}/{level_to_xp(fetch[1])}")
        embed.add_field(name="XP this month", value=fetch[2])

        await ctx.send(embed=embed)

    @level.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        else:
            raise error

    @commands.command(aliases=["top", "top10", "topmonth"])
    async def leaderboard(self, ctx):
        """
        Shows the top 10 users of that month
        """
        guild = self.bot.get_guild(globe.serv_id)
        query = self.c.execute("SELECT ID, month_xp FROM users ORDER BY month_xp DESC")
        # gets get id, month's xp and sort by xp from that month

        query = list(deepcopy(list(query)))  # convert to nice list and

        if not query:  # shouldnt happen
            await ctx.send("Something went wrong uh oh. Tell quantum")
            return

        guild_members = [x.id for x in guild.members]
        in_guild = []

        for i in query:
            if i[0] in guild_members:
                in_guild.append(i)
        tops = in_guild[:10]

        output = "```md\n"
        name = guild.name
        output += name + "\n" + len(name) * "=" + "\n\n"

        for i in range(len(tops)):
            user = tops[i]
            name = guild.get_member(user[0]).name
            output += f"{i + 1}. {name} < {user[1]} xp >\n"

        pos = None
        for i in range(len(in_guild)):
            if in_guild[i][0] == ctx.author.id:
                pos = i + 1
                break

        if pos:
            output += f"\n\n\nYour Position:\n{pos}. {ctx.author.display_name} < {in_guild[pos][1]} xp >"

        output += "\n```"
        await ctx.send(output)

    @commands.command(aliases=["toptotal"])
    async def topall(self, ctx):
        """
        Shows the top 10 users of all time
        """
        guild = self.bot.get_guild(globe.serv_id)
        query = self.c.execute("SELECT ID, XP FROM users ORDER BY XP DESC")
        # gets get id, month's xp and sort by xp from that month

        query = list(deepcopy(list(query)))  # convert to nice list and

        if not query:  # shouldnt happen
            await ctx.send("Something went wrong uh oh. Tell quantum")
            return

        guild_members = [x.id for x in guild.members]
        in_guild = []

        for i in query:
            if i[0] in guild_members:
                in_guild.append(i)
        tops = in_guild[:10]

        output = "```md\n"
        name = guild.name
        output += name + "\n" + len(name) * "=" + "\n\n"

        for i in range(len(tops)):
            user = tops[i]
            name = guild.get_member(user[0]).name
            output += f"{i + 1}. {name} < {user[1]} xp >\n"

        pos = None
        for i in range(len(in_guild)):
            if in_guild[i][0] == ctx.author.id:
                pos = i + 1
                break

        if pos:
            output += f"\n\n\nYour Position:\n{pos}. {ctx.author.display_name} < {in_guild[pos][1]} xp >"

        output += "\n```"
        await ctx.send(output)

    @commands.command(aliases=["pos", "me", "posmonth"])
    async def position(self, ctx, target: discord.Member = None):
        """
        Shows the montly leaderboard centered around either you or the specified user
        """
        if not target:
            target = ctx.author

        query = self.c.execute("SELECT ID, month_xp FROM users ORDER BY month_xp DESC")
        query = query.fetchall()

        user_ids = [x.id for x in ctx.guild.members]  # change "query" to contain users in the server
        in_serv = []
        for i in query:
            if i[0] in user_ids:
                in_serv.append(i)

        query = in_serv

        # get position of user
        index = None
        for i in range(len(query)):
            if query[i][0] == target.id:
                index = i + 1
                break

        # get range to list
        index -= 1  # indexes start at 0 ammirite
        start = index - 5
        end = index + 4

        # crop range to size of array
        if start < 0:
            start = 0
            end = 10
        if end >= len(query):
            end = len(query) - 1

        cropped = query[start:end]

        output = "```md\n"
        name = ctx.guild.name
        output += name + "\n"
        output += "=" * len(name) + "\n\n"
        for i in range(len(cropped)):
            current = cropped[i]
            user = ctx.guild.get_member(current[0])
            if user:
                if user.id == target.id and ctx.author.id == target.id:  # if target is author and this index is them
                    output += f"{i + 1 + start}. YOU < Level {current[1]} xp >\n"
                elif user.id == target.id:  # if this is the target
                    output += f"{i + 1 + start}. {target.display_name.upper()} < Level {current[1]} xp >\n"
                else:
                    output += f"{i + 1 + start}. {user.display_name} < Level {current[1]} xp >\n"
        output += "```"

        await ctx.send(output)

    @commands.command()
    async def posall(self, ctx, target: discord.Member = None):
        """
        Shows a leaderboard centered around either you or the specified user, for all time
        """
        if not target:
            target = ctx.author

        query = self.c.execute("SELECT ID, XP FROM users ORDER BY XP DESC")
        query = query.fetchall()

        user_ids = [x.id for x in ctx.guild.members]  # change "query" to contain users in the server
        in_serv = []
        for i in query:
            if i[0] in user_ids:
                in_serv.append(i)

        query = in_serv

        # get position of user
        index = None
        for i in range(len(query)):
            if query[i][0] == target.id:
                index = i + 1
                break

        # get range to list
        index -= 1  # indexes start at 0 ammirite
        start = index - 5
        end = index + 4

        # crop range to size of array
        if start < 0:
            start = 0
            end = 10
        if end >= len(query):
            end = len(query) - 1

        cropped = query[start:end]

        output = "```md\n"
        name = ctx.guild.name
        output += name + "\n"
        output += "=" * len(name) + "\n\n"
        for i in range(len(cropped)):
            current = cropped[i]
            user = ctx.guild.get_member(current[0])
            if user:
                if user.id == target.id and ctx.author.id == target.id:  # if target is author and this index is them
                    output += f"{i + 1 + start}. YOU < Level {current[1]} xp >\n"
                elif user.id == target.id:  # if this is the target
                    output += f"{i + 1 + start}. {target.display_name.upper()} < Level {current[1]} xp >\n"
                else:
                    output += f"{i + 1 + start}. {user.display_name} < Level {current[1]} xp >\n"
        output += "```"

        await ctx.send(output)


def setup(bot):
    bot.add_cog(Users(bot))


"""
# does some calculations based on the levels and stuff
# dont need it normally
if __name__ == "__main__":
    for i in range(2, 71):
        user = {"level": 1, "xp": 0}
        goal = i
        time = 0
        while user["level"] < goal:
            user["xp"] += 19.5
            if user["xp"] >= calc(user["level"]):
                # print("Level up")
                user["xp"] -= calc(user["level"])
                user["level"] += 1
            time += 6
        time_old = time
        time = time * 60
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        if day >= 1:
            time_f = str(day) + " days " + str(hour) + " hours " + str(minutes) + " minutes"
        elif hour >= 1:
            time_f = str(hour) + " hours " + str(minutes) + " minutes"
        else:
            time_f = f"{minutes} minutes"
        print(f"Level {user['level']} in {time_f}")
"""
