from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    face_registered = models.BooleanField(default=False)
    face_image = models.ImageField(upload_to="student_faces/", null=True, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_profile",
    )
    teacher_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.teacher_id} - {self.name}"


class AttendanceSession(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendance_sessions",
    )
    subject = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    # Retained temporarily for existing database rows.
    # QR code functionality is not used.
    qr_code = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject} - {self.date}"


class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    marked_at = models.DateTimeField(auto_now_add=True)
    face_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'session')

    def __str__(self):
        return f"{self.student.name} - {self.session.subject}"
