from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Кава', 'Чай/Масала', 'Какао/Матча', "Напої", "Десерт", "Добавки"]

description_for_info_pages = {
    "main": "Вітаємо у кав'ярні 'Разом з кавою!'",
    "about": "Ми відчинені з 8 до 22. Кожного дня",
    "payment": as_marked_section(
        Bold("Оплата 💰:"),
        "Сплачуйте замовлення на місці",
        "Сплатити онлайн",
        marker="✅ ",
    ).as_html(),
    "history": as_list(
        as_marked_section(
            Bold("Очищення історії чату 🗑"),
            "Натисніть три точки у верхньому правому куті",
            "Виберіть очистити історію",
            marker="✅ ",
        ),
    ).as_html(),
    'catalog': 'Категорії:',
    'cart': 'Ваш кошик порожній!'
}
