from pathlib import Path
import os
import sqlite3
import sys

from flask import current_app, g
from werkzeug.security import generate_password_hash


def project_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def data_dir():
    path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def upload_dir():
    configured = current_app.config.get("UPLOAD_FOLDER")
    path = Path(configured) if configured else data_dir() / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def database_path():
    configured = current_app.config.get("DATABASE") or os.environ.get("ASSIGNMENT_DB_PATH")
    if configured:
        path = Path(configured)
    else:
        path = data_dir() / "assignment_system.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(database_path())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(seed=True):
    db = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    if seed:
        seed_data(db)
    db.commit()


def ensure_db(seed=True):
    db = get_db()
    table = db.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = 'users'
        """
    ).fetchone()
    if not table:
        init_db(seed=seed)


def seed_data(db):
    exists = db.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
    if exists:
        return

    users = [
        ("admin", "admin123", "系统管理员", "admin", "approved"),
        ("teacher01", "teacher123", "张老师", "teacher", "approved"),
        ("teacher02", "teacher123", "李老师", "teacher", "pending"),
        ("student01", "student123", "王同学", "student", "approved"),
        ("student02", "student123", "赵同学", "student", "approved"),
    ]
    for username, password, name, role, status in users:
        db.execute(
            """
            INSERT INTO users (username, password_hash, name, role, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, generate_password_hash(password), name, role, status),
        )

    teacher_id = db.execute("SELECT id FROM users WHERE username = 'teacher01'").fetchone()["id"]
    student_id = db.execute("SELECT id FROM users WHERE username = 'student01'").fetchone()["id"]
    db.execute(
        """
        INSERT INTO courses (name, description, teacher_id)
        VALUES (?, ?, ?)
        """,
        ("Python 程序设计基础", "面向 Python 基础语法、文件处理和数据库应用的课程。", teacher_id),
    )
    course_id = db.execute("SELECT id FROM courses WHERE name = 'Python 程序设计基础'").fetchone()["id"]
    db.execute(
        "INSERT INTO enrollments (course_id, student_id) VALUES (?, ?)",
        (course_id, student_id),
    )
    db.execute(
        """
        INSERT INTO assignments (course_id, title, description, deadline)
        VALUES (?, ?, ?, ?)
        """,
        (
            course_id,
            "SQLite 数据库练习",
            "完成一个包含增删改查功能的小型数据库程序，并提交说明文档。",
            "2026-06-30 23:59",
        ),
    )
