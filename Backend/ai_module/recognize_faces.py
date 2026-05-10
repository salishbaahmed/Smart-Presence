import cv2
import face_recognition
import pickle

print("[INFO] Loading encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

video = cv2.VideoCapture(0)

present_students = set()

while True:
    ret, frame = video.read()
    if not ret:
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

            # prevent duplicate detection
            if name not in present_students:
                print(f"{name} detected")
                present_students.add(name)

        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, name, (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Recognition", frame)

    key = cv2.waitKey(1)
    
    if key == 27:  
        break
video.release()
cv2.destroyAllWindows()