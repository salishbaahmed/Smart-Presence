import os
from flask import Flask, jsonify, render_template
from database import get_attendance, mark_attendance

# Path to the Frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Frontend'))

app = Flask(__name__, 
            template_folder=frontend_dir,
            static_folder=frontend_dir, 
            static_url_path='/static')


# To test: http://127.0.0.1:5000/
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# To test: http://127.0.0.1:5000/enroll
@app.route("/enroll")
def enroll():
    return render_template("enroll.html")

# To test: http://127.0.0.1:5000/live
@app.route("/live")
def live():
    return render_template("live.html")

# To test: http://127.0.0.1:5000/mark/Ali
@app.route("/mark/<name>")
def mark(name):
    mark_attendance(name)
    return f"{name} marked present"

# To test: http://127.0.0.1:5000/api/attendance
@app.route("/api/attendance")
def attendance():
    # Format the data into what the frontend expects
    records = get_attendance()
    result = []
    for r in records:
        # Expected tuple format from database.py: (id, name, date, time, status)
        result.append({
            'id': r[0],
            'name': r[1],
            'timestamp': f"{r[2]} {r[3]}",
            'status': r[4],
            'source': 'auto' # placeholder since database schema lacks this
        })
    return jsonify(result)

@app.route("/api/stats")
def stats():
    records = get_attendance()
    total = len(records)
    # Just mock up some stats for the dashboard
    return jsonify({
        "total_students": len(set(r[1] for r in records)) if records else 0,
        "present_today": total,
        "absent_today": 0,
        "total_logs": total
    })

# Dummy endpoint so systemIndicator JS doesn't fail
@app.route("/api/system/status")
def system_status():
    return jsonify({
        "ai_running": True, 
        "system_mode": "auto", 
        "active_schedule": {"class_name": "CS-101"}
    })

if __name__ == "__main__":
    app.run(debug=True)