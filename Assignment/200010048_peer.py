import sys
import socket
from time import sleep
from threading import Thread
import os
import argparse


class Peer:

    def __init__(self, manager_host, manager_port, host, port, username, max):
        """
        Initializes a new instance of the Peer class with provided parameters.

        Args:
            manager_host (str): The hostname of the peer manager.
            manager_port (int): The port number of the peer manager.
            host (str): The hostname of the peer.
            port (int): The port number of the peer.
            username (str): The username of the peer.
            max (int): The maximum number of peers to connect to.
        """
        self.server_host = host
        self.server_port = port
        self.manager_address = (manager_host, manager_port)
        self.username = username
        self.max_peers = max
        self.peer_data = None
        self.peer_server_socket = None
        self.is_peer_active = True

    def get_new_socket(self, timeout=float('inf')):
        """
        Creates a new instance of the socket object with the specified timeout value.

        Args:
            timeout (float): The timeout value for the new socket object.

        Returns:
            socket: A new instance of the socket object.
        """
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout != float('inf'):
            temp_socket.settimeout(timeout)
        return temp_socket

    def decode_peer_list(self, peer_list_string):
        """
        Decodes the peer list string and returns a dictionary with username, host and port information.

        Args:
            peer_list_string (str): The string to decode.

        Returns:
            dict: A dictionary with username, host and port information.
        """
        new_dictionary = dict()
        for data in peer_list_string.split("$"):
            try:
                username, host, port = data.split("|")
                new_dictionary[username] = (host, int(port))
            except Exception as e:
                pass
        return new_dictionary

    def parallel_asker_help(self, username, address, responses, file_name):
        """
        A helper function for the parallel_asker method.

        Args:
            username (str): The username of the peer.
            address (tuple): The address of the peer.
            responses (list): A list of responses received.
            file_name (str): The name of the file to retrieve.
        """
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
        """
        Searches for peers that have the requested file.

        Args:
            file_name (str): The name of the file to retrieve.

        Returns:
            list: A list of peers that have the requested file.
        """
        responses = []
        threads = []
        for username, address in self.peer_data.items():
            if username == self.username:
                continue
            temp_thread = Thread(target=self.parallel_asker_help, args=(
                username, address, responses, file_name))
            temp_thread.start()
            threads.append(temp_thread)

        for i in range(len(threads)):
            threads[i].join()
        return responses

    def connect_manager(self):
        """
        Connects to the manager server and sends a JOIN message to the server to register this peer as active. 

        Returns:
            True if connection is successful, False otherwise
        """
        self.manager_conn_socket.connect(self.manager_address)
        self.manager_conn_socket.send(
            f'JOIN:{self.username}:{self.server_host}:{self.server_port}'.encode())
        message = self.manager_conn_socket.recv(1024).decode()
        if message.startswith("ERROR:"):
            print("Error Estabilishing connection...Try changing username... ")
            return False
        return True

    def manager_listner(self):
        """
        Listens to the messages sent by the manager server and updates the peer data dictionary accordingly.

        Returns:
            None
        """
        if not self.connect_manager():
            self.is_peer_active = False
            return
        while True:
            if not self.is_peer_active:
                break
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

    def disconnect_manager(self):
        """
        Sends a QUIT message to the manager server to unregister this peer as active and then closes the connection.

        Returns:
            None
        """
        self.manager_conn_socket.send(f'QUIT:{self.username}'.encode())
        message = self.manager_conn_socket.recv(1024)
        self.manager_conn_socket.close()
        self.is_peer_active = False

    def fetch_helper(self, file_name, chunk, index, file_bytes, remaining, username):
        """
        Helper function to fetch a chunk of a file from a given peer.


        Args:
            file_name: the name of the file being fetched
            chunk: the(start, end) tuple indicating the byte range of the chunk
            index: the index of the chunk being fetched
            file_bytes: the list of byte strings representing the chunks of the file
            remaining: the list indicating which chunks are still remaining to be fetched
            username: the username of the peer from which to fetch the chunk

        Returns:
            None
        """
        try:
            address = self.peer_data[username]
            temp_socket = self.get_new_socket(1)
            temp_socket.connect(address)
            message = f"REQUEST:{file_name}|{chunk[0]}|{chunk[1]}"
            temp_socket.send(message.encode())
            data = temp_socket.recv(65535)
            file_bytes[index] = data
            remaining[index] = True
            print("Chunk ", index, " downloaded...", "From ", username)
        except Exception as e:
            return
        pass

    def handle_fetching(self, file_name, chunks):
        """
        Handles the parallel fetching of a file by dividing it into chunks and fetching them from available peers.


        Args:
            file_name: the name of the file to fetch
            chunks: the list of(start, end) tuples representing the byte ranges of each chunk

        Returns:
            the list of byte strings representing the chunks of the file
        """
        remaining = [False for i in range(len(chunks))]
        file_bytes = [b'' for i in range(len(chunks))]
        while sum(remaining) < len(chunks):
            threads = []
            index = 0
            available_peers = self.parallel_asker(file_name)
            peer_length = len(available_peers)
            peer_index = 0
            if available_peers == 0:
                print("File not found with any peer...")
                return
            while index < len(chunks):
                if remaining[index]:
                    index += 1
                    continue
                file_fetch_thread = Thread(target=self.fetch_helper, args=(
                    file_name, chunks[index], index, file_bytes, remaining, available_peers[peer_index][0]))
                threads.append(file_fetch_thread)
                file_fetch_thread.start()
                peer_index = (peer_index+1) % peer_length
                index += 1
            for i in range(len(threads)):
                threads[i].join()
        return file_bytes

    def peer_pinger(self):
        """
        Main method for peer to search and download files from other active peers.

        Returns:
            None
        """
        if self.is_peer_active == False:
            return
        while True:
            print()
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
                size = min([peer[1] for peer in available_peers])
                no_chunks = (size//4096) + 1
                print(no_chunks, " chunks will be downloaded...")
                recieved = [False for i in range(no_chunks)]
                offsets = [i * size // no_chunks for i in range(no_chunks + 1)]
                offsets[-1] = size
                chunks = [(offsets[i], offsets[i+1]) for i in range(no_chunks)]
                full_file = self.handle_fetching(file_name, chunks)
                if not full_file:
                    continue
                with open(output_name, 'wb') as f:
                    for chunk in full_file:
                        f.write(chunk)

    def peer_message_handler(self, connection):
        """
        The method listens for incoming messages from a peer and handles them accordingly. If the message is an "ASK" message,
        the method checks if the requested file exists in the local directory and responds with a "FOUND" message containing the file size.
        If the message is a "REQUEST" message, the method reads the requested file from the specified byte range and sends it to the peer.
        If the message is anything else, the method breaks out of the loop and closes the connection.

        Args:
            - connection: A socket object representing the connection to the peer.

        Returns:
            - None

        Raises:
            - None
        """
        index = 0
        while True:
            try:
                index += 1
                message = connection.recv(1024).decode()
                if message.startswith("ASK:"):
                    file_name = message.split(":")[1]
                    if file_name in os.listdir():
                        connection.send(
                            f"FOUND:{os.path.getsize(file_name)}".encode())

                elif message.startswith("REQUEST:"):
                    request = message.split(":")[1]
                    file_name = request.split("|")[0]
                    start = int(request.split("|")[1])
                    end = int(request.split("|")[2])
                    with open(file_name, 'rb') as f:
                        f.seek(start)
                        data = f.read(end-start)
                        connection.send(data)

                else:
                    break

            except Exception as e:
                break
        connection.close()

    def peer_listener(self):
        """
        Listens for new peer connections and creates a new thread to handle the messages from the connected peer.
        Runs in an infinite loop until the peer is no longer active.
        """
        if self.is_peer_active == False:
            return
        print("Started Listening for new peers ...")
        while True:
            try:
                connection, addr = self.peer_server_socket.accept()
                new_thread = Thread(
                    target=self.peer_message_handler, args=(connection,))
                new_thread.start()
            except Exception as e:
                if not self.is_peer_active:
                    break
                pass

    def start(self):
        """
        Start the peer-to-peer network.

        This method sets up the server socket and the manager connection socket,
        creates a folder for the peer, and starts the manager listener, peer listener, 
        and peer pinger threads.
        """

        # Setup server socket
        while True:
            try:
                num = int(input("Enter your port number: "))
                username = input("Type your username: ")
                self.username = username
                self.server_port = num
                self.peer_server_socket = self.get_new_socket(2)
                self.peer_server_socket.bind((self.server_host, self.server_port))
                self.peer_server_socket.listen(self.max_peers)
                break
            except:
                print("Port Already in Use...")
                print()

        # Setup manager connection socket
        self.manager_conn_socket = self.get_new_socket(1)

        # Create peer folders
        if (not os.path.exists(self.username)):
            os.mkdir(self.username)
        os.chdir(self.username)
        print()
        print("----------------------------------------------------------------------")
        print(
            f"Store all sharable files in the folder named  '{self.username}'  !!!")
        print("----------------------------------------------------------------------")
        print()

        thread_1 = Thread(target=self.manager_listner)
        thread_2 = Thread(target=self.peer_listener)
        thread_3 = Thread(target=self.peer_pinger)

        thread_1.start()
        sleep(1)
        thread_2.start()
        thread_3.start()


parser = argparse.ArgumentParser(description='Start a peer.')
parser.add_argument('--manager_host', default='localhost',
                    help='manager host address')
parser.add_argument('--manager_port', type=int, default=12000,
                    help='manager host address')
parser.add_argument('--host', default='localhost', help='peer host address')
parser.add_argument('--max', type=int, default=20,
                    help='maximum number of peers')

args = parser.parse_args()


peer = Peer(manager_host=args.manager_host, manager_port=args.manager_port,
            host=args.host, port=None, username=None, max=args.max)
peer.start()
