import discord


def command_usage(ctx: discord.ext.commands.Context):
    return f'Usage: {ctx.bot.command_prefix}{ctx.command.name} {ctx.command.usage}'
