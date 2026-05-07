import os, re, asyncio, aiohttp, yt_dlp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart

BOT_TOKEN = "8612351805:AAGuyw0m-9gQM0E0y6IoLjHTCJOYC4MWv7I"
BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"
START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
os.makedirs("downloads", exist_ok=True)

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:80]

def blue_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "اضفني للكروب", "url": f"https://t.me/{BOT_USERNAME}?startgroup=true", "style": "primary"}],
            [
                {"text": "المطور", "url": f"https://t.me/{DEV_USERNAME}", "style": "primary"},
                {"text": "شراء بوت مشابه", "url": f"https://t.me/{DEV_USERNAME}", "style": "primary"}
            ],
            [{"text": "قناة البوت", "url": f"https://t.me/{FORCE_CHANNEL}", "style": "primary"}]
        ]
    }

async def raw_send_photo(chat_id, photo, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "reply_markup": blue_keyboard()
        })

def start_text():
    return """• هلا بك في بوت ميوزك 🎧

• اضفني للكروب وارفعني مشرف

• اكتب:
يوت اسم الاغنية
تشغيل اسم الاغنية
"""

def download_audio(query):
    base_opts = {
        "format": "bestaudio[filesize<25M]/bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiefile": "cookies.txt",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 15,
        "retries": 3,
        "fragment_retries": 3,
        "concurrent_fragment_downloads": 5,
    }

    sources = [
        ("ytsearch5:", ["android"]),
        ("ytsearch5:", ["ios"]),
        ("ytsearch5:", ["web"]),
        ("scsearch5:", None),
    ]

    last_error = None

    for prefix, client in sources:
        try:
            opts = base_opts.copy()

            if client:
                opts["extractor_args"] = {"youtube": {"player_client": client}}
            else:
                opts.pop("cookiefile", None)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"{prefix}{query}", download=True)

                if info and "entries" in info:
                    for item in info["entries"]:
                        if item:
                            info = item
                            break

                title = clean_filename(info.get("title", "song"))
                file_path = ydl.prepare_filename(info)
                return file_path, title

        except Exception as e:
            last_error = e
            continue

    raise Exception(last_error)

@dp.message(CommandStart())
async def start(message: Message):
    await raw_send_photo(message.chat.id, START_PHOTO, start_text())

@dp.message(F.text.startswith("يوت ") | F.text.startswith("تشغيل "))
async def music(message: Message):
    query = message.text.replace("يوت ", "", 1).replace("تشغيل ", "", 1).strip()
    if not query:
        return await message.reply("اكتب اسم الأغنية")

    msg = await message.reply("🔎 جاري البحث السريع...")

    try:
        file_path, title = await asyncio.to_thread(download_audio, query)

        with open(file_path, "rb") as f:
            audio_data = f.read()

        await message.answer_audio(
            BufferedInputFile(audio_data, filename=f"{title}.mp3"),
            title=title,
            performer="Song fadi",
            caption=f"🎧 {title}",
            reply_to_message_id=message.message_id
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        await msg.edit_text(f"❌ صار خطأ:\n{e}")

async def main():
    print("Bot Running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
