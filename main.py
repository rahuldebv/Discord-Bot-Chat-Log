from discord.ext import commands
from chatlog import ChatLog
import configparser


def token():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.get("bot", "token")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
bot.add_cog(ChatLog(bot))


@bot.event
async def on_ready():
    print(bot.user.name + "#" + bot.user.discriminator + " is now running!")

bot.run(token())
