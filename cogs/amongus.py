import re
import os
import asyncio
from enum import IntEnum
from functools import reduce, partial

from discord.ext import commands
import discord
import emoji

from utils.voice import get_attendees, move_channel


WATCH_MESSAGE = '下のリアクションを押してね'
GUILD_IDS = os.environ.get('_DISCORD_GUILDS', None)


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
        self.channels: list[discord.VoiceChannel] = []
        self.guild_mute: bool = True

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_driven_mover(self, payload: discord.RawReactionActionEvent):
        if self.running:
            return

        print(f'{payload}')

        if GUILD_IDS and payload.guild_id not in GUILD_IDS:
            print(f'{payload.guild_id}で呼ばれたが、対応しないよ')
            return

        # bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            print(f'reacting user is me {payload.user_id} == {self.bot.user.id}')
            return

        if len(self.channels) == 0:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # messageが自分のものじゃなかったら無視
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

        coroutines: list[asyncio.coroutines] = []

        # Reaction判定
        if payload.emoji.name == REACTIONS[GameMode.MEETING]:
            print('MEETING')
            coroutines = self.mute_to_meeting() + self.heaven_to_meeting()
        elif payload.emoji.name == REACTIONS[GameMode.MUTE]:
            print('MUTE')
            coroutines = self.meeting_to_mute() + self.meeting_to_heaven()
        elif payload.emoji.name == REACTIONS[GameMode.FINISH]:
            print('END')
            coroutines = self.finish_game()
        else:
            pass

        print(f'{len(coroutines)=}')

        await asyncio.gather(*coroutines)
        self.running = False

    def mute_to_meeting(self) -> list[asyncio.coroutine]:
        players = get_attendees(self.channels[GameMode.MUTE])

        coroutines = [
            move_channel(
                member=player,
                destination=self.channels[GameMode.MEETING],
                mute=False
            )
            for player in players
        ]
        return coroutines

    def heaven_to_meeting(self):
        players = get_attendees(self.channels[GameMode.HEAVEN])

        coroutines = [
            move_channel(
                member=player,
                destination=self.channels[GameMode.MEETING],
                mute=True,
            )
            for player in players
        ]
        return coroutines

    def meeting_to_mute(self):
        players = get_attendees(self.channels[GameMode.MEETING])
        players = filter(lambda player: not (player.voice.mute or player.voice.self_mute), players)

        # if destination is afk_channel, need not mute by guild
        move_to_mute_channel = partial(move_channel, mute=True) if self.guild_mute else move_channel

        coroutines = [
            move_to_mute_channel(
                member=player,
                destination=self.channels[GameMode.MUTE]
                )
            for player in players
        ]
        return coroutines

    def meeting_to_heaven(self):
        players = get_attendees(self.channels[GameMode.MEETING])
        players = filter(lambda player: player.voice.mute or player.voice.self_mute, players)

        coroutines = [
            move_channel(
                member=player,
                destination=self.channels[GameMode.HEAVEN],
                mute=False,
            )
            for player in players
        ]
        return coroutines

    def finish_game(self):
        players = reduce(lambda p, n: p + n, map(lambda ch: ch.members, self.channels))
        coroutines = [
            move_channel(
                member=player,
                destination=self.channels[GameMode.MEETING],
                mute=False,
            )
            for player in players
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

        if after.channel is self.channels[GameMode.HEAVEN]:
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
        if not ctx.guild:
            await ctx.send('サーバーでやれ')
            return

        if GUILD_IDS and ctx.guild.id not in GUILD_IDS:
            print(f'{ctx.guild.name}で呼ばれたが、対応しないよ')
            return

        if len(args) != 3:
            # raise error
            await ctx.send('引数3つ指定しろ')
            return

        channels: list[discord.VoiceChannel] = []
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

        if channels[GameMode.MUTE] is ctx.guild.afk_channel:
            self.guild_mute = False
        else:
            self.guild_mute = True

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
    global GUILD_IDS
    if GUILD_IDS:
        GUILD_IDS = list(map(lambda id: int(id), GUILD_IDS.split(';')))

    bot.add_cog(AmongUs(bot))
