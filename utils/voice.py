from typing import Optional
from itertools import filterfalse
from discord import Member, VoiceChannel
from discord.abc import GuildChannel

from time import time


def get_members(member: Member, exclude_bot=True) -> list[Member]:
    """
    メンバーが接続しているボイスチャンネルの全メンバーを取得する
    botは除外できる

    Parameters
    ----------
    member: discord.Member
        メンバー
    exclude_bot: bool
        ボットを除外するか

    returns
    ------
    connected_members: list[discord.Member]
        ボイスチャンネルに接続しているメンバーリスト
    """

    state = member.voice
    if not state:
        raise Exception('ボイチャに接続してないヨ〜！')

    connected_members = state.channel.members

    print(f'{connected_members=}')
    if connected_members:
        print(f'{state.channel.voice_states=}')

    if exclude_bot:
        connected_members = filterfalse(lambda mem: mem.bot, connected_members)

    return connected_members


def get_attendees(channel: VoiceChannel, exclude_bot=True) -> list[Member]:
    """
    チャンネルの参加者を取得する
    ボット起動前のチャンネル参加者は取得できない

    Parameters
    ----------
    channel: discord.VoiceChannel
        メンバー
    exclude_bot: bool
        ボットを除外するか

    returns
    ------
    attendees: list[discord.Member]
        ボイスチャンネルに接続しているメンバーリスト
    """
    attendees = filterfalse(lambda attendee: attendee.bot, channel.members)

    return attendees


async def move_channel(
        member: Member,
        destination: VoiceChannel,
        mute: Optional[bool]=None,
        reason: Optional[str] = None
        ):
    startTime = time()
    args = {
        'reason': reason,
        'voice_channel': destination,
        }
    if mute is not None:
        args['mute'] = mute

    await member.edit(**args)
    endTime = time()
    runTime = endTime - startTime
    print(f'move_channel: {runTime}')


def get_channel_by_name(channels: list[GuildChannel], name='') -> GuildChannel:
    channel = discord.utils.get(channels, name=name)
    if channel is None:
        raise Exception(f'#{name}チャンネルは存在しません')
    
    return channel
