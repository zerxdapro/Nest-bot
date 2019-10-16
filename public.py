from discord.ext import commands
import discord
from bs4 import BeautifulSoup
import requests
import re
import globe
import pytz
import datetime as dt


class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(color=member.color)
        if str(embed.colour) == "#000000":
            embed.colour = 0xffffff
        embed.set_author(name=member.display_name, icon_url=member.avatar_url)
        embed.add_field(name="Username", value=member.name, inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Account Creation Date", value=member.created_at.strftime('%d %b %Y'), inline=False)
        embed.add_field(name="Last Server Join Date", value=member.joined_at.strftime('%d %b %Y'), inline=False)
        roles = ""
        for i in list(reversed(member.roles[1:])):
            roles += i.mention + " "
        if roles == "":
            roles = "None"
        embed.add_field(name="Roles", value=roles, inline=False)

        await ctx.send(embed=embed)

    @whois.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("<:redcross:608943524075012117> I can't find that user")
        else:
            raise error

    @commands.command(aliases=["pfp", "picture", "image"])
    async def avatar(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.author
        embed = discord.Embed(title=member.display_name, color=member.colour)
        if str(embed.colour) == "#000000":
            embed.colour = 0xffffff
        embed.set_image(url=member.avatar_url)

        await ctx.send(embed=embed)

    @avatar.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("<:redcross:608943524075012117> I can't find that user")
        else:
            raise error

    @commands.command()
    async def server(self, ctx):
        server = ctx.guild

        embed = discord.Embed(color=ctx.guild.get_member(self.bot.user.id).colour, description=f"**{server.name}**")
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Members", value=server.member_count, inline=False)
        embed.add_field(name="Region", value=str(server.region).title(), inline=False)
        embed.add_field(name="Owner", value=server.owner.mention, inline=False)
        embed.add_field(name="Creation Date", value=server.created_at.strftime('%d %b %Y'), inline=False)
        embed.add_field(name="ID", value=server.id, inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["youtube"])
    async def yt(self, ctx, url):

        search1 = re.search(r"\b(https?:\/\/)?www\.youtube\.com\/watch\?v=([a-zA-Z0-9\-_]+)\b", url)
        search2 = re.search(r"\b(https?://)?youtu.be/([a-zA-Z0-9\-_]+)\b", url)

        if not search1 and not search2:
            await ctx.send(f"{globe.errorx} Please provide a valid youtube video url")
            return

        if search1:
            id = search1.group(2)
        elif search2:
            id = search2.group(2)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, features="html.parser")

        if soup.find("span", class_="watch-title") is None:
            await ctx.send(f"{globe.errorx} Please provide a valid youtube video url")
            return

        title = soup.find("span", class_="watch-title").text.strip()
        a = soup.findAll("a", "yt-uix-sessionlink spf-link")
        a = [x for x in a if x.attrs["href"].startswith("/channel/")][0]
        channel = a.text
        channel_link = "https://youtube.com" + a.attrs["href"]

        embed = discord.Embed(title=title, url=url, color=0xff0000)
        embed.set_author(name=channel, url=channel_link)
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{id}/hqdefault.jpg")

        await ctx.send(embed=embed)

    @commands.command(aliases=["timezone", "tz", "tzs", "searchtz"])
    async def tzsearch(self, ctx, search):
        tzs = pytz.all_timezones
        output = [x for x in tzs if search.lower() in x.lower()]

        if output:
            footer = ""
            if len(output) > 30:
                output = output[:30]
                footer = "\n\n-- Cropped list --"
            header = f"**🌐 Timezones for `{search}`:**\n"
            output = "\n".join(output)

            await ctx.send(header + output + footer)
        else:
            await ctx.send(f"{globe.errorx} No timezones were found for that location")

    @tzsearch.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't provide a timezone")

    @commands.command()
    async def timein(self, ctx, tz):
        tz = [x for x in pytz.all_timezones if x.lower() == tz.lower()]

        if tz:
            tz = tz[0]
            zone = pytz.timezone(tz)
        else:
            await ctx.send(f"{globe.errorx} That timezone isn't available")
            return

        time = dt.datetime.now(zone)

        time = time.strftime("%-I:%M%P on %A, %-d %b")

        await ctx.send(f"🌐 {time} in `{tz}`")

    @timein.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't provide a timezone")


def setup(bot):
    bot.add_cog(Public(bot))
