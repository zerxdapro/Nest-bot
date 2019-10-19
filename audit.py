from discord.ext import commands
import discord
import globe


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_message_delete(self, message):
        if not message.guild.id == globe.serv_id:
            return
        if message.author.bot:
            return
        embed = discord.Embed(description=f"**Message Deleted in {message.channel.mention}**\n{message.content}", colour=0xe47b58)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        embed.set_footer(text=message.created_at.strftime("%-I:%M%p, %-d %b %Y"))

        server = self.bot.get_guild(globe.serv_id)
        channel = server.get_channel(globe.audit_id)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_message_edit(self, old_message, message):
        if message.author.bot:
            return
        if message.content == old_message.content:
            return
        embed = discord.Embed(colour=0x58c1e4, description=f"**Message from {message.author.mention} edited in {message.channel.mention}**", url=message.jump_url)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        embed.add_field(name="Old", value=old_message.content, inline=False)
        embed.add_field(name="New", value=message.content, inline=False)
        if message.edited_at:
            embed.set_footer(text=message.edited_at.strftime("%-I:%M%p, %-d %b %Y"))

        server = self.bot.get_guild(globe.serv_id)
        channel = server.get_channel(globe.audit_id)
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    @commands.check(globe.check_main_serv)
    async def on_member_update(self, old, new):
        if old.display_name != new.display_name:
            embed = discord.Embed(colour=0xe4e458, description=f"**Username changed**")
            embed.set_author(name=new.display_name, icon_url=new.avatar_url)
            embed.add_field(name="Old", value=old.display_name, inline=False)
            embed.add_field(name="New", value=new.display_name, inline=False)

            server = self.bot.get_guild(globe.serv_id)
            channel = server.get_channel(globe.audit_id)
            await channel.send(embed=embed)
        elif old.roles != new.roles:
            if [x for x in old.roles if x not in new.roles]:  # remove role
                aor = "removed from"
                role = [x for x in old.roles if x not in new.roles][0]
            elif [x for x in new.roles if x not in old.roles]:
                aor = "added to"
                role = [x for x in new.roles if x not in old.roles][0]
            else:
                return
            embed = discord.Embed(colour=0xc158e4, description=f"**Role {aor} {new.mention}**")
            embed.add_field(name="Role:", value=role, inline=False)
            embed.set_author(name=new.display_name, icon_url=new.avatar_url)

            server = self.bot.get_guild(globe.serv_id)
            channel = server.get_channel(globe.audit_id)
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
