import os
import unittest
import tempfile

import database


class TestScheduleDatabase(unittest.TestCase):

    def setUp(self):
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()

        database.DB_NAME = self.test_db.name
        database.create_db()

    def tearDown(self):
        os.remove(self.test_db.name)

    def test_add_user(self):
        database.add_user(telegram_id=12345, username="test_user")
        database.add_user(telegram_id=12345, username="test_user")

        self.assertTrue(True)

    def test_add_admin(self):
        database.add_admin(telegram_id=11111)

        result = database.is_admin(telegram_id=11111)

        self.assertTrue(result)

    def test_add_lesson(self):
        database.add_lesson(
            group_name="3321",
            subject="Базы данных",
            teacher="Иванов И.И.",
            classroom="401",
            lesson_date="20.06.2026",
            lesson_time="09:00",
            lesson_type="Лекция"
        )

        lessons = database.get_all_lessons()

        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0][1], "3321")
        self.assertEqual(lessons[0][2], "Базы данных")

    def test_get_lessons_by_group(self):
        database.add_lesson(
            group_name="3321",
            subject="Программирование",
            teacher="Петров П.П.",
            classroom="305",
            lesson_date="21.06.2026",
            lesson_time="10:40",
            lesson_type="Практика"
        )

        lessons = database.get_lessons_by_group("3321")

        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0][1], "3321")

    def test_get_lessons_by_teacher(self):
        database.add_lesson(
            group_name="3321",
            subject="Математика",
            teacher="Сидоров С.С.",
            classroom="202",
            lesson_date="22.06.2026",
            lesson_time="12:20",
            lesson_type="Лекция"
        )

        lessons = database.get_lessons_by_teacher("Сидоров")

        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0][3], "Сидоров С.С.")

    def test_get_lessons_by_date(self):
        database.add_lesson(
            group_name="3321",
            subject="Информатика",
            teacher="Кузнецов К.К.",
            classroom="101",
            lesson_date="23.06.2026",
            lesson_time="14:00",
            lesson_type="Лабораторная"
        )

        lessons = database.get_lessons_by_date("23.06.2026")

        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0][5], "23.06.2026")

    def test_update_lesson(self):
        database.add_lesson(
            group_name="3321",
            subject="Физика",
            teacher="Иванов И.И.",
            classroom="301",
            lesson_date="24.06.2026",
            lesson_time="09:00",
            lesson_type="Лекция"
        )

        lesson_id = database.get_all_lessons()[0][0]

        database.update_lesson(
            lesson_id=lesson_id,
            group_name="3322",
            subject="Физика",
            teacher="Иванов И.И.",
            classroom="302",
            lesson_date="24.06.2026",
            lesson_time="10:40",
            lesson_type="Практика"
        )

        lesson = database.get_lesson_by_id(lesson_id)

        self.assertEqual(lesson[1], "3322")
        self.assertEqual(lesson[4], "302")
        self.assertEqual(lesson[6], "10:40")

    def test_delete_lesson(self):
        database.add_lesson(
            group_name="3321",
            subject="История",
            teacher="Петров П.П.",
            classroom="201",
            lesson_date="25.06.2026",
            lesson_time="15:40",
            lesson_type="Семинар"
        )

        lesson_id = database.get_all_lessons()[0][0]

        deleted_count = database.delete_lesson(lesson_id)
        lessons = database.get_all_lessons()

        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(lessons), 0)


if __name__ == "__main__":
    unittest.main()