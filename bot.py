import os
import re
import asyncio
import aiohttp
import yt_dlp

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
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
            [
                {
                    "text": "اضفني للكروب",
                    "url": f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    "style": "primary"
                }
            ],
            [
                {
                    "text": "المطور",
                    "url": f"https://t.me/{DEV_USERNAME}",
                    "style": "primary"
                },
                {
                    "text": "شراء بوت مشابه",
                    "url": f"https://t.me/{DEV_USERNAME}",
                    "style": "primary"
                }
            ],
            [
                {
                    "text": "قناة البوت",
                    "url": f"https://t.me/{FORCE_CHANNEL}",
                    "style": "primary"
                }
            ]
        ]
    }


def sub_keyboard():
    return {
        "inline_keyboard": [
            [
                {
                    "text": "اشترك بالقناة",
                    "url": f"https://t.me/{FORCE_CHANNEL}",
                    "style": "primary"
                }
            ]
        ]
    }


async def raw_send_photo(chat_id, photo, caption, reply_markup):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    async with aiohttp.ClientSession() as session:
        await session.post(
            url,
            json={
                "chat_id": chat_id,
                "photo": photo,
                "caption": caption,
                "reply_markup": reply_markup
            }
        )


async def raw_send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data)


async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{FORCE_CHANNEL}",
            user_id=user_id
        )

        return member.status in ["member", "administrator", "creator"]

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


def download_audio(query):
    base_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiefile": "cookies.txt",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 20,
        "retries": 5,
        "fragment_retries": 5,
    }

    sources = [
        {
            "search": f"ytsearch10:{query}",
            "extra": {
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android"]
                    }
                }
            }
        },
        {
            "search": f"ytsearch10:{query}",
            "extra": {
                "extractor_args": {
                    "youtube": {
                        "player_client": ["ios"]
                    }
                }
            }
        },
        {
            "search": f"ytsearch10:{query}",
            "extra": {
                "extractor_args": {
                    "youtube": {
                        "player_client": ["web"]
                    }
                }
            }
        },
        {
            "search": f"scsearch5:{query}",
            "extra": {}
        }
    ]

    last_error = None

    for source in sources:
        try:
            opts = base_opts.copy()
            opts.update(source["extra"])

            if source["search"].startswith("scsearch"):
                opts.pop("cookiefile", None)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(source["search"], download=True)

                if info and "entries" in info:
                    for item in info["entries"]:
                        if item:
                            info = item
                            break

                if not info:
                    raise Exception("ما حصلت نتيجة")

                title = clean_filename(info.get("title", "song"))
                file_path = ydl.prepare_filename(info)

                return file_path, title

        except Exception as e:
            last_error = e
            continue

    raise Exception(last_error)


@dp.message(CommandStart())
async def start(message: Message):
    if not await is_subscribed(message.from_user.id):
        return await raw_send_message(
            message.chat.id,
            "⚠️ اشترك بالقناة أولاً",
            sub_keyboard()
        )

    await raw_send_photo(
        message.chat.id,
        START_PHOTO,
        start_text(),
        blue_keyboard()
    )


@dp.message(F.text.startswith("يوت ") | F.text.startswith("تشغيل "))
async def music(message: Message):
    if not await is_subscribed(message.from_user.id):
        return await raw_send_message(
            message.chat.id,
            "⚠️ اشترك بالقناة أولاً",
            sub_keyboard()
        )

    query = (
        message.text
        .replace("يوت ", "", 1)
        .replace("تشغيل ", "", 1)
        .strip()
    )

    if not query:
        return await message.reply("اكتب اسم الأغنية")

    msg = await message.reply("🔎 جاري البحث...")

    try:
        file_path, title = await asyncio.to_thread(download_audio, query)

        await msg.edit_text("📤 جاري الإرسال...")

        await message.answer_audio(
            FSInputFile(file_path),
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
