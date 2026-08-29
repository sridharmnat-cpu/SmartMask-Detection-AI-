import time
import threading
import platform

# Flag and lock to prevent multiple speech threads from running simultaneously
_speech_lock = threading.Lock()
_is_speaking = False
_last_speech_time = 0.0

# Lazy-loaded pyttsx3 engine import or initialization safety
def _speak_worker(text: str):
    global _is_speaking
    with _speech_lock:
        if _is_speaking:
            return
        _is_speaking = True
        
    try:
        import pyttsx3
        # Initialize pyttsx3 engine inside the thread
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Voice alert failure: {e}")
    finally:
        with _speech_lock:
            _is_speaking = False

def play_voice_alert(message: str = "Warning! No mask detected. Please wear a mask.", cooldown: float = 8.0, force: bool = False):
    """
    Spawns a background thread to read the voice alert message, with cooldown guard.
    
    Args:
        message: The text to speak.
        cooldown: Cooldown in seconds.
        force: If True, bypasses cooldown checks (e.g. for Test Voice button).
    """
    global _last_speech_time, _is_speaking
    
    if _is_speaking:
        return False  # Already speaking, ignore
        
    now = time.time()
    if not force and (now - _last_speech_time < cooldown):
        return False  # In cooldown
        
    _last_speech_time = now
    
    t = threading.Thread(target=_speak_worker, args=(message,), daemon=True)
    t.start()
    return True

# Platform-specific beep logic
if platform.system() == "Windows":
    import winsound
    def play_beep():
        try:
            # Beep(frequency, duration_ms)
            winsound.Beep(1000, 180)
        except Exception:
            pass
else:
    def play_beep():
        # Fallback for Linux / macOS
        print("\a", end="", flush=True)

def trigger_beep_alert():
    """
    Plays a short alert beep on a background thread.
    """
    t = threading.Thread(target=play_beep, daemon=True)
    t.start()
