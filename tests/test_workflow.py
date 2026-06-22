import io
import shutil
import unittest
from pathlib import Path

from assignment_system import create_app
from assignment_system.database import init_db


class WorkflowTestCase(unittest.TestCase):
    def setUp(self):
        self.test_root = Path(__file__).resolve().parent.parent / "data" / "test_runtime"
        db_path = self.test_root / "test.sqlite3"
        upload_path = self.test_root / "uploads"
        shutil.rmtree(self.test_root, ignore_errors=True)
        self.test_root.mkdir(parents=True, exist_ok=True)
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(db_path),
                "UPLOAD_FOLDER": str(upload_path),
                "SECRET_KEY": "test-secret",
            }
        )
        with self.app.app_context():
            init_db(seed=True)
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.test_root, ignore_errors=True)

    def login(self, username, password):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    def test_admin_teacher_student_workflow(self):
        response = self.login("student01", "student123")
        self.assertIn("学生工作台".encode("utf-8"), response.data)

        response = self.client.post("/student/assignments/1/submit", data={"content": "已完成数据库练习。"}, follow_redirects=True)
        self.assertIn("作业已提交".encode("utf-8"), response.data)

        self.client.get("/logout")
        response = self.login("teacher01", "teacher123")
        self.assertIn("教师工作台".encode("utf-8"), response.data)

        response = self.client.get("/teacher/assignments/1")
        self.assertIn("已完成数据库练习".encode("utf-8"), response.data)

        response = self.client.post(
            "/teacher/submissions/1/grade",
            data={"score": "92", "comment": "结构清楚。"},
            follow_redirects=True,
        )
        self.assertIn("评分已保存".encode("utf-8"), response.data)

        response = self.client.get("/teacher/assignments/1/export")
        self.assertEqual(response.status_code, 200)
        self.assertIn("王同学".encode("utf-8"), response.data)

    def test_pending_teacher_cannot_login_before_approval(self):
        self.client.post(
            "/register",
            data={
                "username": "newteacher",
                "password": "teacher123",
                "name": "新教师",
                "role": "teacher",
            },
            follow_redirects=True,
        )
        response = self.login("newteacher", "teacher123")
        self.assertIn("等待管理员审核".encode("utf-8"), response.data)

        self.client.get("/logout")
        self.login("admin", "admin123")
        response = self.client.post("/admin/users/6/status/approved", follow_redirects=True)
        self.assertIn("用户状态已更新".encode("utf-8"), response.data)

    def test_invalid_assignment_course_id_shows_message(self):
        response = self.login("teacher01", "teacher123")
        self.assertIn("教师工作台".encode("utf-8"), response.data)

        response = self.client.post(
            "/teacher/assignments",
            data={
                "course_id": "abc",
                "title": "异常表单测试",
                "deadline": "2026-06-01T10:00",
                "description": "模拟表单课程编号异常",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("请选择有效课程".encode("utf-8"), response.data)

    def test_student_enroll_form_uses_post_and_submits(self):
        self.login("teacher01", "teacher123")
        self.client.post(
            "/teacher/courses",
            data={"name": "数据结构实训", "description": "用于测试学生选课。"},
            follow_redirects=True,
        )
        self.client.get("/logout")

        response = self.login("student01", "student123")
        self.assertIn(b'action="/student/courses/2/enroll"', response.data)
        self.assertIn(b'method="post"', response.data)

        response = self.client.post("/student/courses/2/enroll", follow_redirects=True)
        self.assertIn("选课成功".encode("utf-8"), response.data)
        self.assertIn("数据结构实训".encode("utf-8"), response.data)

    def test_chinese_upload_filename_is_preserved(self):
        self.login("student01", "student123")
        response = self.client.post(
            "/student/assignments/1/submit",
            data={
                "content": "上传中文文件名附件。",
                "file": (io.BytesIO("测试内容".encode("utf-8")), "数据库练习报告.docx"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertIn("作业已提交".encode("utf-8"), response.data)

        self.client.get("/logout")
        self.login("teacher01", "teacher123")
        response = self.client.get("/teacher/assignments/1")
        self.assertIn("数据库练习报告.docx".encode("utf-8"), response.data)

        response = self.client.get("/teacher/submissions/1/download")
        self.assertEqual(response.status_code, 200)
        self.assertIn("%E6%95%B0%E6%8D%AE%E5%BA%93", response.headers["Content-Disposition"])
        response.close()


if __name__ == "__main__":
    unittest.main()

