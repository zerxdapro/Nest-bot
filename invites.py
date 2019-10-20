from discord.ext import commands
import discord
import globe
from collections import namedtuple

Inv = namedtuple("Inv", "user code uses temp")


async def format_invites(guild):
    invites = await guild.invites()
    output = []
    for i in invites:
        code = i.id
        user = i.inviter.display_name
        uses = i.uses
        temp = i.max_age == 0
        output.append(Inv(user, code, uses, temp))
    return output


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(globe.serv_id)
        self.invites = None

    async def setup(self):
        self.invites = await format_invites(self.guild)

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_member_join(self, member):
        embed = discord.Embed(colour=0x66e458)
        embed.set_author(name="Member Joined", icon_url=member.avatar_url)

        current = await format_invites(member.guild)
        channel = self.guild.get_channel(globe.audit_id)
        for i in current:  # for EVERY server invite
            search = [x for x in self.invites if x.code == i.code]  # get all with same code
            if not search:  # if no code was found, must be new invite
                if i.uses == 1:
                    embed.description = f"User {member.display_name} joined with invite from {i.user} ({i.code})"
                    await channel.send(embed=embed)
                elif i.uses > 1:  # invite is used more than once and isnt in the list?
                    print("unlogged invite on new invite")
            elif len(search) == 1:  # we have found a shared invite
                if i.uses == search[0].uses + 1:  # gottem
                    embed.description = f"User {member.display_name} joined with invite from {i.user} ({i.code})"
                    await channel.send(embed=embed)
                elif i.uses > search[0].uses + 1:  # unlogged invites
                    print("unlogged invite")
            else:  # duplicate invites
                print("duplicate invites")

        await self.setup()


def setup(bot):
    bot.add_cog(Invites(bot))
