from discord.ext import commands

import traceback
import os
import subprocess

INITIAL_EXTENSIONS = [
    'cogs.hello',
    'cogs.socialdistance',
    'cogs.mahjong',
    'cogs.youtube',
    'cogs.amongus'
]

_DISCORD_TOKEN = os.environ['_DISCORD_TOKEN']

class Natalia(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)

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
    bot = Natalia(command_prefix='!')
    bot.run(_DISCORD_TOKEN)

if __name__ == '__main__':
    main()
