# Import modules
import random
from socket import *
from time import time, sleep

# Set server host and port
server_host = 'localhost'
server_port = 12000

# Set client port
client_port = 12001

# Initialize client Socket
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', client_port))

# Set timeout as 1 second
clientSocket.settimeout(1)
number_of_packets = 10
packets_lost = 0
avg_RTT = 0

print("UDP Pinger Client Running ...")
for sequence_no in range(1, number_of_packets + 1):

    # Generate Ping Message
    start_time = time()
    message = f"Ping {sequence_no} {start_time}"
    clientSocket.sendto(message.encode(), (server_host, server_port))
    print("----------------------------------------")
    print(f"Sequence Number: {sequence_no}")
    try:
        # Message Recieved
        message, address = clientSocket.recvfrom(1024)
        start_time = float(message.decode().split()[2])
        print(f"Reply from {address[0]}: {message.decode()}")
        RTT = time() - start_time
        avg_RTT += RTT
        print(f"RTT: {RTT} s")
    except TimeoutError as e:
        # Timeout
        print("Request timed out")
        packets_lost += 1
    
    sleep(0.5)


print()
print("----------------------------------------")
print("Ping Statistics:")
print(f"Average RTT: {avg_RTT / number_of_packets} ms")
print(f"Packets Lost: {packets_lost} ({packets_lost / number_of_packets * 100} %)")