# import socket

# # Server Configuration
# HOST = "127.0.0.1"  # receiver's IP, now is localhost for testing
# PORT = 65432       # Must match sender's port

# # Create a TCP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind((HOST, PORT))
# sock.listen()

# print(f"Listening for connections on {HOST}:{PORT}...")

# # Accept connection
# conn, addr = sock.accept()
# print(f"Connected by {addr}")

# # Receive and print data
# try:
#     while True:
#         data = conn.recv(1024)  # Receive data in chunks
#         if not data:
#             break  # Exit if no data received
#         print("Received Data:", data.decode())
# finally:
#     conn.close()
#     print("Connection closed")

import socket

def run_server(port):
    HOST = '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        print(f"Server listening on port {port}...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr} on port {port}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Received on port {port}: {data.decode()}")

if __name__ == "__main__":
    # Run three servers, one for each port (can run these in different terminals)
    import threading
    ports = [9000, 9001, 9002, 9003]
    threads = []
    for port in ports:
        t = threading.Thread(target=run_server, args=(port,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
