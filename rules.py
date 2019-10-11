from discord.ext import commands
import discord
import globe
from globe import check_mod
import csv


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(check_mod)
    async def addrule(self, ctx, title: str, desc: str):
        server = ctx.guild
        channel = server.get_channel(globe.rule_id)
        colour = 0xffff66
        with open("data/rules.csv", "r") as fd:
            count = len(fd.readlines())
        embed = discord.Embed(title=f"{count}. {title}", description=desc, color=colour)
        msg = await channel.send(embed=embed)
        with open("data/rules.csv", "a") as fd:
            reader = csv.writer(fd)
            reader.writerow([title, desc, msg.id])

    @commands.command()
    @commands.check(check_mod)
    async def removerule(self, ctx, number: int):
        # get channel for rules
        server = ctx.guild
        channel = server.get_channel(globe.rule_id)
        # open the rules and put into list
        with open("data/rules.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            reader = list(reader)
        # if the index out of range, puke
        if len(reader) < number or number <= 0:
            await ctx.send(f"{globe.errorx} Invalid rule number")
            return
        # get the message of the one we delet
        id = reader[number][2]
        msg = await channel.fetch_message(id)
        # remove that rule from file
        del reader[number]
        # delet message
        await msg.delete()

        # write remaining rules into file
        with open("data/rules.csv", "w") as fd:
            csv_writer = csv.writer(fd, quoting=csv.QUOTE_ALL)
            csv_writer.writerows(reader)

        # open file
        with open("data/rules.csv", "r") as fd:
            reader = list(csv.reader(fd, delimiter=","))
            header = reader[0]
            del reader[0]
            # go through all the items in the rules
            for i in range(len(reader)):
                id = reader[i][2]
                msg = await channel.fetch_message(id)
                embed = msg.embeds[0]
                embed = discord.Embed(title=f'{i+1}. {embed.title.split(" ", 1)[1]}', description=embed.description, colour=embed.colour)
                await msg.edit(embed=embed)

    @commands.command()
    @commands.check(check_mod)
    async def editrule(self, ctx, number: int, title: str, desc: str):
        # get channel for rules
        server = ctx.guild
        channel = server.get_channel(globe.rule_id)
        # open the rules and put into list
        with open("data/rules.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            reader = list(reader)
        # if the index out of range, puke
        if len(reader) < number or number <= 0:
            await ctx.send(f"{globe.errorx} Invalid rule number")
            return
        # get the message of the one we delet
        id = reader[number][2]
        msg = await channel.fetch_message(id)
        embed = discord.Embed(title=f"{number}. " + title, description=desc, color=msg.embeds[0].color)
        reader[number][0] = title
        reader[number][1] = desc
        await msg.edit(embed=embed)
        with open("data/rules.csv", "w") as fd:
            csv_writer = csv.writer(fd, quoting=csv.QUOTE_ALL)
            csv_writer.writerows(reader)


def setup(bot):
    bot.add_cog(Rules(bot))
