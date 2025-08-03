import discord
from config import LOG_CHANNEL_ID

async def log_command(ctx: discord.ext.commands.Context):
    if ctx.guild is None:  # Ignore DMs
        return

    log_channel = ctx.bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return  # Channel not found

    embed = discord.Embed(
        title="📝 Command Executed",
        description=f"**Command:** `{ctx.command}`",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 User", value=f"{ctx.author} (`{ctx.author.id}`)", inline=False)
    embed.add_field(name="💬 Channel", value=f"{ctx.channel.mention}", inline=True)
    embed.add_field(name="📥 Message", value=f"`{ctx.message.content}`", inline=False)
    embed.set_footer(text=f"Guild: {ctx.guild.name} | ID: {ctx.guild.id}")
    embed.timestamp = ctx.message.created_at

    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"⚠️ Failed to log command: {e}")
