import cv2
import os
import time
import numpy as np

dataset = "dataset"

images = []
labels = []
names = {}
id = 0

# Load dataset
for person in os.listdir(dataset):

    names[id] = person
    path = os.path.join(dataset, person)

    for img_name in os.listdir(path):

        img_path = os.path.join(path, img_name)

        img = cv2.imread(img_path,0)

        if img is None:
            continue

        img = cv2.resize(img,(130,100))

        images.append(img)
        labels.append(id)

    id += 1

images = np.array(images)
labels = np.array(labels)

# Train recognizer
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# Load face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cam = cv2.VideoCapture(0)

last_seen = time.time()
away_time = 5   # seconds before locking

while True:

    ret, frame = cam.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray,1.3,5)

    recognized = False

    for (x,y,w,h) in faces:

        face = gray[y:y+h,x:x+w]
        face = cv2.resize(face,(130,100))

        label,confidence = model.predict(face)

        if confidence < 80:

            recognized = True
            name = names[label]

            cv2.putText(frame,name,(x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,(0,255,0),2)

            last_seen = time.time()

        else:

            cv2.putText(frame,"Unknown",(x,y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,(0,0,255),2)

        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    if not recognized:

        if time.time() - last_seen > away_time:

            cam.release()
            cv2.destroyAllWindows()

            os.system("rundll32.exe user32.dll,LockWorkStation")
            break

    cv2.imshow("Laptop Face Security", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()
