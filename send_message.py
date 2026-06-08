import os
import requests

from pintland_calendar import format_message

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

response = requests.post(
    WEBHOOK_URL,
    json={
        "content": format_message()
    }
)

response.raise_for_status()

print("Message sent successfully.")
