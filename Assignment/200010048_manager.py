import socket
from time import sleep, time
from threading import Thread


class Manager:
    def __init__(self, host, port, max):
        self.manager_host = host
        self.manager_port = port
        self.active_peers = dict()
        self.active_conns = dict()
        self.manager_socket = None
        self.max_peers = max
        self.manager_client_socket = None
    
    def get_new_socket(self, timeout=float('inf')):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout != float('inf'):
            temp_socket.settimeout(timeout)
        return temp_socket

    def start(self):
        # Manager Server
        self.manager_socket = self.get_new_socket()
        self.manager_socket.bind((self.manager_host, self.manager_port))
        self.manager_socket.listen(self.max_peers)

        # Manager Client
        self.manager_client_socket = self.get_new_socket(1)

        thread_1 = Thread(target=self.new_connections)
        thread_3 = Thread(target=self.printer)

        thread_1.start()
        thread_3.start()

        thread_1.join()
        thread_3.join()

    def broadcast_message(self, message):
        print("Broadcasting Message:", message)
        for username, connection in self.active_conns.items():
            connection.send(message.encode())
        return

    def peer_list_to_string(self):
        peer_list = ""
        for username, address in self.active_peers.items():
            peer_list += f'{username}|{address[0]}|{address[1]}$'
        return "LIST:"+peer_list


    def printer(self):
        while True:
            print(self.peer_list_to_string())
            sleep(1)

    def handle_message(self, message, connection):
        split_message = message.split(':')
        flag = True
        print(split_message)
        if split_message[0] == 'QUIT':
            return False
            
        elif split_message[0] == 'LIST':
            peer_message = self.peer_list_to_string()
            connection.send(peer_message.encode())
            return True
        
        return True


    def start_transaction(self, username, address, port, connection):
        print("Started Transaction ...")
        timestamp = 0
        while True:
            try:
                if timestamp%10 != 0:
                    try:
                        message = connection.recv(1024)
                        assert self.handle_message(message.decode(), connection)
                    except TimeoutError as e:
                        pass
                else:
                    print(f"Checking for {username} ...")
                    connection.send("CHECK:".encode())
                    response = connection.recv(1024).decode()
                    assert response == "AVAILABLE:"
                timestamp += 1
            except Exception as e:
                print(e)
                break
        
        self.active_conns.pop(username)
        self.active_peers.pop(username)
        broadcast_message = self.peer_list_to_string()
        self.broadcast_message(broadcast_message)
        connection.send("SUCCESS:Quit".encode())
        connection.close()
        print("Ended Transaction ...")
        return

    def new_connections(self):
        print("Started Listening for new peers ...")
        while True:
            try:
                connection, addr = self.manager_socket.accept()
                connection.settimeout(1)
                title, username, address, port = connection.recv(1024).decode().split(':')
                assert title == "JOIN"
                assert self.active_peers.get(username) == None
                self.active_peers[username] = (address, port)
                self.active_conns[username] = connection
                connection.send('SUCCESS:Registered'.encode())
                broadcast_message = self.peer_list_to_string()
                self.broadcast_message(broadcast_message)
                new_thread = Thread(
                    target=self.start_transaction, args=(username, address, port, connection))
                new_thread.start()
            except Exception as e:
                connection.send('ERROR:Bad Request'.encode())
                print(e)


manager = Manager(host='localhost', port=12000, max=10)
manager.start()
