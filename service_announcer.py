
import socket
import json
import time

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

def main():
    username = input("Enter your username: ").strip()
    ip_address = get_local_ip()
    port = 6000
    broadcast_ip = "192.168.1.255"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print(f"Broadcasting as '{username}' with IP {ip_address} every 8 seconds...")

    while True:
        try:
            message = json.dumps({
                "username": username,
                "ip": ip_address
            })
            sock.sendto(message.encode(), (broadcast_ip, port))
            print(f"Broadcast sent: {message} -> {broadcast_ip}:{port}")
            time.sleep(8)
        except KeyboardInterrupt:
            print("Service announcer stopped.")
            break
        except Exception as e:
            print("Broadcast error:", e)
            time.sleep(8)

if __name__ == "__main__":
    main()
