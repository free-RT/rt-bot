import discord
from discord.ext import commands
from typing import List

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.command(aliases=["バン", "ばん", "BAN"])
    async def ban(self, ctx, *members: List[discord.Member]):
        """!lang ja
        --------
        メンバーをBANできます。

        Parameters
        ----------
        members : list[mention]
        誰をBANするかです。空白で区切って複数人指定もできます。"""
        excepts = []
        for m in members:
            try:
                await ctx.guild.ban(m)
            except:
                excepts.append(m)
        if len(excepts) == 0:
            await ctx.reply("完了。", delete_after=5)
        else:
            await ctx.reply(f"BANを実行しました。\n(しかし、{', '.join(excepts)}のBANに失敗しました。)")

    @commands.has_permissions(kick_members=True)
    @commands.command(extras={
        "headding": {
            "ja": "メンバーのキック",
            "en": "Kick members"
        }, "parent": ""
    },
         aliases=["キック", "きっく", "KICK"])
    async def kick(self, ctx, *members: List[discord.Member]):
        """!lang ja
        --------
        メンバーをキックできます。

        Parameters
        ----------
        members : list[member]
        誰をキックするかのメンションです。空白で区切って複数人指定もできます。"""
        excepts = []
        for m in members:
            try:
                await ctx.guild.kick(m)
            except:
                excepts.append(m)
        if len(excepts) == 0:
            await ctx.reply("完了。", delete_after=5)
        else:
            await ctx.reply(f"BANを実行しました。\n(しかし、{', '.join(excepts)}のBANに失敗しました。)")

def setup(bot):
    bot.add_cog(Moderation(bot))
