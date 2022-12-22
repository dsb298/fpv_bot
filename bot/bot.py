import RPi.GPIO as GPIO
import numpy as np
import threading
import socket
import cv2

GPIO.setmode(GPIO.BCM)

# address of your robot
HOST = "192.168.1.162"
PORT = 5415

def video_stream():

    camera = cv2.VideoCapture(0)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

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
                conn.sendall(image_bytes)

    camera.release()
    return

def stop():
    GPIO.output(12, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)

def forward():
    GPIO.output(12, GPIO.LOW)
    GPIO.output(13, GPIO.HIGH)
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(19, GPIO.LOW)

def reverse():
    GPIO.output(12, GPIO.HIGH)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(19, GPIO.HIGH)

def left():
    GPIO.output(12, GPIO.HIGH)
    GPIO.output(13, GPIO.HIGH)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)

def right():
    GPIO.output(12, GPIO.LOW)
    GPIO.output(13, GPIO.LOW)
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(19, GPIO.HIGH)

def control_bot():
    GPIO.setup(12, GPIO.OUT) #0
    GPIO.setup(13, GPIO.OUT) #1
    GPIO.setup(18, GPIO.OUT) #0
    GPIO.setup(19, GPIO.OUT) #1

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT+1))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                command = conn.recv(1)
                com = int.from_bytes(command, byteorder='big')
                if com == 113:
                    stop()
                    break
                elif com == 119:
                    forward()
                elif com == 115:
                    reverse()
                elif com == 97:
                    left()
                elif com == 100:
                    right()
                elif com == 32:
                    stop()

def main():
    stream_thread = threading.Thread(target=video_stream)
    control_thread = threading.Thread(target=control_bot)

    stream_thread.start()
    control_thread.start()

    stream_thread.join()
    control_thread.join()

if __name__ == '__main__':
    main()