import discord
import io
from discord.ext import commands
from chatlog import ChatLog


# Read your private token from bot.token
# This allows easy Git use without hard-coding the token
def get_token():
    bot_token = open("bot.token", "r")
    token = bot_token.readline()
    bot_token.close()
    return token.strip()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))
bot.add_cog(ChatLog(bot))


@bot.event
async def on_ready():
    print("Logged in as:\n{0} (ID: {0.id})".format(bot.user))

bot.run(get_token())
