import socket
import json
import time
from pathlib import Path

Path("../logs").mkdir(parents=True, exist_ok=True)
PEERS_FILE = "../logs/peers.txt"
peers = {}  # IP -> {"username": str, "last_seen": float}

def load_peers():
    try:
        with open(PEERS_FILE, "r") as f:
            for line in f:
                ip, username, last_seen = line.strip().split()
                peers[ip] = {"username": username, "last_seen": float(last_seen)}
    except FileNotFoundError:
        pass

def save_peers():
    with open(PEERS_FILE, "w") as f:
        for ip, info in peers.items():
            f.write(f"{ip} {info['username']} {info['last_seen']:.0f}\n")

def main():
    load_peers()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 6000))  # Requirement 2.2.0-A

    print("Listening for peer broadcasts on port 6000...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            payload = json.loads(data.decode())

            if "username" in payload:
                username = payload["username"]
                current_time = time.time()

                if ip in peers:
                    # Kullanıcı adı değişmişse güncelle
                    if peers[ip]["username"] != username:
                        print(f"{peers[ip]['username']} is now known as {username}")
                        peers[ip]["username"] = username

                    peers[ip]["last_seen"] = current_time
                else:
                    peers[ip] = {"username": username, "last_seen": current_time}
                    print(f"{username} is online")

                save_peers()

        except Exception as e:
            print("Error receiving peer data:", e)

if __name__ == "__main__":
    main()