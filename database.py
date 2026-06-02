import sqlite3


DB_NAME = "schedule.db"


def create_db():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            subject TEXT NOT NULL,
            teacher TEXT NOT NULL,
            classroom TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            lesson_time TEXT NOT NULL,
            lesson_type TEXT NOT NULL
        )
    """)

    connect.commit()
    connect.close()


def add_user(telegram_id, username):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, username)
        VALUES (?, ?)
    """, (telegram_id, username))

    connect.commit()
    connect.close()


def add_admin(telegram_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO admins (telegram_id)
        VALUES (?)
    """, (telegram_id,))

    connect.commit()
    connect.close()


def is_admin(telegram_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id FROM admins
        WHERE telegram_id = ?
    """, (telegram_id,))

    result = cursor.fetchone()
    connect.close()

    return result is not None


def add_lesson(group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        INSERT INTO schedule 
        (group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type))

    connect.commit()
    connect.close()


def get_all_lessons():
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type
        FROM schedule
        ORDER BY lesson_date, lesson_time
    """)

    lessons = cursor.fetchall()
    connect.close()

    return lessons


def get_lessons_by_group(group_name):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type
        FROM schedule
        WHERE group_name LIKE ?
        ORDER BY lesson_date, lesson_time
    """, (f"%{group_name}%",))

    lessons = cursor.fetchall()
    connect.close()

    return lessons


def get_lessons_by_teacher(teacher):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type
        FROM schedule
        WHERE teacher LIKE ?
        ORDER BY lesson_date, lesson_time
    """, (f"%{teacher}%",))

    lessons = cursor.fetchall()
    connect.close()

    return lessons


def get_lessons_by_date(lesson_date):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type
        FROM schedule
        WHERE lesson_date = ?
        ORDER BY lesson_time
    """, (lesson_date,))

    lessons = cursor.fetchall()
    connect.close()

    return lessons


def get_lesson_by_id(lesson_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        SELECT id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type
        FROM schedule
        WHERE id = ?
    """, (lesson_id,))

    lesson = cursor.fetchone()
    connect.close()

    return lesson


def update_lesson(lesson_id, group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        UPDATE schedule
        SET group_name = ?, subject = ?, teacher = ?, classroom = ?,
            lesson_date = ?, lesson_time = ?, lesson_type = ?
        WHERE id = ?
    """, (group_name, subject, teacher, classroom, lesson_date, lesson_time, lesson_type, lesson_id))

    connect.commit()
    updated_count = cursor.rowcount
    connect.close()

    return updated_count


def delete_lesson(lesson_id):
    connect = sqlite3.connect(DB_NAME)
    cursor = connect.cursor()

    cursor.execute("""
        DELETE FROM schedule
        WHERE id = ?
    """, (lesson_id,))

    connect.commit()
    deleted_count = cursor.rowcount
    connect.close()

    return deleted_count