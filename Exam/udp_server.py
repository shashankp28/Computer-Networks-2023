import socket

# Define Host, Port and Buffer
host = "localhost"
port = 2832
buffer_size = 2048

# Object of sokcet class with UDP
UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind the sokcet object to a host and port
# Listening Started
UDP_server_socket.bind((host, port))

print("UDP Server Started...")

while True:
    message, address = UDP_server_socket.recvfrom(buffer_size)
    print("----------------------------------------------")
    print(f"Client message: {message.decode()}\nAddress: {address}")
    num_sum = sum([int(x) for x in message.decode().split()])

    UDP_server_socket.sendto(str(num_sum).encode(), address)

