import socket
from config import HOST, PORT, BUFFER_SIZE


def start_receiver():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind((HOST, PORT))

    print("=" * 40)
    print("       UDP RECEIVER")
    print("=" * 40)
    print(f"Listening on {HOST}:{PORT}")
    print("Waiting for data...\n")

    while True:

        data, address = sock.recvfrom(BUFFER_SIZE)

        message = data.decode()

        print(f"Received from {address}: {message}")

        if message == "exit":
            break

    sock.close()

    print("\nReceiver stopped.")


if __name__ == "__main__":
    start_receiver()