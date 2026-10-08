import cv2
import numpy as np

from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

from pathlib import Path

from .models import AttendanceRecord, AttendanceSession, Student, Teacher


# =========================================================
# FACE RECOGNITION SETTINGS
# =========================================================

FACE_MATCH_THRESHOLD = 0.50


# =========================================================
# HOME
# =========================================================

def home(request):
    return render(
        request,
        "attendance/home.html"
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

def student_login(request):
    return render(
        request,
        "attendance/student_login.html"
    )


# =========================================================
# FACE ATTENDANCE PAGE
# =========================================================

def face_verification(request):

    active_session = AttendanceSession.objects.filter(
        is_active=True
    ).first()

    # Check whether the currently logged-in user
    # is a teacher.

    is_teacher = (
        request.user.is_authenticated
        and Teacher.objects.filter(
            user=request.user
        ).exists()
    )

    return render(
        request,
        "attendance/face_verification.html",
        {
            "active_session": active_session,
            "is_teacher": is_teacher,
        },
    )


# =========================================================
# TEACHER LOGIN
# =========================================================

def teacher_login(request):

    if (
        request.user.is_authenticated
        and Teacher.objects.filter(
            user=request.user
        ).exists()
    ):
        return redirect(
            "teacher_dashboard"
        )

    error = None

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        )

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if (
            user is not None
            and Teacher.objects.filter(
                user=user
            ).exists()
        ):

            login(
                request,
                user
            )

            return redirect(
                "teacher_dashboard"
            )

        error = "Invalid username or password."

    return render(
        request,
        "attendance/teacher_login.html",
        {
            "error": error
        },
    )


# =========================================================
# CHECK TEACHER
# =========================================================

def _is_teacher(user):

    return (
        user.is_authenticated
        and Teacher.objects.filter(
            user=user
        ).exists()
    )


teacher_required = user_passes_test(
    _is_teacher,
    login_url="teacher_login"
)


# =========================================================
# TEACHER DASHBOARD
# =========================================================

@teacher_required
def teacher_dashboard(request):

    teacher = request.user.teacher_profile

    sessions = AttendanceSession.objects.filter(
        teacher=teacher
    ).order_by(
        "-date",
        "-id"
    )

    return render(
        request,
        "attendance/teacher_dashboard.html",
        {
            "sessions": sessions,
            "teacher": teacher,
        },
    )


# =========================================================
# CREATE ATTENDANCE SESSION
# =========================================================

@teacher_required
@require_POST
def create_attendance_session(request):

    teacher = request.user.teacher_profile

    subject = request.POST.get(
        "subject",
        ""
    ).strip()

    if subject:

        AttendanceSession.objects.create(
            teacher=teacher,
            subject=subject,
            is_active=False,
        )

    return redirect(
        "teacher_dashboard"
    )


# =========================================================
# STOP ATTENDANCE
# =========================================================

@teacher_required
@require_POST
def stop_attendance_session(
    request,
    session_id
):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        pk=session_id,
        teacher=teacher,
    )

    session.is_active = False

    session.save(
        update_fields=[
            "is_active"
        ]
    )

    # After stopping attendance,
    # directly open the attendance report.

    return redirect(
        "attendance_report",
        session_id=session.id
    )


# =========================================================
# START / SELECT ATTENDANCE SESSION
# =========================================================

@teacher_required
@require_POST
def select_attendance_session(
    request,
    session_id
):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        pk=session_id,
        teacher=teacher,
    )

    with transaction.atomic():

        # Only one attendance session can be active
        # at a time.

        AttendanceSession.objects.filter(
            is_active=True
        ).exclude(
            pk=session.pk
        ).update(
            is_active=False
        )

        session.is_active = True

        session.save(
            update_fields=[
                "is_active"
            ]
        )

    # Open the face attendance page
    # after starting the session.

    return redirect(
        "face_verification"
    )


# =========================================================
# ATTENDANCE REPORT
# =========================================================

@teacher_required
def attendance_report(
    request,
    session_id
):

    teacher = request.user.teacher_profile

    session = get_object_or_404(
        AttendanceSession,
        pk=session_id,
        teacher=teacher,
    )

    # Get all students registered in the system.

    all_students = Student.objects.all().order_by(
        "student_id"
    )

    # Get attendance records for this session.

    attendance_records = AttendanceRecord.objects.filter(
        session=session
    ).select_related(
        "student"
    )

    # Create a dictionary:
    # student database ID -> attendance record

    record_map = {
        record.student_id: record
        for record in attendance_records
    }

    student_report = []

    present_count = 0
    absent_count = 0

    for student in all_students:

        record = record_map.get(
            student.id
        )

        if record:

            present_count += 1

            student_report.append(
                {
                    "student": student,
                    "status": "Present",
                    "record": record,
                }
            )

        else:

            absent_count += 1

            student_report.append(
                {
                    "student": student,
                    "status": "Absent",
                    "record": None,
                }
            )

    return render(
        request,
        "attendance/attendance_report.html",
        {
            "session": session,
            "student_report": student_report,
            "total_students": len(student_report),
            "present_count": present_count,
            "absent_count": absent_count,
        },
    )


# =========================================================
# TEACHER LOGOUT
# =========================================================

@teacher_required
@require_POST
def teacher_logout(request):

    logout(request)

    return redirect(
        "home"
    )


# =========================================================
# IMAGE READING
# =========================================================

def _read_image(image_bytes):

    image = cv2.imdecode(
        np.frombuffer(
            image_bytes,
            dtype=np.uint8
        ),
        cv2.IMREAD_COLOR
    )

    if image is None or image.size == 0:

        raise ValueError(
            "The image could not be read."
        )

    return image


# =========================================================
# DETECT ONE FACE
# =========================================================

def _single_face(
    detector,
    image
):

    height, width = image.shape[:2]

    detector.setInputSize(
        (width, height)
    )

    _, faces = detector.detect(
        image
    )

    count = (
        0
        if faces is None
        else len(faces)
    )

    if count == 0:

        raise LookupError(
            "No face was detected."
        )

    if count > 1:

        raise LookupError(
            "More than one face was detected."
        )

    return faces[0]


# =========================================================
# CREATE FACE FEATURE
# =========================================================

def _get_face_feature(
    detector,
    recognizer,
    image
):

    face = _single_face(
        detector,
        image
    )

    aligned = recognizer.alignCrop(
        image,
        face
    )

    feature = recognizer.feature(
        aligned
    )

    return feature


# =========================================================
# FACE VERIFICATION / ATTENDANCE
# =========================================================

@require_POST
def verify_face(request):

    def response(
        status,
        message,
        http_status=200,
        extra=None
    ):

        data = {
            "status": status,
            "message": message,
        }

        if extra:
            data.update(extra)

        return JsonResponse(
            data,
            status=http_status
        )

    # -----------------------------------------------------
    # CHECK ACTIVE SESSION
    # -----------------------------------------------------

    active_sessions = list(
        AttendanceSession.objects.filter(
            is_active=True
        )[:2]
    )

    if not active_sessions:

        return response(
            "error",
            "Attendance is not active. Please ask the teacher to start an attendance session.",
            400
        )

    if len(active_sessions) > 1:

        return response(
            "error",
            "More than one attendance session is active. Please contact the teacher.",
            400
        )

    active_session = active_sessions[0]


    # -----------------------------------------------------
    # GET CAMERA IMAGE
    # -----------------------------------------------------

    capture = request.FILES.get(
        "image"
    )

    if capture is None or capture.size == 0:

        return response(
            "error",
            "Camera image is missing. Please try again.",
            400
        )

    if capture.size > 10 * 1024 * 1024:

        return response(
            "error",
            "Captured image is too large. Please try again.",
            400
        )


    # -----------------------------------------------------
    # LOAD FACE MODELS
    # -----------------------------------------------------

    try:

        models_dir = (
            Path(settings.BASE_DIR)
            / "models"
        )

        yunet_path = (
            models_dir
            / "face_detection_yunet_2023mar.onnx"
        )

        sface_path = (
            models_dir
            / "face_recognition_sface_2021dec.onnx"
        )

        if (
            not yunet_path.is_file()
            or not sface_path.is_file()
        ):

            return response(
                "error",
                "Face recognition models are missing on the server.",
                500
            )

        detector = cv2.FaceDetectorYN_create(
            str(yunet_path),
            "",
            (320, 320)
        )

        recognizer = cv2.FaceRecognizerSF_create(
            str(sface_path),
            ""
        )

        if (
            detector is None
            or recognizer is None
        ):

            return response(
                "error",
                "Face recognition models could not be loaded.",
                500
            )


        # -------------------------------------------------
        # READ LIVE CAMERA IMAGE
        # -------------------------------------------------

        captured_image = _read_image(
            capture.read()
        )

        captured_feature = _get_face_feature(
            detector,
            recognizer,
            captured_image
        )


    except LookupError as exc:

        return response(
            "error",
            str(exc),
            400
        )

    except (
        OSError,
        ValueError,
        cv2.error
    ):

        return response(
            "error",
            "The camera image or face model could not be read.",
            500
        )

    except Exception:

        return response(
            "error",
            "Face verification could not be completed. Please try again.",
            500
        )


    # -----------------------------------------------------
    # FIND MATCHING REGISTERED STUDENT
    # -----------------------------------------------------

    best_student = None
    best_similarity = -1.0

    students = Student.objects.filter(
        face_registered=True
    ).exclude(
        face_image=""
    )

    for student in students:

        if not student.face_image:
            continue

        try:

            with student.face_image.open(
                "rb"
            ) as registered_file:

                registered_image = _read_image(
                    registered_file.read()
                )

            registered_feature = _get_face_feature(
                detector,
                recognizer,
                registered_image
            )

            similarity = float(
                recognizer.match(
                    captured_feature,
                    registered_feature,
                    cv2.FaceRecognizerSF_FR_COSINE
                )
            )

            if similarity > best_similarity:

                best_similarity = similarity
                best_student = student

        except Exception:

            # If one student's registered image is
            # damaged or invalid, continue checking
            # the other students.

            continue


    # -----------------------------------------------------
    # NO MATCH
    # -----------------------------------------------------

    if (
        best_student is None
        or best_similarity < FACE_MATCH_THRESHOLD
    ):

        return response(
            "no_match",
            "Face not recognized. Please look directly at the camera and try again.",
            extra={
                "similarity": round(
                    best_similarity,
                    2
                )
            }
        )


    # -----------------------------------------------------
    # MATCH FOUND
    # -----------------------------------------------------

    student = best_student


    # -----------------------------------------------------
    # MARK ATTENDANCE
    # -----------------------------------------------------

    record, created = AttendanceRecord.objects.get_or_create(
        student=student,
        session=active_session,
        defaults={
            "face_verified": True
        }
    )


    # -----------------------------------------------------
    # ALREADY MARKED
    # -----------------------------------------------------

    if not created:

        return response(
            "attendance_already_recorded",
            "Attendance was already marked for this student.",
            extra={
                "student_name": student.name,
                "student_id": student.student_id,
                "subject": active_session.subject,
                "marked_at": timezone.localtime(
                    record.marked_at
                ).strftime(
                    "%d %b %Y, %I:%M %p"
                ),
                "similarity": round(
                    best_similarity,
                    2
                )
            }
        )


    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    return response(
        "attendance_recorded",
        "Attendance marked successfully!",
        extra={
            "student_name": student.name,
            "student_id": student.student_id,
            "subject": active_session.subject,
            "marked_at": timezone.localtime(
                record.marked_at
            ).strftime(
                "%d %b %Y, %I:%M %p"
            ),
            "similarity": round(
                best_similarity,
                2
            )
        }
    )