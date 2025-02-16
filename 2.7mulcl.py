import socket
import threading
import os
import shutil
import subprocess
import glob
import pyautogui

PORT = 12345
ADDRESS = "0.0.0.0"

def handle_client(client_socket, address):
    while True:
        try:
            length = client_socket.recv(4).decode()
            if not length.isdigit():
                client_socket.sendall("0006ERROR".encode())
                continue

            request = client_socket.recv(int(length)).decode()

            if request.upper().startswith("DIR"):
                path = request[4:].strip()
                files = glob.glob(os.path.join(path, "*.*"))
                response = "\n".join(files) if files else "no files found."
            elif request.upper().startswith("DELETE"):
                file_path = request[7:].strip()
                try:
                    os.remove(file_path)
                    response = f"file {file_path} deleted successfully"
                except FileNotFoundError:
                    response = "file not found"
                except Exception as e:
                    response = f"Error: {e}"
            elif request.upper().startswith("COPY"):
                src, dst = request[5:].strip().split()
                try:
                    shutil.copy(src, dst)
                    response = f"file copied from {src} to {dst}"
                except Exception as e:
                    response = f"Error: {e}"
            elif request.upper().startswith("EXECUTE"):
                program = request[8:].strip()
                try:
                    subprocess.call(program, shell=True)
                    response = f"program {program} executed"
                except Exception as e:
                    response = f"Error: {e}"
            elif request.upper() == "SCREENSHOT_TAKE":
                screenshot_path = r"C:\screenshot.jpg"
                image = pyautogui.screenshot()
                image.save(screenshot_path)
                response = f"Screenshot saved at {screenshot_path}"
            elif request.upper() == "PHOTO_SEND":
                screenshot_path = r"C:\screenshot.jpg"
                if os.path.exists(screenshot_path):
                    image_size = os.path.getsize(screenshot_path)
                    size_field = str(len(str(image_size))).zfill(4)
                    client_socket.sendall(size_field.encode())
                    client_socket.sendall(str(image_size).encode())
                    with open(screenshot_path, "rb") as f:
                        client_socket.sendfile(f)
                    continue
                else:
                    response = "Screenshot not found"
            elif request.upper().startswith("NEW_FILE"):
                    name = request[8:].strip()
                    if not name:
                        response = "Error: File name is empty"
                    else:
                        file_path = os.path.join("C:\\Temp\\", name)
                        if not os.path.exists("C:\\Temp\\"):
                            os.makedirs("C:\\Temp\\")
                        try:
                            with open(file_path, 'w') as new_file:
                                response = f"File {name} created successfully at {file_path}"
                        except Exception as e:
                            response = f"Error: {e}"

            full_message = f"{str(len(response)).zfill(4)}{response}"
            client_socket.sendall(full_message.encode())

        except Exception as e:
            print(f"[ERROR] {address}: {e}")
            break

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ADDRESS, PORT))
    server.listen()

    while True:
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

start_server()
