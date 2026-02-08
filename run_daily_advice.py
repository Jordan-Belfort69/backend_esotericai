#!/usr/bin/env python3
"""
Скрипт рассылки «Совет дня» (Совет Арканы).
Запускайте по расписанию (cron/scheduler), например каждые 15 минут.

Логика:
- Читает из БД пользователей с включённым советом дня (daily_tip_settings.enabled=1).
- Для каждого проверяет: текущее время в его timezone попадает в окно [time_from, time_to]
  и ему ещё не отправляли совет сегодня.
- Отправляет: 1) фото (пост с 3 картами), 2) текст с инлайн-кнопками «1», «2», «3».
- При нажатии кнопки обрабатывает бот (bot_main.py) — шлёт рандомную карту и расшифровку.

Картинки: app/img/advice/post.png — пост; app/img/cards/*.png — карты.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from core.config import BOT_TOKEN, ADVICE_POST_IMAGE
from app.db.daily_tip import (
    init_daily_tip_table,
    get_users_enabled_for_advice,
    was_advice_sent_today,
    mark_advice_sent,
)

# Текст поста с кнопками (как на скриншоте)
POST_CAPTION = (
    "☀️ Совет Арканы на завтра\n\n"
    "Выберите карту, а я подскажу, на что обратить внимание и дам напутствие, "
    "чтобы день сложился удачно."
)

INLINE_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="1", callback_data="advice_1"),
        InlineKeyboardButton(text="2", callback_data="advice_2"),
        InlineKeyboardButton(text="3", callback_data="advice_3"),
    ],
])


def _parse_time(s: str | None):
    """Парсит 'HH:MM' или 'HH:MM:SS' в (hour, minute)."""
    if not s:
        return None
    s = s.strip()
    parts = s.split(":")
    if len(parts) >= 2:
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return None


def _time_in_window(local_hour: int, local_minute: int, time_from: str | None, time_to: str | None) -> bool:
    """Проверяет, входит ли локальное время (hour, minute) в окно [time_from, time_to]."""
    from_hm = _parse_time(time_from)
    to_hm = _parse_time(time_to)
    if not from_hm:
        return True  # если время не задано — считаем что окно «всегда» в течение одного запуска
    from_min = from_hm[0] * 60 + from_hm[1]
    to_min = (to_hm[0] * 60 + to_hm[1]) if to_hm else from_min
    now_min = local_hour * 60 + local_min
    if from_min <= to_min:
        return from_min <= now_min <= to_min
    return now_min >= from_min or now_min <= to_min


async def run():
    init_daily_tip_table()
    bot = Bot(token=BOT_TOKEN)

    if not ADVICE_POST_IMAGE.exists():
        print(f"⚠️ Пост-картинка не найдена: {ADVICE_POST_IMAGE}. Положите post.png в app/img/advice/.")
        await bot.session.close()
        return

    users = get_users_enabled_for_advice()
    to_send = []

    for user_id, first_name, time_from, time_to, tz_name in users:
        tz_str = (tz_name or "Europe/Moscow").strip()
        try:
            tz = ZoneInfo(tz_str)
        except Exception:
            tz = ZoneInfo("Europe/Moscow")
        now_local = datetime.now(tz)
        date_str = now_local.strftime("%Y-%m-%d")

        if was_advice_sent_today(user_id, date_str):
            continue
        if not _time_in_window(now_local.hour, now_local.minute, time_from, time_to):
            continue
        to_send.append((user_id, first_name, date_str))

    for user_id, first_name, date_str in to_send:
        try:
            photo = FSInputFile(ADVICE_POST_IMAGE)
            await bot.send_photo(chat_id=user_id, photo=photo, caption=POST_CAPTION, reply_markup=INLINE_KEYBOARD)
            mark_advice_sent(user_id, date_str)
            print(f"✅ Совет дня отправлен user_id={user_id} ({first_name})")
        except Exception as e:
            print(f"❌ Ошибка отправки user_id={user_id}: {e}")

    await bot.session.close()
    print(f"Готово. Отправлено: {len(to_send)} из {len(users)} пользователей с включённым советом дня.")


if __name__ == "__main__":
    asyncio.run(run())
