import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

API_ID = 38266855
API_HASH = "6cc39a629921d107b9f04f6510185f0e"
BOT_TOKEN = "8612351805:AAG0ihwHKncgaj_bYADmThUBbzCXsyQ_CxU"
SESSION_STRING = "AgJH5-cAFn8PoNaKAmPsUjG3jNHIZUBX1R2YgbsAGAo4qSKObNr0Be1b4YLnS7zTXNEzdcc5JxwRdAoTtP_zveSZxAuCeNZZjtmxmmdS-rr_J11cL49ss_AsOX4ft6ysyfzIzfVgkBPR4LSDwHDOS_tIPZv4mwqnF_iIZSZzM6jV-05SD-xzs00-ajXL_HIBO6kQYotvMvgoh1nfmYrq5TbUBNK4YSWK8_QaI8DVV3DEqP1Gw0GJR055wBeGKbpS0knf7T-37_gk3k1yJUM5p4DGPFIFhTjyNYXf6K10aTx_MfLNbc6ND0LOQcJwuvrBh4SRmqcILscXUN8HpRvXwlzc-B4ERQAAAAHgw6HVAA"

BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"

START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
assistant = Client("assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(assistant)

queues = {}
os.makedirs("downloads", exist_ok=True)


async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def force_sub(message):
    await message.reply(
        "⚠️ اشترك بالقناة أولاً حتى تستخدم البوت",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{FORCE_CHANNEL}")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check_sub")]
        ])
    )


def buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ اضفني", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton("📚 طريقة الاستخدام", callback_data="help"),
            InlineKeyboardButton("👨‍💻 المطور", url=f"https://t.me/{DEV_USERNAME}")
        ],
        [InlineKeyboardButton("🛒 شراء بوت مشابه", url=f"https://t.me/{DEV_USERNAME}")]
    ])


def start_caption():
    return (
        "• هلا بك في بوت ميوزك 🎧\n\n"
        "• اضفني إلى مجموعتك وارفعني مشرف\n"
        "• ضيف الحساب المساعد للكروب\n"
        "• افتح مكالمة صوتية وشغل الأغاني\n\n"
        "• الأوامر:\n"
        "يوت فيروز\n"
        "تشغيل فيروز\n"
        "تخطي\n"
        "ايقاف"
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


async def play_next(chat_id):
    if chat_id not in queues or not queues[chat_id]:
        return None

    file_path, title = queues[chat_id].pop(0)

    try:
        await call.change_stream(chat_id, AudioPiped(file_path))
    except:
        await call.join_group_call(chat_id, AudioPiped(file_path))

    return title


@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    if not await is_subscribed(message.from_user.id):
        return await force_sub(message)

    await message.reply_photo(
        START_PHOTO,
        caption=start_caption(),
        reply_markup=buttons()
    )


@bot.on_callback_query(filters.regex("^check_sub$"))
async def check_sub(_, query):
    if await is_subscribed(query.from_user.id):
        await query.message.delete()
        await query.message.reply_photo(
            START_PHOTO,
            caption=start_caption(),
            reply_markup=buttons()
        )
    else:
        await query.answer("❌ بعدك ما مشترك", show_alert=True)


@bot.on_callback_query(filters.regex("^help$"))
async def help_cmd(_, query):
    await query.message.edit_caption(
        "📚 طريقة الاستخدام:\n\n"
        "1- اضف البوت للكروب\n"
        "2- ارفع البوت مشرف\n"
        "3- ضيف الحساب المساعد للكروب\n"
        "4- افتح مكالمة صوتية\n\n"
        "الأوامر:\n"
        "• يوت + اسم الأغنية\n"
        "• تشغيل + اسم الأغنية\n"
        "• تخطي\n"
        "• ايقاف",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ])
    )


@bot.on_callback_query(filters.regex("^back$"))
async def back(_, query):
    await query.message.edit_caption(start_caption(), reply_markup=buttons())


@bot.on_message(filters.regex(r"^(يوت|تشغيل)\s+(.+)"))
async def play(_, message: Message):
    if not await is_subscribed(message.from_user.id):
        return await force_sub(message)

    chat_id = message.chat.id
    query = message.matches[0].group(2)

    msg = await message.reply("🔎 جاري البحث والتحميل...")

    try:
        file_path, title = await asyncio.to_thread(download_audio, query)

        queues.setdefault(chat_id, [])
        empty = len(queues[chat_id]) == 0
        queues[chat_id].append((file_path, title))

        if empty:
            await play_next(chat_id)
            await msg.edit(f"▶️ تم التشغيل:\n{title}")
        else:
            await msg.edit(f"✅ انضاف للطابور:\n{title}")

    except Exception as e:
        await msg.edit(f"❌ خطأ:\n{e}")


@bot.on_message(filters.regex("^تخطي$"))
async def skip(_, message: Message):
    if not await is_subscribed(message.from_user.id):
        return await force_sub(message)

    title = await play_next(message.chat.id)
    if title:
        await message.reply(f"⏭ تم التخطي وتشغيل:\n{title}")
    else:
        await message.reply("ماكو أغاني بالطابور.")


@bot.on_message(filters.regex("^(ايقاف|انهاء)$"))
async def stop(_, message: Message):
    if not await is_subscribed(message.from_user.id):
        return await force_sub(message)

    queues[message.chat.id] = []

    try:
        await call.leave_group_call(message.chat.id)
        await message.reply("⏹ تم إيقاف التشغيل")
    except:
        await message.reply("ماكو تشغيل حالياً.")


async def main():
    await bot.start()
    await assistant.start()
    await call.start()
    print("Bot Running...")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
