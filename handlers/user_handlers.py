"""
User handlers for the Quiz Bot
Handles all user interactions and commands
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.referral_utils import ReferralUtils
from utils.messages import Messages
from config import Config

logger = logging.getLogger(__name__)

class UserHandlers:
    def __init__(self, database):
        self.db = database
        self.referral_utils = ReferralUtils(database)
        self.config = Config()
        self.messages = Messages(self.config.bot_username)
    
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
        
        # Check if user already exists
        existing_user = self.db.get_user(user_id)
        
        if not existing_user:
            # Generate unique referral code for new user
            user_referral_code = self.referral_utils.generate_referral_code(user_id)
            # Add new user to database
            self.db.add_user(user_id, username, first_name, user_referral_code)
        else:
            # Update existing user's username and first_name if changed
            if existing_user['username'] != username or existing_user['first_name'] != first_name:
                self.db.update_user_info(user_id, username, first_name)
        
        # Process referral if provided
        if referral_code:
            await self._process_referral(update, context, referral_code, user_id)
        
        # Check if user has phone number
        current_user = self.db.get_user(user_id)
        if current_user and not current_user.get('phone_number'):
            # Request phone number
            await self._request_phone_number(update, context)
        else:
            # Send welcome message with main menu
            await self._send_main_menu(update, context)
    
    async def _process_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str, referred_user_id: int):
        """Process referral link"""
        referrer = self.db.get_user_by_referral_code(referral_code)
        
        if referrer and referrer['user_id'] != referred_user_id:
            # Check if the referred user has joined the group
            is_group_member = await self._check_group_membership(context, referred_user_id)
            
            if is_group_member:
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
            else:
                # Send message to user to join the group first
                group_link = f"https://t.me/{self.config.group_username}"
                await update.message.reply_text(
                    f"📢 Viktorinaga qatnashish uchun avval @{self.config.group_username} guruhiga qo'shiling!\n\n"
                    f"🔗 Guruh havola: {group_link}\n\n"
                    f"Guruhga qo'shilganingizdan so'ng, /start buyrug'ini qayta yuboring."
                )
    
    async def _send_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send main menu with inline keyboard"""
        keyboard = [
            [InlineKeyboardButton("📊 Mening natijalarim", callback_data="my_results")],
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
        elif data == "admin_participants":
            await self._handle_admin_participants(query, context, user_id)
        elif data == "admin_select_winner":
            await self._handle_admin_select_winner(query, context, user_id)
        elif data == "admin_set_date":
            await self._handle_admin_set_date(query, context, user_id)
        elif data == "admin_winners":
            await self._handle_admin_winners(query, context, user_id)
    
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
        
        # Create pending referral for tracking group joins (only if not exists)
        existing_pending = self.db.get_pending_referral(user['referral_code'])
        if not existing_pending:
            self.db.add_pending_referral(user['referral_code'], user_id)
        
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
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check if user is providing phone number
        if message_text and (message_text.startswith('+') or message_text.isdigit()):
            # Validate phone number format
            if len(message_text) >= 9 and len(message_text) <= 15:
                # Update user's phone number
                success = self.db.update_user_phone(user_id, message_text)
                if success:
                    await update.message.reply_text(
                        "✅ Telefon raqamingiz muvaffaqiyatli saqlandi!\n\n"
                        "Endi viktorinada g'olib bo'lganingizda shu raqam orqali aniqlanasiz."
                    )
                    # Now send main menu
                    await self._send_main_menu(update, context)
                else:
                    await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
            else:
                await update.message.reply_text("❌ Noto'g'ri raqam formati. Qayta urinib ko'ring.")
        else:
            # For other messages, redirect to main menu
            await self._send_main_menu(update, context)
    
    async def _request_phone_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request phone number from user"""
        from telegram import KeyboardButton, ReplyKeyboardMarkup
        
        # Create keyboard with phone number request button
        keyboard = [
            [KeyboardButton("📱 Raqamni yuborish", request_contact=True)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "📱 **Telefon raqamingizni kiriting**\n\n"
            "Viktorinada g'olib bo'lganingizda shu raqam orqali aniqlanasiz.\n\n"
            "Raqamni quyidagi tugma orqali yuboring yoki qo'lda kiriting:\n"
            "Masalan: +998901234567",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new members joining the group via referral links"""
        
        # Skip if bot itself joined
        if update.message.new_chat_members and update.message.new_chat_members[0].id == context.bot.id:
            return
        
        for member in update.message.new_chat_members:
            user_id = member.id
            username = member.username or ""
            first_name = member.first_name or ""
            
            logger.info(f"New member joined group: {user_id}")
            
            # Generate referral code for new user
            user_referral_code = self.referral_utils.generate_referral_code(user_id)
            
            # Add user to database if not exists
            existing_user = self.db.get_user(user_id)
            if not existing_user:
                self.db.add_user(user_id, username, first_name, user_referral_code)
            
            # Try to find if this user joined via a referral link
            # Check pending referrals and match with timing
            pending_referrals = self.db.get_all_pending_referrals()
            
            # If there are pending referrals, we can try to match them
            # For now, we'll use the most recent pending referral as a heuristic
            if pending_referrals:
                most_recent = pending_referrals[0]  # Assuming ordered by newest first
                referrer_id = most_recent['referrer_id']
                referral_code = most_recent['referral_code']
                
                # Add the referral connection
                success = self.db.add_referral(referrer_id, user_id)
                if success:
                    # Remove the processed pending referral
                    self.db.remove_pending_referral(referral_code)
                    
                    # Notify the referrer
                    try:
                        referrer = self.db.get_user(referrer_id)
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 Tabriklaymiz!\n\n"
                                 f"Sizning referalingiz orqali {first_name} guruhga qo'shildi!\n"
                                 f"Sizning referal soningiz: {referrer['referral_count'] + 1}\n"
                                 f"Viktorinaga qatnashish huquqi: {'✅ Bor' if referrer['referral_count'] >= 0 else '❌ Yo`q'}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to notify referrer: {e}")
            
            # Welcome message to new group member
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 @testforviktorina guruhiga xush kelibsiz!\n\n"
                         "Viktorinaga qatnashish uchun botni ishga tushiring: /start"
                )
            except Exception as e:
                logger.error(f"Failed to send welcome message to new member: {e}")
    
    async def _check_group_membership(self, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
        """Check if user is a member of the target group"""
        try:
            # Try to get chat member info
            chat_member = await context.bot.get_chat_member(
                chat_id=f"@{self.config.group_username}", 
                user_id=user_id
            )
            
            # Check if user is a member (not left, kicked, or restricted)
            if chat_member.status in ['member', 'administrator', 'creator']:
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking group membership for user {user_id}: {e}")
            # If we can't check, assume they're not a member
            return False

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await update.message.reply_text(self.messages.help_message())
    
    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact (phone number) sharing"""
        if update.message.contact:
            user_id = update.effective_user.id
            phone_number = update.message.contact.phone_number
            
            # Update user's phone number
            success = self.db.update_user_phone(user_id, phone_number)
            if success:
                from telegram import ReplyKeyboardRemove
                await update.message.reply_text(
                    "✅ Telefon raqamingiz muvaffaqiyatli saqlandi!\n\n"
                    "Endi viktorinada g'olib bo'lganingizda shu raqam orqali aniqlanasiz.",
                    reply_markup=ReplyKeyboardRemove()
                )
                # Now send main menu
                await self._send_main_menu(update, context)
            else:
                await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
    
    async def _handle_admin_participants(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Handle admin participants callback"""
        if not self.db.is_admin(user_id):
            await query.edit_message_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        participants = self.db.get_all_participants()
        if not participants:
            await query.edit_message_text("📋 Hozircha hech kim viktorinaga qatnasha olmaydi.")
            return
        
        message = "👥 **Viktorina qatnashuvchilari:**\n\n"
        for i, participant in enumerate(participants, 1):
            username = f"@{participant['username']}" if participant['username'] else "Username yo'q"
            phone = participant['phone_number'] if participant['phone_number'] else "Telefon yo'q"
            message += f"{i}. {participant['first_name']} ({username})\n"
            message += f"   📱 {phone}\n"
            message += f"   🔗 Referallar: {participant['referral_count']}\n\n"
        
        message += f"**Jami qatnashuvchilar: {len(participants)}**"
        await query.edit_message_text(message, parse_mode='Markdown')
    
    async def _handle_admin_select_winner(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Handle admin select winner callback"""
        if not self.db.is_admin(user_id):
            await query.edit_message_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        participants = self.db.get_all_participants()
        if not participants:
            await query.edit_message_text("❌ Qatnashuvchilar yo'q.")
            return
        
        if len(participants) < 6:
            await query.edit_message_text("❌ Minimum 6 qatnashuvchi bo'lishi kerak.")
            return
        
        import random
        # Select winners
        winners = random.sample(participants, min(6, len(participants)))
        
        # First place - blender
        first_place = winners[0]
        self.db.add_winner(first_place['user_id'], "Blender (1-o'rin)")
        
        # Next 5 - vouchers
        voucher_winners = winners[1:6]
        for winner in voucher_winners:
            self.db.add_winner(winner['user_id'], "100,000 so'm vaucher")
        
        # Format winner message
        message = "🎉 **G'oliblar tanlandi!**\n\n"
        message += f"🥇 **1-o'rin (Blender):**\n"
        message += f"{first_place['first_name']}"
        if first_place['username']:
            message += f" (@{first_place['username']})"
        if first_place['phone_number']:
            message += f"\n📱 {first_place['phone_number']}"
        message += f"\nReferallar: {first_place['referral_count']}\n\n"
        
        message += "🎁 **Vaucher g'oliblari (100,000 so'm):**\n"
        for i, winner in enumerate(voucher_winners, 1):
            message += f"{i}. {winner['first_name']}"
            if winner['username']:
                message += f" (@{winner['username']})"
            if winner['phone_number']:
                message += f" - 📱 {winner['phone_number']}"
            message += f" - {winner['referral_count']} referal\n"
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    async def _handle_admin_set_date(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Handle admin set date callback"""
        if not self.db.is_admin(user_id):
            await query.edit_message_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        await query.edit_message_text(
            "📅 **Viktorina sanasini belgilash**\n\n"
            "Sanani belgilash uchun quyidagi buyruqni ishlating:\n"
            "`/setdate DD.MM.YYYY`\n\n"
            "Masalan: `/setdate 25.12.2024`",
            parse_mode='Markdown'
        )
    
    async def _handle_admin_winners(self, query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Handle admin winners callback"""
        if not self.db.is_admin(user_id):
            await query.edit_message_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        winners = self.db.get_winners()
        if not winners:
            await query.edit_message_text("🏆 Hozircha g'oliblar yo'q.")
            return
        
        message = "🏆 **G'oliblar ro'yxati:**\n\n"
        for winner in winners:
            username = f"@{winner['username']}" if winner['username'] else "Username yo'q"
            message += f"👤 {winner['first_name']} ({username})\n"
            message += f"🎁 {winner['prize_type']}\n"
            message += f"📅 {winner['selected_date']}\n\n"
        
        await query.edit_message_text(message, parse_mode='Markdown')
