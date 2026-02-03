# app/services/tarot_service.py

from typing import Literal

def create_tarot_reading_stub(spread_type: str, question: str) -> str:
    """
    Заглушка генерации расклада Таро.
    Потом сюда можно перенести реальный вызов ИИ.
    """
    spread_map = {
        "one_card": "одной карты",
        "three_cards": "трёх карт",
        "celtic_cross": "кельтского креста",
    }
    spread_text = spread_map.get(spread_type, "одной карты")
    
    if question:
        return (
            f"Расклад Таро ({spread_text}) на вопрос: '{question}'. "
            f"Это заглушка — позже здесь будет текст от ИИ."
        )
    else:
        return (
            f"Расклад Таро ({spread_text}). "
            f"Это заглушка — позже здесь будет текст от ИИ."
        )