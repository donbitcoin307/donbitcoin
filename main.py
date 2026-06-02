import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import (
    create_db,
    add_user,
    add_admin,
    is_admin,
    add_lesson,
    get_all_lessons,
    get_lessons_by_group,
    get_lessons_by_teacher,
    get_lessons_by_date,
    get_lesson_by_id,
    update_lesson,
    delete_lesson
)

from keyboards import main_keyboard, admin_keyboard, lessons_inline_keyboard


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class AddLesson(StatesGroup):
    group_name = State()
    subject = State()
    teacher = State()
    classroom = State()
    lesson_date = State()
    lesson_time = State()
    lesson_type = State()


class SearchByGroup(StatesGroup):
    group_name = State()


class SearchByTeacher(StatesGroup):
    teacher = State()


class SearchByDate(StatesGroup):
    lesson_date = State()


class EditLesson(StatesGroup):
    lesson_id = State()
    group_name = State()
    subject = State()
    teacher = State()
    classroom = State()
    lesson_date = State()
    lesson_time = State()
    lesson_type = State()


class DeleteLesson(StatesGroup):
    lesson_id = State()


def format_lesson(lesson):
    lesson_id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type = lesson

    return (
        f"📌 <b>Занятие №{lesson_id}</b>\n\n"
        f"👥 Группа: {group_name}\n"
        f"📚 Дисциплина: {subject}\n"
        f"👨‍🏫 Преподаватель: {teacher}\n"
        f"🚪 Аудитория: {classroom}\n"
        f"📅 Дата: {lesson_date}\n"
        f"⏰ Время: {lesson_time}\n"
        f"📝 Тип занятия: {lesson_type}"
    )


def format_lessons_list(lessons):
    if not lessons:
        return "Расписание не найдено."

    text = "📋 <b>Расписание:</b>\n\n"

    for lesson in lessons:
        lesson_id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type = lesson

        text += (
            f"№{lesson_id}\n"
            f"📅 {lesson_date} | ⏰ {lesson_time}\n"
            f"👥 {group_name}\n"
            f"📚 {subject}\n"
            f"👨‍🏫 {teacher}\n"
            f"🚪 {classroom}\n"
            f"📝 {lesson_type}\n\n"
        )

    return text


@dp.message(CommandStart())
async def start_handler(message: Message):
    add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    if ADMIN_ID and str(message.from_user.id) == ADMIN_ID:
        add_admin(message.from_user.id)

    await message.answer(
        "Здравствуйте! Я Telegram-бот расписания кафедры.\n\n"
        "С моей помощью можно посмотреть расписание по группе, "
        "преподавателю или выбранной дате.",
        reply_markup=main_keyboard
    )


@dp.message(Command("admin"))
async def admin_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к административному режиму.")
        return

    await message.answer(
        "Административный режим включён.",
        reply_markup=admin_keyboard
    )


@dp.message(F.text == "⬅️ В главное меню")
async def back_to_menu(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_keyboard
    )


@dp.message(F.text == "📋 Все расписание")
async def all_lessons_handler(message: Message):
    lessons = get_all_lessons()
    await message.answer(format_lessons_list(lessons), parse_mode="HTML")


@dp.message(F.text == "👥 Расписание по группе")
async def group_search_start(message: Message, state: FSMContext):
    await state.set_state(SearchByGroup.group_name)
    await message.answer("Введите номер группы:")


@dp.message(SearchByGroup.group_name)
async def group_search_result(message: Message, state: FSMContext):
    lessons = get_lessons_by_group(message.text)
    await state.clear()

    await message.answer(format_lessons_list(lessons), parse_mode="HTML")


@dp.message(F.text == "👨‍🏫 Расписание по преподавателю")
async def teacher_search_start(message: Message, state: FSMContext):
    await state.set_state(SearchByTeacher.teacher)
    await message.answer("Введите фамилию или ФИО преподавателя:")


@dp.message(SearchByTeacher.teacher)
async def teacher_search_result(message: Message, state: FSMContext):
    lessons = get_lessons_by_teacher(message.text)
    await state.clear()

    await message.answer(format_lessons_list(lessons), parse_mode="HTML")


@dp.message(F.text == "📅 Расписание на дату")
async def date_search_start(message: Message, state: FSMContext):
    await state.set_state(SearchByDate.lesson_date)
    await message.answer("Введите дату в формате ДД.ММ.ГГГГ:")


@dp.message(SearchByDate.lesson_date)
async def date_search_result(message: Message, state: FSMContext):
    lessons = get_lessons_by_date(message.text)
    await state.clear()

    await message.answer(format_lessons_list(lessons), parse_mode="HTML")


@dp.message(F.text == "➕ Добавить занятие")
async def add_lesson_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой функции.")
        return

    await state.set_state(AddLesson.group_name)
    await message.answer("Введите номер группы:")


@dp.message(AddLesson.group_name)
async def add_lesson_group(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await state.set_state(AddLesson.subject)
    await message.answer("Введите название дисциплины:")


@dp.message(AddLesson.subject)
async def add_lesson_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddLesson.teacher)
    await message.answer("Введите ФИО преподавателя:")


@dp.message(AddLesson.teacher)
async def add_lesson_teacher(message: Message, state: FSMContext):
    await state.update_data(teacher=message.text)
    await state.set_state(AddLesson.classroom)
    await message.answer("Введите аудиторию:")


@dp.message(AddLesson.classroom)
async def add_lesson_classroom(message: Message, state: FSMContext):
    await state.update_data(classroom=message.text)
    await state.set_state(AddLesson.lesson_date)
    await message.answer("Введите дату занятия в формате ДД.ММ.ГГГГ:")


@dp.message(AddLesson.lesson_date)
async def add_lesson_date(message: Message, state: FSMContext):
    await state.update_data(lesson_date=message.text)
    await state.set_state(AddLesson.lesson_time)
    await message.answer("Введите время занятия, например 09:00:")


@dp.message(AddLesson.lesson_time)
async def add_lesson_time(message: Message, state: FSMContext):
    await state.update_data(lesson_time=message.text)
    await state.set_state(AddLesson.lesson_type)
    await message.answer("Введите тип занятия: лекция, практика или лабораторная:")


@dp.message(AddLesson.lesson_type)
async def add_lesson_type(message: Message, state: FSMContext):
    data = await state.get_data()

    add_lesson(
        group_name=data["group_name"],
        subject=data["subject"],
        teacher=data["teacher"],
        classroom=data["classroom"],
        lesson_date=data["lesson_date"],
        lesson_time=data["lesson_time"],
        lesson_type=message.text
    )

    await state.clear()

    await message.answer(
        "Занятие успешно добавлено в расписание.",
        reply_markup=admin_keyboard
    )


@dp.message(F.text == "✏️ Изменить занятие")
async def edit_lesson_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой функции.")
        return

    lessons = get_all_lessons()

    if not lessons:
        await message.answer("В расписании пока нет занятий.")
        return

    await state.set_state(EditLesson.lesson_id)

    await message.answer(
        "Выберите занятие для изменения:",
        reply_markup=lessons_inline_keyboard(lessons, action="edit")
    )


@dp.callback_query(F.data.startswith("edit_"))
async def edit_lesson_choose(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split("_")[1])
    lesson = get_lesson_by_id(lesson_id)

    if not lesson:
        await callback.message.answer("Занятие не найдено.")
        await callback.answer()
        return

    await state.update_data(lesson_id=lesson_id)
    await state.set_state(EditLesson.group_name)

    await callback.message.answer("Введите новую группу:")
    await callback.answer()


@dp.message(EditLesson.group_name)
async def edit_lesson_group(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await state.set_state(EditLesson.subject)
    await message.answer("Введите новое название дисциплины:")


@dp.message(EditLesson.subject)
async def edit_lesson_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(EditLesson.teacher)
    await message.answer("Введите новое ФИО преподавателя:")


@dp.message(EditLesson.teacher)
async def edit_lesson_teacher(message: Message, state: FSMContext):
    await state.update_data(teacher=message.text)
    await state.set_state(EditLesson.classroom)
    await message.answer("Введите новую аудиторию:")


@dp.message(EditLesson.classroom)
async def edit_lesson_classroom(message: Message, state: FSMContext):
    await state.update_data(classroom=message.text)
    await state.set_state(EditLesson.lesson_date)
    await message.answer("Введите новую дату в формате ДД.ММ.ГГГГ:")


@dp.message(EditLesson.lesson_date)
async def edit_lesson_date(message: Message, state: FSMContext):
    await state.update_data(lesson_date=message.text)
    await state.set_state(EditLesson.lesson_time)
    await message.answer("Введите новое время:")


@dp.message(EditLesson.lesson_time)
async def edit_lesson_time(message: Message, state: FSMContext):
    await state.update_data(lesson_time=message.text)
    await state.set_state(EditLesson.lesson_type)
    await message.answer("Введите новый тип занятия:")


@dp.message(EditLesson.lesson_type)
async def edit_lesson_finish(message: Message, state: FSMContext):
    data = await state.get_data()

    update_lesson(
        lesson_id=data["lesson_id"],
        group_name=data["group_name"],
        subject=data["subject"],
        teacher=data["teacher"],
        classroom=data["classroom"],
        lesson_date=data["lesson_date"],
        lesson_time=data["lesson_time"],
        lesson_type=message.text
    )

    await state.clear()

    await message.answer(
        "Занятие успешно изменено.",
        reply_markup=admin_keyboard
    )


@dp.message(F.text == "❌ Удалить занятие")
async def delete_lesson_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой функции.")
        return

    lessons = get_all_lessons()

    if not lessons:
        await message.answer("В расписании пока нет занятий.")
        return

    await message.answer(
        "Выберите занятие для удаления:",
        reply_markup=lessons_inline_keyboard(lessons, action="delete")
    )


@dp.callback_query(F.data.startswith("delete_"))
async def delete_lesson_callback(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    result = delete_lesson(lesson_id)

    if result > 0:
        await callback.message.answer("Занятие успешно удалено.")
    else:
        await callback.message.answer("Занятие не найдено.")

    await callback.answer()


@dp.callback_query(F.data.startswith("show_"))
async def show_lesson_callback(callback: CallbackQuery):
    lesson_id = int(callback.data.split("_")[1])
    lesson = get_lesson_by_id(lesson_id)

    if not lesson:
        await callback.message.answer("Занятие не найдено.")
        await callback.answer()
        return

    await callback.message.answer(format_lesson(lesson), parse_mode="HTML")
    await callback.answer()


@dp.message()
async def unknown_message(message: Message):
    await message.answer(
        "Я не понял команду. Используйте кнопки меню.",
        reply_markup=main_keyboard
    )


async def main():
    create_db()

    if ADMIN_ID:
        add_admin(int(ADMIN_ID))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())