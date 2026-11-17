
import sqlite3
import hashlib
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "academic_scheduler.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def initialize_database():

    with get_connection() as conn:

        conn.executescript("""

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            instructor TEXT NOT NULL,
            section TEXT NOT NULL,
            duration INTEGER NOT NULL,
            meetings INTEGER NOT NULL,
            preferred_days TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            meeting_no INTEGER NOT NULL,
            day TEXT NOT NULL,
            start_hour INTEGER NOT NULL,
            end_hour INTEGER NOT NULL,
            room TEXT NOT NULL
        );

        """)


def register_user(name, email, password, role):

    with get_connection() as conn:

        try:

            conn.execute("""
                INSERT INTO users(name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email.lower(),
                hash_password(password),
                role
            ))

            return True

        except sqlite3.IntegrityError:

            return False


def authenticate_user(email, password):

    with get_connection() as conn:

        user = conn.execute("""
            SELECT * FROM users
            WHERE email = ? AND password = ?
        """, (
            email.lower(),
            hash_password(password)
        )).fetchone()

        if user:
            return dict(user)

        return None


def has_secretary():

    with get_connection() as conn:

        result = conn.execute("""
            SELECT COUNT(*) FROM users
            WHERE role = 'Secretary'
        """).fetchone()[0]

        return result > 0
