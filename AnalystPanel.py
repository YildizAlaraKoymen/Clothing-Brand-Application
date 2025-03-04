from tkinter import *
from tkinter import messagebox
import sys


class AnalystPanel(Frame):
    def __init__(self,clientSocket):
        Frame.__init__(self)
        self.master.title('Analyst Panel')
        self.pack()
        self.clientSocket = clientSocket
        serverMsg = self.clientSocket.recv(1024).decode()
        print(f"Received from server: {serverMsg}")

        #Creating the header of the panel
        self.header = Label(self, text="Reports", font=("Arial",12))
        self.header.pack(padx=0,pady=10)

        #Frame for radio buttons
        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.radiobutton =IntVar()

        #Creating the options

        self.option1 =Radiobutton(self.frame1,text="(1)What is the most bought item?",variable=self.radiobutton,value=1)
        self.option1.pack(fill="x",padx=10,pady=2)

        self.option2 = Radiobutton(self.frame1, text="(2)Which store has the highest number of operations?", variable=self.radiobutton, value=2)
        self.option2.pack(fill="x", padx=10, pady=2)

        self.option3 = Radiobutton(self.frame1, text="(3)What is the total generated income of the store?",
                                   variable=self.radiobutton, value=3)
        self.option3.pack(fill="x", padx=10, pady=2)

        self.option4 = Radiobutton(self.frame1, text="(4)What is the most returned color for the Basic T-shirt?",
                                   variable=self.radiobutton, value=4)
        self.option4.pack(fill="x", padx=10, pady=2)

        #Frame for Create and Close buttons

        self.Frame2 = Frame(self)
        self.Frame2.pack(padx=5, pady=5)

        self.button1= Button(self.Frame2,text ="Create", command =self.generateReport)
        self.button1.pack(side=LEFT,padx=5,pady=5)

        self.button2 = Button(self.Frame2, text ="Close", command = self.master.quit)
        self.button2.pack(side=LEFT,padx=5,pady=5)

    def generateReport(self):
        selected_option = self.radiobutton.get()
        if selected_option == 0:
            messagebox.showwarning("Input Error", "Please select an option")
            return

        report_message = f"report;{selected_option}".encode()
        print(f"Sending: {report_message}")
        try:
            # Sending the message to the server
            self.clientSocket.send(report_message)
            print(f"Sent: {report_message}")

            # Receiving the server's response
            server_message = self.clientSocket.recv(1024).decode()
            print(f"Received from server: {server_message}")

            # Handling the server response
            # Extract the report content
            self.displayReport(server_message)

        except Exception as e:
            print(f"Error generating report: {e} at " + str(sys.exc_info()[2].tb_lineno))
            messagebox.showerror("Communication Error", f"An error occurred: {e}")

    def displayReport(self, report):
        report_window = Toplevel(self.master)
        report_window.title("Generated Report")
        Label(report_window, text=report, wraplength=500, justify=LEFT).pack(padx=10,pady=10)