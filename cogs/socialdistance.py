import random
from functools import reduce
from itertools import filterfalse
from typing import List

import discord
from discord.ext import commands

from more_itertools import chunked


class ソーシャルディスタンス(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            usage='<チームごとの人数>',
            brief='チーム分けをするヨ！',
            help='接続してるボイチャのみんなをチーム分けするヨ！\n'
                 '人数は100人までにして欲しいナ…♪\n'
                 '例: !team 2\n'
                 'ALl: Natalia, Lyra, Miku, Ibuki, Chinami\n ↓\n'
                 'A: Lyra, Ibuki\n'
                 'B: Chinami, Natalia\n'
                 'C: Miku'
            )
    async def team(self, ctx: commands.Context, num_of_team_member: int = 4):
        members = self.get_members(ctx.author)
        teams = self.divide_per_member(num_of_team_member, members)
        embed = self.create_embed(teams)
        await ctx.send(embed=embed)

    @team.error
    async def team_error(self, ctx: commands.Context, error: Exception):
        print(f'{error=}')
        if isinstance(error, commands.BadArgument):
            await ctx.send('ナニ言ってるかワカラナイヨ…')
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, ValueError):
                await ctx.send('ミクが「みくは彼氏がいるから１円から５万円までにゃ！」って言ってたヨ？')
            else:
                await ctx.send('スシ〜♪')

    def get_members(self, member: discord.Member, exclude_bot=True):
        """
        ctxからボイスチャンネルに接続しているメンバー名リストを取得する
        botは除外できる

        Parameters
        ----------
        self: Object
            self
        ctx: discord.ext.commands.Context
            コンテキスト
            > Represents the context in which a command is being invoked under.
        exclude_bot: bool
            ボットを除外するか

        returns
        ------
        members: List[string]
            ボイスチャンネルに接続しているメンバー名リスト
        """

        state = member.voice
        if not state:
            raise Exception('ボイチャに接続してないヨ〜！')

        connected_members = state.channel.members
        if exclude_bot:
            connected_members = filterfalse(lambda mem: mem.bot, connected_members)

        members = [mem.name for mem in connected_members]
        return members

    def divide_per_member(self, num_of_member: int, members: List[str]) -> List[List[str]]:
        if (num_of_member < 1 or num_of_member > 100):
            raise ValueError('Range Over [1, 100]')

        random.shuffle(members)

        teams = list(chunked(members, num_of_member))

        return teams

    def create_embed(self, teams: List[List[str]]) -> discord.Embed:
        CHAR_A = 65
        embed = discord.Embed(title='チームわけ')
        for index, team in enumerate(teams):
            name = chr(CHAR_A + index)
            value = reduce(lambda x, y: f'{x}, {y}', team)
            embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text='例: 4人チーム作りたいとき→ !team 4')
        return embed


def setup(bot: commands.Bot):
    bot.add_cog(ソーシャルディスタンス(bot))
