from typing import Dict

import discord
from discord.ext import commands

import utils.message as msg


CHATCOLORS = {
    1: 'BLUE',
    200: 'AQUA',
    500: 'GREEN',
    1000: 'YELLOW',
    2000: 'ORANGE',
    5000: 'MAGENTA',
    10000: 'RED'
}

COLORS = {
    'BLUE': 0x134A9D,
    'AQUA': 0x28E4FD,
    'GREEN': 0x32E8B7,
    'YELLOW': 0xFCD748,
    'ORANGE': 0xF37C22,
    'MAGENTA': 0xE72564,
    'RED': 0xE32624
    }


class YouTube(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
            usage='<値段> <?コメント>',
            brief='センキュー・スパチャ♪ ┗(┓卍^o^)卍ﾄﾞｩﾙﾙﾙﾙﾙﾙ↑↑',
            help='気持ちを伝えるゾ！１円玉から諭吉サン５枚までで盛り上げるよ♪\n'
                 'でも、改行は伝えられないミタイ…？\n'
                 '例: !superchat 2434 かわいい\n'
                 '例: !superchat 50000\n'
            )
    async def superchat(self, ctx: commands.Context, tip: int, *comments):
        # 円マーク
        JPY = b'\\xa5'.decode('unicode-escape')
        embed = discord.Embed(
                title=f'{JPY}{tip:,}',
                description=' '.join(comments),
                color=COLORS[chatcolor(tip)]
                )
        embed.set_author(name=ctx.author.display_name)
        embed.set_thumbnail(url=ctx.author.avatar_url_as(
            format='png',
            static_format='png'
            ))
        await ctx.send(embed=embed)

    @superchat.error
    async def superchat_error(self, ctx: commands.Context, error: Exception):
        print(f'{error=}')
        if isinstance(error, commands.BadArgument):
            await ctx.author.send('整数しかワカラナイヨ…')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(msg.command_usage(ctx))


def chatcolor(tip: int, chatcolors: Dict[int, str] = CHATCOLORS) -> str:
    if (tip < 1 or tip > 50000):
        raise ValueError('Range Over [1, 50000]')

    allow_chatcolors = list(filter(lambda cc: cc[0] <= tip, chatcolors.items()))
    color = allow_chatcolors.pop()[1]
    return color


def setup(bot: commands.Bot):
    bot.add_cog(YouTube(bot))
