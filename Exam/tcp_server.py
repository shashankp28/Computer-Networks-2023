import socket


# Define host, port, buffer
host = "localhost"
port = 2832
buffer = 2048

# Object of socket class
TCP_server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)

# Bind to port
TCP_server_socket.bind((host, port))

# Listen
TCP_server_socket.listen(1)

while True:
    print(f"Server Listening on Port {port}")
    connection, address = TCP_server_socket.accept()
    print("----------------------------------------")
    print(f"Connection estabilished with Address: {address}")
    while True:
        try:
            message = connection.recv(buffer).decode()
            nums = [int(x) for x in message.split()]
            new_message = sum(nums)
            print(f"Message recieved: {message}\nSum: {new_message}")
            connection.send(str(new_message).encode())
            

        except:
            print(f"Connection Closed with Address: {address}")
            connection.close()
            break
