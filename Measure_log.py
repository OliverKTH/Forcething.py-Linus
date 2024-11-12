import socket


def get_ports_from_file():
    # Read the ports from the file
    with open("port_info.txt", "r") as file:
        data = file.read().strip()
        tx_port, rx_port = map(int, data.split(","))
        print(f"Read from file - RXport: {rx_port}, TXport: {tx_port}")
    return tx_port, rx_port

Tx, Rx = get_ports_from_file()






