import asyncio
import json
import logging
from typing import Dict, Any

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

from core.config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

API_BASE = "https://web-production-4d81b.up.railway.app/api"
APP_URL = "https://web-production-4d81b.up.railway.app"  # URL фронта

# простое «хранилище состояния» в памяти: user_id -> mode/params
user_states: Dict[int, Dict[str, Any]] = {}


async def call_tarot_api(user_id: int, spread_type: str, question: str) -> str:
    """Вызывает твой /api/tarot и возвращает текст расклада."""
    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE}/tarot"
        payload = {
            "spread_type": spread_type,
            "question": question,
        }
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            return data.get("text", "Не удалось получить расклад.")


# ========== ХЭНДЛЕРЫ ==========


async def on_start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    arg = (command.args or "").strip()
    print("on_start:", user_id, "arg:", repr(arg))

    if arg == "tarot_text":
        user_states[user_id] = {
            "mode": "tarot_text",
            "cards": 1,
            "deck": "rider",
        }
        await message.answer(
            "Вы выбрали текстовый расклад Таро.\n"
            "Напишите подробно свой вопрос."
        )

    elif arg == "tarot_voice":
        user_states[user_id] = {
            "mode": "tarot_voice",
        }
        await message.answer(
            "Вы выбрали Таро по голосу.\n"
            "Отправьте голосовое сообщение до 60 секунд с вашим вопросом."
        )

    elif arg == "tarot_own_photo":
        user_states[user_id] = {
            "mode": "tarot_own_photo",
            "photo_file_id": None,
        }
        await message.answer(
            "Вы выбрали Таро со своими картами.\n"
            "Сначала отправьте одно фото расклада при хорошем освещении."
        )

    else:
        await message.answer(
            "Привет! Нажми кнопку Таро в мини‑аппе, выбери режим и вернись сюда, "
            "чтобы задать вопрос.\n\n"
            "Также можно написать: tarot ваш вопрос — тогда я сделаю простой расклад на одну карту."
        )


async def on_app(message: Message):
    """Присылаем свою WebApp‑кнопку, чтобы открыть мини‑аппу."""
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Открыть Esoteric AI",
                    web_app=WebAppInfo(url=APP_URL),
                )
            ]
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "Нажми кнопку ниже, чтобы открыть мини‑приложение:",
        reply_markup=kb,
    )


async def on_text(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    print("on_text:", user_id, repr(message.text), "state:", state)

    # Временная команда для отладки:
    # если сообщение начинается с "tarot ", делаем расклад на одну карту
    if message.text and message.text.startswith("tarot "):
        question = message.text[len("tarot "):].strip()
        text = await call_tarot_api(user_id, "one_card", question)
        await message.answer("Тестовый расклад по текстовой команде:\n\n" + text)
        return

    if not state:
        return  # обычный текст, не про Таро

    mode = state.get("mode")

    # 1) Текстовый вопрос после выбора режима через start=tarot_text
    if mode == "tarot_text":
        question = message.text.strip()
        spread_type = "one_card" if state.get("cards") == 1 else "three_cards"
        text = await call_tarot_api(user_id, spread_type, question)
        await message.answer(text)
        user_states.pop(user_id, None)

    # 3) Таро со своими картами — текст вопроса после фото
    elif mode == "tarot_own_photo" and state.get("photo_file_id"):
        question = message.text.strip()
        text = await call_tarot_api(user_id, "three_cards", question)
        await message.answer(
            "Интерпретация расклада по вашему фото (заглушка):\n\n" + text
        )
        user_states.pop(user_id, None)


async def on_voice(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    print("on_voice:", user_id, "state:", state)

    if not state or state.get("mode") != "tarot_voice":
        return

    text = await call_tarot_api(user_id, "one_card", "")
    await message.answer(
        "Получила ваше голосовое сообщение. Пока я не умею его распознавать, "
        "поэтому делаю общий голосовой расклад (заглушка):\n\n" + text
    )
    user_states.pop(user_id, None)


async def on_photo(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    print("on_photo:", user_id, "state:", state)

    if not state or state.get("mode") != "tarot_own_photo":
        return

    photo = message.photo[-1]
    state["photo_file_id"] = photo.file_id
    user_states[user_id] = state

    await message.answer(
        "Фото расклада получила.\nТеперь напишите текстовый вопрос, который хотите задать."
    )


# ========== ЗАПУСК ==========


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        allowed_updates=["message", "edited_message"],
    )
    dp = Dispatcher()

    dp.message.register(on_start, CommandStart())
    dp.message.register(on_app, Command("app"))
    dp.message.register(on_voice, F.voice)
    dp.message.register(on_photo, F.photo)
    dp.message.register(on_text, F.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
