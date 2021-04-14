from typing import Optional
from discord.ext import commands
from discord import Intents

import traceback
import os
import sys

INITIAL_EXTENSIONS = [
    'cogs.hello',
    'cogs.socialdistance',
    'cogs.mahjong',
    'cogs.youtube',
    'cogs.amongus'
]

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', None)

class Natalia(commands.Bot):
    def __init__(self, command_prefix, intent: Optional[Intents]=None):
        if not intent:
            intent = Intents.default()

        super().__init__(command_prefix, intent=intent)

        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')

def main():
    if not DISCORD_TOKEN:
        print('The DISCORD_TOKEN variable is not set', file=sys.stderr)
        sys.exit(1)

    # guilds (get_channel)
    # members (get_member)
    # voice_states (VoiceChannel.members, voice_states)
    # guild_messages (on_reaction_add)
    # guild_reactions (..)
    intent = Intents.default()
    intent.guilds = True
    intent.members = True
    intent.voice_states = True
    intent.guild_messages = True
    intent.guild_reactions = True

    print(f'{intent=}')
    bot = Natalia(command_prefix='!', intent=intent)
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
