import os

# ============================================================
# PATHS & DIRECTORIES
# ============================================================
MODEL_PATH = "models/best.pt"
VIOLATION_DIR = "violations"
DB_PATH = "history.db"

# Ensure directories exist
os.makedirs(VIOLATION_DIR, exist_ok=True)

# ============================================================
# DEFAULT DETECTION CONFIGURATIONS
# ============================================================
DEFAULT_CONF = 0.50
DEFAULT_IMGSZ = 416
DEFAULT_FRAME_SKIP = 2

# ============================================================
# DEFAULT ALERT & SCREENSHOT CONFIGURATIONS
# ============================================================
DEFAULT_VOICE_ALERT = True
DEFAULT_VOICE_COOLDOWN = 8.0  # seconds
DEFAULT_AUTO_SCREENSHOT = True
DEFAULT_SCREENSHOT_COOLDOWN = 3.0  # seconds

# ============================================================
# BRANDING & STYLING CONSTANTS
# ============================================================
APP_TITLE = "SMART MASK DETECTER"
APP_SUBTITLE = "AI-Powered Face Mask Safety Monitoring Platform"

# Colors (BGR for OpenCV and hex for CSS)
COLOR_MASK_BGR = (34, 197, 94)      # Green
COLOR_NO_MASK_BGR = (239, 68, 68)   # Red
COLOR_OTHER_BGR = (245, 158, 11)     # Orange

COLOR_MASK_HEX = "#22C55E"
COLOR_NO_MASK_HEX = "#EF4444"
COLOR_OTHER_HEX = "#F59E0B"
COLOR_ACCENT_HEX = "#3B82F6"
COLOR_TEXT_MUTED_HEX = "#94A3B8"
