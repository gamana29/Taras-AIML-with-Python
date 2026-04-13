import cv2
import pygame
import time
import os
import pywhatkit as kit
import sys
#sys.stdout.reconfigure(encoding='utf-8')


# Initialize Pygame for alarm sound
pygame.mixer.init()

# Set up constants
ALARM_SOUND = "alarm1.wav"  # Replace with the path to your alarm sound file
VIDEO_FOLDER = "incident_videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# WhatsApp Configuration
RECIPIENTS = ["+917382444567"]  # Add recipient phone numbers with country code
ALERT_MESSAGE = "⚠️ Alert! Unusual activity detected on campus. Immediate action is required. Check the recorded video for details."

def play_alarm():
    """
    Plays the alarm sound.
    """
    try:
        pygame.mixer.music.load(ALARM_SOUND)
        pygame.mixer.music.play(-1)  # Loop the sound until stopped
    except Exception as e:
        print(f"Error playing sound: {e}")

def stop_alarm():
    """
    Stops the alarm sound.
    """
    pygame.mixer.music.stop()

def send_whatsapp_alert(video_path):
    """
    Sends a WhatsApp alert with the specified message using PyWhatKit.
    """
    for recipient in RECIPIENTS:
        try:
            print(f"Sending WhatsApp alert to {recipient}...")
            # Use sendwhatmsg_instantly to send a plain text message
            kit.sendwhatmsg_instantly(
                recipient,
                f"{ALERT_MESSAGE}\nVideo saved at: {os.path.abspath(video_path)}",
                wait_time=10,  # Optional: Adjust wait time before sending
            )
            print(f"WhatsApp alert sent to {recipient}.")
        except Exception as e:
            print(f"Failed to send WhatsApp alert to {recipient}: {e}")

def detect_motion(frame, prev_frame):
    """
    Detects significant motion by comparing the current frame with the previous frame.
    Returns True if significant motion is detected.
    """
    if prev_frame is None:
        return False

    # Convert frames to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Calculate absolute difference between current and previous frame
    diff = cv2.absdiff(gray_frame, gray_prev_frame)

    # Apply threshold to identify motion areas
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
 
    # Count non-zero pixels (motion intensity)
    motion_intensity = cv2.countNonZero(thresh)

    # Adjust this threshold based on your environment
    return motion_intensity > 50000

def start_surveillance(camera_index=0):
    """
    Starts the surveillance system using the specified camera index.
    """
    cap = cv2.VideoCapture(camera_index)
    prev_frame = None
    recording = False
    video_writer = None
    start_time = None
    alert_triggered = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for natural viewing
        frame = cv2.flip(frame, 1)

        # Detect motion
        motion_detected = detect_motion(frame, prev_frame)

        if motion_detected and not alert_triggered:
            # Start recording video if not already recording
            if not recording:
                print("⚠️ Incident detected: Starting video recording...")
                play_alarm()
                video_path = f"{VIDEO_FOLDER}/incident_{int(time.time())}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                video_writer = cv2.VideoWriter(video_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                start_time = time.time()
                recording = True

        if recording:
            video_writer.write(frame)
            # Stop recording after 10 seconds
            if time.time() - start_time >= 10:
                print("Recording completed. Sending alert...")
                video_writer.release()
                send_whatsapp_alert(video_path)
                alert_triggered = True
                recording = False
                stop_alarm()

        # Reset the alert after a cooldown period (30 seconds)
        if alert_triggered and time.time() - start_time >= 30:
            print("Resetting alert system...")
            alert_triggered = False

        # Display the video feed
        cv2.imshow("Surveillance System", frame)
        prev_frame = frame

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Starting Surveillance System...")
    start_surveillance()
