import socket
import signal
import sys

def signal_handler(sig, frame):
    print("\nClosing server...")
    server_socket.close()
    sys.exit(0)

# Register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP '0.0.0.0' and port 8890
server_socket.bind(('0.0.0.0', 8890))

print("UDP server is running on 0.0.0.0:8890")

while True:
    # Receive data from the client
    data, address = server_socket.recvfrom(1024)  # Buffer size is 1024 bytes
    
    # Print the received data and client address
    print(f"Received data from {address}: {data.decode(encoding="latin-1")}")

    # You can add your processing logic here

# Close the socket when done
server_socket.close()