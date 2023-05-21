import socket
import struct

host = "127.0.0.1"
port = int(input("Port: "))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

while True:
  input_type = int(input("1: Send message without expecting response\n2: Send message and receive response\n3: Send message size first, then the message without expecting response\n4: Send message size first, then the message and receive response\nInput Type: "))
  if input_type == 0:
    break
  else:
    message_to_send = input("Message: ")
    print("message : ", message_to_send)
    if input_type == 1:
      s.send(bytes(message_to_send, "utf-8"))
    elif input_type == 2:
      s.send(bytes(message_to_send, "utf-8"))
      received_message = s.recv(1024)
      print("Received:", str(received_message))
    elif input_type == 3:
      message_size = struct.calcsize(str(len(message_to_send)) + "s")
      s.send(bytes(str(message_size), "utf-8"))
      s.send(bytes(message_to_send, "utf-8"))
    elif input_type == 4:
      message_size = struct.calcsize(str(len(message_to_send)) + "s")
      s.send(bytes(str(message_size), "utf-8"))
      s.send(bytes(message_to_send, "utf-8"))
      received_message = s.recv(1024)
      print("Received:", str(received_message))

s.close()
