from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание на дату")],
        [KeyboardButton(text="👥 Расписание по группе")],
        [KeyboardButton(text="👨‍🏫 Расписание по преподавателю")],
        [KeyboardButton(text="📋 Все расписание")]
    ],
    resize_keyboard=True
)


admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить занятие")],
        [KeyboardButton(text="✏️ Изменить занятие")],
        [KeyboardButton(text="❌ Удалить занятие")],
        [KeyboardButton(text="📋 Все расписание")],
        [KeyboardButton(text="⬅️ В главное меню")]
    ],
    resize_keyboard=True
)


def lessons_inline_keyboard(lessons, action="show"):
    buttons = []

    for lesson in lessons:
        lesson_id = lesson[0]
        group_name = lesson[1]
        subject = lesson[2]
        lesson_date = lesson[5]
        lesson_time = lesson[6]

        buttons.append([
            InlineKeyboardButton(
                text=f"{lesson_date} {lesson_time} | {group_name} | {subject}",
                callback_data=f"{action}_{lesson_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)