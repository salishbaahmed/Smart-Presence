import sqlite3
from datetime import datetime



# ----------------------------------------
# DATABASE CREATION
# ----------------------------------------

def create_database():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        face_id TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

create_database()



# ----------------------------------------
# FUNCTIONS IMPLEMENTATION
# ----------------------------------------


# Add student
def add_student(name, face_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO students (name, face_id) VALUES (?, ?)", (name, face_id))

    conn.commit()
    conn.close()

# Test add student function
add_student("Ali", "ali_01")
add_student("Sara", "sara_01")

def get_students():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()
    return students

# Test Get students function
print(get_students())






# ----------------------------------------
# ATTENDANCE FUNCTIONS IMPLEMENTATION
# ----------------------------------------


# Create Attendance
def mark_attendance(student_name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    SELECT * FROM attendance
    WHERE student_name=? AND date=?
    """, (student_name, current_date))

    existing = cursor.fetchone()

    if not existing:
        cursor.execute("""
        INSERT INTO attendance (student_name, date, time, status)
        VALUES (?, ?, ?, ?)
        """, (student_name, current_date, current_time, "Present"))

    conn.commit()
    conn.close()


# Test mark attendance function
mark_attendance("Ali")
mark_attendance("Sara")



# Get Attendance List
def get_attendance():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    records = cursor.fetchall()

    conn.close()
    return records

# Test Get Attendance List function
print("\nAttendance List: ", get_attendance())


