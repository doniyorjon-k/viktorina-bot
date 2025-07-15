#!/usr/bin/env python3
"""
Telegram Referral Quiz Bot for Household Appliance Store
Main application entry point
"""

import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import Database
from handlers.user_handlers import UserHandlers
from handlers.admin_handlers import AdminHandlers
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class QuizBot:
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.user_handlers = UserHandlers(self.db)
        self.admin_handlers = AdminHandlers(self.db)
        
    def setup_handlers(self, application):
        """Setup all bot handlers"""
        # User command handlers
        application.add_handler(CommandHandler("start", self.user_handlers.start))
        application.add_handler(CommandHandler("help", self.user_handlers.help))
        
        # Admin command handlers
        application.add_handler(CommandHandler("admin", self.admin_handlers.admin_menu))
        application.add_handler(CommandHandler("participants", self.admin_handlers.show_participants))
        application.add_handler(CommandHandler("setwinner", self.admin_handlers.select_winner))
        application.add_handler(CommandHandler("setdate", self.admin_handlers.set_quiz_date))
        application.add_handler(CommandHandler("addadmin", self.admin_handlers.add_admin))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(self.user_handlers.handle_callback))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_handlers.handle_message))
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.user_handlers.handle_new_member))
        
        # Error handler
        application.add_error_handler(self.error_handler)
    
    async def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
    def run(self):
        """Start the bot"""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
            return
            
        application = Application.builder().token(token).build()
        self.setup_handlers(application)
        
        logger.info("Starting Quiz Bot...")
        application.run_polling(allowed_updates=["message", "callback_query", "chat_member"])

if __name__ == "__main__":
    bot = QuizBot()
    bot.run()
