from discord.ext import commands
import discord
from globe import serv_id
import globe
import gs_handler as gsh
from datetime import datetime as dt
import asyncio


role_timer = 10*60


class Members(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        count = len([x for x in self.bot.get_guild(serv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])

        # welcome messages

        msg = "Hey there! Welcome to The Nest :). To keep this server safe, you will need wait ten minutes until you " \
              "get full access to all the channels. While you wait,{} tell us about " \
              "yourself!! We can't wait to meet you <3"
        try:
            await member.send(msg.format(" head on over to the #introductions channels and"))
        except discord.Forbidden:  # if not allowed to dm
            server = self.bot.get_guild(globe.serv_id)
            channel = server.get_channel(globe.intro_id)
            await channel.send(str(member.mention) + " " + msg.format(""))

        role = globe.member_role
        server = self.bot.get_guild(globe.serv_id)
        role = server.get_role(role)

        await asyncio.sleep(role_timer)
        await member.add_roles(role)

        try:
            await member.send("You have been given the regular role and can now see all of the channels!! Have fun")
        except (discord.HTTPException, discord.Forbidden):
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        count = len([x for x in self.bot.get_guild(serv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])

    @commands.command()
    @commands.is_owner()
    async def gsupload(self, ctx):
        """
        Log the member count to google sheets
        """
        count = len([x for x in self.bot.get_guild(serv_id).members if not x.bot])
        status = f"{count} members!"
        await self.bot.change_presence(status=discord.Status('online'), activity=discord.Activity(type=discord.ActivityType.watching, name=status))
        gsh.append_row([dt.now().strftime("%d/%m/%Y %H:%M:%S"), count])
        await ctx.send("✅")


def setup(bot):
    bot.add_cog(Members(bot))
