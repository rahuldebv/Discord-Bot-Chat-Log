import configparser
import pathlib
import fnmatch
import os
import time
import datetime


def not_pm(message):
    return type(message.channel).__name__ == "Channel"


def get_filename(message):
    year = datetime.date.today().year
    week = time.strftime("%U")
    id = message.server.id
    channel = message.channel.name
    return "%s-%s-%s-%s.log" % (year, week, id, channel)


class ChatLog:
    def __init__(self, bot):
        # Get and set role needed to use admin commands
        config = configparser.ConfigParser()
        config.read("config.ini")
        role = config.get("chat_log", "role")
        path = config.get("chat_log", "path")
        addr = config.get("chat_log", "addr")

        # Create data directory if it doesn't exist
        if not os.path.isdir(path):
            os.makedirs(path)

        @bot.event
        async def on_message(message):
            # Admin command to get URL of all the server's log files
            if message.content.startswith("!log all") and not_pm(message):
                # Get list of all server .log files
                for file in os.listdir("/var/www/html"):
                    if fnmatch.fnmatch(file, "*%s.log" % (message.server.id)):
                        file = addr + file
                        await bot.send_message(message.author, file)

            # Admin command to get URL of current week's log file
            elif message.content.startswith("!log") and not_pm(message):
                for r in message.author.roles:
                    if r.name == role:
                        file = get_filename(message)
                        file = addr + file
                        await bot.send_message(message.author, file)

            # Write to log file [Timestamp] [Name] [Messge]
            if not_pm(message):
                file = get_filename(message)
                file = path + file
                with open(file, "a") as f:
                    # Trim the timestamp to only get [y-m-d h:m:s]
                    msg = "[" + str(message.timestamp)[0:19] + "] "

                    # Add author's name and padding (names are 32 chars max)
                    msg += "[" + message.author.name + "] "
                    for x in range(len(message.author.name), 32):
                        msg += " "

                    # Add author's ID and message content and write to file
                    msg += "[ID: " + message.author.id + "] "
                    msg += message.content
                    f.write(msg + "\n")
