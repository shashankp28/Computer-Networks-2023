import socket
from time import sleep
from threading import Thread

class Manager:
    def __init__(self, host, port):
        self.manager_host = host
        self.manager_port = port
        self.active_peers = dict()
        self.manager_socket =  None

    def start(self):
        self.manager_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.manager_socket.settimeout(1)
        self.manager_socket.bind((self.manager_host, self.manager_port))
        
        thread_1 = Thread(target=self.listen)
        thread_2 = Thread(target=self.avalability_scheduler)
        
        thread_1.start()
        thread_2.start()
        
        thread_1.join()
        thread_2.join()
        
    def broadcast_message(self, message):
        print("Broadcasting Message:", message)
        for username, peer in self.active_peers:
            self.manager_socket.sendto(message.encode(), peer)
        return
    
    def peer_list_to_string(self):
        peer_list = ""
        for username, peer in self.active_peers:
            peer_list += str(peer) + "#"
        return "LIST:"+peer_list
    
    def check_availability(self):
        new_list = []
        for peer in self.active_peers:
            peer.send('CHECK:')
            try:
                response = peer.recvfrom(1024).decode()
                if response == 'AVAILABLE:':
                    new_list.append(peer)
            except:
                pass

        if len(new_list) != len(self.active_peers):
            self.active_peers = new_list
            broadcast_message = self.peer_list_to_string()
            self.broadcast_message(broadcast_message)

    def avalability_scheduler(self):
        print("Availability Scheduler Started ...")
        while True:
            self.check_availability()
    
    def handle_message(self, message, address):
        print("Message Arrived:", message.decode(), "From:", address)
        complete = message.split(':')
        if message[0] == 'QUIT':
            try:
                username = complete[1]
                assert self.active_peers[username] == address
                del self.active_peers[username]
            except:
                self.manager_socket.sendto('ERROR:Un-Authorized'.encode(), address)
            
        else:
            try:
                assert self.active_peers.get(complete[1]) == None
                self.active_peers[complete[1]] = address
            except:
                self.manager_socket.sendto('ERROR:Username Already Taken'.encode(), address)
        
        
        broadcast_message = self.peer_list_to_string()
        self.broadcast_message(broadcast_message)
    
    def listen(self):
        print("Started Listening for new peers ...")
        while True:
            try:
                message, address = self.manager_socket.recvfrom(1024)
                self.handle_message(message, address)
            except:
                pass
    

manager = Manager('localhost', 12000)
manager.start()