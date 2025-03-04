from socket import *
from tkinter import *
from tkinter import messagebox

from ClientThread import ClientThread


class LoginScreen(Frame):
    def __init__(self, clientSocket):
        Frame.__init__(self)
        self.clientSocket = clientSocket
        serverMsg = self.clientSocket.recv(1024).decode()
        print(f"Received from server: {serverMsg}")
        print(serverMsg)

        self.master.title("Login")
        self.pack()

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.userNameLabel = Label(self.frame1, text="Username:")
        self.userNameLabel.pack(side=LEFT, padx=5, pady=5)

        self.userNameEntry = Entry(self.frame1, name="username")
        self.userNameEntry.pack(side=LEFT, padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.passwordLabel = Label(self.frame2, text="Password:")
        self.passwordLabel.pack(side=LEFT, padx=5, pady=5)

        self.passwordEntry = Entry(self.frame2, name="password", show = "*")
        self.passwordEntry.pack(side=LEFT, padx=5, pady=5)

        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.loginButton = Button(self.frame3, text="Login", command=self.sendMessage)
        self.loginButton.pack(side=LEFT, padx=5, pady=5)

    def sendMessage(self):
        if not self.userNameEntry.get() or not self.passwordEntry.get():
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
        loginMsg = ("login;" + self.userNameEntry.get() + ";" + self.passwordEntry.get()).encode()
        print(f"Sending: {loginMsg}")
        self.clientSocket.send(loginMsg)
        serverMsg = self.clientSocket.recv(1024).decode()
        print("Login confirmed")
        loginStatus = serverMsg.split(";")[0]
        if loginStatus == "loginfailure":
            messagebox.showinfo(loginStatus, "Login failed")
        elif loginStatus == "loginsuccess":
            print(f"Sending: {serverMsg.encode()}")
            self.clientSocket.send(serverMsg.encode())
            self.master.destroy()


