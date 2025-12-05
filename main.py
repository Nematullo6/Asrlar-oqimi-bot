#!/usr/bin/env python3
"""Telegram Bot - Shafter bot"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os

# Bot tokeni (BotFather dan oling)
TOKEN = "8303721705:AAHerIMYyVxiB29eiJb8BDZ_tgg6omFTu4g"

# Owner chat ID (8079981050)
ADMIN_CHAT_ID = 8079981050

# Social media links
INSTAGRAM_LINK = "https://www.instagram.com/asrlarsadosi16?igsh=MXg4cGprZnFjNXR0NQ=="  # O'z Instagram linkingiz
YOUTUBE_LINK = "https://www.youtube.com/@asrlaroqimi001"    # O'z YouTube linkingiz

# Feedback jarayonidagi state
waiting_for_feedback = {}
user_feedback_storage = {}  # Foydalanuvchi xabarlarini saqlash

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Botni boshlash."""
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n"
        "Men asrlar oqimining botiman.\n\n"
        "Mavjud buyruqlar:\n"
        "/start - Bot haqida ma'lumot\n"
        "/shortcoming - kamchiliklarni yozish\n"
        "/social - Ijtimoiy tarmoqlar"
    )

# /shortcoming buyrug'i
async def shortcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Yordam ko'rsatish."""
    keyboard = [
        [InlineKeyboardButton("📝 Asrlar oqimi kamchiliklari", callback_data="feedback_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🆘 Yordam:\n\n"
        "Menga istalgan xabar yuboring, men javob beraman!\n"
        "Shuningdek, Asrlar oqimi kanali haqida fikringiz bo'lsa, "
        "quyidagi tugmani bosing:",
        reply_markup=reply_markup
    )

# /social buyrug'i - ijtimoiy tarmoqlar
async def social_networks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ijtimoiy tarmoqlar linklarini ko'rsatish."""
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)],
        [InlineKeyboardButton("🎥 YouTube", url=YOUTUBE_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📱 Bizning ijtimoiy tarmoqlarini kuzating:\n\n"
        "Instagram - Har kunlik yangilikllar\n"
        "YouTube - Video darslar va kontentlar",
        reply_markup=reply_markup
    )

# /ping buyrug'i
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ping testi."""
    await update.message.reply_text("🏓 Pong!")

# Callback query handler - feedback topshirish
async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Feedback berish uchun callback."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    waiting_for_feedback[user_id] = True
    
    await query.edit_message_text(
        text="📝 Asrlar oqimi kanalimizdagi kamchiliklarni yozing.\n"
             "Xabar yuborgach, admin qabul qiladi."
    )

# Feedback xabarlarini qabul qilish
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Feedback xabarlarini qabul qilib admin'ga yuborish."""
    user_id = update.message.from_user.id
    
    if user_id in waiting_for_feedback and waiting_for_feedback[user_id]:
        feedback_text = update.message.text
        user_name = update.message.from_user.username or update.message.from_user.first_name
        
        # Foydalanuvchi xabarini saqlash (admin javob berishlari uchun)
        user_feedback_storage[user_id] = {
            "name": user_name,
            "feedback": feedback_text
        }
        
        # Owner'ga xabar yuborish
        try:
            owner_message = (
                f"📬 Yangi feedback:\n\n"
                f"Foydalanuvchi: @{user_name}\n"
                f"User ID: {user_id}\n"
                f"Xabar: {feedback_text}\n\n"
                f"Javob berish uchun:\n"
                f"/reply {user_id} [Sizning xabar]"
            )
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=owner_message
            )
            
            # Foydalanuvchiga tasdiqlash
            await update.message.reply_text(
                "✅ Rahmat! Sizning fikringiz qabul qilindi. Admin tez orada javob beradi."
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Xatolik: {str(e)}"
            )
        
        waiting_for_feedback[user_id] = False
    else:
        # Oddiy xabarlarga javob
        await handle_message(update, context)

# Owner javob berish
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Owner foydalanuvchiga javob beradi."""
    if update.message.from_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Sizda bu buyruqni ishlatish huquqi yo'q.")
        return
    
    try:
        # /reply 123456 salom
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Ishlatish: /reply [User ID] [Xabar]")
            return
        
        user_id = int(args[0])
        reply_text = " ".join(args[1:])
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💬 Admin javob:\n\n{reply_text}"
        )
        
        await update.message.reply_text(
            f"✅ Javob @{user_feedback_storage.get(user_id, {}).get('name', 'User')} ga yuborildi."
        )
    except ValueError:
        await update.message.reply_text("❌ Noto'g'ri User ID.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

# Oddiy xabarlarga javob
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi xabarlarina javob."""
    user_message = update.message.text.lower()
    
    if "salom" in user_message or "assalomu" in user_message:
        await update.message.reply_text("Assalomu alaykum! 👋")
    elif "qaysi eri" in user_message:
        await update.message.reply_text("Sizga qanday yordam kerak? 🤔")
    else:
        await update.message.reply_text(f"Siz yuborgansiz: {update.message.text}\n\nUzur menda xali bu funksiya mavjud emas! ❌")

def main() -> None:
    """Bot ishni boshlash."""
    application = Application.builder().token(TOKEN).build()

    # Buyruq handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("shortcoming", shortcoming_command))
    application.add_handler(CommandHandler("social", social_networks))
    application.add_handler(CommandHandler("reply", reply_to_user))

    # Callback query handler
    application.add_handler(CallbackQueryHandler(feedback_callback, pattern="feedback_channel"))
    
    # Feedback xabarlarini qabul qilish
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("✅ Bot ishlanayapti...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
