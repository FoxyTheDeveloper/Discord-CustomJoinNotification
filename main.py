import os
import json
import wave
import time
import numpy as np
import sounddevice as sd
import winsound
import logging

# ==========================================
# CONFIGURATION
# ==========================================
DB_FILE = 'data.json'
SOUNDS_DIR = 'Sounds'
CUSTOM_JOIN_SOUND = 'custom_join.wav' 
RECORD_DURATION = 1.2 
VOLUME_THRESHOLD = 0.02 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

ACTIONS = {
    '1': 'User Join',
    '2': 'User Leave',
    '3': 'Message',
    '4': 'Mute',
    '5': 'Unmute',
    '6': 'Deafen',
    '7': 'Undeafen',
    '8': 'Screenshare',
    '9': 'Ignored'
}

os.makedirs(SOUNDS_DIR, exist_ok=True)
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f:
        json.dump([], f)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def select_audio_device():
    print("\n" + "="*50)
    print(" 🎧 Scanning Available Audio Devices (Inputs) 🎧 ")
    print("="*50)
    
    devices = sd.query_devices()
    valid_devices = []
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            host_api = sd.query_hostapis(dev['hostapi'])['name']
            valid_devices.append((i, f"{dev['name']} [{host_api}]"))
            
    if not valid_devices:
        logging.error("No active recording devices found on this computer!")
        return None
        
    for idx, (original_i, name) in enumerate(valid_devices):
        print(f"[{idx + 1}] {name}")
        
    print("="*50)
    
    while True:
        try:
            choice = input("\nSelect the device number you want to capture Discord from: ").strip()
            choice = int(choice)
            
            if 1 <= choice <= len(valid_devices):
                selected_index = valid_devices[choice - 1][0]
                selected_name = valid_devices[choice - 1][1]
                print(f"\n✅ Successfully selected: {selected_name}\n")
                return selected_index
            else:
                print("❌ Number out of range, please try again.")
        except ValueError:
            print("❌ Please enter a valid number from the list.")

def calculate_similarity(new_audio, saved_audio, max_shift):
    """Advanced Sliding Cross-Correlation algorithm for perfect matching"""
    if len(new_audio) != len(saved_audio):
        return 0
        
    x_norm = (new_audio - np.mean(new_audio)) / (np.std(new_audio) + 1e-10)
    y_norm = (saved_audio - np.mean(saved_audio)) / (np.std(saved_audio) + 1e-10)
    
    corr = np.correlate(x_norm, y_norm, mode='full') / len(new_audio)
    
    center = len(new_audio) - 1
    best_score = np.max(corr[max(0, center - max_shift) : min(len(corr), center + max_shift + 1)])
    
    return best_score

def process_detected_sound(audio_data, sample_rate):
    """Categorized AI Learning Engine with Sliding Matcher"""
    audio_1d = audio_data.flatten()
    
    chunk_size = 100
    reshaped = np.abs(audio_1d[:len(audio_1d)//chunk_size * chunk_size]).reshape(-1, chunk_size)
    smoothed = np.mean(reshaped, axis=1)
    center_idx = np.argmax(smoothed) * chunk_size
    
    if np.abs(audio_1d[center_idx]) < VOLUME_THRESHOLD:
        return 
        
    pre_peak = int(sample_rate * 0.4)
    post_peak = int(sample_rate * 0.6)
    window_size = pre_peak + post_peak
    
    window = np.zeros(window_size)
    src_start = max(0, center_idx - pre_peak)
    src_end = min(len(audio_1d), center_idx + post_peak)
    dst_start = max(0, pre_peak - (center_idx - src_start))
    dst_end = dst_start + (src_end - src_start)
    
    window[dst_start:dst_end] = audio_1d[src_start:src_end]
    
    if np.sum(window ** 2) < 5.0:
        return
        
    downsample_factor = 10
    fingerprint = window[::downsample_factor] 
    
    max_shift_samples = int((sample_rate / downsample_factor) * 0.1) 
    
    try:
        with open(DB_FILE, 'r') as f:
            db = json.load(f)
            if not isinstance(db, list):
                db = []
    except:
        db = []

    best_score = 0
    matched_action = None
    
    for entry in db:
        saved_fp = np.array(entry.get('fingerprint', []))
        if len(fingerprint) == len(saved_fp):
            score = calculate_similarity(fingerprint, saved_fp, max_shift_samples)
            if score > best_score:
                best_score = score
                matched_action = entry.get('action')

    if best_score > 0.85:
        action_name = ACTIONS.get(matched_action, 'Unknown')
        
        if matched_action == '1': 
            logging.info(f"🎯 KRYX TRIGGER [Match: {best_score*100:.1f}%]: [{action_name}] -> Playing local sound in headphones!")
            
            try:
                winsound.PlaySound(CUSTOM_JOIN_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                logging.error(f"Could not play local sound: {e}")
            
        else:
            logging.info(f"Known sound detected [Match: {best_score*100:.1f}%]: [{action_name}] -> Ignoring.")
    else:
        print("\n" + "="*50)
        if best_score > 0:
            logging.warning(f"🆕 SOUND MISMATCH / NEW SOUND (Highest match: {best_score*100:.1f}%)")
        else:
            logging.warning(f"🆕 COMPLETELY NEW SOUND DETECTED!")
            
        print("\nWhich Discord sound was just played? (Select exact number)")
        for key, value in ACTIONS.items():
            print(f"{key}. {value}")
        
        choice = input("\nEnter number (1-9): ").strip()
        if choice not in ACTIONS:
            choice = '9'
            
        action_name = ACTIONS[choice]
        category_dir = os.path.join(SOUNDS_DIR, action_name)
        os.makedirs(category_dir, exist_ok=True)
        
        timestamp = int(time.time())
        filepath = os.path.join(category_dir, f"{action_name}_{timestamp}.wav")
        
        scaled = np.int16(window * 32767)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(scaled.tobytes())
            
        db.append({
            'fingerprint': fingerprint.tolist(),
            'action': choice
        })
        
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=4)
            
        logging.info(f"✅ Saved to folder '{action_name}'. Memory expanded. Monitoring resumed.")
        print("="*50 + "\n")

# ==========================================
# MAIN LOOP
# ==========================================
def main():
    device_idx = select_audio_device()
    if device_idx is None:
        return

    device_info = sd.query_devices(device_idx)
    sample_rate = int(device_info['default_samplerate'])
    
    logging.info(f"🎧 Starting connection to: {device_info['name']} (Rate: {sample_rate}Hz)")
    logging.info("🚀 Kryx Host Engine is Production Ready. Listening...")

    try:
        with sd.InputStream(device=device_idx, channels=1, samplerate=sample_rate) as stream:
            while True:
                chunk, overflow = stream.read(int(sample_rate * 0.1))
                volume = np.max(np.abs(chunk))

                if volume > VOLUME_THRESHOLD:
                    record_frames = int(sample_rate * RECORD_DURATION)
                    audio_rest, _ = stream.read(record_frames)
                    
                    full_audio = np.concatenate((chunk, audio_rest))
                    process_detected_sound(full_audio, sample_rate)
                    
                    time.sleep(1.0) 
                    
                    if stream.read_available > 0:
                        stream.read(stream.read_available)

    except KeyboardInterrupt:
        logging.info("🛑 Shutting down gracefully...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()