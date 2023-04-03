import socket
import argparse
from time import sleep, time
from threading import Thread


class Manager:
    def __init__(self, host, port, max):
        """
        Initializes a Manager instance.

        Parameters:
        - host (str): the hostname or IP address of the machine where the Manager is running
        - port (int): the port number the Manager will listen to incoming connections on
        - max (int): the maximum number of peers the Manager can handle at once
        """
        self.manager_host = host
        self.manager_port = port
        self.active_peers = dict()
        self.active_conns = dict()
        self.manager_socket = None
        self.max_peers = max
        self.manager_client_socket = None

    def get_new_socket(self, timeout=float('inf')):
        """
        Creates a new socket instance.

        Parameters:
        - timeout (float): optional; the timeout value for the socket (default: infinity)

        Returns:
        - temp_socket (socket): a new socket instance
        """
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout != float('inf'):
            temp_socket.settimeout(timeout)
        return temp_socket

    def start(self):
        """
        Starts the Manager instance and listens for incoming connections from peers.
        """
        
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
        """
        Prints a table of the currently active peers.
        """
        print("Showing Available Peers...")

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
        """Sends the given message to all active connections except the sender.

        Args:
        message (str): The message to be sent to all active connections.
        """
        for username, connection in self.active_conns.items():
            connection.send(message.encode())
        self.printer_help()
        return

    def peer_list_to_string(self):
        """Returns a string representation of the active peers list.

        Returns:
        str: A string representation of the active peers list in the following format:
            "LIST:username1|address1|port1$username2|address2|port2$..."
        """
        peer_list = ""
        for username, address in self.active_peers.items():
            peer_list += f'{username}|{address[0]}|{address[1]}$'
        return "LIST:"+peer_list

    def printer(self):
        """Continuously prints the active connections list every 2 seconds."""
        while True:
            self.printer_help()
            sleep(2)

    def handle_message(self, message, connection):
        """Handles incoming messages from connections and sends appropriate responses.

        Args:
        message (str): The message received from the connection.
        connection (socket): The socket connection from which the message was received.

        Returns:
        bool: True if the message was successfully handled, False if the message is a QUIT message.
        """
        split_message = message.split(':')
        flag = True
        if split_message[0] == 'QUIT':
            return False

        elif split_message[0] == 'LIST':
            peer_message = self.peer_list_to_string()
            connection.send(peer_message.encode())
            return True

        return True

    def start_transaction(self, username, address, port, connection):
        """Starts a new thread for managing a connection with a peer.

        Args:
        username (str): The username of the peer.
        address (str): The IP address of the peer.
        port (str): The port number of the peer.
        connection (socket): The socket connection with the peer.
        """
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
        """Listens for new peer connections and starts a new thread for each connection."""
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


parser = argparse.ArgumentParser(description='Start a manager.')
parser.add_argument('--host', default='localhost', help='host address')
parser.add_argument('--port', type=int, default=12000, help='port number')
parser.add_argument('--max', type=int, default=20, help='maximum number of connections')

args = parser.parse_args()

manager = Manager(host=args.host, port=args.port, max=args.max)
manager.start()
