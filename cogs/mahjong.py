import json
import random

from discord.ext import commands, tasks

from kanjize import int2kanji

MAX_FAN = 13
HANDS_JSON = 'assets/hands.json'
SAYINGS_JSON = 'assets/sayings.json'


class 麻雀(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hand_updater.start()

    @commands.command(
            help='デイリーミッション♪\n'
                 '今日はコノ役で上がってネ！'
            )
    async def 今日の役(self, ctx):
        hand = self.today_hand
        saying = self.random_saying()
        await ctx.send(
                f'今日の役は **{hand["name"]}**♪\n'
                f'{int2kanji(hand["fan"])}翻だヨ！ {saying}'
                )

    @今日の役.error
    async def 今日の役_error(self, ctx, error):
        await ctx.send('タ　ン　ヤ　オ')

    @tasks.loop(hours=24)
    async def hand_updater(self):
        self.today_hand = self.random_hand()

    def random_hand(self):
        """
        飜数に応じた重みランダムで役を出力する

        returns
        -------
        hand: dict
            e.g. {'name': 'タンヤオ', 'fan': 1}
        """

        with open(HANDS_JSON, 'r') as f:
            hands = json.load(f)

        hand_weights = [MAX_FAN - hand['fan'] + 1 for hand in hands]
        hand = random.choices(hands, k=1, weights=hand_weights)
        print(f'{hand=}')
        return hand[0]

    def random_saying(self):
        """
        名言bot
        """

        with open(SAYINGS_JSON, 'r') as f:
            sayings = json.load(f)

        saying = random.choice(sayings)
        return saying


def setup(bot):
    bot.add_cog(麻雀(bot))
