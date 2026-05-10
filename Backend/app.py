import os
from flask import Flask, jsonify, render_template, Response
import cv2
import face_recognition
import pickle
from database import get_attendance, mark_attendance

# Path to the Frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Frontend'))

app = Flask(__name__, 
            template_folder=frontend_dir,
            static_folder=frontend_dir, 
            static_url_path='')

#for the face recognition code
print("[INFO] Loading encodings...")
with open("ai_module/encodings.pickle", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

present_students = set()

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

@app.route("/students")
def students():
    return render_template("students.html")

@app.route("/lookup")
def lookup():
    return render_template("lookup.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/timetable")
def timetable():
    return render_template("timetable.html")

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


#recognize_face.py face recognition code
def gen_frames():
    video = cv2.VideoCapture(0)

    while True:
        success, frame = video.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for (top, right, bottom, left), face_encoding in zip(faces, encodings):

            matches = face_recognition.compare_faces(known_encodings, face_encoding)

            name = "Unknown"

            if True in matches:
                index = matches.index(True)
                name = known_names[index]

                if name not in present_students:
                    print(f"{name} detected")
                    present_students.add(name)

                    
                    mark_attendance(name)

            #drawing the box
            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, name, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        # convert frame → stream
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)