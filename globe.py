import discord
from discord.ext import commands

# global variables

fserv_id = 624784883251675136
welcome_id = 624785035437801492  # correct for prod
# intro_id = 600873358715912200
# 608207927945461780
audit_id = 625115043356475394  # correct
mod_suggest_id = 624785660682960916

# fix
admin = 625116240771284994
mod = 625116299227299840
muted = 625248374127591434

# reg_id = 607607923232735242
rule_id = 624784883251675138
cmd_id = 625115068862038016
pin_id = 624785636678828034
qotd_id = 626172681955573775
bot_2_id = 627985907013910538

react_id = 626340503918739456  # correct

errorx = "<:redcross:608943524075012117>"
upvote = "<:upvote:625819552466468895>"
downvote = "<:downvote:625819552177192966>"


pending_events = []


def check_mod(ctx):
    if isinstance(ctx, discord.Member):
        author = ctx
    else:
        author = ctx.author
    role_ids = [x.id for x in author.roles]
    if set(role_ids) & {mod, admin}:
        return True
    else:
        return False


# def check_heads(ctx):
#     role_ids = [x.id for x in ctx.author.roles]
#     if set(role_ids) & {admin, head}:
#         return True
#     else:
#         return False
#
#
# def check_no_t(ctx):
#     if isinstance(ctx, commands.Context):
#         author = ctx.author
#     elif isinstance(ctx, discord.Member):
#         author = ctx
#     else:
#         author = ctx.author
#     role_ids = [x.id for x in author.roles]
#     if set(role_ids) & {mod, admin, head}:
#         return True
#     else:
#         return False
