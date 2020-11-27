from typing import Union, Optional, List
from functools import reduce
from itertools import islice

from discord.ext import commands
from discord.abc import GuildChannel, PrivateChannel
import discord
import emoji

from utils.voice import get_members, move_channnel


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
        print(f'{payload}')

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            return

        if message.content != WATCH_MESSAGE:
            return

        # 命令を受信したら次の命令のためにユーザーが押したリアクションを削除する
        for reaction in message.reactions:
            await message.remove_reaction(reaction, payload.member)
        
        # Reaction判定
        if payload.emoji.name == MEETING_REACTION:
            await channel.send('MEETING')
        elif payload.emoji.name == MUTE_REACTION:
            await channel.send('MUTE')
        else:
            await channel.send(f'{payload.emoji.name=}')

        # attendees = get_members(payload.member)

        print(f'{channel.name=} {channel.name == "fushimi-general"}')

    @commands.command(
            brief='リアクションを押してほしいナ！',
            )
    async def mover(self, ctx: commands.Context, meeting_channel_name: str = '', mute_channel_name: str = ''):
        if not meeting_channel_name and not mute_channel_name:
            # raise error
            await ctx.send('引数2つ指定しろ')
            return

        voice_channels: List[Optional[discord.VoiceChannel]] = []
        for channel_name in [meeting_channel_name, mute_channel_name]:
            channel = discord.utils.get(ctx.guild.channels, name=channel_name)
            if channel is None:
                # raise error
                await ctx.send(f'{channel_name}は存在しねえ')
                return
            
            if not isinstance(channel, discord.VoiceChannel):
                # raise error
                await ctx.send(f'{channel_name}はボイチャじゃねえ')
                return

            voice_channels.append(channel)
        
        self.channels = {
            'meeting': voice_channels[0],
            'mute': voice_channels[1]
        }

        self.reactions = {
            'meeting': MEETING_REACTION,
            'mute': MUTE_REACTION,
        }

        message = await ctx.send(WATCH_MESSAGE)
        await message.add_reaction(self.reactions['meeting'])
        await message.add_reaction(self.reactions['mute'])

    def init_target_channels(self, meeting_channel_name: str = 'meeting', mute_channel_name: Optional[str] = 'mute', channels: List[Optional[Channel]]):
        meeting_channel = discord.utils.get(channels, name=meeting_channel_name)
        mute_channel = discord.utils.get(channels, name=mute_channel_name)
        self.channels = {
            'meeting': meering_channel,
            'mute': mute_channel
        }

def setup(bot: commands.Bot):
    bot.add_cog(AmongUs(bot))
