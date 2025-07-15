# Quiz Bot - Telegram Referral System

## Overview

A Telegram bot designed for a household appliance store to run referral-based quiz contests. Users must invite friends to become eligible for quiz participation, with winners receiving prizes like blenders and store vouchers.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

✓ Bot successfully implemented with all core features (July 15, 2025)
✓ Database initialized with proper tables for users, referrals, admins, winners
✓ Telegram bot token configured and bot is running
✓ All handlers implemented for user interactions and admin functions
✓ Uzbek language interface fully implemented
✓ Referral system with unique codes working properly
✓ Admin privileges granted to user ID 1385620971 (July 15, 2025)
✓ Group membership checking implemented for @testforviktorina
✓ Bot now requires users to join the group before referral links work
✓ Updated messages to include group requirement information
✓ Changed referral system to provide group invite links instead of bot links
✓ Minimum referrals reduced to 1 for testing purposes
✓ Added manual referral command `/addref` for admin to track group joins
✓ Created pending_referrals table for better tracking
✓ Implemented automatic referral tracking when users join group
✓ Fixed referral count calculations and eligibility updates
✓ System now has 2 eligible participants ready for quiz

## Current Status

The bot is fully functional and ready for use. All major components are working:
- User registration and referral tracking
- Admin panel with participant management (admin: 1385620971)
- Winner selection functionality
- Uzbek language messages throughout
- SQLite database properly initialized
- Group membership verification for @testforviktorina
- Referral system that requires group membership
- Automatic referral processing when users join group via referral links
- 2 eligible participants ready for quiz (minimum 1 referral required)

## System Architecture

### Backend Architecture
- **Language**: Python 3
- **Framework**: python-telegram-bot library
- **Database**: SQLite with thread-safe operations
- **Design Pattern**: Handler-based architecture with separation of concerns

### Key Components

1. **Main Application (`main.py`)**
   - Entry point and bot initialization
   - Handler registration and routing
   - Error handling setup

2. **Database Layer (`database.py`)**
   - SQLite database management
   - Thread-safe operations with locks
   - User, referral, and admin data storage

3. **Handler System**
   - `UserHandlers`: Processes user commands and interactions
   - `AdminHandlers`: Manages admin functionality and controls

4. **Utility Modules**
   - `ReferralUtils`: Handles referral link generation and validation
   - `Messages`: Centralized message templates in Uzbek language

5. **Configuration (`config.py`)**
   - Environment-based configuration
   - Telegram bot settings and admin management

## Data Flow

1. **User Registration**
   - User starts bot via `/start` command
   - System generates unique referral code
   - User data stored in SQLite database

2. **Referral Processing**
   - Referral codes embedded in Telegram deep links
   - New users processed through referral validation
   - Referral counts updated for referring users

3. **Eligibility Check**
   - Users must reach minimum referral threshold (5 friends)
   - Eligibility status tracked in database
   - Admin can view eligible participants

4. **Admin Operations**
   - Admin panel for contest management
   - Winner selection and announcement
   - Participant monitoring and statistics

## External Dependencies

### Required Packages
- `python-telegram-bot`: Telegram Bot API wrapper
- `sqlite3`: Database operations (built-in)
- `threading`: Thread safety (built-in)
- `hashlib`: Referral code generation (built-in)
- `base64`: URL-safe encoding (built-in)

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Bot authentication token
- `BOT_USERNAME`: Bot username for referral links
- `GROUP_ID`: Target group for user participation
- `MIN_REFERRALS`: Minimum referrals required (default: 5)
- `ADMIN_IDS`: Comma-separated list of admin user IDs

## Deployment Strategy

### Database Setup
- SQLite database with automatic table creation
- Thread-safe operations for concurrent access
- Local file storage (`quiz_bot.db`)

### Bot Configuration
- Environment-based configuration management
- Webhook or long-polling deployment options
- Admin privilege system for contest management

### Security Considerations
- Referral code validation to prevent manipulation
- Admin authentication for sensitive operations
- Thread-safe database operations

## Key Features

1. **Referral System**
   - Unique referral codes for each user
   - Automatic referral tracking and validation
   - Minimum referral requirement enforcement

2. **Multi-language Support**
   - Uzbek language interface
   - Centralized message management

3. **Admin Panel**
   - Participant management
   - Winner selection functionality
   - Contest date and settings management

4. **Database Management**
   - User registration and tracking
   - Referral relationship storage
   - Admin privilege management

The system is designed to be easily deployable on platforms like Replit, with minimal external dependencies and straightforward configuration through environment variables.