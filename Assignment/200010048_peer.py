import sys
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

    
    def get_new_socket(self, timeout=float('inf')):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout != float('inf'):
            temp_socket.settimeout(timeout)
        return temp_socket


    def connect_manager(self):
        self.manager_conn_socket.connect(self.manager_address)
        self.manager_conn_socket.send(f'JOIN:{self.username}:{self.server_host}:{self.server_port}'.encode())
        message = self.manager_conn_socket.recv(1024)
        print("MANAGER:", message.decode())
        
    def manager_listner(self):
        self.connect_manager()
        timestamp = 0
        while True:
            try:
                message = self.manager_conn_socket.recv(1024).decode()
                if message == "CHECK:":
                    self.manager_conn_socket.send("AVAILABLE:".encode())
                elif message != "":
                    print(message)
            except Exception as e:
                pass
            timestamp += 1


        
    def disconnect_manager(self):
        self.manager_conn_socket.send(f'QUIT:{self.username}'.encode())
        message = self.manager_conn_socket.recv(1024)
        print("MANAGER:", message.decode())
        self.manager_conn_socket.close()
    
    def downloader(self):
        while True:
            pass 
        
    def start(self):
        
        # Setup server socket
        # self.peer_server_socket = self.get_new_socket(1)
        # self.peer_server_socket.bind((self.server_host, self.server_port))
        # self.peer_server_socket.listen(self.max_peers)

        # Setup manager connection socket
        self.manager_conn_socket = self.get_new_socket(1)

        # TODO: Setup peer connection socket
        # self.peer_client_socket = self.get_new_socket(1)
        
        thread_1 = Thread(target=self.manager_listner)
        thread_2 = Thread(target=self.downloader)
        
        thread_1.start()
        thread_2.start()
        


# num = int(sys.argv[2])
num = 0
# username = input("Type your username: ")
username = f'username{num}'
peer = Peer(manager_host='localhost', manager_port=12000,
            host='localhost', port=num+7000, username=username, max=10)
peer.start()
