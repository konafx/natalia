from typing import Optional
from collections.abc import Callable
from itertools import filterfalse
import asyncio

import discord


def get_members(member: discord.Member, exclude_bot=True) -> list[discord.Member]:
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


def get_attendees(channel: discord.VoiceChannel, exclude_bot=True) -> list[discord.Member]:
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
    attendees = channel.members
    if exclude_bot:
        attendees = list(filterfalse(lambda attendee: attendee.bot, attendees))

    return attendees

def get_muted(member: discord.Member) -> bool:
    if not member.voice:
        raise Exception('ボイチャに接続してないヨ〜！')

    return member.voice.mute or member.voice.self_mute

def attendees_flow(
        source: discord.VoiceChannel,
        destination: discord.VoiceChannel,
        mute: Optional[bool] = None,
        reason: Optional[str] = None,
        sieve: Optional[Callable[discord.Member, bool]] = None
        ) -> list[asyncio.coroutine]:
    """
    """
    attendees = get_attendees(source)
    if sieve:
        attendees = filter(sieve, attendees)

    coroutines = [
        attendee.edit(
            voice_channel=destination,
            mute=mute,
            reason=reason
            )
        for attendee in attendees
    ]

    return coroutines
