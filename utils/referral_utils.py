"""
Referral utility functions
Handles referral link generation and processing
"""

import hashlib
import base64
import logging
from config import Config

logger = logging.getLogger(__name__)

class ReferralUtils:
    def __init__(self, database):
        self.db = database
        self.config = Config()
    
    def generate_referral_code(self, user_id: int) -> str:
        """Generate unique referral code for user"""
        # Create a hash based on user_id and a secret
        secret = "quiz_bot_secret_2024"  # In production, use environment variable
        data = f"{user_id}_{secret}"
        
        # Create SHA256 hash
        hash_object = hashlib.sha256(data.encode())
        hash_hex = hash_object.hexdigest()
        
        # Take first 8 characters and make it URL-safe
        referral_code = base64.urlsafe_b64encode(hash_hex[:8].encode()).decode()[:8]
        
        return f"ref_{referral_code}"
    
    def generate_referral_link(self, referral_code: str) -> str:
        """Generate group invite referral link"""
        # For testforviktorina group, create a group invite link with referral code
        return f"https://t.me/{self.config.group_username}?start={referral_code}"
    
    def validate_referral_code(self, referral_code: str) -> bool:
        """Validate referral code format"""
        if not referral_code:
            return False
        
        if not referral_code.startswith("ref_"):
            return False
        
        if len(referral_code) != 12:  # "ref_" + 8 characters
            return False
        
        return True
    
    def get_referral_stats(self, user_id: int) -> dict:
        """Get referral statistics for user"""
        user = self.db.get_user(user_id)
        
        if not user:
            return {
                'referral_count': 0,
                'eligible': False,
                'needed': self.config.min_referrals
            }
        
        referral_count = user['referral_count']
        eligible = referral_count >= self.config.min_referrals
        needed = max(0, self.config.min_referrals - referral_count)
        
        return {
            'referral_count': referral_count,
            'eligible': eligible,
            'needed': needed
        }
