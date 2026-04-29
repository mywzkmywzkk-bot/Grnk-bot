import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

BOT_TOKEN = "8612351805:AAG0ihwHKncgaj_bYADmThUBbzCXsyQ_CxU"
BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"

START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = telebot.TeleBot(BOT_TOKEN)
os.makedirs("downloads", exist_ok=True)


def is_subscribed(user_id):
    try:
        m = bot.get_chat_member("@" + FORCE_CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False


def sub_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{FORCE_CHANNEL}"))
    kb.add(InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return kb


def main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ اضفني", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"))
    kb.add(
        InlineKeyboardButton("📚 طريقة الاستخدام", callback_data="help"),
        InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USERNAME}")
    )
    kb.add(InlineKeyboardButton("🛒 شراء بوت مشابه", url=f"https://t.me/{DEV_USERNAME}"))
    return kb


def start_text():
    return (
        "• هلا بك في بوت ميوزك 🎧\n\n"
        "• اضفني إلى مجموعتك وارفعني مشرف\n"
        "• اكتب اسم الأغنية والبوت يدزها ملف صوتي\n\n"
        "• الأوامر:\n"
        "يوت فيروز\n"
        "تشغيل فيروز"
    )


def download_audio(query):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "cookiefile": "cookies.txt" if os.path.exists("cookies.txt") else None,
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        return f"downloads/{info['id']}.mp3", info.get("title", "Audio")


@bot.message_handler(commands=["start"])
def start(message):
    if not is_subscribed(message.from_user.id):
        return bot.reply_to(message, "⚠️ اشترك بالقناة أولاً حتى تستخدم البوت", reply_markup=sub_keyboard())

    bot.send_photo(
        message.chat.id,
        START_PHOTO,
        caption=start_text(),
        reply_markup=main_keyboard()
    )


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == "check_sub":
        if is_subscribed(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, START_PHOTO, caption=start_text(), reply_markup=main_keyboard())
        else:
            bot.answer_callback_query(call.id, "❌ بعدك ما مشترك", show_alert=True)

    elif call.data == "help":
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=(
                "📚 طريقة الاستخدام:\n\n"
                "• يوت + اسم الأغنية\n"
                "• تشغيل + اسم الأغنية\n\n"
                "مثال:\n"
                "يوت فيروز سألوني الناس"
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔙 رجوع", callback_data="back")
            )
        )

    elif call.data == "back":
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=start_text(),
            reply_markup=main_keyboard()
        )


@bot.message_handler(func=lambda m: m.text and (m.text.startswith("يوت ") or m.text.startswith("تشغيل ")))
def music(message):
    if not is_subscribed(message.from_user.id):
        return bot.reply_to(message, "⚠️ اشترك بالقناة أولاً حتى تستخدم البوت", reply_markup=sub_keyboard())

    query = message.text.replace("يوت ", "", 1).replace("تشغيل ", "", 1)
    msg = bot.reply_to(message, "🔎 جاري البحث والتحميل...")

    try:
        file_path, title = download_audio(query)
        bot.edit_message_text("📤 جاري إرسال الأغنية...", message.chat.id, msg.message_id)

        with open(file_path, "rb") as audio:
            bot.send_audio(message.chat.id, audio, title=title, caption=f"🎧 {title}")

        bot.delete_message(message.chat.id, msg.message_id)

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        bot.edit_message_text(f"❌ صار خطأ:\n{e}", message.chat.id, msg.message_id)


print("Bot Running...")
bot.infinity_polling()
