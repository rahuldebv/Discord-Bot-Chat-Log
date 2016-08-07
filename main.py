import asyncio
import discord
import random
import json
from discord.ext import commands
from discord.ext.commands import *

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')


class YoloSwag(HelpFormatter):
    def format(self):
        self._paginator = Paginator()
        self._paginator.add_line("play   │ Post YouTube url after !play to add it to the queue")
        self._paginator.add_line("pause  │ Pauses current song")
        self._paginator.add_line("resume │ Resumes current song")
        self._paginator.add_line("skip   │ Skips current song")
        self._paginator.add_line("stop   │ Stop playing music, clear the queue, and leave voice channel")
        self._paginator.add_line("join   │ Makes bot join the voice channel you're in")
        self._paginator.add_line("b      │ I love the olympics")
        self._paginator.add_line("n      │ teehee xd ")
        self._paginator.add_line("cop    │ Hunting time")
        return self._paginator.pages

ys = YoloSwag()


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """Makes bot join the voice channel you're in"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say("You aren't in a voice channel.")
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Post YouTube url after !play to add it to the queue"""
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.play)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses current song"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes current song"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stop playing music, clear the queue, and leave voice channel"""
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Skips current song"""
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say("No music currently playing")
            return
        state.skip()

class Misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def b(self, ctx):
        """I love the olympics"""
        await self.bot.say(":flag_us::swimmer::skin-tone-1::flag_mx:")

    @commands.command(pass_context=True, no_pm=True)
    async def blm(self, ctx):
        """All lives matter"""
        msg = ""
        for x in range(0, 50):
            index = random.randrange(0, len(arrayBLM))
            msg += arrayBLM[index]
        await client.send_message(message.channel, msg)

    @commands.command(pass_context=True, no_pm=True)
    async def cop(self, ctx):
        """Hunting time"""
        await self.bot.say(":man::skin-tone-5::gun::cop::skin-tone-1:")

    @commands.command(pass_context=True, no_pm=True)
    async def n(self, ctx):
        """teehee xd"""
        await self.bot.say("Niggers")

class RPG:
    def __init__(self, bot):
        self.bot = bot
        self.save_interval = 60
        self.timer = 3
        self.gold = 0
        self.players = {}

    @commands.command(pass_context=True, no_pm=True)
    async def quit(self, ctx):
        self.save(ctx.message.server.id)
        await bot.logout()

    @commands.group(pass_context=True, no_pm=True)
    async def roll(self, ctx):
        try:
            content = ctx.message.content
            args = content.split(" ")
            dice = args[1]
            rolls, limit = map(int, dice.split("d"))
        except Exception:
            await bot.say("Error: Not in NdN")
            return

        result = 0
        for r in range(rolls):
            result += random.randint(1, limit)

        msg = ctx.message.author.name + " rolled: " + dice + "\n"
        msg += "Result: " + str(result)
        await bot.say(msg)
        await bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def id(self, ctx):
        await self.bot.say("Your ID is: " + ctx.message.author.id)

    @commands.command(pass_context=True, no_pm=True)
    async def change(self, ctx):
        args = ctx.message.content.split(" ")
        self.timer = int(args[1])

    @commands.command(pass_context=True, no_pm=True)
    async def stats(self, ctx):
        self.check_if_player_exists(ctx.message.author.id)
        id = ctx.message.author.id
        msg = "```" + str(ctx.message.author) + "\n"
        msg += "Gold: " + str(self.players[id]["gold"]) + "```"
        await self.bot.delete_message(ctx.message)
        await self.bot.say(msg)

    @commands.command(pass_context=True, no_pm=True)
    async def grab(self, ctx):
        id = ctx.message.author.id
        self.check_if_player_exists(id)

        if self.gold > 0:
            self.players[id]["gold"] += self.gold
            self.gold = 0
        else:
            await self.bot.say("Nothing to grab")

    @commands.command(pass_context=True, no_pm=True)
    async def start(self, ctx):
        self.load(ctx.message.server.id)
        await self.bot.say("RPG Started")
        await self.generate_loot()
        await self.save_at_interval()

    async def generate_loot(self):
        # Loot Scale: Avg level of players, capped at # of players
        # Example: 20, 1, 1            = 7 -> 3
        # Example: 8, 7, 7, 6, 5, 5, 5 = 6
        loot_scale = 0

        if self.gold == 0:
            self.gold = random.randrange(1, 11)
            await self.bot.say(str(self.gold) + " gold has been dropped")
        await asyncio.sleep(self.timer)
        await self.generate_loot()

    async def save_at_interval(self):
        await asyncio.sleep(self.save_interval)
        self.save(ctx.message.server.id)
        await self.save_at_interval()

    def check_if_player_exists(self, id):
        if id not in self.players:
            self.create_account(id)

    def create_account(self, id):
        self.players[id] = {'gold': 0, 'items': []}
        print(self.players)
        print(self.players[id]["gold"])

    def save(self, id):
        with open(id + ".json", "w") as outfile:
            json.dump(self.players, outfile)

    def load(self, id):
        try:
            with open(id + ".json") as infile:
                self.players = json.load(infile)
        except Exception:
            self.save(id)

    @commands.command(pass_context=True, no_pm=True)
    async def p(self, ctx):
    
        await self.bot.say("Prune test")

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), formatter=ys, description="", pm_help="true")
#bot.add_cog(Music(bot))
#bot.add_cog(Misc(bot))
bot.add_cog(RPG(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run('MjA0MzM1Njk1MzcwNjQ5NjAw.Cm2zYA.NqkHRHfem_PXUZhcIi94ofdKCU0')
