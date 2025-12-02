import speech_recognition as sr
import pyttsx3
import datetime
import sys
import webbrowser
import os
import subprocess
import platform
from dotenv import load_dotenv
import google.generativeai as genai

# =================================================================================
# ⚙️ CONFIGURATION
# =================================================================================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ CRITICAL ERROR: API Key not found in .env file!")
    sys.exit()

# Configure AI
MODEL_NAME = 'gemini-1.5-flash'
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"❌ Model Error: {e}")
    sys.exit()

# AI Instructions
chat_session = model.start_chat(history=[
    {
        "role": "user",
        "parts": [
            "System Instruction: You are Jarvis. Your output is spoken aloud. "
            "Rules: 1. No markdown. 2. No emojis. 3. Concise answers (under 40 words). "
            "4. If asked for code, say you wrote it to console."
        ]
    },
    {
        "role": "model",
        "parts": ["Understood."]
    }
])

# =================================================================================
# 🛠️ CORE FUNCTIONS
# =================================================================================

def speak(text):
    """Speaks text using a fresh engine instance to prevent freezing."""
    if not text: return
    print(f"🤖 JARVIS: {text}")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Try Male voice (usually index 1), fallback to Female (0)
        try: engine.setProperty('voice', voices[1].id)
        except: engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"❌ Audio Error: {e}")

def listen_command():
    """Listens to microphone input."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n👂 Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("🧠 Recognizing...")
            command = r.recognize_google(audio).lower()
            print(f"👤 USER: {command}")
            return command
        except:
            return None

def ask_ai_brain(question):
    try:
        response = chat_session.send_message(question)
        return response.text.replace("*", "").replace("#", "").strip()
    except:
        return "I cannot connect to the brain right now."

def open_specific_app(app_name):
    system = platform.system()
    if system == "Windows":
        app_map = {"notepad": "notepad.exe", "calculator": "calc.exe", "spotify": "spotify.exe", "paint": "mspaint.exe"}
        try:
            if app_name in app_map:
                speak(f"Opening {app_name}")
                subprocess.Popen(app_map[app_name])
            else:
                speak(f"Attempting to open {app_name}")
                os.system(f"start {app_name}")
        except: speak(f"Could not open {app_name}")
    elif system == "Darwin":
        if "notepad" in app_name: app_name = "TextEdit"
        subprocess.call(["open", "-a", app_name])

# =================================================================================
# 🌐 AUTOMATION FUNCTIONS (NEW)
# =================================================================================

def search_google(command):
    # Remove the keywords "google" or "search for" to find the actual topic
    # Example: "Google python code" -> query becomes "python code"
    query = command.replace("open google", "").replace("google", "").replace("search for", "").replace("search", "").strip()
    
    if not query:
        speak("What would you like me to search for?")
        return
        
    speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def search_youtube(command):
    # Example: "Play Iron Man trailer" -> query becomes "Iron Man trailer"
    query = command.replace("open youtube", "").replace("youtube", "").replace("play", "").replace("on", "").strip()
    
    if not query:
        speak("What would you like me to play?")
        return
        
    speak(f"Searching YouTube for {query}")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

# =================================================================================
# 🧠 MAIN LOGIC
# =================================================================================

def handle_command(command):
    if not command: return

    # 1. SYSTEM
    if 'stop' in command or 'exit' in command:
        speak("Goodbye, Sir.")
        sys.exit()

    # 2. BROWSER AUTOMATION (NEW)
    elif 'google' in command or 'search for' in command:
        search_google(command)
        
    elif 'youtube' in command or 'play' in command:
        search_youtube(command)

    # 3. APPS
    elif 'open notepad' in command: open_specific_app("notepad")
    elif 'open calculator' in command: open_specific_app("calculator")
    elif 'open spotify' in command: open_specific_app("spotify")
    elif 'open paint' in command: open_specific_app("paint")

    # 4. TIME/DATE
    elif 'time' in command:
        speak(f"It is {datetime.datetime.now().strftime('%I:%M %p')}")
    elif 'date' in command:
        speak(f"Today is {datetime.date.today().strftime('%B %d, %Y')}")

    # 5. AI BRAIN (Fallback)
    else:
        ai_response = ask_ai_brain(command)
        speak(ai_response)

def main_loop():
    speak("Jarvis is online. Automation systems active.")
    while True:
        command = listen_command()
        handle_command(command)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        sys.exit()