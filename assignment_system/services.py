import csv
import io
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .database import get_db, upload_dir


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class UserService:
    def register(self, username, password, name, role):
        role = role if role in {"teacher", "student"} else "student"
        status = "pending" if role == "teacher" else "approved"
        db = get_db()
        db.execute(
            """
            INSERT INTO users (username, password_hash, name, role, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username.strip(), generate_password_hash(password), name.strip(), role, status),
        )
        db.commit()
        return status

    def authenticate(self, username, password):
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            return None, "用户名或密码错误"
        if user["status"] == "pending":
            return None, "教师账号正在等待管理员审核"
        if user["status"] == "disabled":
            return None, "账号已被停用"
        return user, ""

    def get(self, user_id):
        return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def list_users(self):
        return get_db().execute(
            """
            SELECT id, username, name, role, status, created_at
            FROM users
            ORDER BY role, created_at DESC
            """
        ).fetchall()

    def set_status(self, user_id, status):
        get_db().execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
        get_db().commit()


class CourseService:
    def create(self, name, description, teacher_id):
        db = get_db()
        db.execute(
            """
            INSERT INTO courses (name, description, teacher_id)
            VALUES (?, ?, ?)
            """,
            (name.strip(), description.strip(), teacher_id),
        )
        db.commit()

    def list_all(self):
        return get_db().execute(
            """
            SELECT c.*, u.name AS teacher_name,
                   COUNT(e.id) AS student_count
            FROM courses c
            JOIN users u ON u.id = c.teacher_id
            LEFT JOIN enrollments e ON e.course_id = c.id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
        ).fetchall()

    def list_by_teacher(self, teacher_id):
        return get_db().execute(
            """
            SELECT c.*, COUNT(e.id) AS student_count
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            WHERE c.teacher_id = ?
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """,
            (teacher_id,),
        ).fetchall()

    def list_by_student(self, student_id):
        return get_db().execute(
            """
            SELECT c.*, u.name AS teacher_name
            FROM courses c
            JOIN users u ON u.id = c.teacher_id
            JOIN enrollments e ON e.course_id = c.id
            WHERE e.student_id = ?
            ORDER BY c.created_at DESC
            """,
            (student_id,),
        ).fetchall()

    def get(self, course_id):
        return get_db().execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()

    def enroll(self, course_id, student_id):
        db = get_db()
        db.execute(
            "INSERT OR IGNORE INTO enrollments (course_id, student_id) VALUES (?, ?)",
            (course_id, student_id),
        )
        db.commit()

    def is_teacher_owner(self, course_id, teacher_id):
        course = self.get(course_id)
        return course and course["teacher_id"] == teacher_id


class AssignmentService:
    def create(self, course_id, title, description, deadline):
        db = get_db()
        db.execute(
            """
            INSERT INTO assignments (course_id, title, description, deadline)
            VALUES (?, ?, ?, ?)
            """,
            (course_id, title.strip(), description.strip(), deadline.strip()),
        )
        db.commit()

    def get(self, assignment_id):
        return get_db().execute(
            """
            SELECT a.*, c.name AS course_name, c.teacher_id
            FROM assignments a
            JOIN courses c ON c.id = a.course_id
            WHERE a.id = ?
            """,
            (assignment_id,),
        ).fetchone()

    def list_for_teacher(self, teacher_id):
        return get_db().execute(
            """
            SELECT a.*, c.name AS course_name,
                   COUNT(s.id) AS submit_count
            FROM assignments a
            JOIN courses c ON c.id = a.course_id
            LEFT JOIN submissions s ON s.assignment_id = a.id
            WHERE c.teacher_id = ?
            GROUP BY a.id
            ORDER BY a.created_at DESC
            """,
            (teacher_id,),
        ).fetchall()

    def list_for_student(self, student_id):
        return get_db().execute(
            """
            SELECT a.*, c.name AS course_name, s.id AS submission_id,
                   s.score, s.comment, s.updated_at
            FROM assignments a
            JOIN courses c ON c.id = a.course_id
            JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN submissions s
              ON s.assignment_id = a.id AND s.student_id = e.student_id
            WHERE e.student_id = ?
            ORDER BY a.deadline ASC
            """,
            (student_id,),
        ).fetchall()


class SubmissionService:
    def save(self, assignment_id, student_id, content, file_storage=None):
        filename = None
        stored_filename = None
        if file_storage and file_storage.filename:
            filename = secure_filename(file_storage.filename) or "upload.dat"
            stored_filename = f"{uuid4().hex}_{filename}"
            file_storage.save(upload_dir() / stored_filename)

        db = get_db()
        old = db.execute(
            """
            SELECT * FROM submissions
            WHERE assignment_id = ? AND student_id = ?
            """,
            (assignment_id, student_id),
        ).fetchone()
        if old:
            if not filename:
                filename = old["filename"]
                stored_filename = old["stored_filename"]
            db.execute(
                """
                UPDATE submissions
                SET filename = ?, stored_filename = ?, content = ?,
                    updated_at = ?, score = NULL, comment = ''
                WHERE id = ?
                """,
                (filename, stored_filename, content.strip(), now_text(), old["id"]),
            )
        else:
            db.execute(
                """
                INSERT INTO submissions
                    (assignment_id, student_id, filename, stored_filename, content, submitted_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (assignment_id, student_id, filename, stored_filename, content.strip(), now_text(), now_text()),
            )
        db.commit()

    def list_by_assignment(self, assignment_id):
        return get_db().execute(
            """
            SELECT s.*, u.name AS student_name, u.username
            FROM submissions s
            JOIN users u ON u.id = s.student_id
            WHERE s.assignment_id = ?
            ORDER BY s.updated_at DESC
            """,
            (assignment_id,),
        ).fetchall()

    def get(self, submission_id):
        return get_db().execute(
            """
            SELECT s.*, a.title AS assignment_title, c.teacher_id
            FROM submissions s
            JOIN assignments a ON a.id = s.assignment_id
            JOIN courses c ON c.id = a.course_id
            WHERE s.id = ?
            """,
            (submission_id,),
        ).fetchone()

    def grade(self, submission_id, score, comment):
        db = get_db()
        db.execute(
            """
            UPDATE submissions
            SET score = ?, comment = ?
            WHERE id = ?
            """,
            (float(score), comment.strip(), submission_id),
        )
        db.commit()

    def file_path(self, submission):
        stored = submission["stored_filename"]
        if not stored:
            return None
        path = upload_dir() / stored
        return path if Path(path).exists() else None


class ReportService:
    def assignment_csv(self, assignment_id):
        assignment = AssignmentService().get(assignment_id)
        rows = SubmissionService().list_by_assignment(assignment_id)
        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["作业", assignment["title"]])
        writer.writerow(["课程", assignment["course_name"]])
        writer.writerow([])
        writer.writerow(["学号/账号", "姓名", "提交时间", "文件名", "成绩", "评语"])
        for row in rows:
            writer.writerow([
                row["username"],
                row["student_name"],
                row["updated_at"],
                row["filename"] or "",
                "" if row["score"] is None else row["score"],
                row["comment"] or "",
            ])
        return output.getvalue()

