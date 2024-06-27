import socket
import sys

def fetch_msg_from_other_host(host, port):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    print(f"Connecting to: {host} (port: {port})")
    client_socket.connect((host, port))  # Connect to the server

    message = client_socket.recv(1024).decode()  # Receive message from the server
    print(f"Message from server: {message}")

    client_socket.close()  # Close the connection
    return message

if __name__ == '__main__':
    if len(sys.argv) > 1:
        addr = sys.argv[1]
    else:
        print("Please specify address to connect to (169.254.XXX.XXX).")
        sys.exit()

    port = 8890
    fetch_msg_from_other_host(addr, port)