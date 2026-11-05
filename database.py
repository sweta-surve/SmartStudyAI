
import sqlite3

DATABASE_NAME = "smartstudy.db"


def create_connection():
    """Open a connection to the SmartStudy SQLite database."""
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """Create student and task tables if they do not exist."""
    with create_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                study_hours REAL NOT NULL,
                attendance REAL NOT NULL,
                previous_marks REAL NOT NULL,
                sleep_hours REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                task TEXT NOT NULL,
                priority TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


def save_student(name, course, study_hours, attendance, previous_marks, sleep_hours):
    """Insert a student profile and return its ID."""
    with create_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO students
            (name, course, study_hours, attendance, previous_marks, sleep_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, course, study_hours, attendance, previous_marks, sleep_hours))

        return cursor.lastrowid


def update_student(student_id, name, course, study_hours, attendance, previous_marks, sleep_hours):
    """Update an existing student profile."""
    with create_connection() as connection:
        connection.execute("""
            UPDATE students
            SET name = ?, course = ?, study_hours = ?, attendance = ?,
                previous_marks = ?, sleep_hours = ?
            WHERE id = ?
        """, (name, course, study_hours, attendance, previous_marks, sleep_hours, student_id))


def get_all_students():
    """Return all student profiles, newest first."""
    with create_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM students ORDER BY id DESC"
        )
        return cursor.fetchall()


def get_latest_student():
    """Return the newest student profile."""
    with create_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM students ORDER BY id DESC LIMIT 1"
        )
        return cursor.fetchone()


def save_task(subject, task, priority):
    """Save a new study task and return its ID."""
    with create_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO tasks (subject, task, priority, completed)
            VALUES (?, ?, ?, 0)
        """, (subject, task, priority))

        return cursor.lastrowid


def get_all_tasks():
    """Return all tasks, newest first."""
    with create_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        )
        return cursor.fetchall()


def update_task_status(task_id, completed):
    """Update task completion status."""
    with create_connection() as connection:
        connection.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (int(completed), task_id)
        )


def update_task_details(task_id, subject, task, priority):
    """Update an existing task."""
    with create_connection() as connection:
        connection.execute("""
            UPDATE tasks
            SET subject = ?, task = ?, priority = ?
            WHERE id = ?
        """, (subject, task, priority, task_id))


def delete_task(task_id):
    """Delete a task using its ID."""
    with create_connection() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )


if __name__ == "__main__":
    create_tables()
    print("SmartStudy AI database and tables are ready.")
