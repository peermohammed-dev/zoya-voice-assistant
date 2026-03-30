"""
AI-Based Virtual Voice Assistant - GUI Version
Enhanced version with graphical interface
"""

import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import sys
import random
import pyautogui
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ============================================
# ASSISTANT CONFIGURATION
# ============================================
ASSISTANT_NAME = "Zoya"  # Your custom AI assistant name
WAKE_WORD = f"hey {ASSISTANT_NAME.lower()}"
STOP_WORD = f"stop {ASSISTANT_NAME.lower()}"

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{ASSISTANT_NAME} - AI Voice Assistant")
        self.root.geometry("700x600")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)
        
        # Initialize TTS engine
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 180)
        
        # Assistant state
        self.is_active = False
        self.is_listening = False
        
        self.create_widgets()
        self.start_wake_word_detection()
    
    def create_widgets(self):
        """Create GUI elements"""
        
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text=f"🤖 {ASSISTANT_NAME}",
            font=('Arial', 24, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            title_frame,
            text="AI Virtual Voice Assistant",
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='#888888'
        )
        subtitle_label.pack()
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg='#1e1e1e')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="⚫ OFFLINE",
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='#ff4444'
        )
        self.status_label.pack()
        
        self.status_detail = tk.Label(
            status_frame,
            text=f"Say '{WAKE_WORD}' to activate",
            font=('Arial', 10),
            bg='#1e1e1e',
            fg='#888888'
        )
        self.status_detail.pack()
        
        # Chat Display
        chat_frame = tk.Frame(self.root, bg='#1e1e1e')
        chat_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            font=('Consolas', 10),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#00ff88',
            wrap=tk.WORD,
            state='disabled'
        )
        self.chat_display.pack(fill='both', expand=True)
        
        # Control Buttons
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.activate_btn = tk.Button(
            button_frame,
            text="🎤 Activate",
            font=('Arial', 12, 'bold'),
            bg='#00ff88',
            fg='#000000',
            activebackground='#00cc66',
            command=self.manual_activate,
            width=15,
            cursor='hand2'
        )
        self.activate_btn.pack(side='left', padx=5)
        
        self.deactivate_btn = tk.Button(
            button_frame,
            text="⏹ Deactivate",
            font=('Arial', 12, 'bold'),
            bg='#ff4444',
            fg='#ffffff',
            activebackground='#cc0000',
            command=self.manual_deactivate,
            width=15,
            cursor='hand2',
            state='disabled'
        )
        self.deactivate_btn.pack(side='left', padx=5)
        
        help_btn = tk.Button(
            button_frame,
            text="❓ Help",
            font=('Arial', 12, 'bold'),
            bg='#4444ff',
            fg='#ffffff',
            activebackground='#0000cc',
            command=self.show_help,
            width=15,
            cursor='hand2'
        )
        help_btn.pack(side='left', padx=5)
        
        # Footer
        footer_label = tk.Label(
            self.root,
            text=f"AI Voice Assistant v1.0 | Made with ❤️ using Python",
            font=('Arial', 8),
            bg='#1e1e1e',
            fg='#666666'
        )
        footer_label.pack(pady=5)
    
    def log_message(self, sender, message, color='#ffffff'):
        """Add message to chat display"""
        self.chat_display.config(state='normal')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Insert with color
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.chat_display.insert(tk.END, f"{sender}: ", 'sender')
        self.chat_display.insert(tk.END, f"{message}\n", 'message')
        
        # Configure tags
        self.chat_display.tag_config('timestamp', foreground='#888888')
        self.chat_display.tag_config('sender', foreground='#00ff88', font=('Consolas', 10, 'bold'))
        self.chat_display.tag_config('message', foreground=color)
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def speak(self, text):
        """Text to speech"""
        self.log_message(ASSISTANT_NAME, text, '#00ffff')
        self.engine.say(text)
        self.engine.runAndWait()
    
    def update_status(self, status_text, detail_text, color):
        """Update status display"""
        self.status_label.config(text=status_text, fg=color)
        self.status_detail.config(text=detail_text)
    
    def manual_activate(self):
        """Manually activate assistant"""
        if not self.is_active:
            self.activate_assistant()
    
    def manual_deactivate(self):
        """Manually deactivate assistant"""
        if self.is_active:
            self.deactivate_assistant()
    
    def activate_assistant(self):
        """Activate the assistant"""
        self.is_active = True
        self.update_status("🟢 ONLINE", "Listening for commands...", '#00ff88')
        self.activate_btn.config(state='disabled')
        self.deactivate_btn.config(state='normal')
        self.log_message("SYSTEM", f"{ASSISTANT_NAME} activated!", '#00ff88')
        self.wish_me()
        threading.Thread(target=self.listen_for_commands, daemon=True).start()
    
    def deactivate_assistant(self):
        """Deactivate the assistant"""
        self.is_active = False
        self.update_status("⚫ OFFLINE", f"Say '{WAKE_WORD}' to activate", '#ff4444')
        self.activate_btn.config(state='normal')
        self.deactivate_btn.config(state='disabled')
        self.speak("Goodbye! Have a great day!")
        self.log_message("SYSTEM", f"{ASSISTANT_NAME} deactivated", '#ff4444')
    
    def wish_me(self):
        """Greet user"""
        hour = int(datetime.datetime.now().hour)
        
        if hour >= 0 and hour < 12:
            greeting = "Good Morning!"
        elif hour >= 12 and hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"
        
        self.speak(f"{greeting} I am {ASSISTANT_NAME}, your AI assistant. How may I help you?")
    
    def take_command(self):
        """Listen and recognize speech"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_status("🎤 LISTENING", "Speak now...", '#ffff00')
            self.log_message("SYSTEM", "Listening...", '#ffff00')
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = r.listen(source, timeout=5)
                self.update_status("⚙️ PROCESSING", "Recognizing speech...", '#ff8800')
                self.log_message("SYSTEM", "Processing...", '#ff8800')
                
                query = r.recognize_google(audio, language='en-in')
                self.log_message("YOU", query, '#00ffff')
                self.update_status("🟢 ONLINE", "Command received", '#00ff88')
                return query.lower()
            
            except sr.WaitTimeoutError:
                self.update_status("🟢 ONLINE", "No input detected", '#00ff88')
                return "none"
            except sr.UnknownValueError:
                self.update_status("🟢 ONLINE", "Could not understand", '#00ff88')
                return "none"
            except Exception as e:
                self.update_status("🟢 ONLINE", "Error occurred", '#00ff88')
                return "none"
    
    def listen_for_commands(self):
        """Listen for commands when active"""
        while self.is_active:
            query = self.take_command()
            
            if query != "none":
                if STOP_WORD in query or 'exit' in query or 'bye' in query:
                    self.deactivate_assistant()
                    break
                else:
                    self.process_command(query)
    
    def start_wake_word_detection(self):
        """Background thread for wake word detection"""
        def detect_wake_word():
            r = sr.Recognizer()
            while True:
                if not self.is_active:
                    try:
                        with sr.Microphone() as source:
                            r.adjust_for_ambient_noise(source, duration=0.5)
                            audio = r.listen(source, timeout=2, phrase_time_limit=3)
                            query = r.recognize_google(audio, language='en-in').lower()
                            
                            if WAKE_WORD in query:
                                self.root.after(0, self.activate_assistant)
                    except:
                        pass
        
        threading.Thread(target=detect_wake_word, daemon=True).start()
    
    def process_command(self, query):
        """Process and execute commands"""
        
        if 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"The time is {strTime}")
        
        elif 'date' in query:
            year = datetime.datetime.now().year
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day
            self.speak(f"Today is {day}/{month}/{year}")
        
        elif 'joke' in query:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the programmer quit his job? Because he didn't get arrays!",
                "What do you call a bear with no teeth? A gummy bear!",
            ]
            self.speak(random.choice(jokes))
        
        elif 'open notepad' in query:
            self.speak("Opening Notepad")
            os.system('notepad')
        
        elif 'open calculator' in query:
            self.speak("Opening Calculator")
            os.system('calc')
        
        elif 'open youtube' in query:
            self.speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        
        elif 'open google' in query:
            self.speak("Opening Google")
            webbrowser.open("https://www.google.com")
        
        elif 'wikipedia' in query:
            self.speak("Searching Wikipedia")
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                self.speak("According to Wikipedia")
                self.speak(results)
            except:
                self.speak("Sorry, I couldn't find anything on Wikipedia")
        
        elif 'search' in query:
            self.speak("Searching on Google")
            query = query.replace("search", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
        
        elif 'who are you' in query:
            self.speak(f"I am {ASSISTANT_NAME}, your AI virtual voice assistant created using Python")
        
        elif 'screenshot' in query:
            self.speak("Taking screenshot")
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.expanduser(f"~\\Pictures\\screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            screenshot.save(screenshot_path)
            self.speak("Screenshot saved")
        
        else:
            self.speak("I didn't understand that command. Please try again.")
    
    def show_help(self):
        """Show help dialog"""
        help_text = f"""
🤖 {ASSISTANT_NAME} - Voice Commands

TIME & DATE:
• "What time is it?"
• "What's the date?"

ENTERTAINMENT:
• "Tell me a joke"

APPLICATIONS:
• "Open notepad"
• "Open calculator"

WEBSITES:
• "Open YouTube"
• "Open Google"

SEARCH:
• "Search [topic] on Wikipedia"
• "Search [query]"

SYSTEM:
• "Take screenshot"

GENERAL:
• "Who are you?"
• "Stop {ASSISTANT_NAME}" - Deactivate

ACTIVATION:
• Say "{WAKE_WORD}" to activate
• Or click "Activate" button
        """
        
        messagebox.showinfo(f"{ASSISTANT_NAME} Help", help_text)

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
