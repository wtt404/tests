import discord

def translation_embed(guild, text, language):
    embed = discord.Embed(
        description=text,
        color=discord.Color.dark_theme()
    )

    embed.set_footer(
        text=guild.name,
        icon_url=guild.icon.url if guild.icon else None
    )

    LANGUAGES = {
    "ar": "Arabic",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ru": "Russian",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "he": "Hebrew",
    "it": "Italian",
    "pt": "Portuguese",
    }

    embed.add_field(
        name="Translated from",
        value=LANGUAGES.get(language, language),
        inline=False
    )

    return embed