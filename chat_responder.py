import socket
import json
from common_utils import *
from threading import Thread
from pathlib import Path

LOG_FILE = "../logs/chat_log.txt"
PEERS_FILE = "../logs/peers.txt"
Path("../logs").mkdir(parents=True, exist_ok=True)

def resolve_username(ip_address):
    try:
        with open(PEERS_FILE, "r") as f:
            for line in f:
                ip, username, _ = line.strip().split()
                if ip == ip_address:
                    return username
    except FileNotFoundError:
        pass
    return "Unknown"

def log_message(username, direction, message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp()}] {direction} | {username}: {message}\n")

def handle_client(connection, address):
    ip = address[0]
    username = resolve_username(ip)
    shared_key = None
    des_cipher = None

    try:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            decoded = json_decode(data.decode())

            if "key" in decoded:
                private_num = 7
                received_key = int(decoded["key"])
                response_key = generate_dh_key(private_num, 2)
                connection.send(json_encode({"key": str(response_key)}).encode())
                shared_key = compute_shared_secret(received_key, private_num)
                des_cipher = SimpleDES(shared_key)

            elif "encrypted_message" in decoded:
                if des_cipher is None:
                    print("[ERROR] Encrypted message received before key exchange.")
                    continue
                decrypted = des_cipher.decrypt(decoded["encrypted_message"])
                print(f"[{username}] (Encrypted): {decrypted}")
                log_message(username, "RECEIVED", f"[ENCRYPTED] {decrypted}")

            elif "unencrypted_message" in decoded:
                print(f"[{username}] (Unencrypted): {decoded['unencrypted_message']}")
                log_message(username, "RECEIVED", decoded["unencrypted_message"])

    except Exception as e:
        print("Error handling client:", e)
    finally:
        connection.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 6001))
    server_socket.listen(5)

    print("Chat responder listening on TCP port 6001...")

    while True:
        try:
            conn, addr = server_socket.accept()
            Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("Shutting down responder.")
            break

if __name__ == "__main__":
    main()