"""
Configuration settings for the Quiz Bot
"""

import os

class Config:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot_username = os.getenv("BOT_USERNAME", "QuizBot")
        self.group_id = os.getenv("GROUP_ID")  # The group where users should join
        self.group_username = os.getenv("GROUP_USERNAME", "testforviktorina")  # Group username
        self.min_referrals = int(os.getenv("MIN_REFERRALS", "5"))
        self.admin_ids = self._parse_admin_ids()
        
    def _parse_admin_ids(self):
        """Parse admin IDs from environment variable"""
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            try:
                return [int(admin_id.strip()) for admin_id in admin_ids_str.split(",")]
            except ValueError:
                return []
        return []
    
    @property
    def referral_base_url(self):
        """Base URL for referral links"""
        return f"https://t.me/{self.bot_username}?start="
