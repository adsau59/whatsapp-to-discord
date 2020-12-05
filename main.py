import re
from threading import Thread
from typing import Optional
import time

from supbot import Supbot
from supbot.helper import contact_number_equal as nequal

import discord_client
from config import config

group_name = config.get("whatsapp_group")
supbot: Optional[Supbot] = None
client: Optional[discord_client.MyClient] = None


def find_user(number):
    search = [x for x in config.get("members", []) if nequal(number, x["contact"])]
    return search[0] if len(search) > 0 else None


def group_message(_group_name: str, contact_name: str, message: str):
    if _group_name != group_name:
        return

    match = re.findall(r"([^\s\"']+|\"([^\"]*)\"|'([^']*)')", message)
    parts = [x[0] if x[1] == "" else x[1] for x in match]

    if "@everyone" in message or "@all" in message:
        reply = ""
        for n in [x["contact"] for x in config.get("members", [])]:
            reply += f"@{n} "
        supbot.send_message(group_name, reply, True)

    elif parts[0] == "!add" and len(parts) == 3:

        old_list = config.get("members", [])
        old_list.append({"contact": parts[1], "discord_id": parts[2]})
        config.set("members", old_list)

        supbot.send_message(group_name, "added successfully")

    elif parts[0] in ["!quit", "!exit"]:
        if find_user(contact_name).get("admin", False):
            supbot.send_message(group_name, "quitting...")
            time.sleep(1)

            discord_client.close(client)
            supbot.quit()
        else:
            supbot.send_message(group_name, "You are not my master 😠")

    elif parts[0] in ["!discord", "!dc"] and len(parts) > 1:
        to_send = " ".join(parts[1:])
        user = find_user(contact_name)
        if user is None:
            return
        discord_client.send_message(client, user["discord_id"], to_send)


def forward_message(message):
    supbot.send_message(group_name, message)


def main():
    with supbot:
        supbot.send_message(group_name, "Hello, I'm Back 😊")
        supbot.wait_for_finish()


if __name__ == '__main__':
    supbot = Supbot(group_message_received=group_message)
    Thread(target=main).start()
    client = discord_client.MyClient(forward_message)
    client.run(discord_client.token)
