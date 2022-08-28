#!/usr/bin/env python
import cv2
import mediapipe as mp
import numpy as np
from time import sleep
from display_opts import get_device
from luma.core.render import canvas
from pathlib import Path
from PIL import ImageFont
from luma.core.interface.serial import spi
from luma.oled.device import ssd1306
from flask import Flask, render_template, Response
import requests

app = Flask(__name__, template_folder='public')
app.config["DEBUG"] = True

buttonPIN = 36
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
serial = spi(device=0, port=0)
device = ssd1306(serial)

# Global variables
counter = 0
maxPushups = 10
stage = None
title = ""
amount = ""

@app.route('/', methods=['GET'])
def home():
    print("Rendering home page...")
    return render_template('index.html')

@app.route('/video')
def video():
    # Video feed
    cap = cv2.VideoCapture(0)

    cap.release()
    cv2.destroyAllWindows()

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
    cap.set(cv2.CAP_PROP_FPS, 5)

    return Response(detectPushup(cap), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/open', methods=['GET'])
def open():
    requests.get(url = "http://127.0.0.1:4003/api/1.1")
    return "<p>Opening vault</p>"

@app.route('/close', methods=['GET'])
def close():
    requests.get(url = "http://127.0.0.1:4003/api/12.5")

    return "<p>Closing vault</p>"

@app.route('/reset', methods=['GET'])
def reset():
    global counter
    global stage
    global title
    global amount

    stage = None
    counter = 0
    title =  ""
    amount = ""

    requests.get(url = "http://127.0.0.1:4003/api/1.1")

    return "<p>Reset vault</p>"

# Logic to calculate angle
def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle

# create a font for the hardware display
def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)

font = make_font("code2000.ttf", 24)

def detectPushup(cap):
    global counter
    global maxPushups
    global stage
    global title
    global amount
    global font

    # Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()

            # Get the video props
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH )
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT )

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # image = cv2.flip(image, 1) # mirrors the image if needed
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract the landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates for shoulder angle
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                # Get coordinates for feet to leg angle
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                foot = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

                # Calculate angle
                angleTop = calculate_angle(shoulder, elbow, wrist)
                angleBottom = calculate_angle(ankle, foot, hip)

                cv2.putText(image, str(angleTop),
                            tuple(np.multiply(elbow, [width, height]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA
                                    )

                cv2.putText(image, str(angleBottom),
                            tuple(np.multiply(ankle, [width, height]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA
                                    )

                if stage is None and angleTop > 140 and angleBottom < 50:
                    stage = "up"

                # Detecting the angle for a pushup
                # if angleTop < 100 and angleBottom > 55:
                if angleTop < 100:
                    stage = "down"
                # if angleTop > 140 and angleBottom < 50 and stage =='down':
                if angleTop > 140 and stage =='down':
                    stage="up"
                    # servo = float(12.5 - (((counter / maxPushups) * 10) + 2.5))
                    # print(servo)
                    # requests.get(url = "http://127.0.0.1:4003/api/" + str(servo))
                    counter += 1

                if counter == maxPushups:
                    stage = "complete"
                    requests.get(url = "http://127.0.0.1:4003/api/1.1")
                    sleep(1)

                title = 'PUSHUP COUNTER'
                amount = str(counter)

                # get boundary of this text
                titleSize = cv2.getTextSize(title + ' - ' + str(stage), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                contentSize = cv2.getTextSize(amount, cv2.FONT_HERSHEY_SIMPLEX, 2, 2)[0]

                # get coords based on boundary
                titleX =  int( (width / 2) - (titleSize[0] / 2) ) - 20
                titleY = 22
                contentX =  int( (width) - (contentSize[0] / 2 ) ) - 30
                contentY = 25

                # Some nice visuals for debugging
                # cv2.rectangle(image, ( int(width / 2) - 200 , 40 ), ( int(width / 2) + 200 , 170 ), (0,0,0), -1 )

                cv2.putText(image, title + ' - ' + str(stage), ( titleX , titleY ),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)

                cv2.putText(image, str(counter),
                            ( contentX , contentY ),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2, cv2.LINE_AA)
            except:
                pass

            # Render detections (debug)
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )

            # create visuals for display
            with canvas(device) as draw:
                draw.rectangle(device.bounding_box, outline="white", fill="black")

                if (stage is None):
                    positionText = "Get into position"
                    sizePosition = draw.textsize(positionText)

                    positionContentX = (device.width - sizePosition[0]) / 2
                    positionContentY = (device.height - sizePosition[1]) / 2

                    draw.text((positionContentX, positionContentY), positionText, fill="white", align="center")
                elif (stage is "complete"):
                    positionText = "Great job!"
                    sizePosition = draw.textsize(positionText)

                    positionContentX = (device.width - sizePosition[0]) / 2
                    positionContentY = (device.height - sizePosition[1]) / 2

                    draw.text((positionContentX, positionContentY), positionText, fill="white", align="center")
                else:
                    sizeTitle = draw.textsize(title)
                    sizeContent = draw.textsize(amount)

                    leftTitle = (device.width - sizeTitle[0]) / 2
                    leftContent = (device.width - (sizeContent[0]) - 10 ) / 2

                    draw.text((leftTitle, 10), title, fill="white", align="center")
                    draw.text((leftContent, 25), amount, fill="white", font=font, align="center")

            # Enable this if you want to see the visuals for debugging
            # cv2.imshow('Mediapipe Feed', image)
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

            if cv2.waitKey(10) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                break

            if counter == maxPushups:
                cap.release()
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4004, debug=True)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()