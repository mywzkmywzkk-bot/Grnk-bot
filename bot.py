import os
import re
import asyncio
import aiohttp
import yt_dlp

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    BufferedInputFile
)
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


# الازرار الزرق
def blue_keyboard():
    return {
        "keyboard": [
            [
                {
                    "text": "اضفني للكروب"
                }
            ],
            [
                {
                    "text": "المطور"
                },
                {
                    "text": "شراء بوت مشابه"
                }
            ],
            [
                {
                    "text": "قناة البوت"
                }
            ]
        ],
        "resize_keyboard": True
    }


async def is_subscribed(user_id):
    try:

        member = await bot.get_chat_member(
            chat_id=f"@{FORCE_CHANNEL}",
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return True


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


# تحميل سريع ومحسن
def download_audio(query):

    ydl_opts = {

        "format":
        "bestaudio[filesize<25M]/bestaudio",

        "outtmpl":
        "downloads/%(title)s.%(ext)s",

        "noplaylist": True,

        "quiet": True,

        "no_warnings": True,

        "cookiefile": "cookies.txt",

        "extract_flat": False,

        "socket_timeout": 10,

        "retries": 2,

        "fragment_retries": 2,

        "concurrent_fragment_downloads": 5,

        "extractor_args": {
            "youtube": {
                "player_client": [
                    "android",
                    "ios",
                    "web"
                ]
            }
        }
    }

    searches = [

        f"ytsearch3:{query}",
        f"ytsearch5:{query}",
        f"scsearch2:{query}"

    ]

    last_error = None

    for search in searches:

        try:

            opts = ydl_opts.copy()

            if search.startswith("scsearch"):
                opts.pop("cookiefile", None)

            with yt_dlp.YoutubeDL(opts) as ydl:

                info = ydl.extract_info(
                    search,
                    download=True
                )

                if info and "entries" in info:

                    for item in info["entries"]:

                        if item:
                            info = item
                            break

                if not info:
                    continue

                title = clean_filename(
                    info.get(
                        "title",
                        "song"
                    )
                )

                file_path = ydl.prepare_filename(
                    info
                )

                return file_path, title

        except Exception as e:

            last_error = e
            continue

    raise Exception(last_error)


@dp.message(CommandStart())
async def start(message: Message):

    if not await is_subscribed(
        message.from_user.id
    ):

        return await message.answer(
            "⚠️ اشترك بالقناة أولاً\n"
            f"https://t.me/{FORCE_CHANNEL}"
        )

    await bot.send_photo(

        chat_id=message.chat.id,

        photo=START_PHOTO,

        caption=start_text(),

        reply_markup=blue_keyboard()

    )


# الازرار
@dp.message(F.text == "المطور")
async def dev_btn(message: Message):

    await message.answer(
        f" المطور:\n"
        f"https://t.me/{DEV_USERNAME}"
    )


@dp.message(F.text == "قناة البوت")
async def channel_btn(message: Message):

    await message.answer(
        f" قناة البوت:\n"
        f"https://t.me/{FORCE_CHANNEL}"
    )


@dp.message(F.text == "شراء بوت مشابه")
async def buy_btn(message: Message):

    await message.answer(
        f" راسل المطور:\n"
        f"https://t.me/{DEV_USERNAME}"
    )


@dp.message(F.text == "اضفني للكروب")
async def add_btn(message: Message):

    await message.answer(
        f"https://t.me/{BOT_USERNAME}?startgroup=true"
    )


# تشغيل الاغاني
@dp.message(
    F.text.startswith("يوت ")
    |
    F.text.startswith("تشغيل ")
)
async def music(message: Message):

    if not await is_subscribed(
        message.from_user.id
    ):

        return await message.answer(
            "⚠️ اشترك بالقناة أولاً\n"
            f"https://t.me/{FORCE_CHANNEL}"
        )

    query = (
        message.text
        .replace("يوت ", "", 1)
        .replace("تشغيل ", "", 1)
        .strip()
    )

    if not query:

        return await message.answer(
            "اكتب اسم الأغنية"
        )

    msg = await message.answer(
        "🔎 جاري البحث السريع..."
    )

    try:

        file_path, title = await asyncio.to_thread(
            download_audio,
            query
        )

        await msg.edit_text(
            "📤 جاري الإرسال..."
        )

        with open(file_path, "rb") as f:
            audio_data = f.read()

        audio_file = BufferedInputFile(
            audio_data,
            filename=f"{title}.mp3"
        )

        await message.answer_audio(

            audio=audio_file,

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

        await msg.edit_text(
            f"❌ صار خطأ:\n{e}"
        )


async def main():

    print("Bot Running...")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
