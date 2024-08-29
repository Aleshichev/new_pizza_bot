from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Food', 'Drinks']

description_for_info_pages = {
    "main": "Welcome!",
    "about": "Such-and-such Pizzeria.\n Open 24/7.",
    "payment": as_marked_section(
        Bold("Payment options:"),
        "By card in the bot",
        "Upon receipt (card/cash)",
        "In the establishment",
        marker="✅ ",
    ).as_html(),
    "history": as_list(
        as_marked_section(
            Bold("Очистка истории чата"),
            "Нажмите три точки в правом верхнем углу",
            "Выберите очистить историю",
            "Поставьте галочку для чата тоже",
            marker="✅ ",
        ),
        as_marked_section(Bold("Not allowed:"), "Mail", "Carrier pigeons", marker="❌ "),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Categories:',
    'cart': 'Your cart is empty!'
}
