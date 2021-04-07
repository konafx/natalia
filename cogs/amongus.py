import re
import os
import asyncio
from typing import Optional
from enum import IntEnum
from functools import reduce, partial

from discord.ext import commands
import discord
import emoji

from utils.voice import get_attendees, attendees_flow, get_muted


MOVER_TITLE = 'Amove Us'
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

MODE_NAMES = {
    GameMode.MEETING: '討論開始!',
    GameMode.MUTE: 'SHHHHHHHHHH!',
    GameMode.FINISH: 'Victory or Defeat',
}

CHANNEL_LABELS = {
    GameMode.MEETING: '会話チャンネル',
    GameMode.MUTE: 'ミュートチャンネル',
    GameMode.HEAVEN: '天界部屋'
}


class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_driven_mover(self, payload: discord.RawReactionActionEvent):
        print(f'{payload}')

        if GUILD_IDS and payload.guild_id not in GUILD_IDS:
            print(f'{payload.guild_id}で呼ばれたが、対応しないよ')
            return

        # bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            print(f'reacting user is me {payload.user_id} == {self.bot.user.id}')
            return

        guild = self.bot.get_guild(payload.guild_id)
        current_channel = guild.get_channel(payload.channel_id)
        message = await current_channel.fetch_message(payload.message_id)
        # messageが自分のものじゃなかったら無視
        if message.author.id != self.bot.user.id:
            print('message author is not me')
            return

        if not message.embeds:
            print('not watch message')
            return

        embed = message.embeds[0]

        if embed.title != MOVER_TITLE:
            return

        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        task_remove_reactions = [message.remove_reaction(reaction, payload.member) for reaction in message.reactions]
        await asyncio.gather(*task_remove_reactions)

        # チャンネルを取得する
        channels: list[discord.VoiceChannel] = []
        for embed_proxy in embed.fields:
            channel = guild.get_channel(int(embed_proxy.value))
            if channel is None:
                # raise error
                await current_channel.send(f'{embed_proxy.name}は存在しねえ')
                await message.delete()
                return

            if not isinstance(channel, discord.VoiceChannel):
                # raise error
                await ctx.send(f'{embed_proxy.name}で指定された`{channel.name}`はボイチャじゃねえ')
                await message.delete()
                return

            channels.append(channel)

        guild_mute = None if channels[GameMode.MUTE] is guild.afk_channel else True

        coroutines: list[asyncio.coroutines] = []

        # Reaction判定
        if payload.emoji.name == REACTIONS[GameMode.MEETING]:
            print('MEETING')
            meeting_inflow = partial(
                    attendees_flow,
                    destination=channels[GameMode.MEETING]
                )
            coroutines = meeting_inflow(channels[GameMode.MUTE], mute=False) + meeting_inflow(channels[GameMode.HEAVEN], mute=True)
        elif payload.emoji.name == REACTIONS[GameMode.MUTE]:
            print('MUTE')
            meeting_outflow = partial(
                    attendees_flow,
                    source=channels[GameMode.MEETING]
                )
            coroutines = meeting_outflow(
                    destination=channels[GameMode.MUTE],
                    mute=guild_mute,
                    sieve=lambda player: not get_muted(player)
                ) + meeting_outflow(
                    destination=channels[GameMode.HEAVEN],
                    mute=False,
                    sieve=lambda player: get_muted(player)
                )
        elif payload.emoji.name == REACTIONS[GameMode.FINISH]:
            print('END')
            players = reduce(lambda p, n: p + n, map(lambda ch: ch.members, channels))
            coroutines = [
                    player.edit(
                        reason='ゲーム終了',
                        voice_channel=channels[GameMode.MEETING],
                        mute=False
                        )
                    for player in players
                ]
        else:
            return

        print(f'{len(coroutines)=}')

        await asyncio.gather(*coroutines)

    @commands.command(
            usage='<会話用チャンネル名> <ミュート用チャンネル名> <天界部屋名>',
            brief='リアクションを押してほしいナ！',
            help='３つのチャンネルを使ってAmong Usの部屋移動をやるヨ！\n'
                 ''
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

        self.channels = channels

        description = '各タイミングで**絵文字を押セ！**\n・' + '\n・'.join(map(
                lambda mode: f'{MODE_NAMES[mode[0]]}→{mode[1]}',
                REACTIONS.items()
                ))
        embed = discord.Embed(title=MOVER_TITLE, description=description)
        for mode, label in CHANNEL_LABELS.items():
            embed.add_field(
                name=label,
                value=channels[mode].id
                )

        # 監視対象メッセージを送信
        message = await ctx.send(' '.join(map(lambda channel: channel.name, self.channels)), embed=embed)
        await self.init_reaction_as_button(message)

    async def init_reaction_as_button(self, message: discord.Message):
        task_add_reactions = [message.add_reaction(reaction) for reaction in REACTIONS.values()]

        await asyncio.gather(*task_add_reactions)


def setup(bot: commands.Bot):
    global GUILD_IDS
    if GUILD_IDS:
        GUILD_IDS = list(map(lambda id: int(id), GUILD_IDS.split(':')))

    bot.add_cog(AmongUs(bot))
