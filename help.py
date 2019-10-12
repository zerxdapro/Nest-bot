from discord.ext import commands
import discord
import globe

cmd = {
    "help": {"description": "You are here: list all the commands. If an argument is supplied, the specific help command for that input will be shown", "args": "{command}", "mod": False},
    "colour": {"description": "Display an image of that hex colour", "args": "[hexcol]", "mod": False},
    "testcol": {"description": "Simulate what it would be like if your username was #[hexcol]", "args": "[hexcol]", "mod": False},
    "whois": {"description": "Show information on a user (defaults to you)", "args": "{user}", "mod": False},
    "pfp": {"description": "Display your profile picture. If {user} is provided, it will display their profile picture", "args": "{user}", "mod": False},
    "yt": {"description": "Shows a youtube video's name, channel and thumbnail."
                          "Sometimes discord doesnt show the embed properly so you can use this", "args": "[url]", "mod": False},
    "server": {"description": "Show information on the current server", "args": "", "mod": False},
    "level": {"description": "See someones current level and xp. If you dont specify a user, it will default to you", "args": "{user}", "mod": False},
    "top": {"description": "See the top 10 people on the server leaderboard of activity levels", "args": "", "mod": False},
    "announce": {"description": "Sends [message] in [channel] (can be #channel or the channel ID",
                 "args": "[channel] [message]", "mod": True},
    "addrole": {"description": "Add [role] to [user]", "args": "[user] [role]", "mod": True},
    "kick": {"description": "Kick [user]. Reason is optional", "args": "[user] [reason]", "mod": True},
    "ban": {"description": "Ban [user]. Reason is optional", "args": "[user] [reason]", "mod": True},
    "unban": {"description": "Unban [user]", "args": "[user]", "mod": True},
    "mute": {"description": "Stop [user] for typing for [time] (in minutes e.g. `10`. Time and Reason is optional",
             "args": "[user] [time] [reason]", "mod": True},
    "unmute": {"description": "Unmute [user]", "args": "[user]", "mod": True},
    "purge": {"description": "Delete the last [number] messages in that channel", "args": "[number]", "mod": True},
    "warnings": {"description": "Get all the warnings. If {user} is provided, "
                                "only their warnings will be displayed", "args": "{user}", "mod": True},
    "warn": {"description": "Add a warning for [user]. They will be DMed the reason", "args": "[user] [reason]",
             "mod": True},
    "unwarn": {"description": """Remove the warning from [user]. [snippet] must be a part of the [reason] from /warn. 
    If someone's reason was `rule 1 violation, you stink`, your [snippet] could be `rule 1` or `you stink`. \nYou cant 
    unwarn yourself""", "args": "[user] [snippet]", "mod": True},
    "addrule": {
        "description": "Add a rule to the rules channel. Put [title] and [description] in quotes, the rule number "
                       "will be automatically added to the title",
        "args": "[title] [description]", "mod": True},
    "removerule": {"description": "Remove the rule [number]", "args": "[number]", "mod": True},
    "editrule": {
        "description": "Edit rule [number]. Put [title] and [description] in quotes, the rule number will be "
                       "automatically added to the title",
        "args": "[number] [title] [description]", "mod": True}

}

arg_details = {
    "user": {"input": ["User ID", "Nickname", "Username", "Ping", "Username#number"]},
    "role": {"input": ["Role ID", "Role ping", "Role name"]},
    "channel": {"input": ["Channel ID", "Channel Mention", "Channel name"]},
    "number": {"input": ["A numerical value"]},
    "hexcol": {"input": ["6 digit hexadecimal value"]},
    "url": {"input": ["A url"]},
    "command": {"input": ["A bot command without the /"]},
    "time": {"input": ["1 hrs, 2 minutes", "5min", "2 days 6 seconds", "1 day 4 hours 5 minutes 2 secs"]},
    "title": {"input": ["Any text"]},
    "description": {"input": ["Any text"]},
    "snippet": {"input": ["A portion of the warning"]},
    "reason": {"input": ["The reason for the punishment"]},
    "message": {"input": ["The message to send"]}
}


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command=None):

        bot_cogs = self.bot.cogs.values()
        all_commands = [x.get_commands() for x in bot_cogs]
        all_commands = [x for x in all_commands if x]  # remove cogs where there are no commands
        all_commands = sum(all_commands, [])  # flatten 2d array
        aliases = [[x.name]+x.aliases for x in all_commands]

        if command == "public" or not command:  # full help message
            if globe.check_mod(ctx):
                moderator = True
            else:
                moderator = False

            if command == "public":
                moderator = False

            p = self.bot.command_prefix
            bot = ctx.guild.get_member(self.bot.user.id)
            embed = discord.Embed(title=f"{bot.display_name} Command List", colour=bot.colour)

            for i in cmd.keys():
                if cmd[i]["mod"] and not moderator:
                    break
                name = i
                desc = cmd[i]["description"]
                mod = cmd[i]["mod"]
                c_args = cmd[i]["args"]
                embed.add_field(name=f"{p}{name} {c_args}", value=desc, inline=False)

            await ctx.send(embed=embed)

        else:  # help message for certain command
            listing = [x for x in aliases if command in x]  # get aliases list for command
            if listing:  # listing should never be empty but just in case
                listing = listing[0]  # i <3 generators
                tcommand = [x for x in listing if x in cmd]  # get the command that is in the cmd list
                if tcommand:  # in case no alias matches, we want to keep "command"
                    command = tcommand[0]

            try:
                data = cmd[command]
            except KeyError:
                await ctx.send(f"{globe.errorx} That is not an available command")
                return

            if data["mod"] and not globe.check_mod(ctx):
                await ctx.send(f"{globe.errorx} The {command} command is for mods only")
                return

            bot_member = ctx.guild.get_member(self.bot.user.id)
            embed = discord.Embed(title=f"/{command} {data['args']}", description=data["description"], colour=bot_member.colour)

            aliases = [x for x in aliases if command in x]
            # realistically aliases should always return something but i dont trust it

            if aliases and len(aliases[0]) != 1:
                aliases = "**Aliases:** " + ", ".join(aliases[0])
                embed.description = aliases + "\n" + embed.description

            if data["args"]:
                embed.description += "\n\n__**Arguments**__"
                args = data["args"].split(" ")
            else:
                args = []
            for i in args:
                raw = i
                i = i[1:-1]

                title = i.title()
                if raw[0] == "{":
                    title += " (optional)"

                try:
                    details = arg_details[i]
                    description = ""
                    for i2 in details["input"]:
                        description += f"\n▫ {i2}"

                    embed.add_field(name=title, value=description, inline=False)
                except KeyError:
                    embed.add_field(name=title, value="[No entry for that argument exists]", inline=False)

            if len(args) > 1:
                embed.set_footer(text='If there are multiple arguments in a command, arguments that have spaces will '
                                      'require quotation marks. e.g. "Quantum Cucumber"')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
