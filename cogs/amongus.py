from typing import Union
from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
import discord
import emoji

Channel = Union[GuildChannel, PrivateChannel]

MOVER_CHANNEL = 'moveradmin'
MEETING_REACTION = emoji.emojize(':loudspeaker:')
MUTE_REACTION = emoji.emojize(':zipper-mouth_face:')
WATCH_MESSAGE = 'START'


class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            return

        if message.content != WATCH_MESSAGE:
            return

        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        user = self.bot.get_user(payload.user_id)
        for reaction in message.reactions:
            await message.remove_reaction(reaction, user)

        print(f'{payload}, {message}')
        print(f'{channel.name=} {channel.name == "fushimi-general"}')


    @commands.command(
            brief='リアクションを押してほしいナ！',
            )
    async def mover(self, ctx: commands.Context):
        message = await ctx.send(WATCH_MESSAGE)
        await message.add_reaction(MEETING_REACTION)
        await message.add_reaction(MUTE_REACTION)


def setup(bot: commands.Bot):
    bot.add_cog(AmongUs(bot))
