import os
import re
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    FSInputFile
)
from aiogram.filters import CommandStart
import yt_dlp

TOKEN = "8612351805:AAGuyw0m-9gQM0E0y6IoLjHTCJOYC4MWv7I"

BOT_USERNAME = "FHDNSSBOT"
DEV_USERNAME = "fvamv"
FORCE_CHANNEL = "fadifva"

START_PHOTO = "https://i.ibb.co/xqVzNV7t/db72f6d6-2b6a-4f58-abdc-2f47a3aeb664.jpg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

os.makedirs("downloads", exist_ok=True)

# ================= الازرار =================

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="اضفني للكروب")],
        [
            KeyboardButton(text="المطور"),
            KeyboardButton(text="شراء بوت مشابه")
        ],
        [KeyboardButton(text="قناة البوت")]
    ],
    resize_keyboard=True
)

# ================= تنظيف الاسم =================

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)[:80]

# ================= تحميل الأغاني =================

async def download_song(query):

    loop = asyncio.get_event_loop()

    def run():

        searches = [

            # يوتيوب اندرويد
            {
                "search": f"ytsearch5:{query}",
                "client": ["android"]
            },

            # يوتيوب iOS
            {
                "search": f"ytsearch5:{query}",
                "client": ["ios"]
            },

            # يوتيوب ويب
            {
                "search": f"ytsearch5:{query}",
                "client": ["web"]
            },

            # ساوند كلاود
            {
                "search": f"scsearch5:{query}",
                "client": None
            }
        ]

        last_error = None

        for item in searches:

            try:

                ydl_opts = {

                    "format":
                    "bestaudio[filesize<25M]/bestaudio/best",

                    "outtmpl":
                    "downloads/%(title)s.%(ext)s",

                    "quiet": True,

                    "noplaylist": True,

                    "extractaudio": True,

                    "geo_bypass": True,

                    "nocheckcertificate": True,

                    "socket_timeout": 15,

                    "retries": 3,

                    "fragment_retries": 3,

                    "concurrent_fragment_downloads": 5,

                    "cookiefile": "cookies.txt",

                    "extractor_args": {
                        "youtube": {
                            "player_client":
                            item["client"]
                        }
                    } if item["client"] else {}
                }

                # ساوند كلاود بدون كوكيز
                if item["search"].startswith("scsearch"):
                    ydl_opts.pop("cookiefile", None)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                    info = ydl.extract_info(
                        item["search"],
                        download=True
                    )

                    if "entries" in info:

                        for video in info["entries"]:

                            if not video:
                                continue

                            title = clean_filename(
                                video.get(
                                    "title",
                                    "song"
                                )
                            )

                            # تخطي الشورتات
                            if "/shorts/" in str(
                                video.get("webpage_url", "")
                            ):
                                continue

                            file_path = ydl.prepare_filename(
                                video
                            )

                            return file_path, title

            except Exception as e:

                last_error = e
                continue

        raise Exception(last_error)

    return await loop.run_in_executor(None, run)

# ================= ستارت =================

@dp.message(CommandStart())
async def start(message: Message):

    text = """
• هلا بك في بوت ميوزك 🎧

• اضفني للكروب وارفعني مشرف

• اكتب:
يوت اسم الاغنية
تشغيل اسم الاغنية
"""

    await message.answer_photo(
        photo=START_PHOTO,
        caption=text,
        reply_markup=kb
    )

# ================= المطور =================

@dp.message(F.text == "المطور")
async def developer(message: Message):

    await message.answer(
        f"https://t.me/{DEV_USERNAME}"
    )

# ================= القناة =================

@dp.message(F.text == "قناة البوت")
async def channel(message: Message):

    await message.answer(
        f"https://t.me/{FORCE_CHANNEL}"
    )

# ================= شراء بوت =================

@dp.message(F.text == "شراء بوت مشابه")
async def buy(message: Message):

    await message.answer(
        f"https://t.me/{DEV_USERNAME}"
    )

# ================= اضفني =================

@dp.message(F.text == "اضفني للكروب")
async def add_group(message: Message):

    await message.answer(
        f"https://t.me/{BOT_USERNAME}?startgroup=true"
    )

# ================= تشغيل الموسيقى =================

@dp.message(
    F.text.startswith("يوت ")
    |
    F.text.startswith("تشغيل ")
)
async def music(message: Message):

    query = (
        message.text
        .replace("يوت ", "")
        .replace("تشغيل ", "")
        .strip()
    )

    if not query:
        return

    msg = await message.reply(
        "🔎 جاري البحث السريع..."
    )

    try:

        file_path, title = await download_song(query)

        await msg.edit_text(
            "📤 جاري الارسال..."
        )

        audio = FSInputFile(file_path)

        await message.answer_audio(
            audio=audio,
            title=title,
            performer="Song fadi",
            caption=f"🎧 {title}"
        )

        await msg.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:

        await msg.edit_text(
            f"❌ صار خطأ:\n{e}"
        )

# ================= تشغيل البوت =================

async def main():

    print("Bot Running...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
