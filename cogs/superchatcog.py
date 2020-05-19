from discord import Embed
from discord.ext import commands


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


class SuperchatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            usage='<値段> <?コメント>',
            help='センキュー・スパチャ♪ ┗(┓卍^o^)卍ﾄﾞｩﾙﾙﾙﾙﾙﾙ↑↑\n'
                 '例: !superchat 2434 かわいい\n'
                 '例: !superchat 50000\n'
            )
    async def superchat(self, ctx, tip: int, *comments):
        # 円マーク
        JPY = b'\\xa5'.decode('unicode-escape')
        embed = Embed(
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
    async def superchat_error(self, ctx, error):
        print(f'{error=}')
        if isinstance(error, commands.BadArgument):
            await ctx.send('ナニ言ってるかワカラナイヨ…')


def chatcolor(tip: int, chatcolors: dict = CHATCOLORS):
    if (tip < 1 or tip > 50000):
        raise ValueError('Range Over [1, 50000]')

    allow_chatcolors = list(filter(lambda cc: cc[0] <= tip, chatcolors.items()))
    color = allow_chatcolors.pop()[1]
    return color


def setup(bot):
    bot.add_cog(SuperchatCog(bot))
