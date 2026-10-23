"""Discord gateway entry point. Importing this module never connects to Discord."""
def main():
    from ojisan.core.config import Config
    from ojisan.discord.bot import bot
    bot.run(Config.DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
