from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
import re

from .models import Student, Teacher, AttendanceSession, AttendanceRecord


# =========================================================
# USERNAME VALIDATION
# Only alphabets are allowed
# =========================================================

def validate_alphabetic_username(value):
    if not re.fullmatch(r"[A-Za-z]+", value):
        raise ValidationError(
            "Username must contain only alphabets (A-Z and a-z)."
        )


class AlphabeticUserCreationForm(UserCreationForm):

    username = forms.CharField(
        max_length=150,
        validators=[validate_alphabetic_username],
        help_text="Enter alphabets only. Numbers and special characters are not allowed.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)


class AlphabeticUserChangeForm(UserChangeForm):

    username = forms.CharField(
        max_length=150,
        validators=[validate_alphabetic_username],
        help_text="Enter alphabets only. Numbers and special characters are not allowed.",
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


# =========================================================
# CUSTOM DJANGO USER ADMIN
# =========================================================

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    add_form = AlphabeticUserCreationForm
    form = AlphabeticUserChangeForm

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


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