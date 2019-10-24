from discord.ext import commands
import discord
from helpers import globe
import csv
from string import hexdigits
import random

colour = 0x68c8e0


def get_ticket(user=None, tick_id=None):
    if not user and not tick_id:
        return

    with open("data/tickets.csv", "r") as fd:
        reader = list(csv.reader(fd))[0:]

        for i in reader:
            if i[0] == str(user):
                return i
            elif i[1] == tick_id:
                return i


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.p = self.bot.command_prefix

    @commands.group(aliases=["tk"], invoke_without_command=True)
    async def ticket(self, ctx):
        if ctx.guild:
            await ctx.send(f"{globe.errorx} That command can only be used in DMs")
            return

        ticket = get_ticket(user=ctx.author.id)
        if ticket:
            embed = discord.Embed(title="You have an active support ticket", color=colour)
            embed.description = f"Ticket ID: {ticket[1]}\n"
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You have no support tickets active", color=colour)
            await ctx.send(embed=embed)

    @ticket.group(aliases=["add"])
    @commands.dm_only()
    async def create(self, ctx, *, message):
        ticket = get_ticket(ctx.author.id)
        if ticket:
            embed = discord.Embed(title="You already have an active support ticket", colour=colour)
            embed.description = f"Close the active ticket first to make a new one"
            await ctx.send(embed=embed)
            return

        # no ticket made
        ticket_id = "".join([random.choice(hexdigits) for x in range(6)]).upper()
        while get_ticket(tick_id=ticket_id):  # prevent duplicates
            # if a ticket is found with that ID, make a new id and check that
            ticket_id = "".join([random.choice(hexdigits) for x in range(6)]).upper()  # 6 digit hex value, upper case

        guild = self.bot.get_guild(globe.test_id)  # TODO: fix
        category = discord.utils.get(guild.categories, id=globe.ticket_cat)
        ticket_channel = await category.create_text_channel(ticket_id)
        await ticket_channel.send(f"@here Ticket {ticket_id} created:\n```{message}```")

        with open("data/tickets.csv", "a") as fd:
            writer = csv.writer(fd)
            writer.writerow([ctx.author.id, ticket_id, ticket_channel.id])

        embed = discord.Embed(colour=colour, title="Created ticket")
        embed.description = f"**Ticket ID: {ticket_id}**"
        await ctx.send(embed=embed)

    @ticket.group()
    async def close(self, ctx: commands.Context):
        if ctx.guild and ctx.channel.category_id == globe.ticket_cat:  # called in a ticket channel
            ticket_id = ctx.channel.name.upper()
            ticket = get_ticket(tick_id=ticket_id)

            if not ticket:
                await ctx.send(f"{globe.errorx} This ticket is already closed")
            else:
                member = ctx.guild.get_member(int(ticket[0]))
                if member:  # a user object found, don't dm about ticket if not in server # maybe change??
                    embed = discord.Embed(colour=colour, title=f"Ticket closed by moderator")
                    embed.description = f"**Ticket ID: {ticket[1]}**"
                    await member.send(embed=embed)

                with open("data/tickets.csv", "r") as rf:
                    reader = list(csv.reader(rf))[0:]  # get content
                    with open("data/tickets.csv", "w") as wf:  # clear file
                        writer = csv.writer(wf)

                        for i in reader:  # write everything but the current ticket back into the file
                            if i != ticket:
                                writer.writerow(i)

                await ctx.send(f"{globe.tick} Closed ticket {ticket[1]}")
                await ctx.channel.edit(name=f"Closed- {ctx.channel.name}")

        else:  # DMed
            ticket = get_ticket(user=ctx.author.id)

            if not ticket:
                await ctx.send(f"{globe.errorx} There are no active tickets")
            else:
                guild = self.bot.get_guild(globe.test_id)
                channel = guild.get_channel(int(ticket[2]))

                await channel.send("ℹ  Ticket closed by user")
                await channel.edit(name=f"Closed- {channel.name}")

                with open("data/tickets.csv", "r") as rf:
                    reader = list(csv.reader(rf))[0:]  # get content
                    with open("data/tickets.csv", "w") as wf:  # clear file
                        writer = csv.writer(wf)

                        for i in reader:  # write everything but the current ticket back into the file
                            if i != ticket:
                                writer.writerow(i)

                embed = discord.Embed(colour=colour, title="Ticket closed")
                embed.set_footer(text=f"Ticket ID: {ticket[1]}")
                await ctx.send(embed=embed)

    @ticket.group(aliases=["s", "reply", "r"])
    async def send(self, ctx, *, message):
        if ctx.guild and ctx.channel.category_id == globe.ticket_cat:  # called in a ticket channel
            ticket_id = ctx.channel.name.upper()
            ticket = get_ticket(tick_id=ticket_id)

            if not ticket:
                await ctx.send(f"{globe.errorx} This ticket is closed")
            else:
                member = ctx.guild.get_member(int(ticket[0]))
                if member:
                    embed = discord.Embed(colour=colour, description=message)
                    embed.set_footer(text=f"Ticket ID: {ticket_id}")
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    await member.send(embed=embed)

                    await ctx.message.add_reaction(globe.tick)
                else:
                    await ctx.send(f"{globe.errorx} I can't find the user in the server! `(user left server?)`")
        else:
            ticket = get_ticket(user=ctx.author.id)

            if not ticket:
                await ctx.send(f"{globe.errorx} There are no active tickets")
            else:
                guild = self.bot.get_guild(globe.test_id)
                channel = guild.get_channel(int(ticket[2]))
                embed = discord.Embed(colour=colour, description=message)
                embed.set_author(name=ticket[1], icon_url=self.bot.user.default_avatar_url)
                await channel.send(embed=embed)

                await ctx.message.add_reaction(globe.tick)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):  # if the command handles the error on its own
            return

        error = getattr(error, 'original', error)  # idk found on github

        if isinstance(error, commands.CommandNotFound):  # noone cares lel
            return
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"{globe.errorx} That command can only be used in dms")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} {error.args[0]}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} Your command is missing an argument, consult the help command")
        else:
            raise error


def setup(bot):
    bot.add_cog(Ticket(bot))
