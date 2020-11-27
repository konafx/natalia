from typing import Optional
from itertools import filterfalse
from discord import Member, VoiceChannel
from discord.abc import GuildChannel


def get_attendees(member: Member, exclude_bot=True) -> list[Member]:
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


async def move_channnel(member: Member, destination: VoiceChannel, mute=False, reason: Optional[str] = None):
    await member.edit(
        reason=reason,
        mute=mute,
        voice_channel=destination
        )


def get_channel_by_name(channels: list[GuildChannel], name='') -> GuildChannel:
    channel = discord.utils.get(channels, name=name)
    if channel is None:
        raise Exception(f'#{name}チャンネルは存在しません')
    
    return channel
