import discordbot 
import asyncio
#Hola
def handle_issues(data):   
    action = data.get("action")
    if action == "opened":
        issue = data["issue"]
        title = issue["title"]
        url = issue["html_url"]
        asyncio.run_coroutine_threadsafe(
            discordbot.notify_issue(title, url), discordbot.bot.loop
        )
