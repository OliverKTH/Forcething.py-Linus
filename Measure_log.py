##################import section###################
import socket
import time
from datetime import datetime
import odrive
from odrive.enums import *
###################################################

host = '127.0.0.1'

kg_to_current = 1.0/1.8
# Define the ODrive object
def get_current_position():
    return motor.axis1.encoder.pos_estimate

def get_current_force():
    return motor.axis1.motor.current_control.Iq_measured / kg_to_current

def get_ports_from_file():
    # Read the ports from the file
    with open("port_info.txt", "r") as file:
        data = file.read().strip()
        tx_port, rx_port = map(int, data.split(","))
        print(f"Read from file - RXport: {rx_port}, TXport: {tx_port}")
    return tx_port, rx_port

Tx, Rx = get_ports_from_file()

try:
    motor = odrive.find_any(timeout = 0.1)
except:
    pass

while True:
    try:
        data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
        recv_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    sock.sendto(meas.encode(), (host, Tx)
                
    current_time = time.time()
    if current_time - last_sample_time >= sample_interval:
        if latest_data is not None:
            # Log the most recent data
            log_data(latest_data, latest_speed, latest_force, recv_time)
        last_sample_time = current_time

    # Sleep briefly to avoid high CPU usage
    time.sleep(0.1)






