from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import requests
import re

API_TOKEN = "7785726417:AAGeYXot4tds4ULAmrII11-63fuwr7a8z8A"
VK_TOKEN = "vk1.a.SQ83e3LVTMu_LUxhz-N8IHbqWYvH2RRprkVYwfexVh8iBrkiR2tbifAaKt9koHn6W7_10alM6gVz2CO_EU5uFAr9yH94YtREciABxiP1E7zHDVIqI0O461MB2oeFnkKpg-XaD9pA9JAs1DgAtha1ud3F8N6t6OBjodldmnTm_qR0y9BdqJOrlJsidrBChr28"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎵 Загрузить треки из ВК"))
    return kb

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь ссылку на свой VK профиль, и я загружу аудиозаписи 🎧", reply_markup=main_menu())

@dp.message_handler(lambda msg: "vk.com" in msg.text)
async def get_tracks(message: types.Message):
    try:
        # Извлекаем username из ссылки
        match = re.search(r"https?://(?:www\.)?vk\.com/([a-zA-Z0-9_\.]+)", message.text)
        if not match:
            await message.answer("❌ Не удалось распознать ссылку. Убедись, что ты отправил правильную ссылку на VK профиль.")
            return

        username = match.group(1)

        # Получаем user_id по username
        user_info = requests.get(
            "https://api.vk.com/method/users.get",
            params={
                "access_token": VK_TOKEN,
                "v": "5.131",
                "user_ids": username
            }
        ).json()

        user_id = user_info["response"][0]["id"]

        # Получаем аудио
        audio_response = requests.get(
            "https://api.vk.com/method/audio.get",
            params={
                "access_token": VK_TOKEN,
                "v": "5.131",
                "owner_id": user_id,
                "count": 10
            }
        )

        print("Ответ от VK:", audio_response.text)  # <-- ВАЖНО!

        audio = audio_response.json()

        if "response" in audio:
            tracks = audio["response"]["items"]
            msg = "🎶 Список треков:\n\n"
            for i, t in enumerate(tracks):
                title = f"{t.get('artist', '??')} — {t.get('title', '??')}"
                duration = t.get("duration", 0)
                minutes = duration // 60
                seconds = duration % 60
                msg += f"{i+1}. {title} [{minutes}:{seconds:02d}]\n"
            await message.answer(msg)
        else:
            await message.answer("⚠️ Не удалось получить аудио. Возможно, профиль закрыт или токен недействителен.")

    except Exception as e:
        await message.answer("❗ Произошла ошибка при получении треков.")
        import traceback
        traceback.print_exc()
        print("Ошибка:", e)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
