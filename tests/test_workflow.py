import tempfile
import unittest
from pathlib import Path

from assignment_system import create_app
from assignment_system.database import init_db


class WorkflowTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        db_path = Path(self.tmp.name) / "test.sqlite3"
        upload_path = Path(self.tmp.name) / "uploads"
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
        self.tmp.cleanup()

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


if __name__ == "__main__":
    unittest.main()

