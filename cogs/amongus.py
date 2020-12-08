import os
import asyncio
from enum import IntEnum
from functools import reduce, partial
from datetime import datetime, timezone

from discord.ext import commands
import discord
import emoji
from loguru import logger
import ulid

from utils.voice import attendees_flow, get_muted


MOVER_TITLE = 'Amove Us'
GUILD_IDS = os.environ.get('_DISCORD_GUILDS', None)


class GameMode(IntEnum):
    MEETING = 0
    MUTE = 1
    FINISH = 2


class ChannelType(IntEnum):
    MEETING = 0
    MUTE = 1
    HEAVEN = 2
    LOG = 3


class Mode():
    def __init__(self, *, reaction: str, label: str):
        self.reaction = reaction
        self.label = label


class Channel():
    def __init__(self, *, label: str):
        self.label = label


MODES = {
    GameMode.MEETING: Mode(
        reaction=emoji.emojize(':loudspeaker:'),
        label='討論開始！'
        ),
    GameMode.MUTE: Mode(
        reaction=emoji.emojize(':zipper-mouth_face:'),
        label='SHHHHHHHHHH!!'
        ),
    GameMode.FINISH: Mode(
        reaction=emoji.emojize(':party_popper:'),
        label='Victory or Defeat'
        )
}

CHANNELS = {
    ChannelType.MEETING: Channel(label='会話チャンネル'),
    ChannelType.MUTE: Channel(label='ミュートチャンネル'),
    ChannelType.HEAVEN: Channel(label='天界部屋'),
    ChannelType.LOG: Channel(label='リアクションログ')
}


class AmongUs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_driven_mover(self, payload: discord.RawReactionActionEvent):
        logger.info(payload)
        if GUILD_IDS and payload.guild_id not in GUILD_IDS:
            logger.debug(f'{payload.guild_id}で呼ばれたが、対応しないよ')
            return

        # bot自身のリアクションは無視
        if payload.user_id == self.bot.user.id:
            logger.debug('reacting user is me')
            return

        guild = self.bot.get_guild(payload.guild_id)
        current_channel = guild.get_channel(payload.channel_id)
        message = await current_channel.fetch_message(payload.message_id)
        # messageが自分のものじゃなかったら無視
        if message.author.id != self.bot.user.id:
            logger.debug('message author is not me')
            return

        if not message.embeds:
            logger.debug('not embed message')
            return

        embed = message.embeds[0]

        if embed.title != MOVER_TITLE:
            logger.debug('not watch message')
            return

        event_id = ulid.new()
        logger.info(f'{event_id}: {payload.member}さんが{emoji.demojize(payload.emoji.name)}を押しました')

        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        task_remove_reactions = [message.remove_reaction(reaction, payload.member) for reaction in message.reactions]
        await asyncio.gather(*task_remove_reactions)

        # チャンネルを取得する
        channels: list[discord.VoiceChannel] = []
        for channel_type, embed_proxy in enumerate(embed.fields):
            channel = guild.get_channel(int(embed_proxy.value))
            if channel is None:
                # raise error
                await current_channel.send(f'{embed_proxy.name}は存在しねえ')
                await message.delete()
                return

            if channel_type != ChannelType.LOG and not isinstance(channel, discord.VoiceChannel):
                # raise error
                await current_channel.send(f'{embed_proxy.name}で指定された`{channel.name}`はボイチャじゃねえ')
                await message.delete()
                return

            if channel_type == ChannelType.LOG and not isinstance(channel, discord.TextChannel):
                # LOGチャンネルに記入不可能であればログを出さない
                continue

            channels.append(channel)

        guild_mute = None if channels[ChannelType.MUTE] is guild.afk_channel else True

        coroutines: list[asyncio.coroutines] = []

        # Reaction判定
        if payload.emoji.name == MODES[GameMode.MEETING].reaction:
            logger.debug('MEETING')
            meeting_inflow = partial(
                    attendees_flow,
                    destination=channels[ChannelType.MEETING]
                )
            coroutines = meeting_inflow(
                    source=channels[ChannelType.MUTE],
                    mute=False
                ) + meeting_inflow(
                    source=channels[ChannelType.HEAVEN],
                    mute=True
                )
        elif payload.emoji.name == MODES[GameMode.MUTE].reaction:
            logger.debug('MUTE')
            meeting_outflow = partial(
                    attendees_flow,
                    source=channels[ChannelType.MEETING]
                )
            coroutines = meeting_outflow(
                    destination=channels[ChannelType.MUTE],
                    mute=guild_mute,
                    sieve=lambda player: not get_muted(player)
                ) + meeting_outflow(
                    destination=channels[ChannelType.HEAVEN],
                    mute=False,
                    sieve=lambda player: get_muted(player)
                )
        elif payload.emoji.name == MODES[GameMode.FINISH]:
            logger.debug('END')
            players = reduce(lambda p, n: p + n, map(lambda ch: ch.members, channels))
            coroutines = [
                    player.edit(
                        reason='ゲーム終了',
                        voice_channel=channels[ChannelType.MEETING],
                        mute=False
                        )
                    for player in players
                ]
        else:
            logger.debug('このリアクションは関知しない')

        logger.debug(f'ジョブ数：{len(coroutines)}')

        trigger_member = payload.member.nick if payload.member.nick else payload.member.name
        if len(channels) > ChannelType.LOG:
            coroutines.append(channels[ChannelType.LOG].send(f'{trigger_member}さんが{payload.emoji.name}を押しました'))

        await asyncio.gather(*coroutines)

        logger.success(f'{event_id}: 完了しました')

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
            logger.debug(f'{ctx.guild.name}で呼ばれたが、対応しないよ')
            return

        if len(args) < 3 or 4 < len(args):
            # raise error
            await ctx.send('引数3,4つ指定しろ')
            return

        channels: list[discord.VoiceChannel] = []
        for channel_type, channel_name in enumerate(args):
            channel = discord.utils.get(ctx.guild.channels, name=channel_name)
            if channel is None:
                # raise error
                await ctx.send(f'{channel_name}は存在しねえ')
                return

            if channel_type != ChannelType.LOG and not isinstance(channel, discord.VoiceChannel):
                # raise error
                await ctx.send(f'{channel_name}はボイチャじゃねえ')
                return

            if channel_type == ChannelType.LOG and not isinstance(channel, discord.TextChannel):
                # Logチャンネルがボイチャならパス
                continue

            channels.append(channel)

        self.channels = channels

        description = '各タイミングで**絵文字を押セ！**\n・' + '\n・'.join(map(
                lambda mode: f'{mode.label}→{mode.reaction}',
                MODES.values()
                ))
        embed = discord.Embed(title=MOVER_TITLE, description=description)
        for channel_type, channel in enumerate(channels):
            embed.add_field(
                name=CHANNELS[channel_type].label,
                value=channel.id
                )

        # 監視対象メッセージを送信
        message = await ctx.send(' '.join(map(lambda channel: channel.name, self.channels)), embed=embed)
        await self.init_reaction_as_button(message)

    async def init_reaction_as_button(self, message: discord.Message):
        task_add_reactions = [message.add_reaction(mode.reaction) for mode in MODES.values()]

        await asyncio.gather(*task_add_reactions)


def setup(bot: commands.Bot):
    global GUILD_IDS
    if GUILD_IDS:
        GUILD_IDS = list(map(lambda id: int(id), GUILD_IDS.split(';')))

    bot.add_cog(AmongUs(bot))
