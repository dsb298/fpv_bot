import numpy as np
import threading
import socket
import time
import cv2
import sys

# address of your robot
HOST = "192.168.1.162"
PORT = 5433

def video_stream():

    camera = cv2.VideoCapture(0)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

    # frame = camera.read()[1]
    # cv2.imwrite('img.png', frame)
    # jpeg_data = cv2.imencode('.jpg', frame, encode_param)[1]
    # image_bytes = jpeg_data.tobytes()
    # image_length = len(image_bytes).to_bytes(4, byteorder='big')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                # Take pic
                frame = camera.read()[1]

                # encode to jpeg and convert to bytes for sending
                jpeg_data = cv2.imencode('.jpg', frame, encode_param)[1]
                image_bytes = jpeg_data.tobytes()

                # Need to send length of data first
                image_length = int(len(image_bytes)).to_bytes(2, byteorder='big')

                # send data
                conn.sendall(image_length)
                resp = conn.recv(1)
                while(resp != b'y'):
                    resp = conn.recv(1)
                conn.sendall(image_bytes)

    camera.release()
    return

def main():
    stream_thread = threading.Thread(target=video_stream)
    stream_thread.start()
    stream_thread.join()

if __name__ == '__main__':
    main()