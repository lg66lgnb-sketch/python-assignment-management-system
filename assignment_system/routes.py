from functools import wraps
from urllib.parse import quote

from flask import (
    Response,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from .database import get_db, init_db
from .services import (
    AssignmentService,
    CourseService,
    ReportService,
    SubmissionService,
    UserService,
)


def current_user():
    user_id = session.get("user_id")
    return UserService().get(user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("请先登录。")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                flash("请先登录。")
                return redirect(url_for("login"))
            if user["role"] not in roles:
                flash("当前账号没有访问该页面的权限。")
                return redirect(url_for("index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def register_routes(app):
    @app.context_processor
    def inject_common():
        return {
            "current_user": current_user(),
            "role_names": {
                "admin": "管理员",
                "teacher": "教师",
                "student": "学生",
            },
            "status_names": {
                "pending": "待审核",
                "approved": "正常",
                "disabled": "停用",
            },
        }

    @app.route("/")
    def index():
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        if user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))
        if user["role"] == "teacher":
            return redirect(url_for("teacher_dashboard"))
        return redirect(url_for("student_dashboard"))

    @app.route("/init-demo")
    def init_demo():
        init_db(seed=True)
        flash("演示数据库已初始化。")
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user, message = UserService().authenticate(
                request.form.get("username", ""),
                request.form.get("password", ""),
            )
            if user:
                session.clear()
                session["user_id"] = user["id"]
                flash(f"欢迎回来，{user['name']}。")
                return redirect(url_for("index"))
            flash(message)
        return render_template("auth/login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            name = request.form.get("name", "").strip()
            role = request.form.get("role", "student")
            if not username or not password or not name:
                flash("用户名、密码和姓名不能为空。")
                return render_template("auth/register.html")
            try:
                status = UserService().register(username, password, name, role)
                if status == "pending":
                    flash("教师账号已提交，请等待管理员审核。")
                else:
                    flash("注册成功，请登录。")
                return redirect(url_for("login"))
            except Exception:
                flash("注册失败，用户名可能已经存在。")
        return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("已退出登录。")
        return redirect(url_for("login"))

    @app.route("/admin")
    @role_required("admin")
    def admin_dashboard():
        users = UserService().list_users()
        counts = {
            "users": get_db().execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"],
            "courses": get_db().execute("SELECT COUNT(*) AS total FROM courses").fetchone()["total"],
            "assignments": get_db().execute("SELECT COUNT(*) AS total FROM assignments").fetchone()["total"],
            "submissions": get_db().execute("SELECT COUNT(*) AS total FROM submissions").fetchone()["total"],
        }
        return render_template("admin/dashboard.html", users=users, counts=counts)

    @app.post("/admin/users/<int:user_id>/status/<status>")
    @role_required("admin")
    def admin_set_user_status(user_id, status):
        if status not in {"approved", "disabled", "pending"}:
            flash("状态参数不正确。")
            return redirect(url_for("admin_dashboard"))
        user = UserService().get(user_id)
        if not user:
            flash("用户不存在。")
            return redirect(url_for("admin_dashboard"))
        if user["role"] == "admin" and user["id"] == session.get("user_id"):
            flash("不能停用当前登录的管理员账号。")
            return redirect(url_for("admin_dashboard"))
        UserService().set_status(user_id, status)
        flash("用户状态已更新。")
        return redirect(url_for("admin_dashboard"))

    @app.route("/teacher")
    @role_required("teacher")
    def teacher_dashboard():
        user = current_user()
        courses = CourseService().list_by_teacher(user["id"])
        assignments = AssignmentService().list_for_teacher(user["id"])
        return render_template("teacher/dashboard.html", courses=courses, assignments=assignments)

    @app.post("/teacher/courses")
    @role_required("teacher")
    def teacher_create_course():
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("课程名称不能为空。")
        else:
            CourseService().create(name, description, current_user()["id"])
            flash("课程已创建。")
        return redirect(url_for("teacher_dashboard"))

    @app.post("/teacher/assignments")
    @role_required("teacher")
    def teacher_create_assignment():
        try:
            course_id = int(request.form.get("course_id", 0))
        except (TypeError, ValueError):
            flash("请选择有效课程。")
            return redirect(url_for("teacher_dashboard"))
        if not CourseService().is_teacher_owner(course_id, current_user()["id"]):
            flash("只能给自己的课程布置作业。")
            return redirect(url_for("teacher_dashboard"))
        title = request.form.get("title", "").strip()
        deadline = request.form.get("deadline", "").replace("T", " ")
        description = request.form.get("description", "").strip()
        if not title or not deadline:
            flash("作业标题和截止时间不能为空。")
        else:
            AssignmentService().create(course_id, title, description, deadline)
            flash("作业已发布。")
        return redirect(url_for("teacher_dashboard"))

    @app.route("/teacher/assignments/<int:assignment_id>")
    @role_required("teacher")
    def teacher_assignment_detail(assignment_id):
        assignment = AssignmentService().get(assignment_id)
        if not assignment or assignment["teacher_id"] != current_user()["id"]:
            flash("无权查看该作业。")
            return redirect(url_for("teacher_dashboard"))
        submissions = SubmissionService().list_by_assignment(assignment_id)
        return render_template("teacher/assignment_detail.html", assignment=assignment, submissions=submissions)

    @app.post("/teacher/submissions/<int:submission_id>/grade")
    @role_required("teacher")
    def teacher_grade_submission(submission_id):
        submission = SubmissionService().get(submission_id)
        if not submission or submission["teacher_id"] != current_user()["id"]:
            flash("无权评分该提交。")
            return redirect(url_for("teacher_dashboard"))
        score = request.form.get("score", "")
        comment = request.form.get("comment", "")
        try:
            score_value = float(score)
            if score_value < 0 or score_value > 100:
                raise ValueError
            SubmissionService().grade(submission_id, score_value, comment)
            flash("评分已保存。")
        except ValueError:
            flash("成绩必须是 0 到 100 之间的数字。")
        return redirect(url_for("teacher_assignment_detail", assignment_id=submission["assignment_id"]))

    @app.route("/teacher/submissions/<int:submission_id>/download")
    @role_required("teacher")
    def teacher_download_submission(submission_id):
        submission = SubmissionService().get(submission_id)
        if not submission or submission["teacher_id"] != current_user()["id"]:
            flash("无权下载该文件。")
            return redirect(url_for("teacher_dashboard"))
        path = SubmissionService().file_path(submission)
        if not path:
            flash("该提交没有可下载文件。")
            return redirect(url_for("teacher_assignment_detail", assignment_id=submission["assignment_id"]))
        return send_file(path, as_attachment=True, download_name=submission["filename"])

    @app.route("/teacher/assignments/<int:assignment_id>/export")
    @role_required("teacher")
    def teacher_export_assignment(assignment_id):
        assignment = AssignmentService().get(assignment_id)
        if not assignment or assignment["teacher_id"] != current_user()["id"]:
            flash("无权导出该作业。")
            return redirect(url_for("teacher_dashboard"))
        csv_text = ReportService().assignment_csv(assignment_id)
        filename = f"作业提交统计-{assignment['title']}.csv"
        encoded_filename = quote(filename)
        return Response(
            csv_text,
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )

    @app.route("/student")
    @role_required("student")
    def student_dashboard():
        user = current_user()
        courses = CourseService().list_by_student(user["id"])
        all_courses = CourseService().list_all()
        assignments = AssignmentService().list_for_student(user["id"])
        enrolled_ids = {course["id"] for course in courses}
        return render_template(
            "student/dashboard.html",
            courses=courses,
            all_courses=all_courses,
            enrolled_ids=enrolled_ids,
            assignments=assignments,
        )

    @app.post("/student/courses/<int:course_id>/enroll")
    @role_required("student")
    def student_enroll_course(course_id):
        if not CourseService().get(course_id):
            flash("课程不存在。")
        else:
            CourseService().enroll(course_id, current_user()["id"])
            flash("选课成功。")
        return redirect(url_for("student_dashboard"))

    @app.route("/student/assignments/<int:assignment_id>/submit", methods=["GET", "POST"])
    @role_required("student")
    def student_submit_assignment(assignment_id):
        assignment = AssignmentService().get(assignment_id)
        user = current_user()
        allowed = any(row["id"] == assignment["course_id"] for row in CourseService().list_by_student(user["id"])) if assignment else False
        if not assignment or not allowed:
            flash("请先加入课程后再提交作业。")
            return redirect(url_for("student_dashboard"))
        if request.method == "POST":
            content = request.form.get("content", "")
            file_storage = request.files.get("file")
            if not content.strip() and not (file_storage and file_storage.filename):
                flash("请填写说明或上传文件。")
            else:
                SubmissionService().save(assignment_id, user["id"], content, file_storage)
                flash("作业已提交。")
                return redirect(url_for("student_dashboard"))
        return render_template("student/submit.html", assignment=assignment)
