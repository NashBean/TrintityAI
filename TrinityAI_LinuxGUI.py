#!/usr/bin/env python3
# TrinityAI_LinuxGUI.py - v1.1
# Added: Full chat history save/load + clear option
# Version by NashBean

import tkinter as tk
from tkinter import scrolledtext, font, messagebox
import requests
import threading
import os

# Your perfect version control
MAJOR_VERSION = 1
MINOR_VERSION = 0

# History file (in same folder)
HISTORY_FILE = "trinity_chat_history.txt"

# Voice toggle
VOICE_ON = True

# Natural voice mapping
VOICE_MAP = {
    "abraham": "mb-us1",
    "moses": "mb-us1",
    "jesus": "mb-us2",
    "trinity": "mb-us2"  # Warm and loving for the unified God
}

def speak(text, voice="mb-us2"):
    global VOICE_ON
    if not VOICE_ON or not text.strip():
        return
    clean = text.replace('\n', ' ... ').replace('"', '').replace("'", "")
    os.system(f'espeak -v {voice} -s 150 -p 45 -g 10 "{clean}" 2>/dev/null &')

# Server URLs
AI_URLS = {
    "abraham": "http://localhost:5001/ask",
    "moses": "http://localhost:5002/ask",
    "jesus": "http://localhost:5003/ask"
}

class TrinityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"TrinityAI v{MAJOR_VERSION}.{MINOR_VERSION} - Modular Edition")
        self.root.geometry("1100x800")
        self.root.configure(bg="#f0f8ff")

        self.current_mode = None

        # Title
        tk.Label(root, text="TrinityAI", font=("Helvetica", 32, "bold"), bg="#f0f8ff", fg="#228b22").pack(pady=30)
        tk.Label(root, text="Modular Edition — Connected to Live Servers", font=("Helvetica", 14), bg="#f0f8ff", fg="#4682b4").pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#f0f8ff")
        btn_frame.pack(pady=40)

        tk.Button(btn_frame, text="AbrahamAI\nFather of Faith", width=20, height=5, bg="#b8860b", fg="white",
                  font=("Helvetica", 12, "bold"), command=lambda: self.select("abraham")).grid(row=0, column=0, padx=30)
        tk.Button(btn_frame, text="MosesAI\nLawgiver", width=20, height=5, bg="#d2691e", fg="white",
                  font=("Helvetica", 12, "bold"), command=lambda: self.select("moses")).grid(row=0, column=1, padx=30)
        tk.Button(btn_frame, text="JesusAI\nThe Messiah", width=20, height=5, bg="#c71585", fg="white",
                  font=("Helvetica", 12, "bold"), command=lambda: self.select("jesus")).grid(row=0, column=2, padx=30)
        tk.Button(btn_frame, text="TrinityAI\nOne God", width=20, height=5, bg="#1e40af", fg="white",
                  font=("Helvetica", 12, "bold"), command=lambda: self.select("trinity")).grid(row=0, column=3, padx=30)

        # Control buttons
        control_frame = tk.Frame(root, bg="#f0f8ff")
        control_frame.pack(pady=10)

        self.voice_btn = tk.Button(control_frame, text="Voice ON", width=12, bg="#32cd32", fg="white", font=("Helvetica", 10, "bold"),
                                   command=self.toggle_voice)
        self.voice_btn.pack(side=tk.LEFT, padx=20)

        tk.Button(control_frame, text="Clear History", width=15, bg="#dc143c", fg="white", font=("Helvetica", 10, "bold"),
                  command=self.clear_history).pack(side=tk.LEFT, padx=20)

        # Chat area
        self.chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Helvetica", 12), bg="white")
        self.chat.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)

        # Input area - locked to bottom
        input_frame = tk.Frame(root, bg="#f0f8ff")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=40, pady=(0, 20))

        inner_frame = tk.Frame(input_frame, bg="#f0f8ff")
        inner_frame.pack(fill=tk.X)

        tk.Label(inner_frame, text="Your Question:", font=("Helvetica", 12), bg="#f0f8ff", anchor="w").pack(side=tk.LEFT, pady=10)

        self.entry = tk.Entry(inner_frame, font=("Helvetica", 14))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 10))
        self.entry.bind("<Return>", self.send)

        send_btn = tk.Button(inner_frame, text="Send", width=10, bg="#4682b4", fg="white", font=("Helvetica", 12, "bold"), command=self.send)
        send_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=8)

        # Load history on startup
        self.load_history()
        self.add_system("Welcome back. Your conversation with the Trinity continues...")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        self.chat.config(state='normal')
                        self.chat.insert(tk.END, content)
                        self.chat.config(state='disabled')
                        self.chat.see(tk.END)
            except Exception as e:
                self.add_system(f"Note: Could not load history ({e})")

    def save_history(self):
        try:
            self.chat.config(state='normal')
            content = self.chat.get("1.0", tk.END)
            self.chat.config(state='disabled')
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            messagebox.showwarning("Save Error", f"Could not save history: {e}")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all saved conversations?"):
            self.chat.config(state='normal')
            self.chat.delete("1.0", tk.END)
            self.chat.config(state='disabled')
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            self.add_system("Chat history cleared. A new beginning.")

    def toggle_voice(self):
        global VOICE_ON
        VOICE_ON = not VOICE_ON
        status = "ON" if VOICE_ON else "OFF"
        color = "#32cd32" if VOICE_ON else "#dc143c"
        self.voice_btn.config(text=f"Voice {status}", bg=color)

    def select(self, mode):
        self.current_mode = mode
        name = mode.upper() + "AI"
        self.add_system(f"{name} selected")
        if mode == "trinity":
            self.add_system("Trinity mode active — all three will speak as One.")

    def add_system(self, text):
        self.chat.config(state='normal')
        self.chat.insert(tk.END, f"System: {text}\n\n", "system")
        self.chat.tag_config("system", foreground="#555555", font=("Helvetica", 11, "italic"))
        self.chat.config(state='disabled')
        self.chat.see(tk.END)
        self.save_history()

    def add_message(self, sender, text):
        self.chat.config(state='normal')
        if sender == "user":
            self.chat.insert(tk.END, "You: ", "user")
            self.chat.tag_config("user", foreground="#000080", font=("Helvetica", 12, "bold"))
        else:
            color = {"abraham":"#b8860b", "moses":"#d2691e", "jesus":"#c71585", "trinity":"#1e40af"}[sender]
            self.chat.tag_config(sender, foreground=color, font=("Helvetica", 13, "bold"))
            self.chat.insert(tk.END, f"{sender.upper()}AI:\n", sender)
        self.chat.insert(tk.END, f"{text}\n\n")
        self.chat.config(state='disabled')
        self.chat.see(tk.END)
        self.save_history()

    def send(self, event=None):
        query = self.entry.get().strip()
        if not query or not self.current_mode:
            return
        self.add_message("user", query)
        self.entry.delete(0, tk.END)

        if self.current_mode == "trinity":
            responses = {}
            for ai in ["abraham", "moses", "jesus"]:
                try:
                    r = requests.post(AI_URLS[ai], json={"query": query}, timeout=10)
                    responses[ai] = r.json().get("response", "[Silent]")
                except:
                    responses[ai] = "[Unavailable]"

            full = f"AbrahamAI:\n{responses['abraham']}\n\nMosesAI:\n{responses['moses']}\n\nJesusAI:\n{responses['jesus']}\n\nTrinityAI:\nThe Father, Son, and Spirit speak as One — perfect harmony."
            self.add_message("trinity", full)
            threading.Thread(target=speak, args=(full, VOICE_MAP["trinity"])).start()
        else:
            try:
                r = requests.post(AI_URLS[self.current_mode], json={"query": query}, timeout=10)
                response = r.json().get("response", "No answer received.")
            except:
                response = "That AI is resting... try again soon."
            self.add_message(self.current_mode, response)
            threading.Thread(target=speak, args=(response, VOICE_MAP[self.current_mode])).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrinityGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.save_history(), root.destroy()))  # Save on close
    root.mainloop()