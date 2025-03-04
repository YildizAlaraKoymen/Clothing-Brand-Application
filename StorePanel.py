from operator import indexOf
from socket import *
from tkinter import *
from tkinter import messagebox
import sys

from ServerData import ServerData

class StorePanel(Frame):
    def __init__(self, clientSocket):
        Frame.__init__(self)
        self.clientSocket = clientSocket
        serverMsg = self.clientSocket.recv(1024).decode()
        print(f"Received from server: {serverMsg}")

        self.loginInfo = serverMsg

        self.master.title("Store Panel")

        itemLabel = Label(self.master, text = "Items", font = ("Arial", 14))
        itemLabel2 = Label(self.master)

        itemLabel.grid(row = 0, column = 0, sticky = "n", pady = 2)
        itemLabel2.grid(row = 0, column = 1, sticky = "n", pady = 2)

        data = ServerData()

        self.items = []
        for item in data.items:
            self.items.append((item, BooleanVar()))

        rows = 1
        self.quantity = {}
        self.color = {}

        for item in self.items:
            itemSelection = Checkbutton(self.master, text = item[0].itemName, variable = item[1], name = item[0].itemID)
            itemSelection.grid(row = rows, column = 0, sticky = "w", pady = 2)
            quantityLabel = Label(self.master, text = "Quantity:")
            quantityEntry = Entry(self.master)
            quantityLabel.grid(row=rows, column=1, sticky="n", pady=2)
            quantityEntry.grid(row = rows, column = 2, sticky = "n", pady = 2)
            self.quantity[item[0].itemID] = quantityEntry
            colorLabel = Label(self.master, text = "Color:")
            colorLabel.grid(row = rows, column = 3, sticky = "n", pady = 2)
            colors = list(item[0].type.keys())
            self.color[item[0].itemID] = StringVar()
            self.color[item[0].itemID].set(colors[0])
            columns = 4
            for key in colors:
                colorSelection = Radiobutton(self.master, text = key, value = key, variable = self.color[item[0].itemID], name = item[0].itemID + "-" + key)
                colorSelection.grid(row = rows, column = columns, sticky = "w", pady = 2)

                columns += 1
            rows += 1

        rows += 1
        space = Label(self.master)
        space.grid(row = rows)
        rows += 1
        customerNameLabel = Label(self.master, text = "Customer name:")
        self.customerNameEntry = Entry(self.master, name = "customername")
        customerNameLabel.grid(row = rows, column = 1, sticky = "n", pady = 2)
        self.customerNameEntry.grid(row = rows, column = 2, sticky = "n", pady = 2)

        rows += 1
        PurchaseButton = Button(self.master, text = "Purchase", command = self.sendPurchase)
        PurchaseButton.grid(row = rows, column = 1, sticky = "e", pady = 2)

        ReturnButton = Button(self.master, text = "Return", command = self.sendReturn)
        ReturnButton.grid(row = rows, column = 2, sticky = "n", pady = 2)

        CloseButton = Button(self.master, text = "Close", command = self.close)
        CloseButton.grid(row = rows, column = 3, sticky = "w", pady = 2)

        self.selectedItems = []

    def fillSelectedItems(self):
        for item in self.items:
            if item[1].get():
                if self.quantity[item[0].itemID].get() != "":
                    self.selectedItems.append(item[0])

    def emptySelectedItems(self):
        self.selectedItems = []

    def createMessage(self):

        self.emptySelectedItems()
        self.fillSelectedItems()

        itemInfo = []
        for item in self.selectedItems:
            quantity = self.quantity[item.itemID].get()
            color = self.color[item.itemID].get()
            msg = quantity + "-" + item.itemID + "-" + color
            itemInfo.append(msg)

        itemList = ""
        for item in itemInfo:
            itemList = itemList + item
            if itemInfo.index(item) != len(itemInfo) - 1:
                itemList = itemList + ";"

        return itemList

    def totalQuantity(self):
        self.emptySelectedItems()
        self.fillSelectedItems()
        totalQuantity = 0
        for item in self.selectedItems:
            totalQuantity = int(self.quantity[item.itemID].get()) + totalQuantity

        return str(totalQuantity)

    def getUsername(self):
        return self.loginInfo.split(";")[1]

    def getItem(self, ID):
        for item in self.items:
            if item[0].itemID == ID:
                return item[0]

    def availabilityMessage(self, items):
        try:
            message = ""
            for item in items:
                quantity = item.split("-")[0]
                itemID = item.split("-")[1]
                color = item.split("-")[2]
                unavailableItem = self.getItem(itemID)
                message = "item name: " + unavailableItem.itemName + "-" + color + "-amount: " + quantity + message
                if len(items) - 1 != items.index(item):
                    message = "item name: " + unavailableItem.itemName + "-" + color + "-amount: " + quantity + message + ","

                return "These items are not available: " + message
        except Exception as e:
            print(f"Error creating availability message: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def sendPurchase(self):
        try:
            if self.customerNameEntry.get() == "":
                messagebox.showinfo("Error", "Please enter a customer name.")
                return
            sendStorePanel = "purchase;" + self.getUsername() + ";" + self.totalQuantity() + ";" + self.createMessage() + ";" + self.customerNameEntry.get()
            print(f"Sending: {sendStorePanel.encode()}")
            self.clientSocket.send(sendStorePanel.encode())
            serverMsg = self.clientSocket.recv(1024).decode()
            print(f"Received from server: {serverMsg}")
            status = serverMsg.split(";")[0]
            if status == "purchasesuccess":
                totalOrderCost = serverMsg.split(";")[1]
                messagebox.showinfo("successful operation", "your purchase was completed successfully\nTotal order cost: " + totalOrderCost)
            elif status == "availabilityerror":
                items = serverMsg.split(";")[1:]
                messagebox.showinfo("availability error",self.availabilityMessage(items))
        except Exception as e:
            print(f"Error sending purchase info: {e} at " + str(sys.exc_info()[2].tb_lineno))


    def sendReturn(self):
        try:
            if self.customerNameEntry.get() == "":
                messagebox.showinfo("Error", "Please enter a customer name.")
                return
            sendStorePanel = "return;" + self.getUsername() + ";" + self.totalQuantity() + ";" + self.createMessage() + ";" + self.customerNameEntry.get()
            print(f"Sending: {sendStorePanel.encode()}")
            self.clientSocket.send(sendStorePanel.encode())
            serverMsg = self.clientSocket.recv(1024).decode()
            print(f"Received from server: {serverMsg}")
            if serverMsg == "returnerror":
                messagebox.showinfo("unsuccessful operation", "unsuccessful operation – please re-check the items")
            elif serverMsg == "returnsuccess":
                messagebox.showinfo("successful operation", "your return was completed successfully")
        except Exception as e:
            print(f"Error sending purchase info: {e} at " + str(sys.exc_info()[2].tb_lineno))
    def close(self):
        self.master.destroy()
