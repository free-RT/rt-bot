# RT - RT Communicate, Description: バックエンドと通信をするためのものです。

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Union, Optional

from asyncio import sleep

from discord.ext import commands
import discord

from websockets import connect

from .rt_module.src import rtc, rtc_feature_types as rft

if TYPE_CHECKING:
    from .typed import RT


class RTCGeneralFeatures(commands.Cog):
    def __init__(self, bot: RT):
        self.bot = bot
        for name, value in map(lambda name: (name, getattr(self, name)), dir(self)):
            if name.startswith("get"):
                self.bot.rtc.set_event(value)

    async def get_user(self, user_id: int) -> Optional[rft.User]:
        if user := self.bot.get_user(user_id):
            return rft.User(
                id=user.id, name=user.name,
                avatar_url=user.avatar.url, full_name=str(user)
            )

    async def get_guilds(self, user_id: int) -> list[rft.Guild]:
        return [
            self._prepare_guild(guild)
            for guild in self.bot.guilds
            if guild.get_member(user_id) is not None
        ]

    def _get_guild_child(
        self, guild: rft.Guild, key: str, id_: int
    )-> Optional[dict]:
        data = discord.utils.get(guild[key], id=id_)
        data["guild"] = guild
        return data

    async def get_member(self, data: tuple[rft.Guild, int])-> Optional[rft.Member]:
        return self._get_guild_child(data[0], "members", data[1])

    def _get_channel(
        self, guild: discord.Guild, mode: Optional[Literal["voice", "text"]] = None
    ) -> list[rft.Channel]:
        channels = []
        for channel in guild.channels:
            type_ = "text" \
                if isinstance(channel, (discord.TextChannel, discord.Thread)) \
                else "voice"
            if mode is None or type_ == mode:
                channels.append(rft.Channel(
                    id=channel.id, name=channel.name, guild=None, type=type_
                ))
        return channels

    async def get_channel(self, data: tuple[rft.Guild, int]) -> Optional[rft.Channel]:
        return self._get_guild_child(data[0], "channels", data[1])

    async def get_role(self, data: tuple[rft.Guild, int]) -> Optional[rft.Role]:
        for id_, name in data["roles"].items():
            if id_ == data[1]:
                return rft.Role(id=data[1], name=name)

    def _prepare_guild(self, guild: discord.Guild) -> rft.Guild:
        text_channels = self._get_channel(guild, "text")
        voice_channels = self._get_channel(guild, "voice")
        return rft.Guild(
            id=guild.id, name=guild.name, avatar_url=getattr(guild.icon, "url", ""),
            members=[
                rft.Member(
                    id=member.id, name=member.name, avatar_url=getattr(
                        member.avatar, "url", ""
                    ),
                    full_name=str(member), guild=None
                ) for member in guild.members
            ], text_channels=text_channels, voice_channels=voice_channels,
            channels=text_channels + voice_channels, roles=[
                rft.Role(id=role.id, name=role.name)
                for role in guild.roles
            ]
        )

    async def get_guild(self, guild_id: int) -> Optional[rft.Guild]:
        if guild := self.bot.get_guild(guild_id):
            return self._prepare_guild(guild)

    async def get_lang(self, user_id: int) -> Union[Literal["ja", "en"], str]:
        return self.bot.cogs["Language"].get(user_id)


class ExtendedRTC(rtc.RTConnection):

    bot: RT

    def logger(self, mode: str, *args, **kwargs) -> None:
        return self.bot.print("[RTConnection]", f"[{mode}]", *args, **kwargs)


def setup(bot: RT):
    if not hasattr(bot, "rtc"):
        bot.rtc = self = ExtendedRTC("Bot", loop=bot.loop)
        self.bot = bot

        @bot.listen()
        async def on_close(_):
            if self.ws is not None and not self.ws.closed:
                await self.ws.close(reason="Bot終了のため。")

        async def communicate():
            # 接続をします。
            while not bot.is_closed():
                await bot.wait_until_ready()
                try:
                    await self.communicate(await connect(f"ws://{bot.get_ip()}/rtc"))
                except OSError as e:
                    ...
                self.logger("info", "Disconnected from backend")
                self.logger("info", "Reconnect in three seconds")
                self.ready.clear()
                await sleep(3)

        bot.loop.create_task(communicate(), name="RTConnection")
    bot.add_cog(RTCGeneralFeatures(bot))