"""
Admin handlers for the Quiz Bot
Handles admin commands and functionality
"""

import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.messages import Messages

logger = logging.getLogger(__name__)

class AdminHandlers:
    def __init__(self, database):
        self.db = database
        self.messages = Messages()
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return self.db.is_admin(user_id)
    
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin menu"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        keyboard = [
            [InlineKeyboardButton("👥 Qatnashuvchilar", callback_data="admin_participants")],
            [InlineKeyboardButton("🎯 G'olib tanlash", callback_data="admin_select_winner")],
            [InlineKeyboardButton("📅 Sana belgilash", callback_data="admin_set_date")],
            [InlineKeyboardButton("🏆 G'oliblar", callback_data="admin_winners")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 **Admin Panel**\n\nQuyidagi amallardan birini tanlang:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def show_participants(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all eligible participants"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        participants = self.db.get_all_participants()
        
        if not participants:
            await update.message.reply_text("📋 Hozircha hech kim viktorinaga qatnasha olmaydi.")
            return
        
        message = "👥 **Viktorina qatnashuvchilari:**\n\n"
        for i, participant in enumerate(participants, 1):
            username = f"@{participant['username']}" if participant['username'] else "Username yo'q"
            message += f"{i}. {participant['first_name']} ({username})\n"
            message += f"   Referallar: {participant['referral_count']}\n\n"
        
        message += f"**Jami qatnashuvchilar: {len(participants)}**"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def select_winner(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Select random winners"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        participants = self.db.get_all_participants()
        
        if not participants:
            await update.message.reply_text("❌ Qatnashuvchilar yo'q.")
            return
        
        if len(participants) < 6:
            await update.message.reply_text("❌ Minimum 6 qatnashuvchi bo'lishi kerak.")
            return
        
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
        message += f"\nReferallar: {first_place['referral_count']}\n\n"
        
        message += "🎁 **Vaucher g'oliblari (100,000 so'm):**\n"
        for i, winner in enumerate(voucher_winners, 1):
            message += f"{i}. {winner['first_name']}"
            if winner['username']:
                message += f" (@{winner['username']})"
            message += f" - {winner['referral_count']} referal\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Notify winners
        await self._notify_winners(context, first_place, voucher_winners)
    
    async def _notify_winners(self, context: ContextTypes.DEFAULT_TYPE, first_place: dict, voucher_winners: list):
        """Notify winners about their prizes"""
        # Notify first place winner
        try:
            await context.bot.send_message(
                chat_id=first_place['user_id'],
                text="🎉 **Tabriklaymiz!** 🎉\n\nSiz viktorinada 1-o'rinni egalladingiz va **Blender** yutib oldingiz!\n\nMukofotingizni olish uchun administratorlar bilan bog'laning.",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify first place winner: {e}")
        
        # Notify voucher winners
        for winner in voucher_winners:
            try:
                await context.bot.send_message(
                    chat_id=winner['user_id'],
                    text="🎉 **Tabriklaymiz!** 🎉\n\nSiz viktorinada g'olib bo'ldingiz va **100,000 so'm vaucher** yutib oldingiz!\n\nMukofotingizni olish uchun administratorlar bilan bog'laning.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify voucher winner: {e}")
    
    async def set_quiz_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set quiz date"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📅 Viktorina sanasini belgilash uchun:\n"
                "`/setdate DD.MM.YYYY`\n\n"
                "Masalan: `/setdate 25.12.2024`",
                parse_mode='Markdown'
            )
            return
        
        quiz_date = " ".join(context.args)
        
        if self.db.set_quiz_date(quiz_date):
            await update.message.reply_text(f"✅ Viktorina sanasi belgilandi: **{quiz_date}**", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Sana belgilashda xatolik yuz berdi.")
    
    async def add_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new admin"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "👤 Admin qo'shish uchun:\n"
                "`/addadmin USER_ID`\n\n"
                "Masalan: `/addadmin 123456789`",
                parse_mode='Markdown'
            )
            return
        
        try:
            new_admin_id = int(context.args[0])
            username = context.args[1] if len(context.args) > 1 else ""
            
            if self.db.add_admin(new_admin_id, username):
                await update.message.reply_text(f"✅ Admin qo'shildi: {new_admin_id}")
            else:
                await update.message.reply_text("❌ Admin qo'shishda xatolik yuz berdi.")
                
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri USER_ID formati.")
    
    async def show_winners(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all winners"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text("❌ Sizda admin huquqlari yo'q.")
            return
        
        winners = self.db.get_winners()
        
        if not winners:
            await update.message.reply_text("🏆 Hozircha g'oliblar yo'q.")
            return
        
        message = "🏆 **G'oliblar ro'yxati:**\n\n"
        for winner in winners:
            username = f"@{winner['username']}" if winner['username'] else "Username yo'q"
            message += f"👤 {winner['first_name']} ({username})\n"
            message += f"🎁 {winner['prize_type']}\n"
            message += f"📅 {winner['selected_date']}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
