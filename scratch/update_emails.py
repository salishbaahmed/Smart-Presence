import sqlite3
import os

db_path = r'd:\SmartPresence-main\SmartPresence-main\web_app\database\attendance.db'
conn = sqlite3.connect(db_path)
conn.execute("UPDATE class_schedules SET teacher_email = 'salishbaahmed@gmail.com'")
conn.commit()
conn.close()
print("Teacher emails updated successfully.")
