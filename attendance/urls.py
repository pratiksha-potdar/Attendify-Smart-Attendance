from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "student-login/",
        views.student_login,
        name="student_login",
    ),

    path(
        "teacher-login/",
        views.teacher_login,
        name="teacher_login",
    ),

    path(
        "teacher/sessions/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),

    path(
        "teacher/sessions/create/",
        views.create_attendance_session,
        name="create_attendance_session",
    ),

    path(
        "teacher/sessions/<int:session_id>/select/",
        views.select_attendance_session,
        name="select_attendance_session",
    ),

    path(
        "teacher/sessions/<int:session_id>/stop/",
        views.stop_attendance_session,
        name="stop_attendance_session",
    ),

    path(
        "teacher/sessions/<int:session_id>/report/",
        views.attendance_report,
        name="attendance_report",
    ),

    path(
        "teacher/logout/",
        views.teacher_logout,
        name="teacher_logout",
    ),

    path(
        "face-verification/",
        views.face_verification,
        name="face_verification",
    ),

    path(
        "face-verification/verify/",
        views.verify_face,
        name="verify_face",
    ),
]