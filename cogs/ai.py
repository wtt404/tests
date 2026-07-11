import discord
from discord.ext import commands

from ai.agent import ai


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("AI COG INITIALIZED", flush=True)


    @commands.command(name="ai")
    async def ai(self, ctx, *, prompt: str = None):
        await ctx.typing()
        print(f"COMMAND {ctx.command} | message={ctx.message.id}", flush=True)

        print("=" * 50)
        print("Ai COMMAND")
        print("=" * 50)

        images = []
        for attachment in ctx.message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_bytes = await attachment.read()
                images.append((image_bytes, attachment.content_type))

        if not prompt and not images:
            await ctx.send("Give me a question, or attach an image for me to read.")
            return

        try:
            reply = await ai(prompt or "", images=images)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"-ai command failed: {e}", flush=True)
            await ctx.send(f"Something went wrong: {e}")
            return

        if not reply:
            await ctx.send("Sorry, I couldn't come up with a response.")
            return

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