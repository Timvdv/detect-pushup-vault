# Importing the Flask modules
from flask import Flask, render_template_string, request, jsonify
import RPi.GPIO as GPIO     # Importing the GPIO library
from time import sleep      # Import sleep module from time library
import requests

servo_pin = 4  # GPIO Pin where sero is connected
button_pin = 16  # GPIO Pin where sero is connected

# Define the Pin numbering type. Here we are using BCM type
GPIO.setmode(GPIO.BCM)

# define Servo Pin as output pin
GPIO.setup(servo_pin, GPIO.OUT)

# define button as input pin
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def button_callback(channel):
    print("pressed button")
    requests.get(url = "http://127.0.0.1:4003/api/12.5")

# Init the button event
GPIO.add_event_detect(button_pin,GPIO.RISING,callback=button_callback)

p = GPIO.PWM(servo_pin, 50)
p.start(0)
app = Flask(__name__)

TPL = '''
<html>
    <head><title>Web Page Controlled Servo</title></head>
    <body>
    <h2> Web Page to Control Servo</h2>
        <form method="POST" action="test">
            <h3> Use the slider to rotate servo  </h3>
            <p>Slider   <input type="range" min="1" max="12.5" name="slider" /> </p>
            <input type="submit" value="submit" />
        </form>
    </body>
</html>

'''

@app.route("/")
def home():
    return render_template_string(TPL)

@app.route("/api/<float:value>")
def api(value):
    # Change duty cycle
    p.ChangeDutyCycle(float(value))
    sleep(1)

    # Pause the servo
    p.ChangeDutyCycle(0)

    return jsonify(success=True)


@app.route("/test", methods=["POST"])
def test():
    # Get slider Values
    slider = request.form["slider"]
    # Change duty cycle
    p.ChangeDutyCycle(float(slider))
    sleep(1)
    # Pause the servo
    p.ChangeDutyCycle(0)
    return render_template_string(TPL)

# Run the app on the local development server
if __name__ == "__main__":
    app.run(port=4003)
