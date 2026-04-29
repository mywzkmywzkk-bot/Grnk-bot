import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
import yt_dlp

# ====== بياناتك ======
API_ID = 38266855
API_HASH = "6cc39a629921d107b9f04f6510185f0e"
BOT_TOKEN = "8612351805:AAGXdqskITGiL1SBbmCCUbKn2VxTnfLmnE0"
SESSION_STRING = "AgJH5-cAFn8PoNaKAmPsUjG3jNHIZUBX1R2YgbsAGAo4qSKObNr0Be1b4YLnS7zTXNEzdcc5JxwRdAoTtP_zveSZxAuCeNZZjtmxmmdS-rr_J11cL49ss_AsOX4ft6ysyfzIzfVgkBPR4LSDwHDOS_tIPZv4mwqnF_iIZSZzM6jV-05SD-xzs00-ajXL_HIBO6kQYotvMvgoh1nfmYrq5TbUBNK4YSWK8_QaI8DVV3DEqP1Gw0GJR055wBeGKbpS0knf7T-37_gk3k1yJUM5p4DGPFIFhTjyNYXf6K10aTx_MfLNbc6ND0LOQcJwuvrBh4SRmqcILscXUN8HpRvXwlzc-B4ERQAAAAHgw6HVAA"

# ====== تشغيل ======
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

assistant = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

call = PyTgCalls(assistant)

queues = {}

os.makedirs("downloads", exist_ok=True)

# ====== تحميل يوتيوب ======
def download_audio(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "cookiefile": "cookies.txt",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]

        file_path = f"downloads/{info['id']}.mp3"
        title = info.get("title", "Audio")
        return file_path, title

# ====== تشغيل التالي ======
async def play_next(chat_id):
    if chat_id not in queues or not queues[chat_id]:
        return

    file_path, title = queues[chat_id].pop(0)

    try:
        await call.change_stream(chat_id, AudioPiped(file_path))
    except:
        await call.join_group_call(chat_id, AudioPiped(file_path))

# ====== اوامر ======
@bot.on_message(filters.regex(r"^(تشغيل|يوت)\s+(.+)"))
async def play(_, message: Message):
    chat_id = message.chat.id
    query = message.matches[0].group(2)

    msg = await message.reply("🔎 جاري البحث...")

    try:
        file_path, title = await asyncio.to_thread(download_audio, query)

        if chat_id not in queues:
            queues[chat_id] = []

        queues[chat_id].append((file_path, title))

        if len(queues[chat_id]) == 1:
            await play_next(chat_id)
            await msg.edit(f"▶️ تم التشغيل:\n{title}")
        else:
            await msg.edit(f"✅ انضاف للطابور:\n{title}")

    except Exception as e:
        await msg.edit(f"❌ خطأ:\n{e}")

@bot.on_message(filters.regex(r"^تخطي$"))
async def skip(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:
        return await message.reply("ماكو شي")

    await play_next(chat_id)
    await message.reply("⏭ تم التخطي")

@bot.on_message(filters.regex(r"^(ايقاف|انهاء)$"))
async def stop(_, message: Message):
    chat_id = message.chat.id

    queues[chat_id] = []

    try:
        await call.leave_group_call(chat_id)
        await message.reply("⏹ تم الإيقاف")
    except:
        await message.reply("ماكو تشغيل")

@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply(
        "🎧 بوت ميوزك شغال\n\n"
        "اكتب:\n"
        "تشغيل + اسم اغنية\n"
        "يوت + اسم اغنية\n"
        "تخطي\n"
        "ايقاف"
    )

# ====== تشغيل ======
async def main():
    await bot.start()
    await assistant.start()
    await call.start()
    print("Bot Running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
