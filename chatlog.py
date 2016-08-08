import os

class ChatLog:
    def __init__(self, bot):

        # Create data directory if it doesn't exist
        if not os.path.isdir("data"):
            os.makedirs("data")

        @bot.event
        async def on_message(message):
            if message.content.startswith("!log"):
                with open("data/log.txt", "r") as f:
                    output = f.read()

            # Write to log file [Timestamp] [Name] [Messge]
            with open("data/log.txt", "a") as f:
                msg = "[" + str(message.timestamp)[0:19] + "] "
                msg += "[" + message.author.name + "] "
                msg += "[ID: " + message.author.id + "] "
                msg += message.content
                f.write(msg + "\n")
