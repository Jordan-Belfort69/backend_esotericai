import asyncio
import json
import logging
from typing import Dict, Any

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    WebAppData,
)

from core.config import BOT_TOKEN


logging.basicConfig(level=logging.INFO)

API_BASE = "https://web-production-4d81b.up.railway.app/api"

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


async def on_start(message: Message):
    print("on_start:", message.from_user.id)
    await message.answer(
        "Привет! Нажми кнопку Таро в мини‑аппе, выбери режим и вернись сюда, "
        "чтобы задать вопрос."
    )


async def on_any_message(message: Message):
    """
    Универсальный хендлер: смотрим, что вообще приходит от мини‑аппа,
    и если есть web_app_data — обрабатываем так, как планировали.
    """
    print("RAW MESSAGE:", message.model_dump())

    if message.web_app_data is None:
        # Это обычное сообщение (текст, фото и т.п.)
        # Для текстов дальше срабатывает on_text, для фото — on_photo, для войса — on_voice.
        return

    # Если дошли сюда — у сообщения есть WebAppData
    wad: WebAppData = message.web_app_data
    print("on_web_app_data RAW:", wad)

    try:
        payload = json.loads(wad.data)
    except Exception:
        await message.answer("Не удалось прочитать данные из мини‑приложения.")
        return

    mode_type = payload.get("type")
    user_id = message.from_user.id
    print("on_web_app_data parsed:", user_id, mode_type, payload)

    if mode_type == "tarot_text":
        user_states[user_id] = {
            "mode": "tarot_text",
            "cards": payload.get("cards", 1),
            "deck": payload.get("deck", "rider"),
        }
        await message.answer(
            "Напишите подробно свой вопрос для расклада Таро."
        )

    elif mode_type == "tarot_voice":
        user_states[user_id] = {
            "mode": "tarot_voice",
        }
        await message.answer(
            "Отправьте свой вопрос голосовым сообщением.\n"
            "Голосовое должно быть до 60 секунд."
        )

    elif mode_type == "tarot_own_photo":
        user_states[user_id] = {
            "mode": "tarot_own_photo",
            "photo_file_id": None,
        }
        await message.answer(
            "Сделайте одно фото своих карт при хорошем освещении и отправьте его сюда."
        )

    else:
        await message.answer("Неизвестный тип запроса из мини‑приложения.")


async def on_text(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    print("on_text:", user_id, repr(message.text), "state:", state)

    if not state:
        return  # обычный текст, не про Таро

    mode = state.get("mode")

    # 1) Текстовый вопрос
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
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(on_start, CommandStart())
    # общий хендлер для всех сообщений — он сам проверяет web_app_data
    dp.message.register(on_any_message)
    dp.message.register(on_voice, F.voice)
    dp.message.register(on_photo, F.photo)
    dp.message.register(on_text, F.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
