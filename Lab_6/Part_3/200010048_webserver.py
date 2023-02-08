import socket
from random import randint

server_name = "200010048_weberver"
port_number = 80
host_ip = "localhost"


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host_ip, port_number))

print("Socket created listening on port 80 ...")

while True:
    socket.listen(1)
    sock, addr = socket.accept()

    data = sock.recv(4096)
    try:
        filename = data.decode('utf-8').strip().split(" ")[1][1:]
        response_header = "HTTP/1.1 200 OK\n"
        response_header += "Content-Type: text/html\r\n\r\n"
        with open(filename, "r") as f:
            sock.send(response_header.encode())
            for line in f.readlines():
                sock.send(line.encode())
        print("Sent 200 response to client")
    except Exception as e:
        response_header = "HTTP/1.1 404 Not Found\r\n\r\n"
        sock.send(response_header.encode())
        response_message = "404 Not Found\r\n\r\n"
        sock.send(response_message.encode())
        print("Sent 404 response to client")
        pass
