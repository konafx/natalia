import random
import math
from functools import reduce

from more_itertools import chunked
from discord.ext import commands
from discord import Embed

class TeamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            usage='<チームごとの人数>',
            help='チーム分けをするヨ！\n'
                 '例: !team 2\n'
                 'ALl: Natalia, Lyra, Miku, Ibuki, Chinami\n ↓\n'
                 'A: Lyra, Ibuki\n'
                 'B: Chinami, Natalia\n'
                 'C: Miku'
            )
    async def team(self, ctx, num_of_team_member: int):
        members = self.get_members(ctx)
        teams = self.divide_per_member(num_of_team_member, members)
        msg = self.create_embed(teams)
        await ctx.send(embed=msg)

    @team.error
    async def team_error(self, ctx, error):
        print(f'{error=}')
        if isinstance(error, commands.BadArgument):
            await ctx.send('ナニ言ってるかワカラナイヨ…')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('ボイチャに接続できないヨ……')

    def get_members(self, ctx):
        state = ctx.author.voice
        if not state:
            raise Exception('Cannot connect voice channel')

        members = [mem.name for mem in state.channel.members]
        return members

    def divide_per_member(self, num_of_member: int, members: list):
        random.shuffle(members)

        teams = list(chunked(members, num_of_member))

        return teams

    def create_embed(self, teams):
        CHAR_A = 65
        embed = Embed(title='チームわけ')
        for index, team in enumerate(teams):
            name = chr(CHAR_A + index)
            value = reduce(lambda x, y: f'{x}, {y}', team)
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text='例: 4人チーム作りたいとき→ !team 4')
        return embed

def setup(bot):
    bot.add_cog(TeamCog(bot))
