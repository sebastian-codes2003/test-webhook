import discordbot
import asyncio
from utils.format_date import formate_date


def handle_pull_request(data):
    action = data.get("action")
    if action == "opened":
        pr = data["pull_request"]
        pr_id = pr["id"]
        pr_number = pr["number"]
        pr_title = pr.get("title") or "PR"
        pr_url = pr["html_url"]
        pr_author = pr["user"]["login"]
        pr_author_avatar = pr["user"].get("avatar_url")
        pr_description = pr.get("body") or "Sin descripción"
        pr_base_branch = pr["base"]["ref"]
        pr_head_branch = pr["head"]["ref"]
        pr_created_at = pr["created_at"]
        pr_url = pr["html_url"]
        pr_repository_full = data["repository"]["full_name"] # SebaschaM/test-webhook
        author_repository = pr_repository_full.split("/")[0] # SebaschaM

        pr_data_json = {
            "id": pr_id,
            "number": pr_number,
            "title": pr_title,
            "url": pr_url,
            "author_pr": pr_author,
            "author_avatar": pr_author_avatar,
            "description": pr_description,
            "base_branch": pr_base_branch,
            "head_branch": pr_head_branch,
            "author_repository": author_repository,
            "repository_full": pr_repository_full,
            "created_at": formate_date(pr_created_at),
        }

        asyncio.run_coroutine_threadsafe(
            discordbot.notify_new_pull_request(pr_data_json),
            discordbot.bot.loop,
        )
