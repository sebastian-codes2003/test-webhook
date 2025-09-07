import discordbot
import asyncio


def handle_pull_request(data):
    action = data.get("action")
    if action == "opened":
        pr = data["pull_request"]

        # Extraer información del PR
        number = pr["number"]
        title = pr["title"]
        author = pr["user"]["login"]
        description = pr.get("body") or "Sin descripción"
        base_branch = pr["base"]["ref"]
        head_branch = pr["head"]["ref"]
        created_at = pr["created_at"]

        url = pr["html_url"]

        formatted_title = (
            f"📌 **Pull Request #{number}**\n"
            f"**Título:** {title}\n"
            f"**Autor:** {author}\n"
            f"**Descripción:** {description}\n"
            f"**Ramas:** `{head_branch}` → `{base_branch}`\n"
            f"**Creado en:** {created_at}"
        )

        asyncio.run_coroutine_threadsafe(
            discordbot.notify_pull_request(formatted_title, url),
            discordbot.bot.loop,
        )
