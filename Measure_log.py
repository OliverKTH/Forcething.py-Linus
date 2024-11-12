
import socket

def get_local_ip():
    """
    Returns the IP address of the current machine on the local network.
    """
    # Get the hostname of the local machine
    hostname = socket.gethostname()
    # Resolve the hostname to an IP address
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def find_open_port():
    """
    Finds an available port by letting the OS assign an open port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
        temp_socket.bind(('', 0))  # Bind to any available port
        open_port = temp_socket.getsockname()[1]
    return open_port

host = get_local_ip()
RXport = find_open_port()
TXport = find_open_port()

print(f"IP: {host}, Recieve port: {RXport}, Transmit port: {TXport}")


