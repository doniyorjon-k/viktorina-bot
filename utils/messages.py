"""
Message templates for the Quiz Bot
Contains all user-facing messages in Uzbek
"""

class Messages:
    def __init__(self):
        self.min_referrals = 5
    
    def welcome_message(self) -> str:
        """Welcome message for new users"""
        return """
🎉 **Maishiy texnika do'koni viktorinasiga xush kelibsiz!**

Bu bot orqali siz viktorinaga qatnashish huquqini qo'lga kirita olasiz va ajoyib sovrinlar yutib olishingiz mumkin!

🏆 **Sovrinlar:**
• 1-o'rin: Blender
• 5 kishi: 100,000 so'm vaucher

Quyidagi tugmalardan birini tanlang:
        """
    
    def my_results_message(self, referral_count: int, eligible: bool) -> str:
        """User's referral results message"""
        if eligible:
            return f"""
📊 **Sizning natijangiz:**

✅ Taklif qilingan do'stlar: {referral_count}
✅ Viktorina huquqi: Mavjud

🎉 Tabriklaymiz! Siz viktorinaga qatnasha olasiz!
            """
        else:
            needed = self.min_referrals - referral_count
            return f"""
📊 **Sizning natijangiz:**

👥 Taklif qilingan do'stlar: {referral_count}
❌ Viktorina huquqi: Yo'q

Viktorinaga qatnashish uchun yana {needed} ta do'st taklif qilishingiz kerak.
            """
    
    def invite_friends_message(self, referral_link: str) -> str:
        """Invite friends message with referral link"""
        return f"""
👥 **Do'stlarni taklif qiling!**

Viktorinaga qatnashish uchun kamida {self.min_referrals} ta do'stingizni taklif qiling.

🔗 **Sizning shaxsiy havolangiz:**
`{referral_link}`

Bu havolani do'stlaringiz bilan ulashing. Ular bu havola orqali botga kirishganda, sizga ball qo'shiladi.

⚠️ **Muhim:** Do'stlaringiz avval @testforviktorina guruhiga qo'shilishi kerak!

💡 **Qanday ishlaydi:**
1. Do'stlaringizga guruh havolasini yuboring: https://t.me/testforviktorina
2. Ular guruhga qo'shilgandan so'ng, sizning referal havolangizni yuboring
3. Ular havola orqali botga kirishganda sizga ball qo'shiladi
4. {self.min_referrals} ta do'st taklif qilganingizdan keyin viktorinaga qatnashishingiz mumkin
        """
    
    def rules_message(self, quiz_date: str = None) -> str:
        """Quiz rules message"""
        date_info = f"📅 **Viktorina sanasi:** {quiz_date}" if quiz_date else "📅 **Viktorina sanasi:** Admin tomonidan belgilanadi"
        
        return f"""
📋 **Viktorina qoidalari:**

**🎯 Qatnashish shartlari:**
• @testforviktorina guruhiga a'zo bo'lish shart
• Kamida {self.min_referrals} ta do'stni taklif qilish kerak
• Har bir do'st avval guruhga qo'shilishi, so'ng referral havola orqali botga kirishi shart
• Faqat haqiqiy foydalanuvchilar hisobga olinadi

**🏆 Sovrinlar:**
• 1-o'rin: Blender
• 5 kishi: 100,000 so'm vaucher

**📝 Viktorina jarayoni:**
• G'oliblar random tanlash orqali aniqlanadi
• Barcha talablarni bajargan qatnashuvchilar o'rtasidan
• Natijalar e'lon qilinganidan keyin o'zgartirilmaydi

{date_info}

**📞 Aloqa:**
Savollar uchun administratorlar bilan bog'laning.
        """
    
    def referral_success(self, referred_user_name: str) -> str:
        """Message when someone joins via referral"""
        return f"""
🎉 **Yangi referal!**

{referred_user_name} sizning havolangiz orqali botga qo'shildi!

Referallaringiz soni yangilandi. Natijalarni "Mening natijam" tugmasi orqali ko'ring.
        """
    
    def help_message(self) -> str:
        """Help message"""
        return """
ℹ️ **Yordam:**

Bu bot maishiy texnika do'koni viktorinasi uchun mo'ljallangan.

**Asosiy buyruqlar:**
• /start - Botni ishga tushirish
• /help - Yordam ma'lumotlari

**Qanday ishlaydi:**
1. Botni ishga tushiring
2. Do'stlaringizni taklif qiling
3. Viktorinaga qatnashish huquqini qo'lga kiriting
4. G'olib bo'lish uchun omad tilang!

Batafsil ma'lumot uchun "Qoidalar" tugmasini bosing.
        """
    
    def admin_participants_message(self, participants: list) -> str:
        """Admin message showing participants"""
        if not participants:
            return "📋 Hozircha hech kim viktorinaga qatnasha olmaydi."
        
        message = "👥 **Viktorina qatnashuvchilari:**\n\n"
        for i, participant in enumerate(participants, 1):
            username = f"@{participant['username']}" if participant['username'] else "Username yo'q"
            message += f"{i}. {participant['first_name']} ({username})\n"
            message += f"   Referallar: {participant['referral_count']}\n\n"
        
        message += f"**Jami qatnashuvchilar: {len(participants)}**"
        return message
