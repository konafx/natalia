from typing import Union
from enum import IntEnum
from functools import reduce
import asyncio
import re
from time import time

from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
import discord
import emoji

from utils.voice import get_attendees, move_channel


Channel = Union[GuildChannel, PrivateChannel]

WATCH_MESSAGE = 'START'


class GameMode(IntEnum):
    MEETING = 0
    MUTE = 1
    HEAVEN = 2
    LOG = 3
    FINISH = 4


REACTIONS = {
    GameMode.MEETING: emoji.emojize(':loudspeaker:'),
    GameMode.MUTE: emoji.emojize(':zipper-mouth_face:'),
    GameMode.FINISH: emoji.emojize(':party_popper:')
}


class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.running = False
        self.ghosts = []
        self.channels: list[discord.VoiceChannel] = []

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_driven_mover(self, payload: discord.RawReactionActionEvent):
        if self.running:
            return

        print(f'{payload}')
        print(f'{self.channels}')

        # bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            print(f'reacting user is me {payload.user_id} == {self.bot.user.id}')
            return

        if len(self.channels) == 0:
            return

        # TODO: get_channelがguilds intent必要なので fetch_channelでもいい気がする
        channel = self.bot.get_channel(payload.channel_id)
        # messageが自分のものじゃなかったら無視
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            print('message author is not me')
            return

        # messageが監視対象じゃなければ無視
        watch_message_regex = re.compile(rf'^{WATCH_MESSAGE}')
        if not watch_message_regex.match(message.content):
            print('not watch message')
            return

        self.running = True
        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        for reaction in message.reactions:
            await message.remove_reaction(reaction, payload.member)

        next_mode: GameMode = GameMode.MEETING
        coroutines: list[asyncio.coroutines] = []
        print(
            f'meetings = {list(get_attendees(self.channels[GameMode.MEETING]))}\n'
            f'mutes    = {list(get_attendees(self.channels[GameMode.MUTE]))}\n'
            f'ghosts   = {list(get_attendees(self.channels[GameMode.HEAVEN]))}\n'
            )

        # Reaction判定
        if payload.emoji.name == REACTIONS[GameMode.MEETING]:
            print(f'MEERING')
            coroutines = self.mute_to_meeting() + self.heaven_to_meeting()
        elif payload.emoji.name == REACTIONS[GameMode.MUTE]:
            print(f'MUTE')
            coroutines = self.meeting_to_mute() + self.meeting_to_heaven()
        elif payload.emoji.name == REACTIONS[GameMode.FINISH]:
            print(f'END')
            self.ghosts = []
            coroutines = self.finish_game()
        else:
            pass

        print(f'{len(coroutines)=}')

        startTime = time() #プログラムの終了時刻
        await asyncio.gather(*coroutines)
        endTime = time() #プログラムの終了時刻
        runTime = endTime - startTime #処理時間
        print(f'gather: {runTime}')
        self.running = False

    def mute_to_meeting(self) -> list[asyncio.coroutine]:
        startTime = time()
        attendees = get_attendees(self.channels[GameMode.MUTE])

        coroutines = [
            move_channel(
                member=attendee,
                destination=self.channels[GameMode.MEETING],
                mute=False
            )
            for attendee in attendees
        ]
        endTime = time() #プログラムの終了時刻
        runTime = endTime - startTime #処理時間
        print(f'mute_to_meeting: {runTime}')
        return coroutines

    def heaven_to_meeting(self):
        startTime = time() #プログラムの開始時刻
 
        ghosts = get_attendees(self.channels[GameMode.HEAVEN])
        self.ghosts = list(ghosts)

        coroutines = [
            move_channel(
                member=ghost,
                destination=self.channels[GameMode.MEETING],
                mute=True,
            )
            for ghost in self.ghosts
        ]
        endTime = time() #プログラムの終了時刻
        runTime = endTime - startTime #処理時間
        print(f'heaven_to_meeting: {runTime}')
        return coroutines

    def meeting_to_mute(self):
        startTime = time()
        attendees = get_attendees(self.channels[GameMode.MEETING])
        attendees = filter(lambda attendee: attendee not in self.ghosts, attendees)

        coroutines = [
            move_channel(
                member=attendee,
                destination=self.channels[GameMode.MUTE],
                mute=True,
            )
            for attendee in attendees
        ]
        endTime = time() #プログラムの終了時刻
        runTime = endTime - startTime #処理時間
        print(f'meeting_to_mute: {runTime}')
        return coroutines

    def meeting_to_heaven(self):
        startTime = time()
        coroutines = [
            move_channel(
                member=ghost,
                destination=self.channels[GameMode.HEAVEN],
                mute=False,
            )
            for ghost in self.ghosts
        ]
        endTime = time() #プログラムの終了時刻
        runTime = endTime - startTime #処理時間
        print(f'meeting_to_heawven: {runTime}')
        return coroutines

    def finish_game(self):
        attendees = reduce(lambda p, n: p + n, map(lambda ch: ch.members, self.channels))
        coroutines = [
            move_channel(
                member=attendee,
                destination=self.channels[GameMode.MEETING],
                mute=False,
            )
            for attendee in attendees
        ]
        return coroutines

    @commands.Cog.listener(name='on_voice_state_update')
    async def join_heaven_room(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """
        天界部屋に入ってきたメンバーのサーバーミュートを解除する

        Parameters
        ----------
        member: discord.Member
            メンバー
        before: discord.VoiceChannel
            変更前の状態
        after: discord.VoiceChannel
            変更後の状態

        returns
        ------
        """
        if len(self.channels) == 0:
            return

        if before.channel is self.channels[GameMode.HEAVEN]:
            return

        if not before.mute:
            return

        print(f'{after.channel}, {self.channels[GameMode.HEAVEN]}')
        if after.channel is self.channels[GameMode.HEAVEN]:
            print(f'{before} => {after}')
            print('mute 解除')
            await member.edit(mute=False)

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
        if len(args) != 3:
            # raise error
            await ctx.send('引数2つ指定しろ')
            return

        channels: list[VoiceChannel] = []
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

            channels.append(channel)
        
        self.channels = channels
        
        # 監視対象メッセージを送信
        message = await ctx.send(
                f'{WATCH_MESSAGE} '
                + ' '.join(map(lambda channel: channel.name, self.channels))
                )
        await self.init_reaction_as_button(message)
    
    async def init_reaction_as_button(self, message: discord.Message):
        task_add_reactions = [message.add_reaction(reaction) for reaction in REACTIONS.values()]

        await asyncio.gather(*task_add_reactions)


def setup(bot: commands.Bot):
    bot.add_cog(AmongUs(bot))
