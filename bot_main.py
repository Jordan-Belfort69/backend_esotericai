import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Dict, Any

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    FSInputFile,
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
        # здесь по-прежнему пробрасываем user_id через query (если сделаешь tarot-bot — можно поменять)
        url = f"{API_BASE}/tarot?user_id={user_id}"
        payload = {
            "spread_type": spread_type,
            "question": question,
        }
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            return data.get("text", "Не удалось получить расклад.")


async def call_horoscope_api(user_id: int, zodiac: str, scope: str) -> str:
    """Вызывает /api/horoscope-bot и возвращает текст гороскопа."""
    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE}/horoscope-bot?user_id={user_id}"
        payload = {
            "zodiac": zodiac,
            "scope": scope,
        }
        async with session.post(url, json=payload) as resp:
            print("HOROSCOPE API STATUS:", resp.status)
            body = await resp.text()
            print("HOROSCOPE API BODY:", body)
            try:
                data = json.loads(body)
            except Exception:
                return "Не удалось получить гороскоп (ошибка формата ответа)."
            return data.get("text", "Не удалось получить гороскоп.")


# ========== ХЭНДЛЕРЫ ==========


async def on_start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    arg = (command.args or "").strip()
    print("on_start:", user_id, "arg:", repr(arg))

    # Гороскоп: из веб-аппа переход по ссылке t.me/БОТ?start=horoscope_знак_сфера
    if arg.startswith("horoscope_"):
        rest = arg[len("horoscope_"):].strip()
        parts = rest.split("_", 1)
        zodiac = (parts[0] or "").strip()
        scope = (parts[1] or "none").strip() if len(parts) > 1 else "none"
        if zodiac:
            try:
                text = await call_horoscope_api(user_id, zodiac, scope)
                await message.answer(text)
            except Exception as e:
                logging.exception("Horoscope on_start error: %s", e)
                await message.answer("Не удалось получить гороскоп. Попробуйте позже.")
        else:
            await message.answer("Не удалось определить знак зодиака.")
        return

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


# Формат данных из Mini App (кнопка "Прочитать гороскоп" → отправка в чат):
# { "type": "horoscope", "zodiac": "Овен" | "Телец" | ..., "scope": "none" | "career" | "money" | "love" | "health" }


async def on_web_app_data(message: Message):
    """Обработка данных из Mini App (гороскоп): знак + сфера → чат, бот присылает гороскоп (заглушка)."""
    print("WEB_APP_DATA RAW:", message.web_app_data)  # для отладки

    if not message.web_app_data or not message.web_app_data.data:
        return

    try:
        data = json.loads(message.web_app_data.data)
    except Exception as e:
        logging.warning("Failed to parse web_app_data: %s", e)
        return

    if data.get("type") != "horoscope":
        return

    zodiac = data.get("zodiac")
    scope = data.get("scope", "none")

    if not zodiac:
        await message.answer("Не удалось определить знак зодиака.")
        return

    try:
        text = await call_horoscope_api(message.from_user.id, zodiac, scope)
        await message.answer(text)
    except Exception as e:
        logging.exception("Horoscope handler error: %s", e)
        try:
            await message.answer(
                "Не удалось получить гороскоп. Попробуйте позже или напишите /start."
            )
        except Exception:
            pass


# ========== СОВЕТ ДНЯ: ОБРАБОТКА НАЖАТИЯ КНОПОК 1/2/3 ==========
def _get_daily_advice_cards():
    try:
        from app.data.daily_advice_cards import DAILY_ADVICE_CARDS, get_card_image_path
        return DAILY_ADVICE_CARDS, get_card_image_path
    except Exception as e:
        logging.warning("daily_advice_cards not available: %s", e)
        return [], None


async def on_advice_callback(callback: CallbackQuery):
    """При нажатии на кнопку 1, 2 или 3 — отправляем рандомную карту и её описание (картинка отдельно, текст отдельно)."""
    await callback.answer()
    user_id = callback.from_user.id
    first_name = (callback.from_user.first_name or "Друг").strip()

    cards, get_card_image_path = _get_daily_advice_cards()
    if not cards or not get_card_image_path:
        await callback.message.answer("Совет дня временно недоступен. Попробуйте позже.")
        return

    card = random.choice(cards)
    card_path = get_card_image_path(card)
    if not card_path.exists():
        await callback.message.answer(
            f"Карта: {card['title']}\n\n{card['description']}"
        )
        return

    # Сначала картинка отдельным сообщением
    photo = FSInputFile(card_path)
    await callback.message.answer_photo(photo=photo, caption=card["title"])

    # Затем текст отдельным сообщением (как на скриншоте)
    text = f"Уважаемый(ая) {first_name},\n\n{card['description']}"
    await callback.message.answer(text)


# ========== ЗАПУСК ==========
async def log_any_message(message: Message):
    print("ANY MESSAGE:", message)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        # без allowed_updates, чтобы бот получал web_app_data
    )
    dp = Dispatcher()

    # Сначала специфичные хэндлеры (иначе log_any_message с F() перехватит всё, в т.ч. web_app_data)
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_app, Command("app"))
    dp.message.register(on_voice, F.voice)
    dp.message.register(on_photo, F.photo)
    dp.message.register(on_text, F.text)
    dp.message.register(on_web_app_data, F.web_app_data)

    # Совет дня: инлайн-кнопки 1, 2, 3
    dp.callback_query.register(on_advice_callback, F.data.startswith("advice_"))

    dp.message.register(log_any_message, F())  # лог всего остального

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
