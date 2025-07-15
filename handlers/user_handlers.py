"""
User handlers for the Quiz Bot
Handles all user interactions and commands
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.referral_utils import ReferralUtils
from utils.messages import Messages

logger = logging.getLogger(__name__)

class UserHandlers:
    def __init__(self, database):
        self.db = database
        self.referral_utils = ReferralUtils(database)
        self.messages = Messages()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        username = user.username or ""
        first_name = user.first_name or ""
        
        # Check if user came via referral link
        referral_code = None
        if context.args:
            referral_code = context.args[0]
            logger.info(f"User {user_id} started with referral code: {referral_code}")
        
        # Generate unique referral code for this user
        user_referral_code = self.referral_utils.generate_referral_code(user_id)
        
        # Add user to database
        self.db.add_user(user_id, username, first_name, user_referral_code)
        
        # Process referral if provided
        if referral_code:
            await self._process_referral(update, context, referral_code, user_id)
        
        # Send welcome message with main menu
        await self._send_main_menu(update, context)
    
    async def _process_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str, referred_user_id: int):
        """Process referral link"""
        referrer = self.db.get_user_by_referral_code(referral_code)
        
        if referrer and referrer['user_id'] != referred_user_id:
            success = self.db.add_referral(referrer['user_id'], referred_user_id)
            if success:
                # Notify referrer
                try:
                    await context.bot.send_message(
                        chat_id=referrer['user_id'],
                        text=self.messages.referral_success(update.effective_user.first_name)
                    )
                except Exception as e:
                    logger.error(f"Failed to notify referrer: {e}")
    
    async def _send_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu with inline keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Mening natijam", callback_data="my_results")],
            [InlineKeyboardButton("👥 Do'stlarni taklif qilish", callback_data="invite_friends")],
            [InlineKeyboardButton("📋 Qoidalar", callback_data="rules")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            self.messages.welcome_message(),
            reply_markup=reply_markup
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "my_results":
            await self._show_my_results(query, context, user_id)
        elif data == "invite_friends":
            await self._show_invite_friends(query, context, user_id)
        elif data == "rules":
            await self._show_rules(query, context)
        elif data == "back_to_menu":
            await self._show_main_menu_callback(query, context)
    
    async def _show_my_results(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show user's referral results"""
        user = self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
            return
        
        referral_count = user['referral_count']
        eligible = user['eligible']
        
        keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            self.messages.my_results_message(referral_count, eligible),
            reply_markup=reply_markup
        )
    
    async def _show_invite_friends(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Show invite friends with referral link"""
        user = self.db.get_user(user_id)
        
        if not user:
            await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
            return
        
        referral_link = self.referral_utils.generate_referral_link(user['referral_code'])
        
        keyboard = [
            [InlineKeyboardButton("📤 Havola ulashish", url=f"https://t.me/share/url?url={referral_link}")],
            [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            self.messages.invite_friends_message(referral_link),
            reply_markup=reply_markup
        )
    
    async def _show_rules(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show quiz rules"""
        quiz_date = self.db.get_quiz_date()
        
        keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            self.messages.rules_message(quiz_date),
            reply_markup=reply_markup
        )
    
    async def _show_main_menu_callback(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu from callback"""
        keyboard = [
            [InlineKeyboardButton("📊 Mening natijam", callback_data="my_results")],
            [InlineKeyboardButton("👥 Do'stlarni taklif qilish", callback_data="invite_friends")],
            [InlineKeyboardButton("📋 Qoidalar", callback_data="rules")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            self.messages.welcome_message(),
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        # For now, just redirect to main menu
        await self._send_main_menu(update, context)
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new members joining the group"""
        # This handler can be used to track when users join the group
        # via referral links, but it requires the bot to be in the group
        # and have appropriate permissions
        
        for member in update.message.new_chat_members:
            user_id = member.id
            logger.info(f"New member joined group: {user_id}")
            
            # Here you could implement logic to track group joins
            # and potentially award additional points or benefits
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await update.message.reply_text(self.messages.help_message())
