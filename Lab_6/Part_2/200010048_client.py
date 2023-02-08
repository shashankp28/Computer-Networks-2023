import socket
from random import randint


client_name = "200010048_client"
random_integer = randint(1, 100)
message = f'{client_name} {random_integer}'

target_host = "localhost"
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
client.send(message.encode())

response = client.recv(4096)

message = response.decode().split()

try:
    print("Server response")
    print("Server Name:", message[0])
    print("Server Number:", message[1])
except:
    print("Server Error")
