from discord.ext import commands
import discord
from helpers import globe

PUSHPIN = "📌"
threshhold = 3


class Pin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = []

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == PUSHPIN and not (reaction.message.author == self.bot.user and reaction.message.channel.id == globe.pin_id):
            count = len(await reaction.users().flatten())
            if count >= threshhold and reaction.message.id not in self.cache:
                server = self.bot.get_guild(globe.serv_id)
                channel = server.get_channel(globe.pin_id)

                colour = 0xdd2e44
                message = reaction.message
                author = message.author

                link = message.jump_url

                embed = discord.Embed(description=message.content, colour=colour)
                embed.set_author(name=author.display_name, icon_url=author.avatar_url)
                embed.add_field(name="Details", value=f"[LINK]({link})")

                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)

                await channel.send(f"{PUSHPIN} Message in {message.channel.mention} by {author.mention} was pinned", embed=embed)
                self.cache.append(message.id)


def setup(bot):
    bot.add_cog(Pin(bot))
