"""
SmartPresence — Email Service (Brevo SMTP)

Handles three types of emails:
 1. Student reports  → individual attendance status after each class
 2. Teacher summaries → class attendance overview (present/absent counts)
 3. Error reports    → bugs/crashes → admin email
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def _get_smtp_config():
    """Load SMTP configuration from environment variables."""
    return {
        'server': os.environ.get('SMTP_SERVER', 'smtp-relay.brevo.com'),
        'port': int(os.environ.get('SMTP_PORT', 587)),
        'login': os.environ.get('SMTP_LOGIN', ''),
        'key': os.environ.get('SMTP_KEY', ''),
        'sender': os.environ.get('SMTP_SENDER', ''),
        'admin_email': os.environ.get('ADMIN_EMAIL', ''),
    }


def _send_email(to_email, subject, html_body):
    """Send a single email via SMTP. Returns (success: bool, error: str|None)."""
    cfg = _get_smtp_config()
    if not cfg['login'] or not cfg['key'] or not cfg['sender']:
        return False, "SMTP not configured (missing SMTP_LOGIN, SMTP_KEY, or SMTP_SENDER in .env)"

    if not to_email:
        return False, "No recipient email provided"

    msg = MIMEMultipart('alternative')
    msg['From'] = f"SmartPresence <{cfg['sender']}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(cfg['server'], cfg['port'], timeout=15) as server:
            server.starttls()
            server.login(cfg['login'], cfg['key'])
            server.send_message(msg)
        return True, None
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed — check SMTP_LOGIN and SMTP_KEY"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Email send failed: {str(e)}"


def send_test_email():
    """Send a test email to the admin address to verify SMTP configuration."""
    cfg = _get_smtp_config()
    if not cfg['admin_email']:
        return False, "ADMIN_EMAIL not set in .env"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
        <h2 style="color:#6C63FF;margin-top:0;">✅ SmartPresence Email Test</h2>
        <p>Your SMTP configuration is working correctly.</p>
        <p style="font-size:13px;color:#888;">Server: {cfg['server']}:{cfg['port']}<br>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """
    return _send_email(cfg['admin_email'], "SmartPresence — SMTP Test ✅", html)


def send_student_report(student_email, student_name, class_name, status, date_str):
    """Send individual attendance status to a student after class."""
    status_colors = {
        'Present': '#2ecc71', 'On Time': '#2ecc71', 'Late': '#f39c12',
        'Absent': '#e74c3c', 'Excused': '#888', 'Early Leave': '#3498db'
    }
    color = status_colors.get(status, '#888')
    emoji = '✅' if status in ('Present', 'On Time') else '⚠️' if status == 'Late' else '❌'

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:24px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
        <h2 style="color:#6C63FF;margin-top:0;">📋 Attendance Report</h2>
        <p>Hi <strong>{student_name}</strong>,</p>
        <p>Your attendance for <strong>{class_name}</strong> on <strong>{date_str}</strong>:</p>
        <div style="text-align:center;padding:16px;background:rgba(255,255,255,0.05);border-radius:8px;margin:16px 0;">
            <span style="font-size:32px;">{emoji}</span>
            <h3 style="color:{color};margin:8px 0 0;">{status}</h3>
        </div>
        <p style="font-size:13px;color:#888;">This is an automated message from SmartPresence.</p>
    </div>
    """
    return _send_email(student_email, f"Attendance: {status} — {class_name} ({date_str})", html)


def send_teacher_summary(teacher_email, class_name, date_str, present_list, absent_list):
    """Send class attendance summary to the teacher."""
    total = len(present_list) + len(absent_list)
    present_count = len(present_list)
    absent_count = len(absent_list)
    rate = round(present_count / total * 100, 1) if total > 0 else 0

    present_rows = ''.join(f'<li style="color:#2ecc71;">{name}</li>' for name in present_list) or '<li style="color:#888;">None</li>'
    absent_rows = ''.join(f'<li style="color:#e74c3c;">{name}</li>' for name in absent_list) or '<li style="color:#888;">None</li>'

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
        <h2 style="color:#6C63FF;margin-top:0;">📊 Class Report — {class_name}</h2>
        <p>Date: <strong>{date_str}</strong></p>

        <div style="display:flex;gap:12px;margin:16px 0;">
            <div style="flex:1;text-align:center;padding:12px;background:rgba(46,204,113,0.15);border-radius:8px;">
                <div style="font-size:28px;font-weight:bold;color:#2ecc71;">{present_count}</div>
                <div style="font-size:12px;color:#888;">Present</div>
            </div>
            <div style="flex:1;text-align:center;padding:12px;background:rgba(231,76,60,0.15);border-radius:8px;">
                <div style="font-size:28px;font-weight:bold;color:#e74c3c;">{absent_count}</div>
                <div style="font-size:12px;color:#888;">Absent</div>
            </div>
            <div style="flex:1;text-align:center;padding:12px;background:rgba(108,99,255,0.15);border-radius:8px;">
                <div style="font-size:28px;font-weight:bold;color:#6C63FF;">{rate}%</div>
                <div style="font-size:12px;color:#888;">Rate</div>
            </div>
        </div>

        <h4 style="color:#2ecc71;margin-bottom:4px;">✅ Present ({present_count})</h4>
        <ul style="margin-top:4px;">{present_rows}</ul>

        <h4 style="color:#e74c3c;margin-bottom:4px;">❌ Absent ({absent_count})</h4>
        <ul style="margin-top:4px;">{absent_rows}</ul>

        <p style="font-size:13px;color:#888;margin-top:16px;">SmartPresence — Automated Class Report</p>
    </div>
    """
    return _send_email(teacher_email, f"Class Report: {class_name} — {date_str} ({present_count}/{total} present)", html)


def send_error_report(error_title, error_details):
    """Send error/bug report to admin email."""
    cfg = _get_smtp_config()
    if not cfg['admin_email']:
        return False, "ADMIN_EMAIL not set"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
        <h2 style="color:#e74c3c;margin-top:0;">🐛 Error Report</h2>
        <p><strong>{error_title}</strong></p>
        <pre style="background:#0d0d1a;padding:12px;border-radius:8px;font-size:12px;overflow-x:auto;color:#ccc;">{error_details}</pre>
        <p style="font-size:13px;color:#888;">Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """
    return _send_email(cfg['admin_email'], f"SmartPresence Error: {error_title}", html)

def generate_and_send_class_report(schedule_id, db_path):
    """
    Generate and send attendance reports for a specific class schedule.
    Returns a status dict.
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get the schedule
    sched = conn.execute("SELECT * FROM class_schedules WHERE id = ?", (schedule_id,)).fetchone()
    if not sched:
        conn.close()
        return {"error": "Schedule not found"}

    class_name = sched['class_name']
    teacher_email = sched['teacher_email'] if 'teacher_email' in sched.keys() else ''
    today = datetime.now().strftime('%Y-%m-%d')

    # Get all attendance logs for today linked to this schedule
    logs = conn.execute("""
        SELECT al.*, s.name, s.email as student_email, s.student_id as sid
        FROM attendance_logs al
        JOIN students s ON al.student_id = s.id
        WHERE al.schedule_id = ? AND date(al.timestamp) = ?
    """, (schedule_id, today)).fetchall()

    # Get ALL enrolled students to determine who's absent
    all_students = conn.execute("SELECT id, name, email FROM students").fetchall()
    conn.close()

    # Build present/absent lists
    present_ids = set()
    present_list = []
    absent_list = []
    student_statuses = {}  # id -> (name, email, status)

    for log in logs:
        sid = log['student_id']
        present_ids.add(sid)
        status = log['status']
        student_statuses[sid] = (log['name'], log['student_email'], status)
        if status in ('Present', 'On Time', 'Late'):
            present_list.append(log['name'])
        else:
            absent_list.append(log['name'])

    # Students with no log at all = Absent
    for s in all_students:
        if s['id'] not in present_ids:
            absent_list.append(s['name'])
            student_statuses[s['id']] = (s['name'], s['email'], 'Absent')

    # Send individual student emails
    sent_count = 0
    fail_count = 0
    errors = []

    for sid, (name, email, status) in student_statuses.items():
        if email:
            ok, err = send_student_report(email, name, class_name, status, today)
            if ok:
                sent_count += 1
            else:
                fail_count += 1
                errors.append(f"{name}: {err}")

    # Send teacher summary
    teacher_sent = False
    if teacher_email:
        ok, err = send_teacher_summary(teacher_email, class_name, today, present_list, absent_list)
        teacher_sent = ok
        if not ok:
            errors.append(f"Teacher: {err}")

    # If any errors, send error report to admin
    if errors:
        send_error_report(
            f"Email Report Errors — {class_name}",
            '\n'.join(errors)
        )

    return {
        "success": True,
        "class_name": class_name,
        "date": today,
        "students_emailed": sent_count,
        "students_failed": fail_count,
        "teacher_emailed": teacher_sent,
        "present": len(present_list),
        "absent": len(absent_list)
    }
