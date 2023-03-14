from socket import *
import base64
import sys
import ssl

to_email = input("Type Email Address of Recipient: ")

msg = "\r\n I love computer networks!" 
endmsg = "\r\n.\r\n"


# Choose a mail server (e.g. Google mail server) and call it mailserver 

#Fill in start	
mailserver = "smtp.gmail.com"
#Fill in end


# Create socket called clientSocket and establish a TCP connection with mailserver 

#Fill in start
clientSocket = socket(AF_INET, SOCK_STREAM) 
clientSocket.connect((mailserver, 587))
print("Connection Established")
#Fill in end


recv = clientSocket.recv(1024).decode() 
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')
    sys.exit(0)


# Send HELO command and print server response. 
heloCommand = 'HELO Alice\r\n' 
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')
    sys.exit(0)
print("HELO command sent")

command = "STARTTLS\r\n"
clientSocket.send(command.encode())
recv1 = clientSocket.recv(1024)
print(recv1)
clientSocket = ssl.wrap_socket(clientSocket)
print("Wrapped Socket in SSL")

#Info for username and password
username = "smtplab23@gmail.com"
password = "lmvgusmmhxkmzoti"
base64_str = ("\x00"+username+"\x00"+password).encode()
base64_str = base64.b64encode(base64_str)
authMsg = "AUTH PLAIN ".encode()+base64_str+"\r\n".encode()
clientSocket.send(authMsg)
recv_auth = clientSocket.recv(1024)
print(recv_auth.decode())
print("AUTH command sent")


# Send MAIL FROM command and print server response. 

# Fill in start
mailFrom = f"MAIL FROM: <{username}>\r\n"
clientSocket.send(mailFrom.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')
    sys.exit(0)
print("MAIL FROM command sent")
# Fill in end

# Send RCPT TO command and print server response.

# Fill in start
rcptTo = f"RCPT TO: <{to_email}>\r\n"
clientSocket.send(rcptTo.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')
    sys.exit(0)
print("RCPT TO command sent")
# Fill in end


# Send DATA command and print server response. 

# Fill in start
dataCMD = "DATA\r\n"
clientSocket.send(dataCMD.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '354':
    print('354 reply not received from server.')
    sys.exit(0)
print("DATA command sent")
# Fill in end


# Send message data. 

# Fill in start
clientSocket.send(msg.encode())
# Fill in end

# Message ends with a single period. 

# # Fill in start
clientSocket.send(endmsg.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')
    sys.exit(0)
print("Message sent")
# Fill in end

# Send QUIT command and ge server response.

# Fill in start
quitCMD = "QUIT\r\n"
clientSocket.send(quitCMD.encode())
recv1 = clientSocket.recv(1024).decode() 
print(recv1)
if recv1[:3] != '221':
    print('221 reply not received from server.')
    sys.exit(0)
print("QUIT command sent")
# Fill in end
