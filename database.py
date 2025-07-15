"""
Database management for Telegram Quiz Bot
Handles SQLite database operations for users, referrals, quiz settings, and admins
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Tuple
import threading

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "quiz_bot.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    referral_count INTEGER DEFAULT 0,
                    eligible BOOLEAN DEFAULT 0,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    referral_code TEXT UNIQUE
                )
            ''')
            
            # Referrals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_id) REFERENCES users (user_id),
                    UNIQUE(referrer_id, referred_id)
                )
            ''')
            
            # Quiz settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_settings (
                    id INTEGER PRIMARY KEY,
                    quiz_date TEXT,
                    status TEXT DEFAULT 'pending',
                    winners_selected BOOLEAN DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Admins table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY,
                    username TEXT,
                    permissions TEXT DEFAULT 'full',
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Winners table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS winners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    prize_type TEXT,
                    selected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Pending referrals table for tracking group joins via referral links
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referral_code TEXT,
                    referrer_id INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
    
    def add_user(self, user_id: int, username: str, first_name: str, referral_code: str) -> bool:
        """Add a new user to the database"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, referral_code)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, referral_code))
                
                conn.commit()
                conn.close()
                logger.info(f"User {user_id} added successfully")
                return True
            except Exception as e:
                logger.error(f"Error adding user {user_id}: {e}")
                return False
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user information by user_id"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, username, first_name, referral_count, eligible, referral_code
                    FROM users WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {
                        'user_id': result[0],
                        'username': result[1],
                        'first_name': result[2],
                        'referral_count': result[3],
                        'eligible': result[4],
                        'referral_code': result[5]
                    }
                return None
            except Exception as e:
                logger.error(f"Error getting user {user_id}: {e}")
                return None
    
    def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Add a referral relationship"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if referral already exists
                cursor.execute('''
                    SELECT COUNT(*) FROM referrals 
                    WHERE referrer_id = ? AND referred_id = ?
                ''', (referrer_id, referred_id))
                
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    return False
                
                # Add referral
                cursor.execute('''
                    INSERT INTO referrals (referrer_id, referred_id)
                    VALUES (?, ?)
                ''', (referrer_id, referred_id))
                
                # Update referrer's count
                cursor.execute('''
                    UPDATE users SET referral_count = referral_count + 1
                    WHERE user_id = ?
                ''', (referrer_id,))
                
                # Check if user is now eligible (1+ referrals)
                cursor.execute('''
                    UPDATE users SET eligible = 1
                    WHERE user_id = ? AND referral_count >= 1
                ''', (referrer_id,))
                
                conn.commit()
                conn.close()
                logger.info(f"Referral added: {referrer_id} -> {referred_id}")
                return True
            except Exception as e:
                logger.error(f"Error adding referral: {e}")
                return False
    
    def get_user_by_referral_code(self, referral_code: str) -> Optional[dict]:
        """Get user by referral code"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, username, first_name, referral_count, eligible
                    FROM users WHERE referral_code = ?
                ''', (referral_code,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {
                        'user_id': result[0],
                        'username': result[1],
                        'first_name': result[2],
                        'referral_count': result[3],
                        'eligible': result[4]
                    }
                return None
            except Exception as e:
                logger.error(f"Error getting user by referral code: {e}")
                return None
    
    def get_all_participants(self) -> List[dict]:
        """Get all eligible participants"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_id, username, first_name, referral_count
                    FROM users WHERE eligible = 1
                    ORDER BY referral_count DESC
                ''')
                
                results = cursor.fetchall()
                conn.close()
                
                participants = []
                for row in results:
                    participants.append({
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'referral_count': row[3]
                    })
                
                return participants
            except Exception as e:
                logger.error(f"Error getting participants: {e}")
                return []
    
    def add_admin(self, admin_id: int, username: str) -> bool:
        """Add admin to database"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO admins (admin_id, username)
                    VALUES (?, ?)
                ''', (admin_id, username))
                
                conn.commit()
                conn.close()
                logger.info(f"Admin {admin_id} added successfully")
                return True
            except Exception as e:
                logger.error(f"Error adding admin: {e}")
                return False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM admins WHERE admin_id = ?', (user_id,))
                result = cursor.fetchone()[0] > 0
                conn.close()
                
                return result
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")
                return False
    
    def set_quiz_date(self, quiz_date: str) -> bool:
        """Set quiz date"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO quiz_settings (id, quiz_date)
                    VALUES (1, ?)
                ''', (quiz_date,))
                
                conn.commit()
                conn.close()
                logger.info(f"Quiz date set to: {quiz_date}")
                return True
            except Exception as e:
                logger.error(f"Error setting quiz date: {e}")
                return False
    
    def get_quiz_date(self) -> Optional[str]:
        """Get current quiz date"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT quiz_date FROM quiz_settings WHERE id = 1')
                result = cursor.fetchone()
                conn.close()
                
                return result[0] if result else None
            except Exception as e:
                logger.error(f"Error getting quiz date: {e}")
                return None
    
    def add_winner(self, user_id: int, prize_type: str) -> bool:
        """Add winner to database"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO winners (user_id, prize_type)
                    VALUES (?, ?)
                ''', (user_id, prize_type))
                
                conn.commit()
                conn.close()
                logger.info(f"Winner added: {user_id} - {prize_type}")
                return True
            except Exception as e:
                logger.error(f"Error adding winner: {e}")
                return False
    
    def get_winners(self) -> List[dict]:
        """Get all winners"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT w.user_id, u.username, u.first_name, w.prize_type, w.selected_date
                    FROM winners w
                    JOIN users u ON w.user_id = u.user_id
                    ORDER BY w.selected_date DESC
                ''')
                
                results = cursor.fetchall()
                conn.close()
                
                winners = []
                for row in results:
                    winners.append({
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'prize_type': row[3],
                        'selected_date': row[4]
                    })
                
                return winners
            except Exception as e:
                logger.error(f"Error getting winners: {e}")
                return []
    
    def add_pending_referral(self, referral_code: str, referrer_id: int) -> bool:
        """Add pending referral for group joins"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if pending referral already exists
                cursor.execute('''
                    SELECT COUNT(*) FROM pending_referrals 
                    WHERE referral_code = ? AND referrer_id = ?
                ''', (referral_code, referrer_id))
                
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    logger.info(f"Pending referral already exists: {referral_code}")
                    return True
                
                cursor.execute('''
                    INSERT INTO pending_referrals (referral_code, referrer_id)
                    VALUES (?, ?)
                ''', (referral_code, referrer_id))
                
                conn.commit()
                conn.close()
                logger.info(f"Pending referral added: {referral_code} -> {referrer_id}")
                return True
            except Exception as e:
                logger.error(f"Error adding pending referral: {e}")
                return False
    
    def get_pending_referral(self, referral_code: str) -> Optional[dict]:
        """Get pending referral by code"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT referrer_id FROM pending_referrals 
                    WHERE referral_code = ?
                ''', (referral_code,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {'referrer_id': result[0]}
                return None
            except Exception as e:
                logger.error(f"Error getting pending referral: {e}")
                return None
    
    def remove_pending_referral(self, referral_code: str) -> bool:
        """Remove processed pending referral"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM pending_referrals WHERE referral_code = ?
                ''', (referral_code,))
                
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"Error removing pending referral: {e}")
                return False
