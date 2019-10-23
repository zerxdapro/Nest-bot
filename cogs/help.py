from discord.ext import commands
import discord
from helpers import globe

arg_details = {
    "user": {"input": ["User ID", "Username", "Ping", "Username#number"]},
    "member": {"input": ["User ID", "Nickname", "Username", "Ping", "Username#number"]},
    "role": {"input": ["Role ID", "Role ping", "Role name"]},
    "channel": {"input": ["Channel ID", "Channel Mention", "Channel name"]},
    "number": {"input": ["A numerical value"]},
    "hexcol": {"input": ["6 digit hexadecimal value", "#ff0000"]},
    "url": {"input": ["A url"]},
    "command": {"input": ["A bot command without the /"]},
    "time": {"input": ["1 hrs, 2 minutes", "5min", "2 days 6 seconds", "1 day 4 hours 5 minutes 2 secs"]},
    "title": {"input": ["Any text"]},
    "description": {"input": ["Any text"]},
    "snippet": {"input": ["A portion of the warning"]},
    "reason": {"input": ["The reason for the punishment"]},
    "message": {"input": ["The message to send"]},
    "timezone": {"input": ["A timezone, typically in the format Country/City"]},
    "question": {"input": ["The question to ask"]},
    "answers": {"input": ["All of the answers seperated by spaces"]},
    "name": {"input": ["idk"]},
    "code": {"input": ["Code to run"]},
    "cog": {"input": ["A cog to load into the bot"]},
    "date": {"input": ["1 Jan", "Feb 21"]},
    "time_and_reason": {"input": ["e"]}
}


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context, *, command=None):
        """
        You are here
        See all the available commands, if a command is specified `help command` the long help listing will be shown
        """
        if not command:
            cmd = list(self.bot.commands)
            server = self.bot.get_guild(globe.serv_id)

            title = f"{self.bot.user.name} Command List"
            embed = discord.Embed(colour=server.get_member(self.bot.user.id).colour)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name=title, icon_url=self.bot.user.avatar_url)

            out = ""

            for i in cmd:
                if not i.hidden:
                    try:
                        can_run = await i.can_run(ctx)
                    except Exception:
                        print("error")
                        can_run = False

                    if can_run:
                        embed.add_field(name=str(i), value=str(i.help).split("\n")[0], inline=False)

            await ctx.send(embed=embed)

        elif command == "public":
            cmd = list(self.bot.commands)
            server = self.bot.get_guild(globe.serv_id)

            title = f"{self.bot.user.name} Command List"
            embed = discord.Embed(colour=server.get_member(self.bot.user.id).colour)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_author(name=title, icon_url=self.bot.user.avatar_url)

            for i in cmd:
                if not i.hidden:
                    checks = list(map(str, i.checks))
                    checks = " ".join(checks)
                    if "check_mod" not in checks and "is_owner" not in checks:
                        embed.add_field(name=str(i), value=str(i.help).split("\n")[0], inline=False)

            await ctx.send(embed=embed)

        else:  # command supplied
            command = self.bot.get_command(command)

            if not command or command.hidden:
                await ctx.send(f"{globe.errorx} That command doesn't exist")
                return

            try:
                can_run = await command.can_run(ctx)
            except Exception:
                await ctx.send(f"{globe.errorx} You aren't allowed to run the `{command.qualified_name}` command")
                return

            if not can_run:
                await ctx.send(f"{globe.errorx} You aren't allowed to run the `{command.qualified_name}` command")
                return

            desc = command.help
            aliases = ", ".join(command.aliases)
            if aliases:
                desc = f"**Aliases:** {aliases}\n{desc}"

            args = command.clean_params
            title = f"{self.bot.command_prefix}{command.qualified_name} "

            embed = discord.Embed(title=title, colour=ctx.guild.get_member(self.bot.user.id).colour)

            arguments = []  # generate arguments
            for i in args:
                i = args[i]
                optional = i.default

                examples = list(arg_details[i.name].values())[0]
                examples = "\n▫ " + "\n▫ ".join(examples)
                if optional:
                    title += f"[{i.name}] "
                    embed.add_field(name=i.name.title(), value=examples, inline=False)
                else:
                    title += f"{{{i.name}}} "
                    embed.add_field(name=f"{i.name.title()} (optional)", value=examples, inline=False)

            embed.description = desc
            embed.title = title
            embed.set_thumbnail(url=self.bot.user.avatar_url)

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
