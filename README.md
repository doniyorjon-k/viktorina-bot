# Maishiy Texnika Do'koni Viktorina Bot

Bu bot maishiy texnika do'koni uchun referal asosidagi viktorina o'tkazish uchun ishlab chiqilgan.

## Asosiy Funksiyalar

### Foydalanuvchilar Uchun

1. **Botni Ishga Tushirish**
   - `/start` - Botni ishga tushirish va asosiy menyu
   - Har bir foydalanuvchi uchun noyob referal kodi yaratiladi

2. **Asosiy Menyu Tugmalari**
   - 📊 **Mening natijam** - Referal hisobini ko'rish va qatnashish huquqini tekshirish
   - 👥 **Do'stlarni taklif qilish** - Shaxsiy referal havolani olish va ulashish
   - 📋 **Qoidalar** - Viktorina qoidalari va sovrinlar haqida ma'lumot

3. **Referal Tizimi**
   - Har bir foydalanuvchi noyob referal havolaga ega
   - Minimum 5 ta do'stni taklif qilish kerak
   - Referal orqali kelgan do'stlar avtomatik hisoblanadi

### Adminlar Uchun

Adminlar quyidagi buyruqlardan foydalanishi mumkin:

1. **`/admin`** - Admin panelini ochish
2. **`/participants`** - Barcha qatnashuvchilarni ko'rish
3. **`/setwinner`** - Random g'oliblarni tanlash
4. **`/setdate DD.MM.YYYY`** - Viktorina sanasini belgilash
5. **`/addadmin USER_ID`** - Yangi admin qo'shish

## Sovrinlar

- 🥇 **1-o'rin**: Blender
- 🎁 **5 kishi**: 100,000 so'm vaucher

## Texnik Ma'lumotlar

- **Dasturlash tili**: Python 3
- **Kutubxona**: python-telegram-bot
- **Ma'lumotlar bazasi**: SQLite
- **Interfeys tili**: O'zbek tili

## Sozlash

1. BotFather orqali yangi bot yarating
2. Bot tokenini `TELEGRAM_BOT_TOKEN` environment variable sifatida qo'ying
3. Botni ishga tushiring: `python main.py`
4. Birinchi adminni qo'shish uchun `ADMIN_IDS` environment variable ishlatiladi

## Foydalanish Misoli

1. Foydalanuvchi `/start` buyrug'ini beradi
2. Bot 3 ta tugma ko'rsatadi
3. Foydalanuvchi "Do'stlarni taklif qilish" tugmasini bosadi
4. Bot shaxsiy referal havolani beradi
5. Foydalanuvchi do'stlariga havolani yuboradi
6. Do'stlari havola orqali botga kiradi
7. 5 ta do'st taklif qilgandan keyin qatnashish huquqi hosil bo'ladi
8. Admin viktorina kunida random g'oliblarni tanlaydi

## Xavfsizlik

- Referal kodlar noyob va hashlangan
- Admin huquqlari tekshiriladi
- Ma'lumotlar bazasi thread-safe
- Barcha amallar loglangan

Bot to'liq ishga tayyor va barcha funksiyalar sinovdan o'tgan!
=======
# viktorina-bot