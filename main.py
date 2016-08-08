from discord.ext import commands
from chatlog import ChatLog
import configparser

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
bot.add_cog(ChatLog(bot))


@bot.event
async def on_ready():
    print(bot.user.name + "#" + bot.user.discriminator + " is now running!")

config = configparser.ConfigParser()
config.read("config.ini")
bot.run(config.get("bot", "token"))
