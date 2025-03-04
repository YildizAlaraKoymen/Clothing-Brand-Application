from StorePanel import StorePanel

HOST = "127.0.0.1"
PORT = 5000

from socket import *
from tkinter import *
from tkinter import messagebox

from LoginScreen import LoginScreen
from StorePanel import StorePanel
from AnalystPanel import AnalystPanel

if __name__ == "__main__":
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((HOST, PORT))
    window = LoginScreen(clientSocket)
    window.mainloop()
    serverMsg = clientSocket.recv(1024).decode()
    print(f"Received from server: {serverMsg}")
    role = serverMsg.split(";")[2]
    if role == "store":#If role is store -> open store panel
        print("Role confirmed, opening store panel")
        print(f"Sending: {serverMsg.encode()}")
        clientSocket.send(serverMsg.encode())
        window = StorePanel(clientSocket)
        window.mainloop()
    elif role == "analyst":#If role is analyst -> open analyst panel
        print("Role confirmed, opening analyst panel")
        print(f"Sending: {serverMsg.encode()}")
        clientSocket.send(serverMsg.encode())
        window = AnalystPanel(clientSocket)
        window.mainloop()
