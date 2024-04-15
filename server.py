import cv2
import depthai as dai
from binascii import crc32

import socket, pickle,struct,imutils

# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = "192.168.73.240"
print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Accept client connection
server_socket.bind(socket_address)
server_socket.listen(5)
print("LISTENING AT:",socket_address)
client_socket, client_address = server_socket.accept()
print(f"Client connected from {client_address}")

# Initialize the Oak-D camera
pipeline = dai.Pipeline()

# Add video node to the pipeline
cam = pipeline.createColorCamera()
cam.setBoardSocket(dai.CameraBoardSocket.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_720_P)
cam.setVideoSize(424, 240)

cam.setFps(30)

# Create output for video stream
videoOut = pipeline.createXLinkOut()
videoOut.setStreamName("video")
cam.video.link(videoOut.input)

# Set up the pipeline and start streaming
with dai.Device(pipeline) as device:
    videoQueue = device.getOutputQueue(name="video", maxSize=1, blocking=False)
    
    while True:
        frame = videoQueue.get()
        resized_frame = cv2.resize(frame.getCvFrame(), (424,240))

        # Encode and send frame with checksum:
        data = pickle.dumps(resized_frame)
        data = pickle.dumps(frame.getCvFrame())
        data_size = len(data)
        checksum = crc32(data)
        
        client_socket.sendall(struct.pack("L", data_size))
        client_socket.sendall(struct.pack("L", checksum))
        client_socket.sendall(data)
        
        cv2.imshow("Oak-D Stream", frame.getCvFrame())
        if cv2.waitKey(1) == ord('q'):
            break

# Close connections and release resources
client_socket.close()
server_socket.close()
cv2.destroyAllWindows()