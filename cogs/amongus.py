from typing import Union, Optional
from functools import reduce
from itertools import islice
from enum import IntEnum
import asyncio

from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
import discord
import emoji

from utils.voice import get_attendees, move_channnel


Channel = Union[GuildChannel, PrivateChannel]

MOVER_CHANNEL = 'moveradmin'
WATCH_MESSAGE = 'START'


class GameMode(IntEnum):
    MEETING = 0
    MUTE = 1


REACTIONS = {
    GameMode.MEETING: emoji.emojize(':loudspeaker:'),
    GameMode.MUTE: emoji.emojize(':zipper-mouth_face:')
}


class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channels: list[discord.VoiceChannel] = []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print(f'{payload}')

        # bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        # messageが自分のものじゃなかったら無視
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            return

        # messageが監視対象じゃなければ無視
        if message.content != WATCH_MESSAGE:
            return

        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        for reaction in message.reactions:
            await message.remove_reaction(reaction, payload.member)
        
        next_mode: GameMode = GameMode.MEETING
        # Reaction判定
        if payload.emoji.name == REACTIONS[GameMode.MEETING]:
            next_mode = GameMode.MEETING
        elif payload.emoji.name == REACTIONS[GameMode.MUTE]:
            next_mode = GameMode.MUTE
        else:
            await channel.send(f'{payload.emoji.name=}')
            return

        attendees = get_attendees(payload.member)

        print(f'{self.channels}')
        # task? queue
        for attendee in attendees:
            await move_channnel(
                attendee,
                self.channels[next_mode],
                True if next_mode == GameMode.MUTE else False
                )

        print(f'{channel.name=} {channel.name == "fushimi-general"}')

    @commands.command(
            brief='リアクションを押してほしいナ！',
            )
    async def mover(self, ctx: commands.Context, *args):
        """
        乗組員を移動させるチャンネルを設定する

        Parameters
        ----------
        ctx : commands.Context
            [description]
        """
        if len(args) != 2:
            # raise error
            await ctx.send('引数2つ指定しろ')
            return

        for channel_name in args:
            channel = discord.utils.get(ctx.guild.channels, name=channel_name)
            if channel is None:
                # raise error
                await ctx.send(f'{channel_name}は存在しねえ')
                return
            
            if not isinstance(channel, discord.VoiceChannel):
                # raise error
                await ctx.send(f'{channel_name}はボイチャじゃねえ')
                return

            self.channels.append(channel)
        
        # 監視対象メッセージを送信
        message = await ctx.send(WATCH_MESSAGE)
        await self.init_reaction_as_button(message)
    
    async def init_reaction_as_button(self, message: discord.Message):
        task_add_reaction_meeting = asyncio.create_task(
            message.add_reaction(REACTIONS[GameMode.MEETING])
        )
        task_add_reaction_mute = asyncio.create_task(
            message.add_reaction(REACTIONS[GameMode.MUTE])
        )
        await task_add_reaction_meeting
        await task_add_reaction_mute


def setup(bot: commands.Bot):
    bot.add_cog(AmongUs(bot))
