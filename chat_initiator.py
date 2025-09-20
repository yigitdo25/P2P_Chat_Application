import socket
import json
import time
from pathlib import Path
from common_utils import *
from datetime import datetime

PEERS_FILE = "../logs/peers.txt"
LOG_FILE = "../logs/chat_log.txt"

Path("../logs").mkdir(parents=True, exist_ok=True)

def load_peers():
    peers = {}
    try:
        with open(PEERS_FILE, "r") as f:
            for line in f:
                ip, username, last_seen = line.strip().split()
                peers[username] = {
                    "ip": ip,
                    "last_seen": float(last_seen)
                }
    except FileNotFoundError:
        print("No peers found.")
    return peers

def display_users(peers):
    now = time.time()
    print("\n--- Available Users ---")
    for name, info in peers.items():
        status = "Online" if now - info["last_seen"] <= 10 else "Away"
        print(f"{name} ({status})")
    print("------------------------\n")

def log_message(username, direction, message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp()}] {direction} | {username}: {message}\n")

def secure_chat(target_ip, target_username):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((target_ip, 6001))

        private_num = int(input("Enter your secret number (integer): "))
        key_json = json_encode({"key": str(generate_dh_key(private_num, 2))})
        client_socket.send(key_json.encode())

        response = client_socket.recv(1024).decode()
        parsed = json_decode(response)
        if "key" not in parsed:
            print("Key exchange failed.")
            client_socket.close()
            return
        shared_key = compute_shared_secret(int(parsed["key"]), private_num)
        des_cipher = SimpleDES(shared_key)

        while True:
            msg = input("Enter your message (type /exit to quit): ").strip()
            if msg.lower() == "/exit":
                break
            encrypted_msg = des_cipher.encrypt(msg)
            msg_json = json_encode({"encrypted_message": encrypted_msg})
            client_socket.send(msg_json.encode())
            log_message(target_username, "SENT", f"[ENCRYPTED] {msg}")

        client_socket.close()

    except Exception as e:
        print("Secure chat failed:", e)

def unsecure_chat(target_ip, target_username):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(10)
        client_socket.connect((target_ip, 6001))

        while True:
            msg = input("Enter your message (type /exit to quit): ").strip()
            if msg.lower() == "/exit":
                break
            msg_json = json_encode({"unencrypted_message": msg})
            client_socket.send(msg_json.encode())
            log_message(target_username, "SENT", msg)

        client_socket.close()

    except Exception as e:
        print("Unsecure chat failed:", e)

def view_history():
    try:
        with open(LOG_FILE, "r") as f:
            print("\n--- Chat History ---")
            for line in f:
                print(line.strip())
            print("---------------------\n")
    except FileNotFoundError:
        print("No history available.")

def main():
    while True:
        try:
            choice = input("Choose: Users / Chat / History > ").strip().lower()
            if choice == "users":
                peers = load_peers()
                display_users(peers)
            elif choice == "chat":
                peers = load_peers()
                username = input("Enter the username you want to chat with: ").strip()
                if username not in peers:
                    print("User not found.")
                    continue
                secure = input("Secure chat? (yes/no): ").strip().lower()
                if secure == "yes":
                    secure_chat(peers[username]["ip"], username)
                else:
                    unsecure_chat(peers[username]["ip"], username)
            elif choice == "history":
                view_history()
            else:
                print("Invalid option. Please choose again.")
        except KeyboardInterrupt:
            print("\nExiting Chat Initiator...")
            break

if __name__ == "__main__":
    main()