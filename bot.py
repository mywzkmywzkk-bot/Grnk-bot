import os
import re
import telebot
import yt_dlp

from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

BOT_TOKEN = "8612351805:AAGuyw0m-9gQM0E0y6IoLjHTCJOYC4MWv7I"
BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"

START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = telebot.TeleBot(BOT_TOKEN)

os.makedirs("downloads", exist_ok=True)


def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:80]


def is_subscribed(user_id):

    try:

        member = bot.get_chat_member(
            "@" + FORCE_CHANNEL,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return True


def music_keyboard():

    markup = InlineKeyboardMarkup(row_width=2)

    btn1 = InlineKeyboardButton(
        "اضفني للكروب",
        url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
    )

    btn2 = InlineKeyboardButton(
        "المطور",
        url=f"https://t.me/{DEV_USERNAME}"
    )

    btn3 = InlineKeyboardButton(
        "شراء بوت مشابه",
        url=f"https://t.me/{DEV_USERNAME}"
    )

    btn4 = InlineKeyboardButton(
        "قناة البوت",
        url=f"https://t.me/{FORCE_CHANNEL}"
    )

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)

    return markup


def sub_keyboard():

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "اشترك بالقناة",
            url=f"https://t.me/{FORCE_CHANNEL}"
        )
    )

    return markup


def start_text():

    return (
        "• هلا بك في بوت ميوزك 🎧\n\n"
        "• اضفني للكروب وارفعني مشرف\n\n"
        "• اكتب:\n"
        "يوت اسم الاغنية\n"
        "تشغيل اسم الاغنية\n\n"
        "• مثال:\n"
        "يوت فيروز\n\n"
        f"• المطور: @{DEV_USERNAME}"
    )


def try_download(search_query, opts):

    with yt_dlp.YoutubeDL(opts) as ydl:

        info = ydl.extract_info(
            search_query,
            download=True
        )

        if info and "entries" in info:
            info = info["entries"][0]

        if not info:
            raise Exception("ما حصلت نتيجة")

        title = clean_filename(
            info.get("title", "song")
        )

        file_path = ydl.prepare_filename(info)

        return file_path, title


def download_audio(query):

    base_opts = {

        "format": "bestaudio",

        "outtmpl":
        "downloads/%(title)s.%(ext)s",

        "cookiefile": "cookies.txt",

        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,

        "socket_timeout": 15,
        "retries": 3,
        "fragment_retries": 3,
    }

    sources = [

        {
            "search": f"ytsearch5:{query}",

            "extra": {
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android"]
                    }
                }
            }
        },

        {
            "search": f"ytsearch5:{query}",

            "extra": {
                "extractor_args": {
                    "youtube": {
                        "player_client": ["web"]
                    }
                }
            }
        },

        {
            "search": f"scsearch1:{query}",
            "extra": {}
        }

    ]

    last_error = None

    for source in sources:

        try:

            opts = base_opts.copy()

            opts.update(
                source["extra"]
            )

            if "scsearch1:" in source["search"]:
                opts.pop(
                    "cookiefile",
                    None
                )

            return try_download(
                source["search"],
                opts
            )

        except Exception as e:

            last_error = e
            continue

    raise Exception(last_error)


@bot.message_handler(commands=["start"])
def start(message):

    if not is_subscribed(
        message.from_user.id
    ):

        return bot.reply_to(
            message,
            "⚠️ اشترك بالقناة أولاً",
            reply_markup=sub_keyboard()
        )

    bot.send_photo(
        message.chat.id,
        START_PHOTO,
        caption=start_text(),
        reply_markup=music_keyboard()
    )


@bot.message_handler(
    func=lambda m:
    m.text and (
        m.text.startswith("يوت ")
        or
        m.text.startswith("تشغيل ")
    )
)
def music(message):

    if not is_subscribed(
        message.from_user.id
    ):

        return bot.reply_to(
            message,
            "⚠️ اشترك بالقناة أولاً",
            reply_markup=sub_keyboard()
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
            "اكتب اسم الأغنية"
        )

    msg = bot.reply_to(
        message,
        "🔎 جاري البحث..."
    )

    try:

        file_path, title = download_audio(
            query
        )

        bot.edit_message_text(
            "📤 جاري الإرسال...",
            message.chat.id,
            msg.message_id
        )

        with open(
            file_path,
            "rb"
        ) as audio:

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

bot.infinity_polling(
    skip_pending=True
        )
