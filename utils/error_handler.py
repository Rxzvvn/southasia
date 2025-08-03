import discord
from discord.ext import commands
from utils.embeds import create_error_embed

async def handle_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        embed = create_error_embed(
            title="❌ Unknown Command",
            reason="This command does not exist.",
            usage=",<command> <args>",
            example=",help"
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = create_error_embed(
            title="❌ Missing Argument",
            reason=f"You missed a required argument: `{error.param.name}`.",
            usage=f",{ctx.command.qualified_name} <{error.param.name}>",
            example=f",{ctx.command.qualified_name} example"
        )
    elif isinstance(error, commands.MissingPermissions):
        embed = create_error_embed(
            title="❌ Missing Permissions",
            reason="You don’t have permission to use this command.",
            usage=f",{ctx.command.qualified_name}",
            example=f",{ctx.command.qualified_name} @user"
        )
    elif isinstance(error, commands.CommandOnCooldown):
        embed = create_error_embed(
            title="⏳ Command Cooldown",
            reason=f"You're using this command too fast. Try again in {round(error.retry_after, 1)} seconds.",
            usage=f",{ctx.command.qualified_name}",
            example=f",{ctx.command.qualified_name} ..."
        )
    else:
        embed = create_error_embed(
            title="🚨 Unknown Error",
            reason=str(error),
            usage=f",{ctx.command.qualified_name}",
            example=f",{ctx.command.qualified_name} ..."
        )
        # Log the traceback to console for devs
        import traceback
        print("Unhandled Command Error:")
        traceback.print_exception(type(error), error, error.__traceback__)

    try:
        await ctx.reply(embed=embed, mention_author=False)
    except:
        await ctx.send(embed=embed)
