from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    name: str
    role: str
    status: str


@dataclass
class Course:
    id: int
    name: str
    description: str
    teacher_id: int


@dataclass
class Assignment:
    id: int
    course_id: int
    title: str
    description: str
    deadline: str


@dataclass
class Submission:
    id: int
    assignment_id: int
    student_id: int
    filename: str
    content: str
    score: float | None
    comment: str

