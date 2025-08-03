import discord

def create_error_embed(title: str, reason: str, usage: str, example: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=f"❌ **Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.add_field(name="📘 Usage", value=usage, inline=False)
    embed.add_field(name="💡 Example", value=example, inline=False)
    embed.set_footer(text="Command failed")
    return embed

def create_success_embed(title: str, message: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=f"✅ {message}",
        color=discord.Color.green()
    )
    embed.set_footer(text="Command successful")
    return embed

def create_info_embed(title: str, message: str) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Info")
    return embed
