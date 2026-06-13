import os
import requests

def send_line_message(notification_text: str) -> None:
    url = "https://api.line.me/v2/bot/message/push"
    
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }

    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": notification_text
            }
        ]
    }
    
    requests.post(url, headers=headers, json=data)
