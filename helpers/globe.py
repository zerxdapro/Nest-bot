import discord

# global variables

# server IDs
serv_id = 624784883251675136
test_id = 472333365610151936

# channels
react_id = 626340503918739456
welcome_id = 624785035437801492
intro_id = 627986269900898325
audit_id = 625115043356475394
suggest_id = 624785660682960916
main_id = 624785415651590155
# Categories
ticket_cat = 636874065570955264

# fix
admin = 625116240771284994
mod = 625116299227299840

# roles
member_role = 633963699413188609
rule_id = 624784883251675138
cmd_id = 625115068862038016
pin_id = 624785636678828034
qotd_id = 626172681955573775
bot_2_id = 627985907013910538
bday_id = 631704872516845579
muted = 636667306923130911

# emojis
errorx = "<:redcross:608943524075012117>"
upvote = "<:upvote:625819552466468895>"
downvote = "<:downvote:625819552177192966>"
tick = "<:greentick:608943523823222785>"


pending_events = []


# checks

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



def check_main_serv(ctx):
    return serv_id == ctx.guild.id
