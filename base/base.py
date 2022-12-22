import numpy as np
import threading
import socket
import cv2

# address of your robot
HOST = "192.168.1.162"
PORT = 5433

def recv_frame(s):
    # Get jpeg frame size and convert from bytes
    sizeData = s.recv(2)
    frameSize = int.from_bytes(sizeData, byteorder='big')

    # Let server know we received the size, and is now safe to send data
    s.sendall(b'y')

    # Want to save read data directly to a preallocated space in memory. Allocate that space here
    frameData = np.empty([frameSize], dtype=np.uint8)
    cntr = 0

    # Get entire frame in order and put into preallocated space in memory
    while(cntr < frameSize):
        dataChunk = np.frombuffer(s.recv(1024), dtype=np.uint8)
        length = len(dataChunk)
        try:
            frameData[cntr:cntr+length] = dataChunk
        except ValueError:
            frameData[cntr:cntr+length-2] = dataChunk
        cntr += length

    # Return readable Mat frame
    return cv2.imdecode(frameData, cv2.IMREAD_COLOR)


def video_stream():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while(1):
            frame = recv_frame(s)
            cv2.imshow("window_name", frame)
            c = cv2.waitKey(1)
            if c == 27:
                cv2.destroyAllWindows()
                return
    return

def main():
    stream_thread = threading.Thread(target=video_stream)
    stream_thread.start()
    stream_thread.join()

if __name__ == '__main__':
    main()
