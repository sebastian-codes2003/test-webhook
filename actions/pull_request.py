import discordbot
import asyncio

def handle_pull_request(data):
    action = data.get("action")
    if action == "opened":
        pr = data["pull_request"]
        title = pr["title"]
        url = pr["html_url"]
        asyncio.run_coroutine_threadsafe(
            discordbot.notify_pull_request(title, url), discordbot.bot.loop
        )
