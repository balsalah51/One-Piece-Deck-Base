#!/usr/bin/env python3
"""OPDB Discord bot — channels, leader rooms, consensus posts, and flair."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BOT_DIR))

from opdb_bot.envload import describe_token_search, load_guild_id, load_token  # noqa: E402

from opdb_bot.config import (  # noqa: E402
    GENERIC_CATEGORIES,
    LEADERS,
    METAS,
    SITE_URL,
    leaders_for_meta,
    planned_channel_names,
    refresh_leaders,
)
from opdb_bot.data import all_planned_messages, load_card_cache, load_consensus  # noqa: E402
from opdb_bot.emojis import ensure_all_faces  # noqa: E402


def print_plan() -> None:
    cache = load_card_cache()
    consensus = load_consensus()
    print(f"OPDB Discord plan · {SITE_URL}")
    print(f"Leaders: {len(LEADERS)}")
    print()
    for spec in GENERIC_CATEGORIES:
        print(f"# {spec['name']}")
        for ch in spec["channels"]:
            flag = " [page]" if ch.get("readonly") else ""
            print(f"  #{ch['name']}{flag} — {ch['topic']}")
        print()
    for meta in METAS:
        print(f"# {meta['category']}")
        print(f"  #{meta['discussion']} — {meta['topic']}")
        for leader in leaders_for_meta(meta["key"]):
            entry = consensus.get(leader["id"]) or {}
            n = entry.get("lists") or 0
            print(f"  #{leader['key']}  {leader['name']} ({leader['id']})  {n} lists")
        print()
    print("Flair roles:")
    for leader in LEADERS:
        print(f"  {leader['name']}  emoji:{leader['key'].replace('-', '_')}")
    print()
    names = planned_channel_names()
    print(f"{len(names)} channels planned")
    for item in all_planned_messages(cache, consensus):
        embed = item["embed"]
        print(
            f"  consensus {item['leader']['id']}: "
            f"{len(embed['description'])} desc chars, footer={embed['footer']}"
        )


async def run_bot() -> None:
    import discord
    from discord import app_commands
    from discord.ext import commands

    from opdb_bot.flair import FlairView
    from opdb_bot.guildsetup import post_consensus, post_info_pages, setup_guild
    from opdb_bot.config import channel_name

    token, token_source = load_token(BOT_DIR)
    if not token:
        raise SystemExit(
            "No bot token found.\n"
            f"{describe_token_search(BOT_DIR)}\n"
            "In this same Command Prompt run:\n"
            "  set /p DISCORD_TOKEN=Paste token and press Enter: \n"
            "  set PYTHONUTF8=1\n"
            "  python bot.py"
        )

    guild_id_raw = load_guild_id(BOT_DIR)
    try:
        guild_id = int(guild_id_raw) if guild_id_raw else None
    except ValueError:
        raise SystemExit(
            "DISCORD_GUILD_ID must be empty or the server number. Do not put the token there."
        )

    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    def allowed_guild(guild: discord.Guild | None) -> bool:
        if guild is None:
            return False
        if guild_id is None:
            return True
        return guild.id == guild_id

    def is_admin(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        perms = interaction.user.guild_permissions
        return bool(perms.administrator or perms.manage_guild)

    @bot.event
    async def on_ready() -> None:
        refresh_leaders()
        ensure_all_faces(download=False)
        bot.add_view(FlairView())
        try:
            if guild_id:
                bot.tree.copy_global_to(guild=discord.Object(id=guild_id))
                await bot.tree.sync(guild=discord.Object(id=guild_id))
            else:
                await bot.tree.sync()
        except discord.HTTPException as exc:
            print("slash sync failed:", exc)
        print(f"OPDB bot ready as {bot.user} in {len(bot.guilds)} guild(s)")

    @bot.event
    async def on_member_join(member: discord.Member) -> None:
        if not allowed_guild(member.guild):
            return
        welcome = discord.utils.get(member.guild.text_channels, name="welcome")
        flair = discord.utils.get(member.guild.text_channels, name="flair")
        if welcome is None:
            return
        bits = [f"Welcome {member.mention}."]
        if flair:
            bits.append(f"Grab a leader face in {flair.mention}.")
        try:
            await welcome.send(" ".join(bits))
        except discord.HTTPException:
            pass

    @bot.tree.command(name="opdb-setup", description="Create OPDB channels, flair, and consensus posts")
    async def opdb_setup(interaction: discord.Interaction) -> None:
        if not allowed_guild(interaction.guild) or not is_admin(interaction):
            await interaction.response.send_message("Admins only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        assert interaction.guild is not None
        refresh_leaders()
        try:
            log = await setup_guild(interaction.guild, post_lists=True)
        except Exception as exc:  # noqa: BLE001
            await interaction.followup.send(
                f"Setup stopped: {exc}. Check Command Prompt. Run /opdb-setup again to continue.",
                ephemeral=True,
            )
            raise
        bot.add_view(FlairView())
        leaders_made = sum(1 for L in LEADERS if L["key"] in log)
        await interaction.followup.send(
            f"Setup complete. {leaders_made}/{len(LEADERS)} leader rooms. "
            "Check OP17 and Format staples on the left. Re-run anytime.",
            ephemeral=True,
        )

    @bot.tree.command(name="opdb-consensus", description="Refresh pinned consensus lists in every leader channel")
    async def opdb_consensus(interaction: discord.Interaction) -> None:
        if not allowed_guild(interaction.guild) or not is_admin(interaction):
            await interaction.response.send_message("Admins only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        assert interaction.guild is not None
        refresh_leaders()
        updated = 0
        missing = []
        for leader in LEADERS:
            channel = discord.utils.get(interaction.guild.text_channels, name=channel_name(leader))
            if channel is None:
                missing.append(leader["key"])
                continue
            await post_consensus(channel, leader)
            updated += 1
        extra = f" Missing channels: {', '.join(missing)}." if missing else ""
        await interaction.followup.send(f"Updated {updated} consensus posts.{extra}", ephemeral=True)

    @bot.tree.command(name="opdb-flair", description="Repost the leader flair page")
    async def opdb_flair(interaction: discord.Interaction) -> None:
        if not allowed_guild(interaction.guild) or not is_admin(interaction):
            await interaction.response.send_message("Admins only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        assert interaction.guild is not None
        refresh_leaders()
        flair = discord.utils.get(interaction.guild.text_channels, name="flair")
        if flair is None:
            await interaction.followup.send("No #flair channel. Run `/opdb-setup` first.", ephemeral=True)
            return
        channels = {ch.name: ch for ch in interaction.guild.text_channels}
        await post_info_pages(interaction.guild, channels)
        bot.add_view(FlairView())
        await interaction.followup.send("Flair page refreshed.", ephemeral=True)

    @bot.tree.command(name="opdb-leader", description="Post this channel's consensus list")
    @app_commands.describe(leader="Leader key, or leave blank to use this channel")
    async def opdb_leader(interaction: discord.Interaction, leader: str | None = None) -> None:
        if interaction.guild is None or not allowed_guild(interaction.guild):
            await interaction.response.send_message("Not in the OPDB guild.", ephemeral=True)
            return
        key = (leader or getattr(interaction.channel, "name", "") or "").strip().lower()
        match = next((L for L in LEADERS if L["key"] == key or L["id"].lower() == key), None)
        if match is None:
            choices = ", ".join(L["key"] for L in LEADERS)
            await interaction.response.send_message(f"Unknown leader. Try: {choices}", ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.followup.send("Use this in a text channel.")
            return
        await post_consensus(channel, match)
        await interaction.followup.send(f"Posted {match['name']} consensus.")

    try:
        print(f"Starting bot (token from {token_source}, {len(token)} chars)")
        await bot.start(token)
    except discord.LoginFailure:
        raise SystemExit(
            "Discord rejected the token (401). Use Bot → Reset Token → Copy, "
            "not the Application ID or Client Secret. Then run the set /p line again."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="OPDB Discord bot")
    parser.add_argument("--plan", action="store_true", help="Print the channel/flair/consensus plan and exit")
    parser.add_argument("--emojis", action="store_true", help="Crop leader-face PNGs into assets/emojis and exit")
    args = parser.parse_args()
    if args.plan:
        print_plan()
        return
    if args.emojis:
        for path in ensure_all_faces(force=True):
            print("wrote", path)
        return
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
