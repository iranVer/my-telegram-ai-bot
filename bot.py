import os
import tempfile
import asyncio
from threading import Thread

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from ai import ask_ai
from database import (
    init_db,
    save_user,
    save_message,
    get_history,
    clear_history,
)
from downloader import download_video, download_audio
from voice import voice_to_text, text_to_voice
from admin import is_admin, admin_stats


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

web = Flask(__name__)


@web.route("/")
def home():
    return "MyGPT is running!"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)


# =========================
# MAIN MENU
# =========================

def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "🧠 هوش مصنوعی",
                callback_data="ai"
            ),
            InlineKeyboardButton(
                "📥 دانلودر",
                callback_data="download"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎤 Voice AI",
                callback_data="voice"
            ),
            InlineKeyboardButton(
                "🔊 متن → صدا",
                callback_data="tts"
            ),
        ],
        [
            InlineKeyboardButton(
                "🖼️ Vision",
                callback_data="vision"
            ),
            InlineKeyboardButton(
                "📄 فایل",
                callback_data="file"
            ),
        ],
        [
            InlineKeyboardButton(
                "🧹 پاک کردن حافظه",
                callback_data="clear"
            ),
            InlineKeyboardButton(
                "⚙️ تنظیمات",
                callback_data="settings"
            ),
        ],
        [
            InlineKeyboardButton(
                "ℹ️ راهنما",
                callback_data="help"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def download_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "🎬 دانلود ویدیو",
                callback_data="video"
            )
        ],
        [
            InlineKeyboardButton(
                "🎵 دانلود صدا",
                callback_data="audio"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 برگشت",
                callback_data="home"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    save_user(
        user.id,
        user.username,
        user.first_name
    )

    context.user_data["mode"] = "ai"

    await update.message.reply_text(
        """
╭──────────────────╮
│     🤖 MyGPT     │
│  دستیار هوشمند   │
╰──────────────────╯

سلام 👋

من دستیار هوش مصنوعی تو هستم.

از منوی زیر انتخاب کن 👇
""",
        reply_markup=main_menu()
    )


# =========================
# BUTTONS
# =========================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data == "home":

        context.user_data["mode"] = "ai"

        await query.edit_message_text(
            "🏠 منوی اصلی",
            reply_markup=main_menu()
        )

    elif data == "ai":

        context.user_data["mode"] = "ai"

        await query.edit_message_text(
            "🧠 حالت هوش مصنوعی فعال شد.\n\n"
            "هر چیزی می‌خوای بپرس.",
            reply_markup=main_menu()
        )

    elif data == "download":

        context.user_data["mode"] = "download"

        await query.edit_message_text(
            "📥 دانلودر\n\n"
            "نوع دانلود را انتخاب کن:",
            reply_markup=download_menu()
        )

    elif data == "video":

        context.user_data["mode"] = "video"

        await query.edit_message_text(
            "🎬 لینک ویدیو را ارسال کن."
        )

    elif data == "audio":

        context.user_data["mode"] = "audio"

        await query.edit_message_text(
            "🎵 لینک را ارسال کن تا صدا استخراج شود."
        )

    elif data == "voice":

        context.user_data["mode"] = "voice"

        await query.edit_message_text(
            "🎤 یک پیام صوتی بفرست."
        )

    elif data == "tts":

        context.user_data["mode"] = "tts"

        await query.edit_message_text(
            "🔊 متنی که می‌خواهی به صدا تبدیل شود را بفرست."
        )

    elif data == "vision":

        await query.edit_message_text(
            "🖼️ قابلیت Vision در مرحله بعد فعال می‌شود.",
            reply_markup=main_menu()
        )

    elif data == "file":

        await query.edit_message_text(
            "📄 فایل را ارسال کن.\n"
            "پردازش فایل را در مرحله بعد کامل می‌کنیم.",
            reply_markup=main_menu()
        )

    elif data == "clear":

        clear_history(
            update.effective_user.id
        )

        await query.edit_message_text(
            "🧹 حافظه مکالمه پاک شد.",
            reply_markup=main_menu()
        )

    elif data == "settings":

        await query.edit_message_text(
            "⚙️ تنظیمات\n\n"
            "🌐 فارسی\n"
            "🇬🇧 English\n\n"
            "تنظیمات بیشتر در نسخه بعدی.",
            reply_markup=main_menu()
        )

    elif data == "help":

        await query.edit_message_text(
            """
ℹ️ راهنمای MyGPT

🧠 هوش مصنوعی
با من چت کن و حافظه مکالمه داشته باش.

📥 دانلودر
لینک محتوایی که اجازه دانلودش را داری ارسال کن.

🎤 Voice AI
ویس را به متن تبدیل می‌کند.

🔊 متن → صدا
متن را به فایل صوتی تبدیل می‌کند.

🧹 پاک کردن حافظه
تاریخچه گفتگو را پاک می‌کند.
""",
            reply_markup=main_menu()
        )


# =========================
# TEXT
# =========================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = update.message.text.strip()

    mode = context.user_data.get(
        "mode",
        "ai"
    )

    user_id = update.effective_user.id

    # DOWNLOAD VIDEO

    if mode == "video":

        if not text.startswith("http"):

            await update.message.reply_text(
                "🔗 لطفاً لینک معتبر بفرست."
            )

            return

        msg = await update.message.reply_text(
            "⏳ در حال دریافت ویدیو..."
        )

        try:

            filename = await asyncio.to_thread(
                download_video,
                text
            )

            with open(filename, "rb") as file:

                await update.message.reply_document(
                    document=file
                )

            await msg.delete()

            os.remove(filename)

        except Exception as e:

            print(e)

            await msg.edit_text(
                "❌ دانلود انجام نشد."
            )

        return

    # DOWNLOAD AUDIO

    if mode == "audio":

        if not text.startswith("http"):

            await update.message.reply_text(
                "🔗 لینک معتبر ارسال کن."
            )

            return

        msg = await update.message.reply_text(
            "⏳ در حال دریافت صدا..."
        )

        try:

            filename = await asyncio.to_thread(
                download_audio,
                text
            )

            with open(filename, "rb") as file:

                await update.message.reply_audio(
                    audio=file
                )

            await msg.delete()

            os.remove(filename)

        except Exception as e:

            print(e)

            await msg.edit_text(
                "❌ دریافت صدا انجام نشد."
            )

        return

    # TTS

    if mode == "tts":

        msg = await update.message.reply_text(
            "🔊 در حال ساخت صدا..."
        )

        try:

            filename = tempfile.mktemp(
                suffix=".mp3"
            )

            await asyncio.to_thread(
                text_to_voice,
                text,
                filename
            )

            with open(filename, "rb") as file:

                await update.message.reply_audio(
                    audio=file
                )

            await msg.delete()

            os.remove(filename)

        except Exception as e:

            print(e)

            await msg.edit_text(
                "❌ ساخت صدا انجام نشد."
            )

        return

    # AI

    await update.message.chat.send_action(
        "typing"
    )

    history = get_history(
        user_id
    )

    history.append({
        "role": "user",
        "content": text
    })

    try:

        answer = await asyncio.to_thread(
            ask_ai,
            history
        )

        save_message(
            user_id,
            "user",
            text
        )

        save_message(
            user_id,
            "assistant",
            answer
        )

        await update.message.reply_text(
            answer
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ خطایی در هوش مصنوعی رخ داد."
        )


# =========================
# VOICE
# =========================

async def voice_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    msg = await update.message.reply_text(
        "🎤 در حال تبدیل ویس..."
    )

    try:

        voice = update.message.voice

        telegram_file = await context.bot.get_file(
            voice.file_id
        )

        filename = tempfile.mktemp(
            suffix=".ogg"
        )

        await telegram_file.download_to_drive(
            filename
        )

        text = await asyncio.to_thread(
            voice_to_text,
            filename
        )

        await msg.edit_text(
            "📝 متن ویس:\n\n" + text
        )

        os.remove(filename)

    except Exception as e:

        print(e)

        await msg.edit_text(
            "❌ تبدیل ویس انجام نشد."
        )


# =========================
# ADMIN
# =========================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not is_admin(
        update.effective_user.id
    ):

        await update.message.reply_text(
            "⛔ دسترسی ندارید."
        )

        return

    await update.message.reply_text(
        "👑 پنل مدیریت\n\n"
        + admin_stats()
    )


# =========================
# MAIN
# =========================

def main():

    init_db()

    Thread(
        target=run_web,
        daemon=True
    ).start()

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "admin",
            admin
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            buttons
        )
    )

    application.add_handler(
        MessageHandler(
            filters.VOICE,
            voice_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("🤖 MyGPT started!")

    application.run_polling()


if __name__ == "__main__":
    main()
