import discord
from discord.ext import commands
from utils.checks import is_staff
from utils.embeds import create_error_embed, create_success_embed, create_info_embed
from utils.logger import log_command
from utils.data_handler import load_warnings, save_warnings

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.command(name="warn", aliases=["w"])
    @is_staff()
    async def warn_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to warn.",
                usage=",warn @user <reason>",
                example=",warn @Troll Spamming links"
            )
            return await ctx.send(embed=embed)

        # DM the user
        try:
            await member.send(
                f"⚠️ You have been warned in **{ctx.guild.name}** by {ctx.author}.\nReason: **{reason}**"
            )
        except:
            pass  # DMs closed

        # Store warning in JSON
        user_id = str(member.id)
        if user_id not in self.warnings_data:
            self.warnings_data[user_id] = []

        self.warnings_data[user_id].append({
            "moderator": str(ctx.author),
            "reason": reason
        })
        save_warnings(self.warnings_data)

        # Confirmation to the moderator
        embed = create_success_embed(
            title="User Warned",
            message=f"{member.mention} has been warned for: **{reason}**"
        )
        await ctx.send(embed=embed)

        # Friendly syntax reminder
        if ctx.invoked_with == "warn":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="You can use `,w` instead of `,warn` to save time!"
            )
            await ctx.send(embed=tip)

        # Log command
        await log_command(ctx)


async def setup(bot):
    await bot.add_cog(Moderation(bot))

    @commands.command(name="ban", aliases=["b"])
    @is_staff()
    async def ban_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to ban.",
                usage=",ban @user <reason>",
                example=",ban @Raider Alt account"
            )
            return await ctx.send(embed=embed)

        try:
            await member.send(f"🔨 You have been banned from **{ctx.guild.name}**.\nReason: **{reason}**")
        except:
            pass  # DMs off

        try:
            await member.ban(reason=f"{reason} | Banned by {ctx.author}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Action Denied",
                reason="I don't have permission to ban that user.",
                usage=",ban @user <reason>",
                example=",ban @Spammer Posting NSFW"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="User Banned",
            message=f"{member.mention} has been banned for: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "ban":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Next time you can use `,b` instead of `,ban` to save time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

import re

def parse_duration(time_str):
    match = re.match(r"(\d+)([smhd])", time_str)
    if not match:
        return None
    time_value, unit = int(match.group(1)), match.group(2)
    return {
        "s": time_value,
        "m": time_value * 60,
        "h": time_value * 3600,
        "d": time_value * 86400
    }.get(unit, None)

    @commands.command(name="tempban", aliases=["tb"])
    @is_staff()
    async def tempban_user(self, ctx, member: discord.Member = None, time: str = None, *, reason: str = "No reason provided."):
        if not member or not time:
            embed = create_error_embed(
                title="Missing Arguments",
                reason="You must specify a user and a time duration.",
                usage=",tempban @user 2h <reason>",
                example=",tempban @Spammer 1d Raid attempt"
            )
            return await ctx.send(embed=embed)

        duration_seconds = parse_duration(time)
        if not duration_seconds:
            embed = create_error_embed(
                title="Invalid Time Format",
                reason="Time format must be like `10m`, `2h`, or `1d`.",
                usage=",tempban @user 10m <reason>",
                example=",tempban @Troll 30m Spamming links"
            )
            return await ctx.send(embed=embed)

        try:
            await member.send(f"⛔ You have been temporarily banned from **{ctx.guild.name}** for {time}.\nReason: **{reason}**")
        except:
            pass

        try:
            await member.ban(reason=f"Tempbanned by {ctx.author} for {time} | {reason}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Ban Failed",
                reason="I don't have permission to ban that user.",
                usage=",tempban @user 10m <reason>",
                example=",tempban @Spammer 30m Flooding voice"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="User Tempbanned",
            message=f"{member.mention} has been banned for **{time}**.\nReason: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "tempban":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Use `,tb` instead of `,tempban` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

        # Schedule unban
        async def unban_later():
            await asyncio.sleep(duration_seconds)
            try:
                await ctx.guild.unban(member, reason="Tempban expired")
                await ctx.channel.send(f"🔓 {member} has been unbanned after tempban.")
            except:
                pass

        self.bot.loop.create_task(unban_later())

    @commands.command(name="kick", aliases=["k"])
    @is_staff()
    async def kick_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to kick.",
                usage=",kick @user <reason>",
                example=",kick @Troll Advertising scam links"
            )
            return await ctx.send(embed=embed)

        try:
            await member.send(f"👢 You have been kicked from **{ctx.guild.name}**.\nReason: **{reason}**")
        except:
            pass  # DMs closed

        try:
            await member.kick(reason=f"Kicked by {ctx.author} | {reason}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Kick Failed",
                reason="I don't have permission to kick that user.",
                usage=",kick @user <reason>",
                example=",kick @Troll NSFW in VC"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="User Kicked",
            message=f"{member.mention} has been kicked for: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "kick":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="You can use `,k` instead of `,kick` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="jail", aliases=["j"])
    @is_staff()
    async def jail_user(self, ctx, member: discord.Member = None, time: str = None, *, reason: str = "No reason provided."):
        JAIL_ROLE_ID = 1401353254083760160
        jail_role = ctx.guild.get_role(JAIL_ROLE_ID)

        if not member or not time:
            embed = create_error_embed(
                title="Missing Arguments",
                reason="You must specify a user and a time duration.",
                usage=",jail @user 30m <reason>",
                example=",jail @Raider 1h Spamming scam links"
            )
            return await ctx.send(embed=embed)

        duration_seconds = parse_duration(time)
        if not duration_seconds:
            embed = create_error_embed(
                title="Invalid Time Format",
                reason="Use formats like `10m`, `2h`, or `1d`.",
                usage=",jail @user 30m <reason>",
                example=",jail @Spammer 15m NSFW spam"
            )
            return await ctx.send(embed=embed)

        if not jail_role:
            return await ctx.send("⚠️ Jail role not found in the server.")

        # Store original roles (except @everyone)
        original_roles = [r for r in member.roles if r != ctx.guild.default_role]
        try:
            await member.send(f"🚨 You have been jailed in **{ctx.guild.name}** for {time}.\nReason: **{reason}**")
        except:
            pass

        try:
            await member.edit(roles=[jail_role], reason=f"Jailed by {ctx.author} | {reason}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Jail Failed",
                reason="I don't have permission to change that user's roles.",
                usage=",jail @user 30m <reason>",
                example=",jail @Alt 1h Raid links"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="User Jailed",
            message=f"{member.mention} has been jailed for **{time}**.\nReason: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "jail":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="You can use `,j` instead of `,jail` to save time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

        # Schedule unjail
        async def unjail_later():
            await asyncio.sleep(duration_seconds)
            try:
                await member.edit(roles=original_roles, reason="Jail expired")
                await ctx.channel.send(f"🔓 {member.mention} has been unjailed after {time}.")
            except:
                pass

        self.bot.loop.create_task(unjail_later())
        
            @commands.command(name="warnings", aliases=["warns"])
    @is_staff()
    async def check_warnings(self, ctx, member: discord.Member = None):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to check warnings.",
                usage=",warnings @user",
                example=",warnings @Spammer"
            )
            return await ctx.send(embed=embed)

        user_id = str(member.id)
        warnings = self.warnings_data.get(user_id, [])

        if not warnings:
            embed = create_info_embed(
                title="No Warnings",
                message=f"{member.mention} has no warnings on record."
            )
            return await ctx.send(embed=embed)

        description = ""
        for i, warn in enumerate(warnings, 1):
            mod = warn["moderator"]
            reason = warn["reason"]
            description += f"**{i}.** Warned by `{mod}`\n➡️ Reason: {reason}\n\n"

        embed = discord.Embed(
            title=f"📋 Warnings for {member}",
            description=description,
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Total Warnings: {len(warnings)}")
        await ctx.send(embed=embed)

        await log_command(ctx)

    @commands.command(name="history", aliases=["h"])
    @is_staff()
    async def command_history(self, ctx, member: discord.Member = None, command_type: str = None):
        if not member or not command_type:
            embed = create_error_embed(
                title="Missing Arguments",
                reason="You must mention a user and specify a command type.",
                usage=",history @user warn",
                example=",history @Spammer warn"
            )
            return await ctx.send(embed=embed)

        command_type = command_type.lower()

        if command_type not in ["warn", "warns", "warning", "warnings"]:
            embed = create_error_embed(
                title="Invalid Command Type",
                reason="Only `warn` history is currently supported.",
                usage=",history @user warn",
                example=",history @Spammer warn"
            )
            return await ctx.send(embed=embed)

        user_id = str(member.id)
        warnings = self.warnings_data.get(user_id, [])

        if not warnings:
            embed = create_info_embed(
                title="No Warnings Found",
                message=f"{member.mention} has no warning history."
            )
            return await ctx.send(embed=embed)

        description = ""
        for i, warn in enumerate(warnings, 1):
            mod = warn["moderator"]
            reason = warn["reason"]
            description += f"**{i}.** Warned by `{mod}`\n➡️ Reason: {reason}\n\n"

        embed = discord.Embed(
            title=f"📚 Warning History for {member}",
            description=description,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Command history: warn | Total: {len(warnings)}")
        await ctx.send(embed=embed)

        await log_command(ctx)

    @commands.command(name="stripstaff", aliases=["ss"])
    @is_staff()
    async def strip_staff_role(self, ctx, member: discord.Member = None):
        STAFF_ROLE_ID = 1400967381869658182
        staff_role = ctx.guild.get_role(STAFF_ROLE_ID)

        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to strip the Staff role from.",
                usage=",stripstaff @user",
                example=",stripstaff @InactiveMod"
            )
            return await ctx.send(embed=embed)

        if not staff_role or staff_role not in member.roles:
            embed = create_info_embed(
                title="No Staff Role",
                message=f"{member.mention} does not have the Staff role."
            )
            return await ctx.send(embed=embed)

        try:
            await member.remove_roles(staff_role, reason=f"Stripped by {ctx.author}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't remove the Staff role — check my role position.",
                usage=",stripstaff @user",
                example=",stripstaff @Staff"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="Staff Role Removed",
            message=f"{member.mention} has been stripped of the Staff role."
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "stripstaff":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Next time, you can use `,ss` instead of `,stripstaff`!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="lockdown", aliases=["ld"])
    @is_staff()
    async def lockdown_channel(self, ctx, duration: str = None, *, reason: str = "No reason provided."):
        if not duration:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must specify a duration for the lockdown.",
                usage=",lockdown 10m <reason>",
                example=",lockdown 5m Raid prevention"
            )
            return await ctx.send(embed=embed)

        seconds = parse_duration(duration)
        if not seconds:
            embed = create_error_embed(
                title="Invalid Time Format",
                reason="Use formats like `10m`, `2h`, or `1d`.",
                usage=",lockdown 10m <reason>",
                example=",lockdown 30m spam"
            )
            return await ctx.send(embed=embed)

        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False

        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't modify channel permissions.",
                usage=",lockdown 10m <reason>",
                example=",lockdown 15m bot raid"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔒 Channel Locked",
            message=f"{ctx.channel.mention} has been locked for **{duration}**.\nReason: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "lockdown":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Use `,ld` instead of `,lockdown` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

        # Schedule unlock
        async def unlock_channel_later():
            await asyncio.sleep(seconds)
            overwrite.send_messages = None  # Reset to default
            try:
                await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason="Lockdown expired")
                await ctx.send(f"🔓 {ctx.channel.mention} has been automatically unlocked.")
            except:
                pass

        self.bot.loop.create_task(unlock_channel_later())

    @commands.command(name="unlock", aliases=["ul"])
    @is_staff()
    async def unlock_channel(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages is not False:
            embed = create_info_embed(
                title="Not Locked",
                message="This channel isn’t currently locked for @everyone."
            )
            return await ctx.send(embed=embed)

        overwrite.send_messages = None  # Reset to default

        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason="Channel manually unlocked")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't change channel permissions to unlock it.",
                usage=",unlock",
                example=",unlock"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔓 Channel Unlocked",
            message=f"{ctx.channel.mention} has been manually unlocked by {ctx.author.mention}."
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "unlock":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="You can use `,ul` instead of `,unlock` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="modstats", aliases=["ms"])
    @is_staff()
    async def mod_stats(self, ctx):
        mod_name = str(ctx.author)
        warnings_issued = 0

        for warns in self.warnings_data.values():
            for warn in warns:
                if warn["moderator"] == mod_name:
                    warnings_issued += 1

        embed = discord.Embed(
            title=f"📈 Mod Stats: {ctx.author.display_name}",
            description="Here’s your current moderation activity:",
            color=discord.Color.purple()
        )
        embed.add_field(name="⚠️ Warnings Issued", value=warnings_issued, inline=False)
        embed.set_footer(text="Stats tracked since bot was last deployed.")

        await ctx.send(embed=embed)

        if ctx.invoked_with == "modstats":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="You can use `,ms` instead of `,modstats` to save time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="remind", aliases=["rm"])
    @is_staff()
    async def soft_remind(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to remind.",
                usage=",remind @user <reason>",
                example=",remind @User Be more respectful"
            )
            return await ctx.send(embed=embed)

        # Attempt to DM the user
        try:
            await member.send(
                f"📩 **Reminder from {ctx.guild.name}**\nA staff member has asked to remind you of the following:\n\n🔹 **Reason:** {reason}"
            )
        except discord.Forbidden:
            embed = create_error_embed(
                title="Failed to DM User",
                reason="The user has DMs disabled or blocked the bot.",
                usage=",remind @user <reason>",
                example=",remind @Troll Please read rules"
            )
            return await ctx.send(embed=embed)

        # Confirm to the moderator
        embed = create_success_embed(
            title="Reminder Sent",
            message=f"{member.mention} has been sent a soft reminder.\nReason: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "remind":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Next time you can use `,rm` instead of `,remind`!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="unjail", aliases=["uj"])
    @is_staff()
    async def unjail_user(self, ctx, member: discord.Member = None):
        JAIL_ROLE_ID = 1401353254083760160
        jail_role = ctx.guild.get_role(JAIL_ROLE_ID)

        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to unjail.",
                usage=",unjail @user",
                example=",unjail @User"
            )
            return await ctx.send(embed=embed)

        if not jail_role or jail_role not in member.roles:
            embed = create_info_embed(
                title="Not Jailed",
                message=f"{member.mention} is not jailed currently."
            )
            return await ctx.send(embed=embed)

        try:
            await member.remove_roles(jail_role, reason=f"Unjailed by {ctx.author}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't remove the jail role from that user.",
                usage=",unjail @user",
                example=",unjail @User"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔓 User Unjailed",
            message=f"{member.mention} has been manually unjailed."
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "unjail":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Next time you can use `,uj` instead of `,unjail`!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="unmute", aliases=["um"])
    @is_staff()
    async def unmute_user(self, ctx, member: discord.Member = None):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to unmute.",
                usage=",unmute @user",
                example=",unmute @MutedUser"
            )
            return await ctx.send(embed=embed)

        if not member.timed_out_until:
            embed = create_info_embed(
                title="Not Muted",
                message=f"{member.mention} is not currently timed out."
            )
            return await ctx.send(embed=embed)

        try:
            await member.edit(timeout=None, reason=f"Unmuted by {ctx.author}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't remove the timeout from that user. Make sure I have `MODERATE_MEMBERS` and my role is higher.",
                usage=",unmute @user",
                example=",unmute @Alt"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔊 User Unmuted",
            message=f"{member.mention} has been unmuted."
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "unmute":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Use `,um` instead of `,unmute` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)


    @commands.command(name="unban", aliases=["ub"])
    @is_staff()
    async def unban_user(self, ctx, *, user: str = None):
        if not user:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must specify the user ID or tag to unban.",
                usage=",unban user#0000",
                example=",unban 1234567890"
            )
            return await ctx.send(embed=embed)

        bans = await ctx.guild.bans()
        target = None
        for ban in bans:
            if str(ban.user.id) == user or str(ban.user) == user:
                target = ban.user
                break

        if not target:
            embed = create_info_embed(
                title="User Not Found",
                message="That user isn’t currently banned."
            )
            return await ctx.send(embed=embed)

        try:
            await ctx.guild.unban(target, reason=f"Unbanned by {ctx.author}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't unban that user.",
                usage=",unban user#0000",
                example=",unban 1234567890"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔓 User Unbanned",
            message=f"{target} has been unbanned."
        )
        await ctx.send(embed=embed)

        await log_command(ctx)

    @commands.command(name="mute", aliases=["m"])
    @is_staff()
    async def mute_user(self, ctx, member: discord.Member = None, time: str = None, *, reason: str = "No reason provided."):
        if not member or not time:
            embed = create_error_embed(
                title="Missing Arguments",
                reason="You must mention a user and duration.",
                usage=",mute @user 10m <reason>",
                example=",mute @Spammer 15m NSFW language"
            )
            return await ctx.send(embed=embed)

        seconds = parse_duration(time)
        if not seconds:
            embed = create_error_embed(
                title="Invalid Time Format",
                reason="Use formats like `10m`, `1h`, or `1d`.",
                usage=",mute @user 30m <reason>",
                example=",mute @User 1h Trolling"
            )
            return await ctx.send(embed=embed)

        try:
            until = discord.utils.utcnow() + discord.timedelta(seconds=seconds)
            await member.edit(timeout=until, reason=f"Muted by {ctx.author} | {reason}")
        except discord.Forbidden:
            embed = create_error_embed(
                title="Permission Error",
                reason="I couldn't timeout this user. I may lack `MODERATE_MEMBERS` or the user is above me.",
                usage=",mute @user 10m <reason>",
                example=",mute @Alt 20m mic spam"
            )
            return await ctx.send(embed=embed)

        embed = create_success_embed(
            title="🔇 User Muted",
            message=f"{member.mention} has been muted for **{time}**.\nReason: **{reason}**"
        )
        await ctx.send(embed=embed)

        if ctx.invoked_with == "mute":
            tip = create_info_embed(
                title="💡 Quick Tip",
                message="Use `,m` instead of `,mute` next time!"
            )
            await ctx.send(embed=tip)

        await log_command(ctx)

    @commands.command(name="notes")
    @is_staff()
    async def view_notes(self, ctx, member: discord.Member = None):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to view notes.",
                usage=",notes @user",
                example=",notes @SomeUser"
            )
            return await ctx.send(embed=embed)

        user_id = str(member.id)
        notes = self.notes_data.get(user_id, [])

        if not notes:
            embed = create_info_embed(
                title="No Notes Found",
                message=f"{member.mention} has no staff notes."
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f"🗒️ Notes for {member}",
            color=discord.Color.dark_teal()
        )
        for i, note in enumerate(notes, 1):
            embed.add_field(
                name=f"#{i} by {note['moderator']}",
                value=note['content'],
                inline=False
            )
        await ctx.send(embed=embed)

        await log_command(ctx)

    @commands.command(name="notes_add")
    @is_staff()
    async def add_note(self, ctx, member: discord.Member = None, *, note: str = None):
        if not member or not note:
            embed = create_error_embed(
                title="Missing Arguments",
                reason="You must mention a user and provide a note.",
                usage=",notes add @user <note>",
                example=",notes add @Raider Said slurs in VC"
            )
            return await ctx.send(embed=embed)

        user_id = str(member.id)
        if user_id not in self.notes_data:
            self.notes_data[user_id] = []

        self.notes_data[user_id].append({
            "moderator": str(ctx.author),
            "content": note
        })
        save_notes(self.notes_data)

        embed = create_success_embed(
            title="Note Added",
            message=f"Note added for {member.mention}."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="notes_clear")
    @is_staff()
    async def clear_notes(self, ctx, member: discord.Member = None):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to clear notes.",
                usage=",notes clear @user",
                example=",notes clear @Troll"
            )
            return await ctx.send(embed=embed)

        user_id = str(member.id)
        if user_id in self.notes_data:
            del self.notes_data[user_id]
            save_notes(self.notes_data)
            embed = create_success_embed(
                title="Notes Cleared",
                message=f"All notes cleared for {member.mention}."
            )
        else:
            embed = create_info_embed(
                title="No Notes",
                message=f"{member.mention} has no notes to clear."
            )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="jaillist")
    @is_staff()
    async def view_jailed_users(self, ctx):
        JAIL_ROLE_ID = 1401353254083760160
        jail_role = ctx.guild.get_role(JAIL_ROLE_ID)

        if not jail_role:
            embed = create_error_embed(
                title="Jail Role Missing",
                reason="The jail role could not be found. Please check the ID.",
                usage=",jaillist",
                example=",jaillist"
            )
            return await ctx.send(embed=embed)

        jailed_members = [member.mention for member in jail_role.members]

        if not jailed_members:
            embed = create_info_embed(
                title="No Jailed Members",
                message="There are currently no jailed users in this server."
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="🚨 Currently Jailed Users",
            description="\n".join(jailed_members),
            color=discord.Color.dark_red()
        )
        embed.set_footer(text=f"Total: {len(jailed_members)} users")
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="imute", aliases=["im"])
    @is_staff()
    async def image_mute(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to restrict.",
                usage=",imute @user <reason>",
                example=",imute @User Spamming NSFW links"
            )
            return await ctx.send(embed=embed)

        overwrite = ctx.channel.overwrites_for(member)
        overwrite.attach_files = False
        overwrite.embed_links = False

        try:
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=reason)
        except discord.Forbidden:
            return await ctx.send("❌ I don't have permission to change this member's channel settings.")

        embed = create_success_embed(
            title="📵 Image & Link Mute",
            message=f"{member.mention} can no longer send attachments or embed links in this channel."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="iumute", aliases=["ium"])
    @is_staff()
    async def image_unmute(self, ctx, member: discord.Member = None, *, reason: str = "Restoring link/image permission"):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to restore permissions to.",
                usage=",iumute @user",
                example=",iumute @User"
            )
            return await ctx.send(embed=embed)

        overwrite = ctx.channel.overwrites_for(member)
        overwrite.attach_files = None
        overwrite.embed_links = None

        try:
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=reason)
        except discord.Forbidden:
            return await ctx.send("❌ I don't have permission to update permissions for this user.")

        embed = create_success_embed(
            title="✅ Image & Link Unmuted",
            message=f"{member.mention}'s permissions to send files and embed links have been restored."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="rmute", aliases=["rm"])
    @is_staff()
    async def reaction_mute(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to restrict reactions.",
                usage=",rmute @user <reason>",
                example=",rmute @User Abusing reactions"
            )
            return await ctx.send(embed=embed)

        overwrite = ctx.channel.overwrites_for(member)
        overwrite.add_reactions = False
        overwrite.use_external_emojis = False

        try:
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=reason)
        except discord.Forbidden:
            return await ctx.send("❌ I can't update that member's channel permissions.")

        embed = create_success_embed(
            title="🔕 Reaction Mute",
            message=f"{member.mention} can no longer react or use external emojis in this channel."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="runmute", aliases=["rum"])
    @is_staff()
    async def reaction_unmute(self, ctx, member: discord.Member = None, *, reason: str = "Restoring reaction permission"):
        if not member:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to restore reaction permissions.",
                usage=",runmute @user",
                example=",runmute @User"
            )
            return await ctx.send(embed=embed)

        overwrite = ctx.channel.overwrites_for(member)
        overwrite.add_reactions = None
        overwrite.use_external_emojis = None

        try:
            await ctx.channel.set_permissions(member, overwrite=overwrite, reason=reason)
        except discord.Forbidden:
            return await ctx.send("❌ I can't restore that member's channel permissions.")

        embed = create_success_embed(
            title="✅ Reaction Unmuted",
            message=f"{member.mention}'s ability to react and use emojis has been restored."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="purge", aliases=["p"])
    @is_staff()
    async def purge_messages(self, ctx, amount: int = None):
        if not amount or amount < 1:
            embed = create_error_embed(
                title="Missing or Invalid Argument",
                reason="You must specify how many messages to delete.",
                usage=",purge 25",
                example=",purge 10"
            )
            return await ctx.send(embed=embed)

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)

        embed = create_success_embed(
            title="🧹 Messages Purged",
            message=f"Deleted **{len(deleted)}** messages from {ctx.channel.mention}."
        )
        await ctx.send(embed=embed, delete_after=5)
        await log_command(ctx)

    @commands.command(name="purge_links", aliases=["pl"])
    @is_staff()
    async def purge_links(self, ctx, amount: int = 100):
        await ctx.message.delete()

        def has_link(msg):
            return "http://" in msg.content or "https://" in msg.content

        deleted = await ctx.channel.purge(limit=amount, check=has_link)

        embed = create_success_embed(
            title="🔗 Links Purged",
            message=f"Deleted **{len(deleted)}** messages with links."
        )
        await ctx.send(embed=embed, delete_after=5)
        await log_command(ctx)

    @commands.command(name="purge_images", aliases=["pi"])
    @is_staff()
    async def purge_images(self, ctx, amount: int = 100):
        await ctx.message.delete()

        def has_attachment(msg):
            return len(msg.attachments) > 0

        deleted = await ctx.channel.purge(limit=amount, check=has_attachment)

        embed = create_success_embed(
            title="🖼️ Images Purged",
            message=f"Deleted **{len(deleted)}** messages with attachments."
        )
        await ctx.send(embed=embed, delete_after=5)
        await log_command(ctx)

    @commands.command(name="purge_contains", aliases=["pc"])
    @is_staff()
    async def purge_contains(self, ctx, word: str = None, amount: int = 100):
        if not word:
            embed = create_error_embed(
                title="Missing Word",
                reason="You must specify a word to match against.",
                usage=",purge contains badword",
                example=",pc scam"
            )
            return await ctx.send(embed=embed)

        await ctx.message.delete()

        def contains_word(msg):
            return word.lower() in msg.content.lower()

        deleted = await ctx.channel.purge(limit=amount, check=contains_word)

        embed = create_success_embed(
            title="🗑️ Word Filter Purge",
            message=f"Deleted **{len(deleted)}** messages containing `{word}`."
        )
        await ctx.send(embed=embed, delete_after=5)
        await log_command(ctx)

    @commands.command(name="purge_embeds", aliases=["pe"])
    @is_staff()
    async def purge_embeds(self, ctx, amount: int = 100):
        await ctx.message.delete()

        def has_embed(msg):
            return len(msg.embeds) > 0

        deleted = await ctx.channel.purge(limit=amount, check=has_embed)

        embed = create_success_embed(
            title="🧾 Embed Purge",
            message=f"Deleted **{len(deleted)}** messages with embeds."
        )
        await ctx.send(embed=embed, delete_after=5)
        await log_command(ctx)

    @commands.command(name="softban", aliases=["sb"])
    @is_staff()
    async def softban_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            return await ctx.send(embed=create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to softban.",
                usage=",softban @user <reason>",
                example=",softban @Alt Spam cleanup"
            ))

        try:
            await member.ban(reason=f"Softban by {ctx.author} | {reason}", delete_message_days=1)
            await ctx.guild.unban(member, reason="Softban complete")
        except discord.Forbidden:
            return await ctx.send("❌ I don’t have permission to softban that user.")

        embed = create_success_embed(
            title="🔨 Softban Executed",
            message=f"{member.mention} was softbanned and unbanned immediately."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="hardban", aliases=["hb"])
    @is_staff()
    async def hardban_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided."):
        if not member:
            return await ctx.send(embed=create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to hardban.",
                usage=",hardban @user <reason>",
                example=",hb @Troll Alt account"
            ))

        try:
            await member.ban(reason=f"Hardban by {ctx.author} | {reason}", delete_message_days=7)
        except discord.Forbidden:
            return await ctx.send("❌ I don’t have permission to hardban that user.")

        embed = create_success_embed(
            title="🚫 Hardban Executed",
            message=f"{member.mention} has been hardbanned and messages removed."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="clearinvites", aliases=["ci"])
    @is_staff()
    async def clear_all_invites(self, ctx):
        invites = await ctx.guild.invites()
        count = 0
        for invite in invites:
            try:
                await invite.delete(reason=f"Cleared by {ctx.author}")
                count += 1
            except:
                continue

        embed = create_success_embed(
            title="🔗 Invites Cleared",
            message=f"Deleted **{count}** invite links from the server."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="drag")
    @is_staff()
    async def drag_user(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send(embed=create_error_embed(
                title="Missing Argument",
                reason="You must mention a user to drag.",
                usage=",drag @user",
                example=",drag @User"
            ))

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be in a voice channel to drag someone.")

        try:
            await member.move_to(ctx.author.voice.channel)
        except discord.Forbidden:
            return await ctx.send("❌ I can’t move that user.")

        embed = create_success_embed(
            title="📥 User Dragged",
            message=f"{member.mention} has been moved to your voice channel."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="nuke")
    @is_staff()
    async def nuke_channel(self, ctx):
        channel = ctx.channel
        new_channel = await channel.clone(reason=f"Nuked by {ctx.author}")
        await channel.delete(reason="Nuked")

        embed = create_success_embed(
            title="💣 Channel Nuked",
            message=f"{channel.name} was nuked and recreated as {new_channel.mention}."
        )
        await new_channel.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="talk")
    @is_staff()
    async def allow_talking(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None

        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except:
            return await ctx.send("❌ I couldn't update permissions.")

        embed = create_success_embed(
            title="🔊 Talking Enabled",
            message="This channel is now open for messages."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="hide")
    @is_staff()
    async def hide_channel(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = False

        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except:
            return await ctx.send("❌ I couldn't hide the channel.")

        embed = create_success_embed(
            title="🙈 Channel Hidden",
            message="This channel is now hidden from @everyone."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="unhide")
    @is_staff()
    async def unhide_channel(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.view_channel = True

        try:
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except:
            return await ctx.send("❌ I couldn't unhide the channel.")

        embed = create_success_embed(
            title="👀 Channel Visible",
            message="This channel is now visible to @everyone."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="slowmode")
    @is_staff()
    async def set_slowmode(self, ctx, value: str = None):
        if not value:
            embed = create_error_embed(
                title="Missing Argument",
                reason="You must specify `off`, `on`, or a number of seconds.",
                usage=",slowmode 10",
                example=",slowmode off"
            )
            return await ctx.send(embed=embed)

        if value.lower() in ["off", "0"]:
            await ctx.channel.edit(slowmode_delay=0)
            msg = "Slowmode has been **disabled**."
        elif value.lower() == "on":
            await ctx.channel.edit(slowmode_delay=5)
            msg = "Slowmode set to **5 seconds**."
        elif value.isdigit():
            delay = int(value)
            if delay > 21600:
                return await ctx.send("⏱️ Slowmode cannot exceed 21600 seconds.")
            await ctx.channel.edit(slowmode_delay=delay)
            msg = f"Slowmode set to **{delay} seconds**."
        else:
            return await ctx.send("⚠️ Invalid slowmode format.")

        embed = create_success_embed(title="🐢 Slowmode Updated", message=msg)
        await ctx.send(embed=embed)
        await log_command(ctx)

    @commands.command(name="lockvc")
    @is_staff()
    async def lock_voice_channel(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You must be in a voice channel to lock it.")

        vc = ctx.author.voice.channel
        overwrite = vc.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False

        try:
            await vc.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        except:
            return await ctx.send("❌ I couldn’t lock the voice channel.")

        embed = create_success_embed(
            title="🔒 Voice Channel Locked",
            message=f"{vc.name} is now locked."
        )
        await ctx.send(embed=embed)
        await log_command(ctx)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

