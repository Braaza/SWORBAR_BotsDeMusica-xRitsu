from ..models import LavalinkPlayer
import disnake
from ..converters import fix_characters, time_format
import itertools
from typing import List


def load(player: LavalinkPlayer) -> List[disnake.Embed]:

    embed = disnake.Embed(color=player.bot.get_color(player.guild.me))
    embed_queue = None

    if not player.paused:
        embed.set_author(
            name="Tocando Agora:",
            icon_url="https://cdn.discordapp.com/attachments/480195401543188483/895862881105616947/music_equalizer.gif"
        )
    else:
        embed.set_author(
            name="Em Pausa:",
            icon_url="https://cdn.discordapp.com/attachments/480195401543188483/896013933197013002/pause.png"
        )

    embed.set_footer(
        text=str(player),
        icon_url="https://cdn.discordapp.com/attachments/480195401543188483/907119505971486810/speaker-loud-speaker.gif"
    )

    if player.current.is_stream:
        duration = "🔴 **⠂Livestream**"
    else:
        duration = f"⏰ **⠂Duração:** `{time_format(player.current.duration)}`"

    txt = f"[**{player.current.title}**]({player.current.uri})\n\n" \
          f"> {duration}\n" \
          f"> 💠 **⠂Uploader**: `{player.current.author}`\n" \
          f"> ✋ **⠂Pedido por:** {player.current.requester.mention}\n" \
          f"> 🔊 **⠂Volume:** `{player.volume}%`"

    if player.current.repeats:
        txt += f"\n> 🔂 **⠂Repetições restantes:** `{player.current.repeats}`"

    if player.current.playlist:
        txt += f"\n> 📑 **⠂Playlist:** [`{fix_characters(player.current.playlist['name'], limit=17)}`]({player.current.playlist['url']})"

    txt += "\n"

    if player.command_log:
        txt += f"```ini\n[Última Interação]:```{player.command_log}\n"

    if len(player.queue):

        char_limit = 26 if not player.static else 33

        queue_txt = "\n".join(
            f"`{n + 1}) [{time_format(t.duration) if t.duration else '🔴 Livestream'}]` [`{fix_characters(t.title, char_limit)}`]({t.uri})"
            for n, t
            in (enumerate(itertools.islice(player.queue, (20 if player.static else 3))))
        )

        if not player.static:

            txt += f"```ini\n[Próximas Músicas]:``` {queue_txt}"

            if (qsize := len(player.queue)) > 3:
                txt += f"\n\n`E mais {qsize - 3}" + (f" |` {player.msg_ad}" if player.msg_ad else " músicas`")
            else:
                txt += f"\n\n{player.msg_ad}" if player.msg_ad else ""

        else:

            embed_queue = disnake.Embed(title=f"Músicas na fila:", color=player.bot.get_color(player.guild.me),
                                        description=f"\n{queue_txt}")
            if (qsize := len(player.queue)) > 20:
                embed_queue.description += f"\n\nE mais **{qsize - 20}** músicas."
            txt += f"{'-' * 40}\n{player.msg_ad}" if player.msg_ad else ""

    else:
        txt += f"{'-' * 40}\n{player.msg_ad}" if player.msg_ad else ""

    embed.description = txt

    if player.static:
        embed.set_image(url=player.current.thumb)
    else:
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/480195401543188483/795080813678559273/rainbow_bar2.gif")
        embed.set_thumbnail(url=player.current.thumb)

    player.bot.loop.create_task(player.process_rpc(player.vc.channel))

    embeds = [embed_queue, embed] if embed_queue else [embed]

    return embeds