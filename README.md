# securitycamera
Set of scripts for motion detection and a DIY security camera on PC and Raspberry Pi

The setup and usage are described in detail in this video: https://youtu.be/Jb_5d0TSlAw

To help support this software and other open-source projects, please consider subscribing to my YouTube channel: https://www.youtube.com/@jeoresearch

---

## Features
- Detects motion using OpenCV.
- Sends email notifications with images attached when motion is detected.
- Configurable cooldown period between email alerts.
- Compatible with the Raspberry Pi Camera Module and USB webcams.

---

## Requirements
- Raspberry Pi (with camera module or USB webcam)
- Python 3
- Libraries:
  - `opencv-python`
  - `numpy`
  - `smtplib`
  - `picamera2` (for Raspberry Pi Camera Module)

Install the required dependencies:
```bash
sudo apt update
sudo apt install -y python3-opencv python3-numpy python3-picamera2
```

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/SecurityCamPi.git
   cd SecurityCamPi
   ```

2. Ensure the script is executable:
   ```bash
   chmod +x SecurityCamPi.py
   ```

3. Test the script:
   ```bash
   python3 SecurityCamPi.py
   ```

---

## Usage
- Edit the script `SecurityCamPi.py` to configure email details:
  ```python
  sender_email = "your_new_email@gmail.com"  # Replace with the new email (for sending from Pi)
  receiver_email = "your_main_email@gmail.com"  # Replace with your email (for receving images)
  password = "aaaabbbbccccdddd"  # Replace with your app password
  ```

- Run the script manually:
  ```bash
  python3 SecurityCamPi.py
  ```

### Running at Startup
To configure the script to start at boot:
1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/SecurityCamPi.service
   ```
2. Add the following content and replace "user" in /home/user and User=user with your login:
   ```ini
   [Unit]
   Description=Motion Detection Script
   After=multi-user.target

   [Service]
   ExecStart=/usr/bin/python3 /home/user/SecurityCamPi.py
   WorkingDirectory=/home/user
   User=user
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable the service:
   ```bash
   sudo systemctl enable SecurityCamPi.service
   sudo systemctl start SecurityCamPi.service
   ```

---

## Configuration
- **Motion Sensitivity**:
  Adjust `min_movement_area` in the script to set the minimum size of detected objects:
  ```python
  min_movement_area = 500
  ```

- **Email Cooldown**:
  Set the cooldown period (in seconds) between email alerts:
  ```python
  email_cooldown = 20
  ```

- **Headless Mode**:
  To run without OpenCV windows, comment out the following lines in the script:
  ```python
  cv2.imshow("Webcam Feed", frame)
  cv2.imshow("PMOG Visualization", fgmask)
  ```

---

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
- [OpenCV](https://opencv.org/)
- [Picamera2](https://github.com/raspberrypi/picamera2)
