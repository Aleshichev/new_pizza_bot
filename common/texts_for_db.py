from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Кава', 'Чай/Масала', 'Какао/Матча', "Напої", "Десерт", "Добавки"]

description_for_info_pages = [
    {
        "name": "main",
        "description": "Вітаємо у кав'ярні 'Разом з кавою!'",
    },
    {
        "name": "about",
        "description": "Ми відчинені з 9 до 22. Кожного дня",
    },
    {
        "name": "payment",
        "description": as_marked_section(
            Bold("Оплата 💰:"),
            "Сплачуйте замовлення на місці",
            "Сплатити онлайн",
            marker="✅ ",
        ).as_html(),
    },
    {
        "name": "history",
        "description": as_list(
            as_marked_section(
                Bold("Очищення історії чату 🗑"),
                "Натисніть три точки у верхньому правому куті",
                "Виберіть очистити історію",
                marker="✅ ",
            ),
        ).as_html(),
    },
    {
        "name": "catalog",
        "description": "Категорії:",
    },
    {
        "name": "cart",
        "description": "Ваш кошик порожній!",
    },
]

