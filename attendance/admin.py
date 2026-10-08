from django.contrib import admin
from .models import Student, Teacher, AttendanceSession, AttendanceRecord


# =========================================================
# STUDENT ADMIN
# =========================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_id",
        "name",
        "email",
        "face_registered",
        "face_image",
    )

    search_fields = (
        "student_id",
        "name",
        "email",
    )

    list_filter = (
        "face_registered",
    )


# =========================================================
# TEACHER ADMIN
# =========================================================

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        "teacher_id",
        "name",
        "email",
        "user",
    )

    search_fields = (
        "teacher_id",
        "name",
        "email",
        "user__username",
    )


# =========================================================
# ATTENDANCE SESSION ADMIN
# =========================================================

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):

    list_display = (
        "subject",
        "teacher",
        "date",
        "is_active",
    )

    list_filter = (
        "is_active",
        "date",
        "teacher",
    )

    search_fields = (
        "subject",
        "teacher__name",
        "teacher__teacher_id",
    )

    fields = (
        "subject",
        "teacher",
        "date",
        "is_active",
    )

    readonly_fields = (
        "date",
    )


# =========================================================
# ATTENDANCE RECORD ADMIN
# =========================================================

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "session",
        "marked_at",
        "face_verified",
    )

    list_filter = (
        "face_verified",
        "session",
        "marked_at",
    )

    search_fields = (
        "student__student_id",
        "student__name",
        "session__subject",
    )

    readonly_fields = (
        "marked_at",
    )