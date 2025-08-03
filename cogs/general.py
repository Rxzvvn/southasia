import discord
from discord.ext import commands, tasks
from utils.embed import create_embed, create_error_embed, create_info_embed, create_success_embed
from utils.logger import log_command
import json
from datetime import datetime
from pathlib import Path
import asyncio

BIRTHDAY_PATH = Path("data/birthdays.json")

def load_birthdays():
    if not BIRTHDAY_PATH.exists():
        return {}
    with open(BIRTHDAY_PATH, "r") as f:
        return json.load(f)

def save_birthdays(data):
    with open(BIRTHDAY_PATH, "w") as f:
        json.dump(data, f, indent=4)

birthdays = load_birthdays()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_reminder_loop.start()

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        embed = discord.Embed(
            title=f"{user.name}'s Avatar",
            description=f"[Click to view]({user.display_avatar.url})",
            color=discord.Color.blue()
        )
        embed.set_image(url=user.display_avatar.url)
        await ctx.send(embed=embed)
        await log_command(ctx, "avatar", {"user": str(user)})

    @commands.command()
    async def donate(self, ctx):
        embed = create_embed(
            ctx,
            title="Support the Bot",
            description="You can donate to support the bot's hosting expenses [here](https://donatebot.io/).",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "donate", {})

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title="Server Info",
            description=f"Information about **{guild.name}**",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)
        await log_command(ctx, "serverinfo", {})

    @commands.command(aliases=["whois"])
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in member.roles[1:]] or ["None"]

        embed = discord.Embed(
            title=f"🔍 User Info: {member}",
            color=member.color,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Top Role", value=member.top_role.mention)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d %b %Y"))
        embed.add_field(name="Created Account", value=member.created_at.strftime("%d %b %Y"))
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)
        await ctx.send(embed=embed)
        await log_command(ctx, "userinfo", {"user": str(member)})

    @commands.group(invoke_without_command=True)
    async def birthday(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        uid = str(member.id)
        if uid not in birthdays:
            return await ctx.send(embed=create_info_embed("Birthday Not Set", f"{member.mention} has not set a birthday."))

        date = datetime.strptime(birthdays[uid], "%Y-%m-%d")
        embed = discord.Embed(
            title="🎂 Birthday Info",
            description=f"{member.mention}'s birthday is on **{date.strftime('%d %B')}**",
            color=discord.Color.pink()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "birthday", {"user": str(member)})

    @birthday.command(name="set")
    async def set_birthday(self, ctx, date: str = None):
        if not date:
            return await ctx.send(embed=create_error_embed(
                title="Missing Date",
                reason="You must provide a date in the format YYYY-MM-DD.",
                usage=",birthday set 2005-03-20",
                example=",birthday set 2003-11-15"
            ))
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            if dt.year > 2025 or dt.year < 1900:
                raise ValueError
        except:
            return await ctx.send(embed=create_error_embed(
                title="Invalid Format",
                reason="Please use the format: `YYYY-MM-DD`.",
                usage=",birthday set 2005-04-12",
                example=",birthday set 1999-12-31"
            ))

        uid = str(ctx.author.id)
        birthdays[uid] = date
        save_birthdays(birthdays)

        embed = discord.Embed(
            title="✅ Birthday Saved",
            description=f"Your birthday was set to **{dt.strftime('%d %B')}**.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "birthday set", {"date": date})

    @birthday.command(name="remove")
    async def remove_birthday(self, ctx):
        uid = str(ctx.author.id)
        if uid in birthdays:
            del birthdays[uid]
            save_birthdays(birthdays)
            embed = create_success_embed("Birthday Removed", "Your birthday has been removed.")
            await ctx.send(embed=embed)
            await log_command(ctx, "birthday remove", {})
        else:
            await ctx.send(embed=create_info_embed("Not Set", "You don’t have a birthday saved."))

    @commands.command(name="birthdays")
    async def list_birthdays(self, ctx):
        if not birthdays:
            return await ctx.send(embed=create_info_embed("🎉 Birthdays", "No birthdays are currently registered."))

        sorted_data = sorted(birthdays.items(), key=lambda x: x[1])
        desc = ""
        for uid, date in sorted_data:
            user = ctx.guild.get_member(int(uid))
            name = user.mention if user else f"`{uid}`"
            dt = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B")
            desc += f"🎂 {name} — {dt}\n"

        embed = discord.Embed(
            title="🎉 Registered Birthdays",
            description=desc[:4000],
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "birthdays", {})

    @tasks.loop(hours=24)
    async def birthday_reminder_loop(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(1400809302423375942)
        if not channel:
            return

        today = datetime.utcnow().strftime("%m-%d")
        for uid, date in birthdays.items():
            if datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d") == today:
                user = self.bot.get_user(int(uid))
                if user:
                    embed = discord.Embed(
                        title="🎉 Happy Birthday!",
                        description=f"Everyone wish {user.mention} a wonderful birthday! 🎂",
                        color=discord.Color.gold()
                    )
                    embed.set_thumbnail(url=user.display_avatar.url)
                    await channel.send(embed=embed)

    @birthday_reminder_loop.before_loop
    async def before_birthday_loop(self):
        now = datetime.utcnow()
        next_run = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run = next_run.replace(day=now.day + 1)
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)

async def setup(bot):
    await bot.add_cog(General(bot))