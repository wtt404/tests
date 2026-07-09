import discord
from discord.ext import commands

from ai.agent import ai


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AI COG INITIALIZED", flush=True)


    @commands.command(name="ai")
    async def ai(self, ctx, *, prompt):
        await ctx.typing()
        print(f"COMMAND {ctx.command} | message={ctx.message.id}", flush=True)

        print("=" * 50)
        print("Ai COMMAND")
        print("=" * 50)

        reply = await ai(prompt)

        if len(reply) > 2000:
            reply = reply[:1990] + "..."

        await ctx.send(reply)

    @commands.command()
    async def translate(self, ctx, *, text):
        await ctx.typing()
        print(f"COMMAND {ctx.command} | message={ctx.message.id}", flush=True)

        from services.detector import detect
        from services.dispatcher import dispatch

        detected = detect(text)

        if detected:
            # An X/Telegram link was pasted: reuse the normal fetch + media pipeline.
            await dispatch(ctx.message, detected)
            return

        # Plain text: translate it directly.
        from services.language import detect_language
        from services.translation import translate as translate_text
        from services.embeds import translation_embed

        language = detect_language(text)
        translated = await translate_text(text)

        if not translated:
            await ctx.send("Sorry, I couldn't translate that.")
            return

        embed = translation_embed(ctx.guild, translated, language)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AI(bot))