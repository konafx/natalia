from typing import Union
from discord.ext import commands
from discord import Reaction, Member, User

class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Union[Member, User]):
        print(f'{reaction=}, {user=}')

def setup(bot: commands.Bot):
    bot.add_cog(AmongUs(bot))
