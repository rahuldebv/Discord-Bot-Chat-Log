import discord
from discord.ext import commands
import io
from chatlog import ChatLog
import configparser

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
bot.add_cog(ChatLog(bot))


@bot.event
async def on_ready():
    print("Logged in as:\n{0} (ID: {0.id})".format(bot.user))

config = configparser.ConfigParser()
config.read("config.ini")
bot.run(config.get("bot", "token"))
