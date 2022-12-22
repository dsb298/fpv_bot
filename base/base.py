from queue import Queue
import numpy as np
import threading
import socket
import cv2

# address of your robot
HOST = "192.168.1.162"
PORT = 5415

def recv_frame(s):
    # Get jpeg frame size and convert from bytes
    sizeData = s.recv(2)
    frameSize = int.from_bytes(sizeData, byteorder='big')

    # Want to save read data directly to a preallocated space in memory. Allocate that space here
    frameData = np.empty([frameSize], dtype=np.uint8)
    cntr = 0

    # Get entire frame in order and put into preallocated space in memory
    while(cntr < frameSize):
        buffSize = frameSize - cntr
        dataChunk = np.frombuffer(s.recv(buffSize), dtype=np.uint8)
        length = len(dataChunk)
        frameData[cntr:cntr+length] = dataChunk
        cntr += length

    # Return readable Mat frame
    return cv2.imdecode(frameData, cv2.IMREAD_COLOR)


def video_stream(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        prev_c = ''
        while(1):
            frame = recv_frame(s)
            cv2.imshow("window_name", frame)

            c = cv2.waitKey(10)
            if c != prev_c:
                command.put(c)
            if c == 113:
                cv2.destroyAllWindows()
                break
            prev_c = c
    return

def controller(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT+1))

        while(1):
            val = command.get()
            if(val != -1):
                # com = bytes(str(val),'UTF-8')
                com = int(val).to_bytes(1, byteorder='big')
                sock.sendall(com)

def main():
    command = Queue()

    stream_thread = threading.Thread(target=video_stream, args=(command,))
    control_thread = threading.Thread(target=controller, args=(command,))

    stream_thread.start()
    control_thread.start()

    stream_thread.join()
    control_thread.join()

if __name__ == '__main__':
    main()
