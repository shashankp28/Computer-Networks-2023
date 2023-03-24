import socket
from time import sleep
from threading import Thread

class Manager:
    def __init__(self, host, port, client_host, client_port, max):
        self.manager_host = host
        self.manager_port = port
        self.active_peers = dict()
        self.active_conns = dict()
        self.manager_socket =  None
        self.max_peers = max
        self.manager_client_host = client_host
        self.manager_client_port = client_port
        self.manager_client_socket = None

    def start(self):
        # Manager Server
        self.manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager_socket.bind((self.manager_host, self.manager_port))
        self.manager_socket.listen(self.max_peers)

        # Manager Client
        self.manager_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager_client_socket.settimeout(1)
        
        thread_1 = Thread(target=self.new_connections)
        # thread_2 = Thread(target=self.avalability_scheduler)
        # thread_3 = Thread(target=self.printer)
        
        thread_1.start()
        # thread_2.start()
        # thread_3.start()
        
        thread_1.join()
        # thread_2.join()
        # thread_3.join()
        
    def broadcast_message(self, message):
        print("Broadcasting Message:", message)
        for username, address in self.active_peers.items():
            self.manager_client_socket.connect(address)
            self.manager_client_socket.send(message.encode())
            self.manager_client_socket.close()
        return
    
    def peer_list_to_string(self):
        peer_list = ""
        print(self.active_peers)
        for username, address in self.active_peers.items():
            peer_list +=  f'{username}:{address[0]}:{address[1]}#'
        return "LIST:"+peer_list
    
    def check_availability(self):
        new_active = dict()
        new_conns = dict()
        for username, address in self.active_peers.items():
            try:
                self.manager_client_socket.connect(address)
                self.manager_client_socket.send('CHECK:'.encode())
                response = self.active_conns[username].recv(1024)
                if response.decode() == 'AVAILABLE:':
                    new_active[username] = address
                    new_conns[username] = self.active_conns[username]
                self.manager_client_socket.close()
            except Exception as e:
                print(e)

        if len(new_active) != len(self.active_peers):
            self.active_peers = new_active
            self.active_conns = new_conns
            broadcast_message = self.peer_list_to_string()
            self.broadcast_message(broadcast_message)
    
    def printer(self):
        while True:
            print(self.peer_list_to_string())
            sleep(1)

    def avalability_scheduler(self):
        print("Availability Scheduler Started ...")
        while True:
            self.check_availability()
            sleep(10)
            
    
    def handle_message(self, message, connection):
        complete = message.split(':')
        flag = True
        print(complete)
        if message[0] == 'QUIT':
            try:
                username = complete[1]
                del self.active_peers[username]
                del self.active_conns[username]
                connection.send('SUCCESS:De-Registered')
                flag = False

            except Exception as e:
                print(e)
                connection.send('ERROR:Un-Authorized'.encode())
                flag = True
            
        else:
            try:
                assert self.active_peers.get(complete[1]) == None
                self.active_peers[complete[1]] = (complete[2], int(complete[3]))
                self.active_conns[complete[1]] = connection
                connection.send('SUCCESS:Registered'.encode())
                flag = True
            except Exception as e:
                print(e)
                connection.send('ERROR:Bad Request'.encode())
                flag = False
        

        broadcast_message = self.peer_list_to_string()
        self.broadcast_message(broadcast_message)
        return flag
        
    def start_transaction(self, connection):
        print("Started Transaction ...")
        while True:
            message = connection.recv(1024)
            try:
                assert self.handle_message(message.decode(), connection)
            except Exception as e:
                print(e)
                break
            
    
    def new_connections(self):
        print("Started Listening for new peers ...")
        while True:
            try:
                connection, addr = self.manager_socket.accept()
                new_thread = Thread(target=self.start_transaction, args=(connection,))
                new_thread.start()
            except Exception as e:
                print(e)
            
    

manager = Manager('localhost', 12000, 'localhost', 12001, 10)
manager.start()