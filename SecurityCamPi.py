import cv2
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from picamera2 import Picamera2

# Email details
sender_email = "your_new_email@gmail.com"  # Replace with the new email (for sending from Pi)
receiver_email = "your_main_email@gmail.com"  # Replace with your email (for receving images)
password = "aaaabbbbccccdddd"  # Replace with your app password

# Initialize Picamera2
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()

# Initialize background subtractor with custom PMOG parameters
fgbg = cv2.createBackgroundSubtractorMOG2(history=80, varThreshold=5, detectShadows=False)

# Movement sensitivity
min_movement_area = 500  # Minimum area to detect motion

# Time tracking for consistent motion and email rate-limiting
motion_start_time = None  # Start time of motion
motion_duration_threshold = 0.3  # Seconds of consistent motion required
last_email_time = 0  # Last time an email was sent
email_cooldown = 20  # Minimum time (in seconds) between emails


def send_email(image):
    """Send an email with the attached image."""
    try:
        # Encode the frame as a JPEG for emailing
        _, encoded_image = cv2.imencode('.jpg', image)
        image_bytes = encoded_image.tobytes()

        # Email content
        subject = "Motion Detected"
        body = "Motion has been detected. See the attached image for details."
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Create a MIMEBase object for the in-memory image attachment
        mime_base = MIMEBase("application", "octet-stream")
        mime_base.set_payload(image_bytes)
        encoders.encode_base64(mime_base)
        mime_base.add_header(
            "Content-Disposition",
            "attachment; filename=motion_detected.jpg"
        )
        message.attach(mime_base)

        # Connect to Gmail SMTP server and send email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)  # Use the app password here
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully with motion-detected image!")
    except Exception as e:
        print(f"Failed to send email: {e}")


while True:
    # Capture the frame from Picamera2
    frame = picam2.capture_array()
    frame = cv2.cvtColor(picam2.capture_array(), cv2.COLOR_RGBA2BGR)

    # Apply background subtraction
    fgmask = fgbg.apply(frame)

    # Threshold the mask to remove shadows
    _, thresh = cv2.threshold(fgmask, 245, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables to hold the bounds of the encompassing box
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), float('-inf'), float('-inf')

    # Flag to determine if motion is detected
    motion_detected = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_movement_area:
            motion_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)

    # Check for consistent motion over time
    if motion_detected:
        if motion_start_time is None:
            motion_start_time = time.time()  # Record the start time of motion
        elif time.time() - motion_start_time >= motion_duration_threshold:
            # If motion has been consistent for the threshold duration
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(frame, "Motion Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)

            # Send an email if the cooldown period has elapsed
            current_time = time.time()
            if current_time - last_email_time >= email_cooldown:
                send_email(frame)
                last_email_time = current_time  # Update the last email sent time
    else:
        motion_start_time = None  # Reset the motion start time if no motion

    # Gradually increase the minimum movement area requirement
    min_movement_area += 1  # Increase sensitivity requirement over time

    # Display the original frame with bounding boxes
    cv2.imshow("Webcam Feed", frame)

    # Display the PMOG result for visualization
    cv2.imshow("PMOG Visualization", fgmask)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the camera and release resources
picam2.stop()
cv2.destroyAllWindows()
