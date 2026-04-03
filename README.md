# Discord-CustomJoinNotification
Discord Sound Trigger
An intelligent audio monitoring system that listens to Discord's notification sounds (via a loopback or virtual cable) and triggers custom local actions. The system uses a Sliding Cross-Correlation algorithm to "fingerprint" and identify specific sounds even with slight timing variations.

🚀 Features
Real-time Monitoring: Low-latency audio stream analysis.

AI Learning Engine: If a sound isn't recognized, the script asks you to categorize it and saves it to a local database (data.json).

Custom Triggers: Specifically designed to play a custom sound file when a "User Join" event is detected.

Audio Fingerprinting: Uses Normalized Cross-Correlation to ensure high accuracy (85%+ match threshold).

🛠️ Requirements
Python 3.8+

Virtual Audio Cable (Recommended): To route Discord's output as an input for the script (e.g., VB-Cable or Voicemeeter).

Windows OS: Uses winsound for local playback.

Dependencies
Install the required Python libraries:

Bash

``pip install numpy sounddevice winsound``
📋 Setup & Usage
Prepare your audio:
Open the volume mixer and find the Discord's System Notifications mixer and thhen set the outputt to Virtual Audio Cable.
<img width="582" height="397" alt="image" src="https://github.com/user-attachments/assets/17c129b4-2aa3-4d81-aed0-3aa10930b762" />


Ensure you have a file named custom_join.wav in the root directory if you want the "Join" trigger to work.

Run the script:

Bash
python main.py
Select Device:
Upon startup, the script will list all available input devices. Select the index of the virtual cable capturing Discord audio.

Training Mode:
The first time a sound plays (e.g., a message or someone joining), the script will alert you that a NEW SOUND was detected.

Select the correct action from the list (1-9).

The script saves the "fingerprint" to data.json.

Next time that sound plays, it will be recognized automatically!

⚙️ Configuration
You can tweak the following variables in the main.py file:

VOLUME_THRESHOLD: Minimum volume to trigger detection (default: 0.02).

RECORD_DURATION: Length of the sound snippet to analyze (default: 1.2 seconds).

DB_FILE: The JSON file where sound signatures are stored.

📂 Project Structure
main.py: The core engine.

data.json: Database of learned sound fingerprints.

Sounds/: Directory where recorded .wav samples of Discord sounds are organized by category.

custom_join.wav: Your custom sound to play on "Join" events.

⚖️ License
This project is provided for educational and personal use. Feel free to fork and modify!


Ensure your custom_join.wav is actually in the folder before running.

Enjoy building! 🎧
