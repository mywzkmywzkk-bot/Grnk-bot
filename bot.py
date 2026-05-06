import os
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

BOT_TOKEN = "8612351805:AAFNKU1istmFRWV7vcrSCU0o-aOwGEIXSv0"
BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"

START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = telebot.TeleBot(BOT_TOKEN)

os.makedirs("downloads", exist_ok=True)


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def is_subscribed(user_id):
    try:
        member = bot.get_chat_member("@" + FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return True


def start_buttons():
    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(
        InlineKeyboardButton(
            "➕ اضفني للكروب",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "👨‍💻 المطور",
            url=f"https://t.me/{DEV_USERNAME}"
        ),
        InlineKeyboardButton(
            "🛒 شراء بوت مشابه",
            url=f"https://t.me/{DEV_USERNAME}"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "📢 قناة البوت",
            url=f"https://t.me/{FORCE_CHANNEL}"
        )
    )

    return kb


def sub_buttons():
    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(
        InlineKeyboardButton(
            "📢 اشترك بالقناة",
            url=f"https://t.me/{FORCE_CHANNEL}"
        )
    )

    return kb


def start_text():
    return (
        "• هلا بك في بوت ميوزك 🎧\n\n"
        "• اضفني للكروب وارفعني مشرف\n\n"
        "• اكتب:\n"
        "يوت اسم الاغنية\n"
        "تشغيل اسم الاغنية\n\n"
        "• مثال:\n"
        "يوت فيروز\n\n"
        "• المطور: @fvamv"
    )


def download_audio(query):

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiefile": "cookies.txt",

        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },

        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 60,
        "retries": 20,
        "fragment_retries": 20,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            f"ytsearch1:{query}",
            download=True
        )

        if "entries" in info:
            info = info["entries"][0]

        title = clean_filename(info.get("title", "song"))

        file_path = ydl.prepare_filename(info)

        return file_path, title


@bot.message_handler(commands=["start"])
def start(message):

    if not is_subscribed(message.from_user.id):
        return bot.reply_to(
            message,
            "⚠️ اشترك بالقناة أولاً حتى تستخدم البوت",
            reply_markup=sub_buttons()
        )

    bot.send_photo(
        message.chat.id,
        START_PHOTO,
        caption=start_text(),
        reply_markup=start_buttons()
    )


@bot.message_handler(
    func=lambda m: m.text and (
        m.text.startswith("يوت ")
        or
        m.text.startswith("تشغيل ")
    )
)
def music(message):

    if not is_subscribed(message.from_user.id):
        return bot.reply_to(
            message,
            "⚠️ اشترك بالقناة أولاً حتى تستخدم البوت",
            reply_markup=sub_buttons()
        )

    query = (
        message.text
        .replace("يوت ", "", 1)
        .replace("تشغيل ", "", 1)
        .strip()
    )

    if not query:
        return bot.reply_to(
            message,
            "اكتب اسم الأغنية."
        )

    msg = bot.reply_to(
        message,
        "🔎 جاري البحث والتحميل..."
    )

    try:

        file_path, title = download_audio(query)

        bot.edit_message_text(
            "📤 جاري إرسال الأغنية...",
            message.chat.id,
            msg.message_id
        )

        with open(file_path, "rb") as audio:

            bot.send_audio(
                message.chat.id,
                audio,
                title=title,
                performer="Song fadi",
                caption=f"🎧 {title}",
                reply_to_message_id=message.message_id
            )

        bot.delete_message(
            message.chat.id,
            msg.message_id
        )

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        bot.edit_message_text(
            f"❌ صار خطأ:\n{e}",
            message.chat.id,
            msg.message_id
        )


print("Bot Running...")
bot.infinity_polling(skip_pending=True)
