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
        thread_2 = Thread(target=self.printer)

        thread_1.start()
        thread_2.start()

        thread_1.join()
        thread_2.join()
    
    def printer_help(self):
        print("Showing Availabel Peers...")

        username_heading = 'Username'
        host_heading = 'Host'
        port_heading = 'Port'

        username_max_len = len(username_heading)
        host_max_len = len(host_heading)
        port_max_len = len(port_heading)
        max_lengths = [username_max_len, host_max_len, port_max_len]

        for user, (host, port) in self.active_peers.items():
            max_lengths[0] = max(max_lengths[0], len(user))
            max_lengths[1] = max(max_lengths[1], len(host))
            max_lengths[2] = max(max_lengths[2], len(str(port)))

        username_format = f'{{:<{max_lengths[0]}}}'
        host_format = f'{{:<{max_lengths[1]}}}'
        port_format = f'{{:<{max_lengths[2]}}}'

        top_border = f'+{"-" * (max_lengths[0] + 2)}+{"-" * (max_lengths[1] + 2)}+{"-" * (max_lengths[2] + 2)}+'
        bottom_border = top_border
        left_border = '|'
        right_border = '|'

        print(top_border)
        print(f'{left_border} {username_format.format(username_heading)} {right_border} {host_format.format(host_heading)} {right_border} {port_format.format(port_heading)} {right_border}')
        print(
            f'{left_border}{"-" * max_lengths[0]}-+-{"-" * max_lengths[1]}-+-{"-" * max_lengths[2]}--{right_border}')

        index = 0
        for user, (host, port) in self.active_peers.items():
            print(f'{left_border} {username_format.format(user)} {right_border} {host_format.format(host)} {right_border} {port_format.format(port)} {right_border}')
            if index != len(self.active_peers)-1:
                print("-"*len(top_border))
            index += 1

        print(bottom_border+"\n")
        return

    def broadcast_message(self, message):
        for username, connection in self.active_conns.items():
            connection.send(message.encode())
        self.printer_help()
        return

    def peer_list_to_string(self):
        peer_list = ""
        for username, address in self.active_peers.items():
            peer_list += f'{username}|{address[0]}|{address[1]}$'
        return "LIST:"+peer_list

    def printer(self):
        while True:
            self.printer_help()
            sleep(2)

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
        timestamp = 0
        while True:
            try:
                if timestamp % 3 == 0:
                    try:
                        message = connection.recv(1024)
                        assert self.handle_message(
                            message.decode(), connection)
                    except TimeoutError as e:
                        pass
                else:
                    connection.send("CHECK:".encode())
                    response = connection.recv(1024).decode()
                    assert response == "AVAILABLE:"
                timestamp = (timestamp+1) % 3
            except Exception as e:
                print(e)
                break

        self.active_conns.pop(username)
        self.active_peers.pop(username)
        broadcast_message = self.peer_list_to_string()
        self.broadcast_message(broadcast_message)
        try:
            connection.send("SUCCESS:Quit".encode())
            connection.close()
        except:
            pass
        return

    def new_connections(self):
        print("Started Listening for new peers ...")
        while True:
            try:
                connection, addr = self.manager_socket.accept()
                connection.settimeout(1)
                title, username, address, port = connection.recv(
                    1024).decode().split(':')
                assert title == "JOIN"
                assert self.active_peers.get(username) == None
                self.active_peers[username] = (address, port)
                self.active_conns[username] = connection
                connection.send('SUCCESS:Registered'.encode())
                broadcast_message = self.peer_list_to_string()
                self.broadcast_message(broadcast_message)
                new_thread = Thread(target=self.start_transaction, args=(
                    username, address, port, connection))
                new_thread.start()
            except Exception as e:
                connection.send('ERROR:Bad Request'.encode())


manager = Manager(host='localhost', port=12000, max=10)
manager.start()
