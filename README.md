# Pushup vault
This project is built for a YouTube video. It will use a Raspberry Pi camera to detect if someone is doing pushups.
When this is the case, and there are 10 pushups being done the vault will open automatically using the Servo.

## Hardware setup
This project requires a hardware setup, all of the lasercut files are open source and the part list is available below
the YouTube video (coming soon) so make sure to check it out.

## Get started with the software
- First install all of the required dependencies
- Change the code to the correct pins are used for your particular setup
- Run the `servoServer.py`
- Also run `detectPushup.py` in another shell
- Visit `http://{your-raspberry-pi}.local:4004/` and check out the control panel!