import os

# --- API KEYS ---
# Groq Keys (Tried sequentially)
GROQ_API_KEYS = [
    os.environ.get("GROQ_API_KEY_1", "YOUR_GROQ_API_KEY_1"),
    os.environ.get("GROQ_API_KEY_2", "YOUR_GROQ_API_KEY_2"),
    os.environ.get("GROQ_API_KEY_3", "YOUR_GROQ_API_KEY_3"),
]

# Gemini Keys (Tried sequentially for visual analysis)
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_API_KEY_1", "YOUR_GEMINI_API_KEY_1"),
    os.environ.get("GEMINI_API_KEY_2", "YOUR_GEMINI_API_KEY_2"),
    os.environ.get("GEMINI_API_KEY_3", "YOUR_GEMINI_API_KEY_3"),
]

# --- MODELS ---
# Llama 3.3 for fast responses
FAST_MODEL = "llama-3.3-70b-versatile"
# For deep thinking mode
THINK_MODEL = "llama-3.1-70b-versatile"
# For visual analysis (Vision)
GEMINI_MODEL = "gemini-2.0-flash-exp"

# --- DIRECTORY PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Automatically finds the Desktop path
BRAIN_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "LAMA_Brain")
SCREENSHOTS_FOLDER = os.path.join(BRAIN_FOLDER, "Screenshots")

# Create directories
if not os.path.exists(BRAIN_FOLDER):
    os.makedirs(BRAIN_FOLDER)
if not os.path.exists(SCREENSHOTS_FOLDER):
    os.makedirs(SCREENSHOTS_FOLDER)
