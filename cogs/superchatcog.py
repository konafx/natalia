from discord import Embed
from discord.ext import commands


class SuperChatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            usage='<値段> <?コメント>',
            help='センキュー・スパチャ♪ ┗(┓卍^o^)卍ﾄﾞｩﾙﾙﾙﾙﾙﾙ↑↑\n'
                 '例: !superchat 2434 かわいい\n'
                 '例: !superchat 50000\n'
            )
    async def superchat(self, ctx, tip: int, comment: str):
        msg = self.create_embed()
        await ctx.send(embed=msg)

    @superchat.error
    async def team_error(self, ctx, error):
        print(f'{error=}')
        if isinstance(error, commands.BadArgument):
            await ctx.send('ナニ言ってるかワカラナイヨ…')


def setup(bot):
    bot.add_cog(SuperChatCog(bot))
