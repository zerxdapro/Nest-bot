from discord.ext import commands
import discord
from helpers import globe
import sqlite3 as sql
import datetime as dt
import random
from copy import deepcopy

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
        if random.randint(0, 2) > 0 or ctx.author.bot or (
                ctx.channel.id in blacklist and ctx.content.lower().startswith("owo")):
            return
        user = ctx.author
        id = user.id

        search = self.c.execute("SELECT * FROM users WHERE ID=?", (id,))
        fetch = deepcopy(search.fetchone())
        if fetch is None:
            time = '2019-01-04T16:41:24.647172'
            self.c.execute("INSERT INTO users (Name,ID,Level,XP,xp_time) VALUES (?,?,?,?,?)",
                           (user.display_name, id, 1, 0, time))
            self.conn.commit()
            fetch = (user.display_name, id, 1, 0, time)

        search = list(fetch)
        if dt.datetime.strptime(search[4], "%Y-%m-%dT%H:%M:%S.%f") + dt.timedelta(minutes=2) <= dt.datetime.now():
            # add xp and stuff
            search[3] += random.randint(15, 25)
            if search[3] >= level_to_xp(search[2]):
                search[3] -= level_to_xp(search[2])
                search[2] += 1

                server = self.bot.get_guild(globe.serv_id)
                bot_2 = server.get_channel(globe.bot_2_id)

                embed = discord.Embed(title=f"You've reached level {search[2]}!", color=0x3ac797)
                embed.set_author(name=user.display_name, icon_url=user.avatar_url)

                #   if random.randint(0, 5):
                #       embed.set_footer(text="Earn more xp to level up by participating in chat")

                await bot_2.send(user.mention, embed=embed)

            search = (search[2], search[3], dt.datetime.now().isoformat(), search[1])
            self.c.execute("UPDATE users SET Level=?, XP=?, xp_time=? WHERE ID=?", search)
            self.conn.commit()

    @commands.command(aliases=["xp"])
    async def level(self, ctx, member: discord.Member = None):
        """
        Display your level, position and xp on the server
        """
        if not member:
            member = ctx.author

        search = self.c.execute("SELECT XP, Level FROM users WHERE ID=?", (member.id,))
        fetch = deepcopy(search.fetchone())
        if not fetch:
            await ctx.send("That user has no xp")

        embed = discord.Embed(color=member.color)
        if str(embed.colour) == "#000000":
            embed.colour = 0xffffff
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Level", value=fetch[1])
        bar = make_bar(fetch[0], level_to_xp(fetch[1]), 15)
        embed.add_field(name="XP", value=bar + f" {fetch[0]}/{level_to_xp(fetch[1])}")

        query = self.c.execute("SELECT ID, XP, Level FROM users ORDER BY Level DESC, XP DESC")
        query = query.fetchall()
        index = None
        for i in range(len(query)):
            if query[i][0] == member.id:
                index = i + 1
                break

        members = [x for x in ctx.guild.members if not x.bot]
        embed.add_field(name="Position on server leaderboard", value=f"{index}/{len(members)}")

        await ctx.send(embed=embed)

    @level.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        else:
            raise error

    ''''@commands.command(aliases=["top", "top10"])
    async def OLDBOARD(self, ctx):
        """
        Display the top 10 users based on server activity
        """
        author = ctx.author.id
        query = self.c.execute("SELECT ID, XP, Level, Name FROM users ORDER BY Level DESC, XP DESC LIMIT 10")
        query.
        fetch = query.fetchall()
        output = "```md\n"
        name = ctx.guild.name
        output += name + "\n"
        output += "=" * len(name) + "\n\n"

        for i in range(len(fetch)):
            current = fetch[i]
            user = ctx.guild.get_member(current[0])
            if user:
                output += f"{i + 1}. {user.display_name} < Level {current[2]} {current[1]} xp >\n"
            else:
                # here is where we would get += 1
                output += f"{i + 1}. {current[3]} (User left server)  < Level {current[2]} {current[1]} xp >\n"

        query = self.c.execute("SELECT ID, XP, Level FROM users ORDER BY Level DESC, XP DESC")
        query = query.fetchall()
        index = None
        for i in range(len(query)):
            if query[i][0] == author:
                index = i + 1
                break
        if index:
            output += "\n\nYour Position:"
            output += f"\n{index}. You < Level {query[index - 1][2]} {query[index - 1][1]} xp >"
        else:
            output += "\n\nYou don't have a position on the leaderbord yet"

        output += "\n```"

        await ctx.send(output)'''

    @commands.command(aliases=["top", "top10"])
    async def leaderboard(self, ctx):
        """
        Display the top 10 users based on server activity
        """
        author = ctx.author.id
        query = self.c.execute("SELECT ID, XP, Level FROM users ORDER BY Level DESC, XP DESC")
        output = "```md\n"
        name = ctx.guild.name
        output += name + "\n"
        output += "=" * len(name) + "\n\n"

        user_ids = [x.id for x in ctx.guild.members]
        in_serv = []
        for i in query:
            if i[0] in user_ids:
                in_serv.append(i)

        top = in_serv[:10]

        for i in range(len(top)):
            current = top[i]
            user = ctx.guild.get_member(current[0])
            if user:
                output += f"{i + 1}. {user.display_name} < Level {current[2]} {current[1]} xp >\n"
            else:
                # here is where we would get += 1
                output += f"{i + 1}. {current[3]} (User left server)  < Level {current[2]} {current[1]} xp >\n"

        index = None
        for i in range(len(in_serv)):
            if in_serv[i][0] == author:
                index = i + 1
                break
        if index:
            output += "\n\nYour Position:"
            output += f"\n{index}. You < Level {in_serv[index - 1][2]} {in_serv[index - 1][1]} xp >"
        else:
            output += "\n\nYou don't have a position on the leaderbord yet"

        output += "\n```"

        await ctx.send(output)

    @commands.command(aliases=["pos", "me"])
    async def position(self, ctx, target: discord.Member = None):
        """
        Display a version of the leaderboard but showing the people directly above and below you
        """
        if not target:
            target = ctx.author

        query = self.c.execute("SELECT ID, XP, Level, Name FROM users ORDER BY Level DESC, XP DESC")
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
            end = len(query)-1

        cropped = query[start:end]

        output = "```md\n"
        name = ctx.guild.name
        output += name + "\n"
        output += "=" * len(name) + "\n\n"
        for i in range(len(cropped)):
            current = cropped[i]
            user = ctx.guild.get_member(current[0])
            if user:
                if user.id == target.id:
                    output += f"{i + 1 + start}. YOU < Level {current[2]} {current[1]} xp >\n"
                else:
                    output += f"{i + 1 + start}. {user.display_name} < Level {current[2]} {current[1]} xp >\n"
            else:
                output += f"{i + 1 + start}. {current[3]} (User left server)  < Level {current[2]} {current[1]} xp >\n"
        output += "```"

        await ctx.send(output)

    @commands.command()
    @commands.is_owner()
    async def refreshlevels(self, ctx):
        """
        Goes through all the users and updates their nicknames
        """
        server = self.bot.get_guild(globe.serv_id)

        query = self.c.execute("SELECT * FROM users")
        all = query.fetchall()

        all = [x for x in map(list, all)]

        for i in all:
            member = server.get_member(i[1])
            if member:
                i[0] = member.display_name

        for i in all:
            self.c.execute("UPDATE users SET Name=? WHERE ID=?", (i[0], i[1]))
        self.conn.commit()

        await ctx.send("✅")


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
