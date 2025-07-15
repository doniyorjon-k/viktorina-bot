# Admin Guide - Maishiy Texnika Viktorina Bot

## Admin Akkaunti

✅ **Sizning admin ID:** 1385620971  
✅ **Username:** @testforviktorina  
✅ **Admin huquqlari:** To'liq  

## Admin Buyruqlari

### 1. `/admin` - Admin Panel
Admin panelini ochadi va quyidagi tugmalarni ko'rsatadi:
- 👥 Qatnashuvchilar - Barcha eligble foydalanuvchilarni ko'rish
- 🎯 G'olib tanlash - Random 6 ta g'olibni tanlash
- 📅 Sana belgilash - Viktorina sanasini o'rnatish
- 🏆 G'oliblar - Avvalgi g'oliblarni ko'rish

### 2. `/participants` - Qatnashuvchilar Ro'yxati
- Minimum 5 ta referal qilgan barcha foydalanuvchilarni ko'rsatadi
- Har birining referal sonini ko'rsatadi

### 3. `/setwinner` - G'oliblarni Tanlash
- **Minimum 6 ta qatnashuvchi bo'lishi kerak**
- 1 ta birinchi o'rin (Blender)
- 5 ta vaucher g'olibi (100,000 so'm)
- Random tanlash
- G'oliblarga avtomatik xabar yuboriladi

### 4. `/setdate DD.MM.YYYY` - Sana Belgilash
Misol: `/setdate 25.12.2024`

### 5. `/addadmin USER_ID` - Yangi Admin Qo'shish
Misol: `/addadmin 123456789`

## Viktorina Jarayoni

### 1. Tayyorgarlik
- Viktorina sanasini belgilang: `/setdate 31.12.2024`
- Qatnashuvchilarni tekshiring: `/participants`

### 2. G'oliblarni Tanlash
- Kamida 6 ta qatnashuvchi bo'lganini tekshiring
- `/setwinner` buyrug'ini bering
- G'oliblarga avtomatik xabar yuboriladi

### 3. Natijalarni E'lon Qilish
- G'oliblar ro'yxatini olasiz
- Bu ro'yxatni guruhda e'lon qilishingiz mumkin

## Guruh Talablari

**Muhim:** Foydalanuvchilar avval @testforviktorina guruhiga qo'shilishi kerak, so'ngina referal havolalar ishlaydi.

### Jarayon:
1. Foydalanuvchi @testforviktorina guruhiga qo'shiladi
2. Referal havola orqali botga kiradi
3. Bot guruh a'zoligini tekshiradi
4. Agar a'zo bo'lsa, referal hisoblanadi
5. Agar a'zo bo'lmasa, guruhga qo'shilish talab qilinadi

## Statistika Ko'rish

### Ma'lumotlar Bazasini Ko'rish:
```
sqlite3 quiz_bot.db "SELECT COUNT(*) FROM users;" # Jami foydalanuvchilar
sqlite3 quiz_bot.db "SELECT COUNT(*) FROM users WHERE eligible = 1;" # Qatnashuvchilar
sqlite3 quiz_bot.db "SELECT COUNT(*) FROM referrals;" # Jami referallar
sqlite3 quiz_bot.db "SELECT * FROM winners;" # G'oliblar
```

## Muammolarni Hal Qilish

### Agar Bot Ishlamasa:
1. Bot tokenini tekshiring
2. Bot ishlab turganini tekshiring
3. Loglarni ko'ring

### Agar Referal Ishlamasa:
1. Foydalanuvchi guruh a'zosimi?
2. Referal kodi to'g'rimi?
3. Bir xil foydalanuvchi o'zini referal qila olmaydi

### G'olib Tanlashda Muammo:
1. Kamida 6 ta qatnashuvchi bo'lishi kerak
2. Har biri 5+ referal qilgan bo'lishi kerak

## Xavfsizlik

- Faqat ishonchli odamlarga admin huquqi bering
- Bot tokenini hech kimga bermang
- Ma'lumotlar bazasini muntazam zaxiralang

Bot to'liq ishga tayyor va test qilingan!