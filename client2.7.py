import socket

SERVER_IP = "127.0.0.1"
PORT = 12345

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, PORT))
    print("Connected to the server.")

    while True:
        command = input("Enter a command: ").strip()
        length = str(len(command)).zfill(4)
        full_message = length + command
        client.sendall(full_message.encode())

        if command.upper().startswith("PHOTO_SEND"):
            header_length = int(client.recv(4).decode())
            image_size = int(client.recv(header_length).decode())
            with open("received_screenshot.jpg", "wb") as f:
                received = 0
                while received < image_size:
                    data = client.recv(4096)
                    f.write(data)
                    received += len(data)
            print("Screenshot received.")
        else:
            length_field = client.recv(4).decode()
            response_length = int(length_field)
            response = client.recv(response_length).decode()
            print(response)

        if command.upper() == "EXIT":
            break

    client.close()

start_client()
