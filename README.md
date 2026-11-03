# Attendify – Smart Face Recognition Attendance System

Attendify is a Django-based attendance management system that uses face recognition technology to identify students and automatically mark their attendance.

## Features

- Face detection and recognition using OpenCV.
- Automatic attendance marking.
- Teacher login and dashboard.
- Create, select and manage attendance sessions.
- View attendance reports.
- Student and teacher management.
- Duplicate attendance prevention.

## Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Computer Vision:** OpenCV, YuNet, SFace
- **Model Format:** ONNX

## How It Works

1. Teacher logs into the system.
2. Teacher creates an attendance session.
3. Student stands in front of the camera.
4. System detects and verifies the registered face.
5. Attendance is marked automatically.
6. Teacher can view the attendance report.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/pratiksha-potdar/Attendify-Smart-Attendance.git
```

### 2. Open the project folder

```bash
cd Attendify-Smart-Attendance
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment (Windows)

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create an admin account

```bash
python manage.py createsuperuser
```

### 8. Run the application

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Important Notes

- This project is designed for local execution.
- Student face images and database files should remain private.
- The ONNX model files are required for face recognition.
- Student and teacher records must be configured before using the system.

## Future Enhancements

- Attendance analytics and statistics.
- Export attendance reports.
- Improved user interface.
- Additional face verification improvements.

## Author

**Pratiksha Potdar**

GitHub: [pratiksha-potdar](https://github.com/pratiksha-potdar)