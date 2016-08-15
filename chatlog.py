import configparser
import pathlib
import fnmatch
import os
import time
import datetime


def not_pm(message):
    return type(message.channel).__name__ == "Channel"


def get_path(message):
    id = message.server.id
    year = datetime.date.today().year
    week = time.strftime("%U")
    return "%s/%s/%s/" % (id, year, week)


def get_filename(message):
    year = datetime.date.today().year
    week = time.strftime("%U")
    id = message.server.id
    channel = message.channel.name

    path = "%s/%s/%s/" % (id, year, week)
    file_name = "%s-%s-%s.log" % (year, week, channel)

    return path + file_name


def testing(message, file):
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


class ChatLog:
    def __init__(self, bot):
        # Get and set role needed to use admin commands
        config = configparser.ConfigParser()
        config.read("config.ini")
        role = config.get("chat_log", "role")
        path = config.get("chat_log", "path")
        addr = config.get("chat_log", "addr")

        @bot.event
        async def on_message(message):
            # Admin command to get URL of current week's log file
            if message.content.startswith("!log") and not_pm(message):
                thing = "{}/?server={}".format(addr, message.server.id)
                await bot.send_message(message.author, thing)

            # Write to log file [Timestamp] [Name] [Messge]
            if not_pm(message):
                file = path + get_filename(message)
                try:
                    testing(message, file)
                except:
                    os.makedirs(path + get_path(message))
                    file = path + get_filename(message)
                    try:
                        testing(message, file)
                    except:
                        print("Something bad happened")
