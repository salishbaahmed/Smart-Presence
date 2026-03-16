from flask import Flask, jsonify
from database import get_attendance, mark_attendance

app = Flask(__name__)

# To test: http://127.0.0.1:5000/mark/Ali
@app.route("/mark/<name>")
def mark(name):
    mark_attendance(name)
    return f"{name} marked present"

# To test: http://127.0.0.1:5000/attendance
@app.route("/attendance")
def attendance():
    return jsonify(get_attendance())

if __name__ == "__main__":
    app.run(debug=True)