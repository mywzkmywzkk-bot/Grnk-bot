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


# اشتراك إجباري
def is_subscribed(user_id):
    try:
        m = bot.get_chat_member("@" + FORCE_CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return True


def sub_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{FORCE_CHANNEL}"))
    kb.add(InlineKeyboardButton("✅ تحقق", callback_data="check_sub"))
    return kb


def main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ اضفني للكروب", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"))
    kb.add(
        InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USERNAME}"),
        InlineKeyboardButton("🛒 شراء بوت مشابه", url=f"https://t.me/{DEV_USERNAME}")
    )
    return kb


def start_text():
    return (
        "• أهلاً بك في بوت فادي 🎧\n\n"
        "• اكتب:\n"
        "يوت + اسم الأغنية\n\n"
        "مثال:\n"
        "يوت فيروز"
    )


# تحميل من SoundCloud بدون ffmpeg
def download_audio(query):
    search = f"scsearch1:{query}"

    opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(search, download=True)

        if "entries" in info:
            info = info["entries"][0]

        file_path = ydl.prepare_filename(info)
        title = info.get("title", "Audio")
        return file_path, title


@bot.message_handler(commands=["start"])
def start(message):
    if not is_subscribed(message.from_user.id):
        return bot.reply_to(message, "اشترك بالقناة أولاً", reply_markup=sub_keyboard())

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
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ بعدك ما مشترك", show_alert=True)


@bot.message_handler(func=lambda m: m.text and m.text.startswith("يوت "))
def music(message):
    if not is_subscribed(message.from_user.id):
        return bot.reply_to(message, "اشترك بالقناة أولاً", reply_markup=sub_keyboard())

    query = message.text.replace("يوت ", "", 1)
    msg = bot.reply_to(message, "🔎 جاري البحث...")

    try:
        file_path, title = download_audio(query)

        with open(file_path, "rb") as audio:
            bot.send_audio(message.chat.id, audio, title=title)

        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ صار خطأ:\n{e}", message.chat.id, msg.message_id)


print("Bot Running...")
bot.infinity_polling()
