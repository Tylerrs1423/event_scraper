import os
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    """
    Lightweight wrapper around Slack WebClient.

    Requires environment variables:
      - SLACK_BOT_TOKEN: xoxb- token for your bot
      - SLACK_CHANNEL_ID: channel ID to post into (e.g. C0123456789)
    """

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None) -> None:
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN", "").strip()
        self.channel_id = channel_id or os.getenv("SLACK_CHANNEL_ID", "").strip()
        self.client = WebClient(token=self.bot_token) if self.bot_token else None

    def is_configured(self) -> bool:
        return bool(self.client and self.channel_id)

    def send_message(self, text: str) -> bool:
        """Send a plain-text message to the configured channel. Returns True on success."""
        if not self.is_configured():
            return False
        try:
            self.client.chat_postMessage(channel=self.channel_id, text=text)
            return True
        except SlackApiError:
            return False


