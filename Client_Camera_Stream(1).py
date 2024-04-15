import cv2
import socket
import pickle
import struct
from binascii import crc32

# Connect to server socket
host_ip = "192.168.73.240"  # Replace with server IP address
port = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host_ip, port))

received_data = b''
while True:
    # Receive data size and checksum
    data_size = struct.unpack("L", client_socket.recv(struct.calcsize("L")))[0]
    checksum = struct.unpack("L", client_socket.recv(struct.calcsize("L")))[0]

    # Receive and accumulate data
    while len(received_data) < data_size:
        packet = client_socket.recv(data_size - len(received_data))
        if not packet:
            break
        received_data += packet

    # Verify data integrity
    if crc32(received_data) != checksum:
        print("Error: Data corrupted!")
        received_data = b''
        continue

    # Decode frame from pickle data
    frame = pickle.loads(received_data)
    
    # Display frame
    cv2.imshow("Oak-D Stream (Client)", frame)
    received_data = b''

    # Check for keyboard interrupt
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Close connection and release resources
client_socket.close()
cv2.destroyAllWindows()