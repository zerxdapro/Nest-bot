from discord.ext import commands
import discord
from globe import fserv_id
import globe
import gs_handler as gsh
from datetime import datetime as dt


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        count = len([x for x in self.bot.get_guild(fserv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        count = len([x for x in self.bot.get_guild(fserv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])

    @commands.command()
    @commands.is_owner()
    async def gsupload(self, ctx):
        count = len([x for x in self.bot.get_guild(fserv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])
        await ctx.send("✅")


def setup(bot):
    bot.add_cog(Members(bot))
