from socket import *
from threading import *
from ClientThread import ClientThread
from ServerData import ServerData

HOST = "127.0.0.1"
PORT = 5000

if __name__ == "__main__":
    serverData = ServerData()  # Load user data
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind((HOST, PORT))
    serverSocket.listen()

    print(f"Server listening on {HOST}:{PORT}")
    while True:
        try:
            clientSocket, clientAddress = serverSocket.accept()
            print(f"Connection from {clientAddress}")
            newClient = ClientThread(clientSocket, clientAddress, serverData)
            newClient.start()

            print("All clients have finished.")
        except Exception as e:
            print(f"Error starting the server: {e}")
