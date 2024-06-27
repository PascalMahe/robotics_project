import socket
import psutil

def get_link_local_addresses():
    link_local_addresses = []
    
    # Iterate through network interfaces
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Check for link-local IPv4 addresses
            if addr.family == socket.AF_INET and addr.address.startswith("169.254.") and interface.startswith("Ethernet"):
                link_local_addresses.append({
                    'interface': interface,
                    'ip_address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
    
    return link_local_addresses


def server_program():
    # host = '169.254.33.138'  # Server's IP address
    host = '0.0.0.0'  # Server's IP address
    # host = 'fe80::c93c:d34e:73de:ef39%9' # fails
    # host = 'fe80::c93c:d34e:73de:ef39' # fails
    port = 8890       # Port to listen on

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    server_socket.bind((host, port))  # Bind to the address and port
    server_socket.listen(1)  # Listen for a connection

    print(f"Server listening on {host}:{port}")

    conn, address = server_socket.accept()  # Accept a connection
    print(f"Connection from {address}")

    message = "Hello from A"
    conn.send(message.encode())  # Send message to the clientp

    conn.close()  # Close the connection

if __name__ == '__main__':
    # server_program()

    link_local_addresses = get_link_local_addresses()
    
    if link_local_addresses:
        print("Link-local addresses found:")
        for address in link_local_addresses:
            print(f"Interface: {address['interface']}, IP Address: {address['ip_address']}, Netmask: {address['netmask']}, Broadcast: {address['broadcast']}")
    else:
        print("No link-local addresses found.")