from discord.ext import commands
import discord
from helpers import globe
import yaml


"""
Dont ever use this again quantum. seriously.
"""


def story_channel(ctx):
    return ctx.channel.id == globe.story_id


class Story(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_data = yaml.load(open("data/bot.yml", "r"))
        # print(self.bot_data)
        self.story_id = self.bot_data["story_msg"]
        self.user_buffer = None

    @commands.Cog.listener()
    async def on_message(self, ctx):
        msg = ctx.content

        if not story_channel(ctx):
            return
        elif ctx.author.id == self.bot.user.id:
            return
        elif ctx.author == self.user_buffer:  # if author is the last person to add
            await ctx.channel.send(f"{globe.errorx} You were the last person to add to the story", delete_after=5)
            await ctx.delete(delay=5)
            return
        elif len(msg.split(" ")) > 1:  # if more than one word in message
            await ctx.channel.send(f"{globe.errorx} Your addition can only be one word", delete_after=5)
            await ctx.delete(delay=5)
            return
        elif "@" in msg:
            await ctx.channel.send(f"{globe.errorx} Your message can't contain a '@' in it", delete_after=5)
            await ctx.delete(delay=5)
            return
        elif len(msg) > 20:
            await ctx.channel.send(f"{globe.errorx} Your addition is too long", delete_after=5)
            await ctx.delete(delay=5)
            return

        story_msg = await ctx.channel.fetch_message(self.story_id)
        if story_msg.content.startswith("(The last person to add to the story was "):
            content = story_msg.content
            content = content.split("\n", 2)[2]
        else:
            content = ""

        if msg == ".":
            appended = f"(The last person to add to the story was {ctx.author.display_name})\n\n{content}. "
        else:
            appended = f"(The last person to add to the story was {ctx.author.display_name})\n\n{content} {msg}"

        if len(appended) > 2000:
            await story_msg.edit(content=story_msg.content.split("\n", 2)[2])
            appended = "(The last person to add to the story was {})\n\n{}".format(ctx.author.display_name, msg)
            story_msg = await ctx.channel.send(appended)

            self.story_id = story_msg.id
            self.bot_data["story_msg"] = story_msg.id
            yaml.dump(self.bot_data, open("data/bot.yml", "w"))

        else:
            await story_msg.edit(content=appended)
        self.user_buffer = ctx.author
        await ctx.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.check(story_channel)
    async def set(self, ctx, *, args):
        story_msg = await ctx.channel.fetch_message(self.story_id)
        await story_msg.edit(content=args)


def setup(bot):
    bot.add_cog(Story(bot))
