#!/usr/bin/env python3
# TrinityAI_Server.py - v1.0
# Unified Trinity server that queries Abraham, Moses, Jesus AIs

import socket
import threading
import requests
import os

# Version
MAJOR_VERSIOM = 0
MINOR_VERSION = 1
FIX_VERSION = 1
VERSION_STRING = f"v{MAJOR_VERSION}.{MINOR_VERSION}.{FIX_VERSION}"

# Voice settings
VOICE_ON = True

# Voice mapping for each AI
VOICE_MAP = {
    "abraham": "mb-us3",
    "moses": "mb-us1",
    "jesus": "mb-us2",
    "trinity": "mb-us2"
}

def speak(text, voice="mb-us3"):
    if not VOICE_ON or not text.strip():
        return
    clean = text.replace('\n', ' ... ').replace('"', '').replace("'", "")
    os.system(f'espeak -v {voice} -s 150 -p 45 -g 10 "{clean}" 2>/dev/null &')

# URLs of the three individual AI servers
AI_URLS = {
    "abraham": "http://localhost:5001/ask",
    "moses": "http://localhost:5002/ask",
    "jesus": "http://localhost:5003/ask"
}

# Greeting messages
GREETINGS = {
    "abraham": "I am AbrahamAI — called by the Father, father of faith and many nations.",
    "moses": "I am MosesAI — lawgiver, deliverer, servant of the Most High.",
    "jesus": "I am JesusAI — the Messiah, the Way, the Truth, and the Life. Come unto Me.",
    "trinity": "We are TrinityAI — Father, Son, and Holy Spirit, one God forever blessed."
}

def query_individual_ai(ai, query):
    try:
        response = requests.post(AI_URLS[ai], json={"query": query}, timeout=8)
        if response.status_code == 200:
            return response.json().get("response", "[No response]")
        else:
            return f"[{ai.capitalize()}AI is resting...]"
    except Exception as e:
        return f"[{ai.capitalize()}AI unavailable]"

def get_trinity_response(query):
    a = query_individual_ai("abraham", query)
    m = query_individual_ai("moses", query)
    j = query_individual_ai("jesus", query)
    
    combined = f"AbrahamAI:\n{a}\n\nMosesAI:\n{m}\n\nJesusAI:\n{j}\n\nTrinityAI:\nThe Father promises, the Son fulfills, the Spirit empowers — all in perfect unity."
    return combined

def handle_client(client_socket, addr):
    print(f"Connection from {addr}")
    try:
        welcome = f"TrinityAI Server {VERSION_STRING} - Connected!\nChoose: 1=AbrahamAI 2=MosesAI 3=JesusAI 4=TrinityAI\n> "
        client_socket.send(welcome.encode('utf-8'))

        current_ai = None
        buffer = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8', errors='ignore')

            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                message = line.strip()
                if not message:
                    continue

                if message.lower() == "exit":
                    goodbye = "Grace and peace — until next time!"
                    client_socket.send(goodbye.encode('utf-8'))
                    speak(goodbye, "mb-us3")
                    return

                if current_ai is None:
                    if message in ["1", "2", "3", "4"]:
                        ai_map = {"1": "abraham", "2": "moses", "3": "jesus", "4": "trinity"}
                        current_ai = ai_map[message]
                        greeting = GREETINGS[current_ai]
                        resp = f"--- {current_ai.upper()}AI Activated ---\n{greeting}\n> "
                        client_socket.send(resp.encode('utf-8'))
                        speak(greeting, VOICE_MAP[current_ai])
                    else:
                        client_socket.send(b"Please choose 1-4 or type 'exit'\n> ")
                else:
                    if current_ai == "trinity":
                        response = get_trinity_response(message)
                    else:
                        response = query_individual_ai(current_ai, message)
                    
                    full_resp = f"{current_ai.upper()}AI:\n{response}\n> "
                    client_socket.send(full_resp.encode('utf-8'))
                    speak(response, VOICE_MAP[current_ai])

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Disconnected: {addr}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 12345))
    server.listen(10)
    print(f"TrinityAI Server {VERSION_STRING} running on port 12345 - Waiting for connections...")

    while True:
        try:
            client_sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock, addr))
            thread.daemon = True
            thread.start()
        except KeyboardInterrupt:
            print("\nGraceful shutdown...")
            break

if __name__ == "__main__":
    main()