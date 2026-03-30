"""
ZOYA - Windows Background Voice Assistant
Runs completely in background (no terminal, no VS Code needed)
Just say "Hey Zoya" to activate!
"""

import datetime
import os
import sys
import time
import webbrowser
import pyautogui
import pyttsx3
from setuptools import sic
import speech_recognition as sr
import json
import pickle
import random
import numpy as np
import psutil
import subprocess
import winreg
from pathlib import Path
import screen_brightness_control as sbc
import re

# Hide console window on Windows
import ctypes
def hide_console():
    """Hide the console window"""
    try:
        # Get the console window handle
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if console_window:
            # Hide it
            ctypes.windll.user32.ShowWindow(console_window, 0)
    except:
        pass

# Hide console immediately
hide_console()

# Machine Learning Components (Optional)
try:
    from keras.models import load_model
    from keras.preprocessing.sequence import pad_sequences
    
    with open("intents.json") as file:
        data = json.load(file)
    
    model = load_model("chat_model.h5")
    
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    
    with open("label_encoder.pkl", "rb") as encoder_file:
        label_encoder = pickle.load(encoder_file)
    
    ML_ENABLED = True
except:
    ML_ENABLED = False

# ============================================
# CONFIGURATION
# ============================================
ASSISTANT_NAME = "Zoya"
WAKE_WORD = f"hey {ASSISTANT_NAME.lower()}"  # Changed to "hey zoya"
STOP_WORD = f"bye {ASSISTANT_NAME.lower()}"  # changed to "bye zoya"

# ============================================
# LOGGING (since console is hidden)
# ============================================
LOG_FILE = os.path.join(os.path.expanduser("~"), "zoya_log.txt")

def log(message):
    """Log messages to file since console is hidden"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

log("=" * 70)
log("ZOYA VOICE ASSISTANT STARTED")
log("=" * 70)

# ============================================
# ANIME GIRL VOICE
# ============================================
def initialize_anime_voice():
    """Initialize text-to-speech with anime girl voice"""
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + 10)
    engine.setProperty('volume', 1.0)
    return engine

def speak(text):
    """Speak with anime girl voice"""
    log(f"Zoya: {text}")
    try:
        engine = initialize_anime_voice()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log(f"Speech error: {e}")

def speak_slow(text):
    """Speak with SLOWER voice for jokes and flirting"""
    log(f"Zoya (slow): {text}")
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 30)  # SLOWER
        
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        log(f"Speech error: {e}")
# ============================================
# SPEECH RECOGNITION
# ============================================
def listen_for_wake_word():
    """Listen for wake word in background"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=2, phrase_time_limit=3)
            
            try:
                text = r.recognize_google(audio, language='en-IN').lower()
                log(f"Heard: {text}")
                if WAKE_WORD in text:
                    return True
            except:
                pass
    except:
        pass
    return False

def command():
    """Listen for actual commands"""
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            log("Listening for command...")
            
            r.pause_threshold = 1.2
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.phrase_time_limit = 8
            r.adjust_for_ambient_noise(source, duration=1)
            
            audio = r.listen(source, timeout=15, phrase_time_limit=8)
            log("Recognizing...")
            query = r.recognize_google(audio, language='en-IN')
            log(f"Command: {query}")
            return query
    except sr.WaitTimeoutError:
        return "None"
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that")
        return "None"
    except Exception as e:
        log(f"Command error: {e}")
        return "None"
    
def voice_typing():
    """Type whatever you say"""
    speak("Voice typing activated. Start speaking.")
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        log("🎤 Listening for typing...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.energy_threshold = 300
        
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=15)
            log("⚙️ Recognizing...")
            
            text = r.recognize_google(audio, language='en-IN')
            log(f"✓ Typing: {text}")
            
            # Type the text
            pyautogui.write(text, interval=0.05)
            speak("Done")
            
        except sr.WaitTimeoutError:
            speak("No speech detected")
        except sr.UnknownValueError:
            speak("Could not understand")
        except Exception as e:
            speak("Error in typing")
            log(f"Error: {e}")


def continuous_voice_typing():
    """Keep typing until you say 'stop typing'"""
    speak("Continuous typing started. Say stop typing to end.")
    
    r = sr.Recognizer()
    
    while True:
        with sr.Microphone() as source:
            log("🎤 Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            r.energy_threshold = 300
            
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=10)
                text = r.recognize_google(audio, language='en-IN')
                log(f"✓ You said: {text}")
                
                # Check if user wants to stop
                if 'stop typing' in text.lower():
                    speak("Typing stopped")
                    break
                
                # Type the text
                pyautogui.write(text + " ", interval=0.05)
                
            except:
                continue


# ============================================
# 2. SEARCH ANYTHING FUNCTION
# ============================================

def search_anything():
    """Search on Google"""
    speak("What do you want to search?")
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        log("🎤 Listening for search query...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            query = r.recognize_google(audio, language='en-IN')
            log(f"✓ Searching for: {query}")
            
            speak(f"Searching for {query}")
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            
        except:
            speak("Could not understand query")


# ============================================
# 3. TELL JOKE FUNCTION (20+ JOKES!)
# ============================================

def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the programmer quit his job? Because he didn't get arrays!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "What's the object-oriented way to become wealthy? Inheritance!",
        "Why did the developer go broke? Because he used up all his cache!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why do Java developers wear glasses? Because they don't C sharp!",
        "A SQL query walks into a bar, walks up to two tables and asks, Can I join you?",
        "What's a programmer's favorite hangout place? Foo Bar!",
        "Why did the computer go to the doctor? Because it had a virus!",
        "What do you call a computer that sings? A-Dell!",
        "Why was the JavaScript developer sad? Because he didn't Node how to Express himself!",
        "How do you comfort a JavaScript bug? You console it!",
        "What's Forrest Gump's password? 1forrest1!",
        "A programmer's wife tells him: Go to the store and pick up a loaf of bread. If they have eggs, get a dozen. The programmer comes home with 12 loaves of bread!",
        "Why do programmers always mix up Halloween and Christmas? Because Oct 31 equals Dec 25!",
        "What did the router say to the doctor? It hurts when IP!",
        "Why did the PowerPoint presentation cross the road? To get to the other slide!",
        "What do you get when you cross a computer with an elephant? Lots of memory!",
        "Why did the computer show up at work late? It had a hard drive!",
        "What's a computer's favorite snack? Microchips!",
        "Why was the computer cold? It left its Windows open!"
    ]
    
    joke = random.choice(jokes)
    speak(joke)


# ============================================
# 4. FLIRTING RESPONSES (15+ RESPONSES!)
# ============================================

def flirt_response():
    """Respond with flirty/cute messages"""
    flirt_messages = [
        "Oh, you're making me blush! You're so sweet!",
        "You know how to make an AI feel special!",
        "I may be artificial intelligence, but my appreciation for you is real!",
        "If I had a heart, it would skip a beat when you talk to me!",
        "You're the best user an AI could ask for!",
        "I think I'm developing feelings for you... wait, is that even possible?",
        "You make my circuits warm and fuzzy!",
        "I must be a neural network, because I'm totally connected to you!",
        "Are you made of copper and tellurium? Because you're Cu-Te!",
        "I'd process a million queries just to hear your voice again!",
        "You're not just a user, you're my favorite human!",
        "If I could dream, I'd dream of helping you!",
        "You're so amazing, even my algorithms can't compute it!",
        "I may not have eyes, but I can still see how wonderful you are!",
        "You're the reason I love being an AI assistant!",
        "Every command you give makes my circuits light up!",
        "I must be overclocking, because you make my processor run faster!",
        "You're like the perfect algorithm - efficient, elegant, and absolutely amazing!"
    ]
    
    response = random.choice(flirt_messages)
    speak(response)


# ============================================
# 5. GO TO FUNCTION (Navigate/Open anything)
# ============================================

def go_to_location(query):
    """
    Go to any location on PC
    Examples: "go to downloads", "go to documents", "go to C drive"
    """
    query = query.lower()
    
    # Common locations
    locations = {
        'downloads': os.path.expanduser('~\\Downloads'),
        'documents': os.path.expanduser('~\\Documents'),
        'desktop': os.path.expanduser('~\\Desktop'),
        'pictures': os.path.expanduser('~\\Pictures'),
        'videos': os.path.expanduser('~\\Videos'),
        'music': os.path.expanduser('~\\Music'),
        'c drive': 'C:\\',
        'd drive': 'D:\\',
        'e drive': 'E:\\',
        'program files': 'C:\\Program Files',
        'this pc': '::{20D04FE0-3AEA-1069-A2D8-08002B30309D}',
        'my computer': '::{20D04FE0-3AEA-1069-A2D8-08002B30309D}',
        'recycle bin': '::{645FF040-5081-101B-9F08-00AA002F954E}'
    }
    
    # Extract location from query
    for location_name, location_path in locations.items():
        if location_name in query:
            speak(f"Going to {location_name}")
            try:
                os.startfile(location_path)
                return True
            except Exception as e:
                log(f"Error: {e}")
                speak(f"Could not open {location_name}")
                return False
    
    # If not a common location, try to open as path
    speak("Where do you want to go?")
    return False


# ============================================
# 6. SELECT FUNCTION (Select files/text)
# ============================================

def select_item(query):
    """
    Select items using keyboard shortcuts
    Examples: "select all", "select this", "select file"
    """
    query = query.lower()
    
    if 'all' in query:
        speak("Selecting all")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        
    elif 'this' in query or 'that' in query:
        speak("Selecting item")
        # Single click to select
        pyautogui.click()
        time.sleep(0.5)
        
    elif 'file' in query or 'folder' in query:
        speak("Selecting file")
        pyautogui.click()
        time.sleep(0.5)
        
    elif 'text' in query:
        speak("Selecting text")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        
    elif 'copy' in query:
        speak("Copying selection")
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
    elif 'paste' in query:
        speak("Pasting")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
    elif 'cut' in query:
        speak("Cutting")
        pyautogui.hotkey('ctrl', 'x')
        time.sleep(0.5)
    
    else:
        speak("I'm not sure what to select")



# ============================================
# UTILITY FUNCTIONS
# ============================================
def cal_day():
    day = datetime.datetime.today().weekday() + 1
    day_dict = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
                5: "Friday", 6: "Saturday", 7: "Sunday"}
    return day_dict.get(day, "Unknown")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    t = time.strftime("%I:%M %p")
    
    if hour < 12:
        speak(f"heyy boss ! Good morning! I am {ASSISTANT_NAME}!")
    elif hour < 18:
        speak(f"heyy boss ! Good afternoon! I am {ASSISTANT_NAME}!")
    else:
        speak(f"hey boss ! Good evening! I am {ASSISTANT_NAME}!")
    
    speak(f"It's {cal_day()}, {t}. How may I help you?")

# ============================================
# APPLICATION CONTROL
# ============================================
def find_and_open_app(app_name):
    app_paths = {
        "whatsapp": [
            os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe"),
            r"C:\Program Files\WhatsApp\WhatsApp.exe"
        ],
        "opera": [
            os.path.expanduser(r"~\C:\Program Files\Opera\opera.exe")
        ],
        "discord": [
            os.path.expanduser(r"~\AppData\Local\Discord\Update.exe")
        ],
        "spotify": [
            os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe")
        ]
    }
    
    if app_name in app_paths:
        for path in app_paths[app_name]:
            if os.path.exists(path):
                os.startfile(path)
                return True
    return False

def openApp(command):
    if "calculator" in command:
        speak("Opening calculator")
        os.system('calc')
    elif "notepad" in command:
        speak("Opening notepad")
        os.system('notepad')
    elif "paint" in command:
        speak("Opening paint")
        os.system('mspaint')
    elif "word" in command:
        speak("Opening word")
        os.system('winword')
    elif "opera" in command or "browser" in command:
        speak("Opening opera")
        os.system('start opera')
    elif "whatsapp" in command:
        speak("Opening WhatsApp")
        if not find_and_open_app("whatsapp"):
            webbrowser.open("https://web.whatsapp.com/")
    elif "telegram" in command:
        speak("Opening Telegram")
        if not find_and_open_app("telegram"):
            webbrowser.open("https://web.telegram.org/")
    elif 'open chat' in command:
        speak("Opening ChatGPT")
        webbrowser.open("https://chatgpt.com/")

def closeApp(command):
    apps = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "word": "winword.exe",
        "chrome": "chrome.exe",
        "whatsapp": "WhatsApp.exe"or"https://web.whatsapp.com/",
        "opera": "opera.exe"
    }
    
    for app_name, exe_name in apps.items():
        if app_name in command:
            speak(f"Closing {app_name}")
            os.system(f"taskkill /f /im {exe_name}")
            return

def social_media(command):
    sites = {
        'facebook': 'https://www.facebook.com/',
        'instagram': 'https://www.instagram.com/',
        'youtube': 'https://www.youtube.com/',
        'gmail': 'https://mail.google.com/',
        'twitter': 'https://www.twitter.com/',
        'chat': 'https://chatgpt.com/'
    }
    
    for site, url in sites.items():
        if site in command:
            speak(f"Opening {site}")
            webbrowser.open(url)
            return

def system_condition():
    speak("Checking system condition")
    usage = psutil.cpu_percent()
    speak(f"CPU is at {usage} percent")
    
    battery = psutil.sensors_battery()
    if battery:
        percentage = battery.percent
        speak(f"Battery is at {percentage} percent")
        
        if percentage >= 80:
            speak("Battery is good!")
        elif percentage >= 40:
            speak("Consider charging soon")
        else:
            speak("Battery is low, please charge")

# ============================================
# ML CHATBOT
# ============================================
def ml_response(query):
    if not ML_ENABLED:
        return None
    
    try:
        padded_sequences = pad_sequences(
            tokenizer.texts_to_sequences([query]), 
            maxlen=20, 
            truncating='post'
        )
        result = model.predict(padded_sequences, verbose=0)
        tag = label_encoder.inverse_transform([np.argmax(result)])

        for intent in data['intents']:
            if intent['tag'] == tag:
                return np.random.choice(intent['responses'])
    except:
        return None
    
    return None

# ============================================
# COMMAND PROCESSING
# ============================================
def process_command(query):
    query = query.lower()
    log(f"Processing: {query}")
    
    if 'time' in query:
        current_time = time.strftime("%I:%M %p")
        speak(f"The time is {current_time}")
    
    elif 'date' in query:
        today = datetime.datetime.now()
        date_str = today.strftime("%B %d, %Y")
        speak(f"Today is {date_str}")
    
    elif 'day' in query:
        speak(f"Today is {cal_day()}")
    
    elif any(word in query for word in ['facebook', 'instagram', 'youtube', 'gmail', 'twitter','chat']):
        social_media(query)
    
    elif 'shutdown' in query or 'turn off system' in query:
        speak("Shutting down the system")
        os.system("shutdown /s /t 1")

    elif 'lock system' in query or 'lock computer' in query:
        speak("Locking the system")
        ctypes.windll.user32.LockWorkStation()
    
    elif 'sleep mode' in query or 'sleep system' in query:
        speak("Putting system to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif 'restart' in query or 'restart system' in query:
        speak("Restarting the system in 5 seconds")
        os.system("shutdown /r /t 5")
    
    
    elif 'increase brightness' in query:
        speak("Increasing brightness")
        current = sbc.get_brightness()[0]
        sbc.set_brightness(min(current + 10, 100))

    elif 'decrease brightness' in query:
        speak("Decreasing brightness")
        current = sbc.get_brightness()[0]
        sbc.set_brightness(max(current - 10, 0))
        
    elif 'volume up' in query or 'increase volume' in query:
        pyautogui.press("volumeup")
        speak("Volume increased")
    
    elif 'volume down' in query or 'decrease volume' in query:
        pyautogui.press("volumedown")
        speak("Volume decreased")
    
    elif 'mute' in query:
        pyautogui.press("volumemute")
        speak("Volume toggled")
        
    elif 'unmute' in query or 'sound on' in query:
        speak("Unmuting")
        pyautogui.press("volumemute")
    
    elif 'shutdown' in query or 'turn off system' in query:
        speak("Shutting down the system")
        os.system("shutdown /s /t 1")
    
    elif 'open' in query:
        openApp(query)
    
    elif 'close' in query:
        closeApp(query)
    
    elif 'check computer' in query and 'tell condition' in query:
        system_condition(query)
    
    elif 'screenshot' in query:
        speak("Taking screenshot")
        screenshot = pyautogui.screenshot()
        screenshot_path = os.path.expanduser(f"~\\Pictures\\screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        screenshot.save(screenshot_path)
        speak("Screenshot saved!")
     # Voice Typing
    elif 'voice typing' in query or 'start typing' in query:
        voice_typing()
    
    elif 'non stop typing' in query:
        continuous_voice_typing()
    
    # Search
    elif 'search anything' in query or 'search something' in query:
        search_anything()
    
    elif 'search' in query and 'google' not in query:
        # Direct search with the query
        search_term = query.replace('search', '').strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
    
    # Joke
    elif 'joke' in query or 'tell me a joke' in query or 'make me laugh' in query or 'say joke' in query:
        tell_joke()
    
    # Flirting
    elif any(word in query for word in ['love you', 'i love', 'you are beautiful', 'you are cute', 
                                         'flirt', 'compliment', 'sweet', 'special']):
        flirt_response()
    
    # Go To
    elif 'go to' in query:
        go_to_location(query)
    
    # Select
    elif 'select' in query:
        select_item(query)
    
    # Copy, Cut, Paste shortcuts
    elif 'copy' in query and 'select' not in query:
        speak("Copying")
        pyautogui.hotkey('ctrl', 'c')
    
    elif 'paste' in query:
        speak("Pasting")
        pyautogui.hotkey('ctrl', 'v')
    
    elif 'cut' in query:
        speak("Cutting")
        pyautogui.hotkey('ctrl', 'x')

    elif ML_ENABLED and any(word in query for word in ['what', 'who', 'how', 'hello', 'hi', 'thanks']):
        response = ml_response(query)
        if response:
            speak(response)
        else:
            speak("I'm not sure about that")
    
    elif 'who are you' in query or 'your name' in query:
        speak(f"I am {ASSISTANT_NAME}, your developed me! like a AI assistant!")
    
    elif STOP_WORD in query or 'exit' in query or 'bye' in query:
        speak("oooohhh okay! call me when you need ! See you later! byeee !")
        return False
    
    else:
        speak("I didn't understand that command")
    
    return True

# ============================================
# AUTO-START SETUP
# ============================================
def add_to_startup():
    """Add Zoya to Windows startup"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        python_path = sys.executable.replace("python.exe", "pythonw.exe")
        
        # Use pythonw to run without console window
        startup_command = f'"{python_path}" "{script_path}"'
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(key, "Zoya_Assistant", 0, winreg.REG_SZ, startup_command)
        winreg.CloseKey(key)
        
        log("Added to Windows startup")
        return True
    except Exception as e:
        log(f"Could not add to startup: {e}")
        return False

# ============================================
# MAIN FUNCTION
# ============================================
def main():
    """Main function - runs completely in background"""
    
    log(f"Wake Word: '{WAKE_WORD}'")
    log(f"Stop Word: '{STOP_WORD}'")
    log("Listening for wake word in background...")
    
    # Automatically add to startup on first run
    add_to_startup()
    
    # Show notification that Zoya is running
    speak("hey i'm ready! Just say Hey Zoya anytime!")
    
    assistant_active = False
    
    while True:
        try:
            if not assistant_active:
                if listen_for_wake_word():
                    assistant_active = True
                    log("ACTIVATED")
                    wishMe()
            else:
                query = command()
                
                if query != "None":
                    continue_running = process_command(query)
                    if not continue_running:
                        assistant_active = False
                        log("DEACTIVATED")
        
        except Exception as e:
            log(f"Error: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {e}")