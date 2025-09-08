import discordbot
import asyncio
from utils.format_date import formate_date


def handle_pull_request(data):
    action = data.get("action")
    if action == "opened":
        pr = data["pull_request"]

        # Construir el diccionario con toda la info
        pr_data = {
            "number": pr["number"],
            "title": pr["title"],
            "author": pr["user"]["login"],
            "author_avatar": pr["user"].get("avatar_url"),
            "description": pr.get("body") or "Sin descripción",
            "base_branch": pr["base"]["ref"],
            "head_branch": pr["head"]["ref"],
            "created_at": formate_date(pr["created_at"]),
            "url": pr["html_url"],
        }

        asyncio.run_coroutine_threadsafe(
            discordbot.notify_pull_request(pr_data),
            discordbot.bot.loop,
        )
