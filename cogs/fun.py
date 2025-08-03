import discord
import random
from discord.ext import commands
from utils.embed import create_embed, create_error_embed, log_command

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball", aliases=["magic8"])
    async def magic8ball(self, ctx, *, question: str = None):
        if not question:
            return await ctx.send(embed=create_error_embed(
                title="Missing Question",
                reason="You must ask a question for the 8ball to answer.",
                usage=",8ball <your question>",
                example=",8ball will I be rich?"
            ))
        responses = [
            "Yes.", "No.", "Maybe.", "Absolutely!", "I don't think so.",
            "Ask again later.", "Definitely not.", "Certainly!", "Without a doubt.", "Doubtful."
        ]
        response = random.choice(responses)
        embed = discord.Embed(
            title="🎱 8Ball",
            description=f"**Question:** {question}
**Answer:** {response}",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "8ball", {"question": question})

    @commands.command()
    async def say(self, ctx, *, message: str = None):
        if not message:
            return await ctx.send(embed=create_error_embed(
                title="Missing Message",
                reason="You must provide a message for the bot to say.",
                usage=",say <message>",
                example=",say Hello world!"
            ))
        await ctx.message.delete()
        embed = create_embed(ctx, title="📢 Message", description=message, color=discord.Color.blue())
        await ctx.send(embed=embed)
        await log_command(ctx, "say", {"message": message})

    @commands.command(name="coinflip", aliases=["flip", "coin"])
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "coinflip", {"result": result})

    @commands.command()
    async def rate(self, ctx, *, item: str = None):
        if not item:
            return await ctx.send(embed=create_error_embed(
                title="Missing Item",
                reason="You need to provide something for me to rate.",
                usage=",rate <thing>",
                example=",rate my outfit"
            ))
        rating = random.randint(0, 100)
        embed = discord.Embed(
            title="📊 Rating Machine",
            description=f"I rate **{item}** a **{rating}/100**!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        await log_command(ctx, "rate", {"item": item, "rating": rating})

async def setup(bot):
    await bot.add_cog(Fun(bot))