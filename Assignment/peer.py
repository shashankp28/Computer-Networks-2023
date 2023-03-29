import sys
import socket
from time import sleep
from threading import Thread
import os

class Peer:

    def __init__(self, manager_host, manager_port, host, port, username, max):
        self.server_host = host
        self.server_port = port
        self.manager_address = (manager_host, manager_port)
        self.username = username
        self.max_peers = max
        self.peer_data = None
        self.peer_server_socket = None
        self.is_peer_active = True

    def get_new_socket(self, timeout=float('inf')):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout != float('inf'):
            temp_socket.settimeout(timeout)
        return temp_socket

    def decode_peer_list(self, peer_list_string):
        # TODO: From peer list (str) get data structure (List[tuple])
        new_dictionary = dict()
        for data in peer_list_string.split("$"):
            try:
                username, host, port = data.split("|")
                new_dictionary[username] = (host, int(port))
            except Exception as e:
                pass
        return new_dictionary

    def parallel_asker_help(self, username, address, responses, file_name):
        temp_socket = self.get_new_socket(1)
        try:
            temp_socket.connect(address)
            temp_socket.send(f'ASK:{file_name}'.encode())
            message = temp_socket.recv(1024).decode()
            file_size = int(message.split(":")[1])
            responses.append((username, file_size))
        except Exception as e:
            pass
        temp_socket.close()

    def parallel_asker(self, file_name):
        # TODO: Ask all peers if they have required files
        responses = []
        threads = []
        for username, address in self.peer_data.items():
            if username == self.username: continue
            temp_thread = Thread(target=self.parallel_asker_help, args=(
                username, address, responses, file_name))
            temp_thread.start()
            threads.append(temp_thread)
        
        for i in range(len(threads)): threads[i].join()
        print("Responses: ", responses)
        return responses


    def connect_manager(self):
        self.manager_conn_socket.connect(self.manager_address)
        self.manager_conn_socket.send(
            f'JOIN:{self.username}:{self.server_host}:{self.server_port}'.encode())
        message = self.manager_conn_socket.recv(1024)
        print("MANAGER:", message.decode())

    def manager_listner(self):
        self.connect_manager()
        timestamp = 0
        while True:
            if not self.is_peer_active: break
            try:
                message = self.manager_conn_socket.recv(1024).decode()
                if message == "CHECK:":
                    self.manager_conn_socket.send("AVAILABLE:".encode())
                elif message.startswith("LIST:"):
                    peer_list_string = message.split(":")
                    if len(peer_list_string) > 1:
                        new_dict = self.decode_peer_list(peer_list_string[1])
                    self.peer_data = new_dict
            except Exception as e:
                pass
            timestamp += 1

    def disconnect_manager(self):
        self.manager_conn_socket.send(f'QUIT:{self.username}'.encode())
        message = self.manager_conn_socket.recv(1024)
        print("MANAGER:", message.decode())
        self.manager_conn_socket.close()
        self.is_peer_active = False

    def peer_pinger(self):
        while True:
            file_name = input("Enter the file name you want (Q to quit): ")
            if file_name == 'Q': 
                self.disconnect_manager()
                sys.exit(1)
            if file_name in os.listdir():
                print("The file requested already exists...")
                continue
            output_name = input("Enter the name of downloaded file: ")
            available_peers = self.parallel_asker(file_name)
            if len(available_peers) == 0:
                print("File not found with any peer...")
            else:
                print("File found with peer...")
                
    def peer_message_handler(self, connection):
        # TODO: Handle messages from peers
        connection.settimeout(5)
        while True:
            try:
                message = connection.recv(1024).decode()
                if message.startswith("ASK:"):
                    file_name = message.split(":")[1]
                    if file_name in os.listdir():
                        print(f"Found Asked File: {file_name}")
                        connection.send(f"FOUND:{os.path.getsize(file_name)}".encode())
                    else:
                        print(f"Not found Asked File: {file_name}")

            except:
                break
        print("Closed Connection with Peer...")
        connection.close()
        
    def peer_listener(self):
        print("Started Listening for new peers ...")
        while True:
            try:
                connection, addr = self.peer_server_socket.accept()
                new_thread = Thread(target=self.peer_message_handler, args=(connection,))
                new_thread.start()
            except Exception as e:
                if not self.is_peer_active: break
                pass

    
    def start(self):

        # Setup server socket
        self.peer_server_socket = self.get_new_socket(2)
        self.peer_server_socket.bind((self.server_host, self.server_port))
        self.peer_server_socket.listen(self.max_peers)

        # Setup manager connection socket
        self.manager_conn_socket = self.get_new_socket(1)
        
        # Create peer folders
        if (not os.path.exists(self.username)):
            os.mkdir(self.username)
        os.chdir(self.username)

        thread_1 = Thread(target=self.manager_listner)
        thread_2 = Thread(target=self.peer_listener)
        thread_3 = Thread(target=self.peer_pinger)

        thread_1.start()
        thread_2.start()
        thread_3.start()


num = int(input("Enter your peer number: "))
# num = 0
# username = input("Type your username: ")
username = f'username{num}'
peer = Peer(manager_host='localhost', manager_port=12000,
            host='localhost', port=num+7000, username=username, max=10)
peer.start()
