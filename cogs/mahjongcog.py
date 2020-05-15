import random
import json

from kanjize import int2kanji
from discord.ext import commands

MAX_FAN = 13
class MahjongCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            help='デイリーミッション♪\n'
                 '今日はコノ役で上がってネ！'
            )
    async def 今日の役(self, ctx):
        with open('assets/hands.json', 'r') as f:
            hands = json.load(f)

        hand_weights = [MAX_FAN - hand['fan'] + 1 for hand in hands]
        hand = random.choices(hands, k=1, weights=hand_weights)
        print(f'{hand=}')
        await ctx.send(f'{hand[0]["name"]} ({int2kanji(hand[0]["fan"])}翻)')

    @今日の役.error
    async def 今日の役_error(self, ctx, error):
        await ctx.send('タ　ン　ヤ　オ')

def setup(bot):
    bot.add_cog(MahjongCog(bot))
