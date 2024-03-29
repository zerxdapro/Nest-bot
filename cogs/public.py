from discord.ext import commands
import discord
from helpers import globe
import pytz
import datetime as dt
import re
import requests
from PIL import Image, ImageFont, ImageDraw
from helpers.image_handler import mask_circle_transparent
from bs4 import BeautifulSoup


class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, *, member: discord.Member = None):
        """
        Gathers some general information about the specified user
        If no user provided, the target will be yourself
        """
        if not member:
            member = ctx.author
        embed = discord.Embed(color=member.color)
        if str(embed.colour) == "#000000":  # if user doesnt have a role, make it white
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
            await ctx.send(f"{globe.errorx} I can't find that user")
        else:
            raise error

    @commands.command(aliases=["pfp", "picture", "image"])
    async def avatar(self, ctx, *, member: discord.Member = None):
        """
        Get the profile picture of a user. If no user is provided, it will show your profile picture.

        Sometimes the image may not be displayed, that is a discord side issue.
        """
        if not member:
            member = ctx.author
        embed = discord.Embed(title=member.display_name, color=member.colour, url=str(member.avatar_url))
        if str(embed.colour) == "#000000":
            embed.colour = 0xffffff
        embed.set_image(url=member.avatar_url)

        await ctx.send(embed=embed)

    @avatar.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{globe.errorx} I can't find that user")
        else:
            raise error

    @commands.command()
    async def server(self, ctx):
        """
        Show some general information on the current server
        """
        server = ctx.guild

        embed = discord.Embed(color=ctx.guild.get_member(self.bot.user.id).colour, description=f"**{server.name}**")
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Members", value=server.member_count, inline=False)
        embed.add_field(name="Region", value=str(server.region).title(), inline=False)
        embed.add_field(name="Owner", value=server.owner.mention, inline=False)
        embed.add_field(name="Creation Date", value=server.created_at.strftime('%d %b %Y'), inline=False)
        embed.add_field(name="ID", value=server.id, inline=False)

        await ctx.send(embed=embed)

    # i think discord fixed this but im proud of the code so i wont delete
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
        """
        Shows a list of timezones that can be used in the bot based of a search
        """
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
            await ctx.send(f"{globe.errorx} No timezones were found for that location\n This link may help: "
                           f"http://kevalbhatt.github.io/timezone-picker/ Select your location on the map and run "
                           f"this command again with the Country/City or Continent/City value from the site")

    @tzsearch.error
    async def do_repeat_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{globe.errorx} You didn't provide a timezone")
        else:
            raise error

    @commands.command()
    async def timein(self, ctx, tz):
        """
        Get the time in the specified timezone
        """
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
        else:
            raise error

    @commands.command(aliases=["bot", "botinfo"])
    async def info(self, ctx):
        """
        Show some basic info about the bot
        """
        bot = ctx.guild.get_member(self.bot.user.id)
        qc = await self.bot.fetch_user(self.bot.owner_id)  # if you clone this for some damn reason you better fix this
        embed = discord.Embed(colour=bot.colour)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Library", value="discord.py")
        embed.add_field(name="Code", value="[Github Repository](https://github.com/Quantum-Cucumber/nest-bot/)")
        embed.add_field(name="Creator", value=qc)

        await ctx.send(embed=embed)

    @commands.command(aliases=["color"])
    async def colour(self, ctx, hexcol):
        """
        Show an image of the given colour
        """
        rex = re.match(r"#([0-9a-f]{6})", hexcol, re.IGNORECASE)
        if rex:
            await ctx.trigger_typing()
            image = Image.new("RGB", (256, 256), hexcol)
            image.save("image.png")
            await ctx.send(f"🖌 Colour: {hexcol}", file=discord.File("image.png"))
        else:
            await ctx.send(f"{globe.errorx} That input is not a hexadecimal colour")

    @commands.command(aliases=["coltest", "colourtest", "role", "testcolour"])
    async def testcol(self, ctx, hexcol):
        """
        Creates an image showing what it would look like if your role was that colour
        """
        rex = re.match(r"#([0-9a-f]{6})", hexcol, re.IGNORECASE)
        if rex:
            await ctx.trigger_typing()
            font_path = "images/Whitney Medium.ttf"
            padding = 20
            pfp = Image.open(requests.get(ctx.author.avatar_url_as(format="png", size=128), stream=True).raw)
            pfp = mask_circle_transparent(pfp)
            font = ImageFont.truetype(font_path, 39)
            width = padding * 3 + font.getsize("M" * 32)[0] + 128
            height = 128 + padding * 2
            image = Image.new("RGBA", (width, height), "#36393f")
            image.paste(pfp, (padding, padding, 128 + padding, 128 + padding), pfp)

            font = ImageFont.truetype(font_path, 42)
            draw = ImageDraw.Draw(image)
            draw.text((128 + padding * 2, padding), ctx.author.display_name, font=font, fill=hexcol)
            draw.text((128 + padding * 2 + 1, padding), ctx.author.display_name, font=font, fill=hexcol)
            height = font.getsize(ctx.author.display_name)[1]
            font = ImageFont.truetype(font_path, 39)
            draw.text((128 + padding * 2, padding * 1.5 + height), f"{ctx.guild.name}", font=font,
                      fill="#dcddde")
            image.save("image.png")
            await ctx.send(f"🖌 Colour: {hexcol}", file=discord.File("image.png"))
        else:
            await ctx.send(f"{globe.errorx} That input is not a hexadecimal colour")


def setup(bot):
    bot.add_cog(Public(bot))
