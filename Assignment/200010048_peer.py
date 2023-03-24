import socket
from time import sleep
from threading import Thread


class Peer:
    
    def __init__(self, manager_host, manager_port, host, port, username, max):
        self.server_host = host
        self.server_port = port
        self.manager_address = (manager_host, manager_port)
        self.username = username
        self.max_peers = max
        
        # Setup server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.settimeout(1)
        self.server_socket.listen(self.max_peers)
        
        # Setup client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(1)

    def connect_manager(self):
        self.client_socket.connect(self.manager_address)
        self.client_socket.send(f'JOIN:{self.username}:{self.server_host}:{self.server_port}'.encode())
        message = self.client_socket.recv(1024)
        print("MANAGER:", message.decode())

        
    def disconnect_manager(self):
        self.client_socket.send(f'QUIT:{self.username}'.encode())
        message = self.client_socket.recv(1024)
        print("MANAGER:", message.decode())
        self.client_socket.close()
    
    
    def test(self):
        self.connect_manager()
        sleep(5)
        self.disconnect_manager()


# username = input("Type your username: ")
username = 'hello'
peer = Peer('localhost', 12000, 'localhost', 8888, username, 10)
peer.test()
