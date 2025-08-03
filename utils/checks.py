from discord.ext import commands
from config import STAFF_ROLE_ID, PIC_PERM_ROLE_ID, LINK_PERM_ROLE_ID

def is_staff():
    async def predicate(ctx):
        if any(role.id == STAFF_ROLE_ID for role in ctx.author.roles):
            return True
        raise commands.MissingPermissions(["Staff Role"])
    return commands.check(predicate)

def has_pic_perm():
    async def predicate(ctx):
        if any(role.id == PIC_PERM_ROLE_ID for role in ctx.author.roles):
            return True
        raise commands.MissingPermissions(["Pic Perm Role"])
    return commands.check(predicate)

def has_link_perm():
    async def predicate(ctx):
        if any(role.id == LINK_PERM_ROLE_ID for role in ctx.author.roles):
            return True
        raise commands.MissingPermissions(["Link Perm Role"])
    return commands.check(predicate)
