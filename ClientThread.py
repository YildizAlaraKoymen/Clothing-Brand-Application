import sys
from threading import Thread
from typing import ItemsView
from Operation import *

from ServerData import ServerData
import threading

class ClientThread(Thread):
    def __init__(self, clientSocket, clientAddress, serverData):
        super().__init__()
        self.clientSocket = clientSocket
        self.clientAddress = clientAddress
        self.serverData = serverData
        self.lock = threading.RLock()
        print("Connection successful from ", self.clientAddress)

    def getUser(self, username):#Return user object by username
        for user in self.serverData.users:
            if user.username == username:
                return user

        return None

    def findRole(self, username):#Return user role by username
        user = self.getUser(username)
        if user is not None:
            return user.role
        else:
            return None

    def createLoginMessage(self, status, clientMsg):#Create login message
        if status:
            records = clientMsg.split(";")
            records[0] = "loginsuccess"
            records[2] = self.findRole(records[1])
            return ";".join(records)
        else:
            return "loginfailure"

    def checkLogin(self, username, password, clientMsg):#Authenticate login credentials
        try:
            for user in self.serverData.users:
                if user.username == username:
                    if user.password == password:
                        serverMsg = self.createLoginMessage(True, clientMsg)
                        print(f"Sending: {serverMsg}")
                        self.clientSocket.send(serverMsg.encode())
                        return
            serverMsg = self.createLoginMessage(False, clientMsg).encode()
            print(f"Sending: {serverMsg}")
            self.clientSocket.send(serverMsg)
        except Exception as e:
            print(f"Error checking login: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def getItem(self, ID):#Get item based on ID
        for item in self.serverData.items:
            if item.itemID == ID:
                return item
        return None

    def getTotalOrderCost(self, ID, color, quantity):#Get total cost of order
        item = self.getItem(ID)
        return int(item.type[color][0]) * int(quantity)

    def updateItems(self, ID, color, quantity, typeof):
        self.lock.acquire()
        if typeof == "purchase":#Remove quantity from item object if purchase
            item = self.getItem(ID)
            item.type[color][1] = str(int(item.type[color][1]) - int(quantity))
            self.serverData.updateItems()#Also update items.txt
        elif typeof == "return":#Add quantity from item object if purchase
            item = self.getItem(ID)
            item.type[color][1] = str(int(item.type[color][1]) + int(quantity))
            self.serverData.updateItems()#Also update items.txt
        self.lock.release()

    def getAvailableItems(self, items):#Get all items that are available to purchase
        try:
            availableItems = []
            for item in items:
                quantity = item.split("-")[0]
                ID = item.split("-")[1]
                color = item.split("-")[2]
                itemCheck = self.getItem(ID)
                if int(quantity) <= int(itemCheck.type[color][1]):
                    availableItems.append(item)

            return availableItems
        except Exception as e:
            print(f"Error getting available items: {e} at " + str(sys.exc_info()[2].tb_lineno))
    def getNonAvailableItems(self, items):#Get all items that are not available to purchase
        try:
            nonAvailableItems = []
            for item in items:
                quantity = item.split("-")[0]
                ID = item.split("-")[1]
                color = item.split("-")[2]
                itemCheck = self.getItem(ID)
                if int(quantity) > int(itemCheck.type[color][1]):
                    nonAvailableItems.append(item)
            return nonAvailableItems
        except Exception as e:
            print(f"Error getting non available items: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def checkPurchase(self, items, clientMsg):
        try:
            nonAvailableItems = self.getNonAvailableItems(items)
            availableItems = self.getAvailableItems(items)
            if len(nonAvailableItems) > 0:#If at least one unavailable item -> error
                serverMsg = "availabilityerror;"
                for item in nonAvailableItems:
                    if nonAvailableItems.index(item) == len(nonAvailableItems) - 1:
                        serverMsg = serverMsg + item
                    else:
                        serverMsg = serverMsg + item + ";"
                print(f"Sending: {serverMsg.encode()}")
                self.clientSocket.send(serverMsg.encode())
            else:
                cost = 0
                if len(availableItems) > 0:#Calculate total order cost for all available items
                    for item in availableItems:
                        itemRec = item.split("-")
                        quantity = itemRec[0]
                        itemID = itemRec[1]
                        color = itemRec[2]
                        cost = cost + self.getTotalOrderCost(itemID, color, quantity)
                        self.lock.acquire()
                        self.updateItems(itemID, color, quantity, "purchase")
                        self.lock.release()
                    serverMsg = "purchasesuccess;" + str(cost)
                    print(f"Sending: {serverMsg.encode()}")
                    self.clientSocket.send(serverMsg.encode())
                    self.lock.acquire()
                    self.serverData.addOperation(clientMsg, availableItems)#Update operations.txt
                    self.lock.release()
        except Exception as e:
            print(f"Error checking purchase: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def getCustomer(self, customerName):#Get customer by customer name
        for customer in self.serverData.customers:
            if customer.name == customerName:
                return customer

    def ifNotPurchased(self, customer, itemInfo):#If less or equal to purchase then it is allowed
        try:
            for operation in customer.operations:
                if isinstance(operation, Purchase):
                    itemRec = itemInfo.split("-")
                    returnedQuantity = itemRec[0]
                    returnedItemID = itemRec[1]
                    returnedColor = itemRec[2]
                    for item in operation.itemList:
                        itemRec = item.split("-")
                        purchasedQuantity = itemRec[0]
                        purchasedItemID = itemRec[1]
                        purchasedColor = itemRec[2]
                        if returnedItemID == purchasedItemID and returnedColor == purchasedColor:
                            if purchasedQuantity >= returnedQuantity:
                                return True

            return False
        except Exception as e:
            print(f"Error checking return: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def customerReturned(self, customer):#If customer returned an object return true
        for operation in customer.operations:
            if isinstance(operation, Return):
                return True

        return False

    def getTotalReturn(self, customer, ID):#Calculate total quantity of return a specific item has by a customer
        totalReturn = 0
        for operation in customer.operations:
            if isinstance(operation, Return):
                for item in operation.itemList:
                    if item.split("-")[1] == ID:
                        totalReturn = totalReturn + int(item.split("-")[0])
        print("totalReturn: " + str(totalReturn))
        return totalReturn

    def getTotalPurchase(self, customer, ID):#Calculate total quantity of purchase a specific item has by a customer
        totalPurchase = 0
        for operation in customer.operations:
            if isinstance(operation, Purchase):
                for item in operation.itemList:
                    if item.split("-")[1] == ID:
                        totalPurchase = totalPurchase + int(item.split("-")[0])
        print("totalPurchase: " + str(totalPurchase))
        return totalPurchase


    def ifNotAlreadyReturned(self, customer, itemInfo):
        try:
            if not self.customerReturned(customer):#If customer had no returns return true
                return True
            for operation in customer.operations:
                if isinstance(operation, Return):#Return is allowed is customer wants to return less or equal to the available quantity of item
                    itemRec = itemInfo.split("-")
                    returnedQuantity = itemRec[0]
                    returnedItemID = itemRec[1]
                    returnedColor = itemRec[2]
                    for item in operation.itemList:
                        itemRec = item.split("-")
                        alreadyReturnedItemID = itemRec[1]
                        alreadyReturnedColor = itemRec[2]
                        if returnedItemID == alreadyReturnedItemID and returnedColor == alreadyReturnedColor:
                            item = self.getItem(alreadyReturnedItemID)
                            print("item: "+ item.type[returnedColor][1])
                            if self.getTotalReturn(customer, alreadyReturnedItemID) + int(returnedQuantity) <= self.getTotalPurchase(customer, alreadyReturnedItemID):
                                return True

            return False
        except Exception as e:
            print(f"Error checking return: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def checkReturnAvailability(self, customer, items, availableItems):#Get all available to return items
        for item in items:
            if not self.ifNotPurchased(customer, item):
                return False
            else:
                if not self.ifNotAlreadyReturned(customer, item):
                    return False
                else:
                    availableItems.append(item)
                    return True

    def checkReturn(self, items, clientMsg):
        try:
            availableItems = []
            records = clientMsg.split(";")
            customerName = records[-1]
            customer = self.getCustomer(customerName)
            if self.checkReturnAvailability(customer, items, availableItems):
                serverMsg = "returnsuccess".encode()
                print(f"Sending: {serverMsg}")
                self.clientSocket.send(serverMsg)
                for item in items:
                    quantity = item.split("-")[0]
                    itemID = item.split("-")[1]
                    color = item.split("-")[2]
                    self.lock.acquire()
                    self.updateItems(itemID, color, quantity, "return")#Update items.txt
                    self.lock.release()
                self.lock.acquire()
                self.serverData.addOperation(clientMsg, availableItems)#Update operations.txt
                self.lock.release()
            else:
                serverMsg = "returnerror".encode()
                print(f"Sending: {serverMsg}")
                self.clientSocket.send(serverMsg)

        except Exception as e:
            print(f"Error checking return: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def checkReport(self, no):#send appropriate report
        serverMsg = "errorCreatingReport".encode()
        if no == 1:
            serverMsg = self.serverData.get_most_bought_item().encode()
        elif no == 2:
            serverMsg = self.serverData.get_highest_operations_store().encode()
        elif no == 3:
            serverMsg = self.serverData.get_total_generated_income().encode()
        elif no == 4:
            serverMsg = self.serverData.get_most_returned_color().encode()
        print(f"Sending: {serverMsg}")
        self.clientSocket.send(serverMsg)

    def run(self):
        try:
            print("Sending: connection status...")
            self.clientSocket.send("Server: connection successful".encode())
            while True:
                clientMsg = self.clientSocket.recv(1024).decode()
                print(f"Received from client: {clientMsg}")
                if not clientMsg or clientMsg == "exit":
                    break
                clientMsgRecords = clientMsg.split(";")
                if clientMsgRecords[0] == "login":
                    self.checkLogin(clientMsgRecords[1], clientMsgRecords[2], clientMsg)
                if clientMsgRecords[0] == "loginsuccess":
                    print(f"Sending: {clientMsg.encode()}")
                    self.clientSocket.send(clientMsg.encode())
                elif clientMsgRecords[0] == "purchase":
                    self.checkPurchase(clientMsgRecords[3:-1], clientMsg)
                elif clientMsgRecords[0] == "return":
                    self.checkReturn(clientMsgRecords[3:-1], clientMsg)
                elif clientMsgRecords[0] == "report":
                    self.checkReport(int(clientMsgRecords[1]))

        except Exception as e:
            print(f"Error handling client message during run: {e} at " + str(sys.exc_info()[2].tb_lineno))
        finally:
            print("Connection disconnected from ", self.clientAddress)
            self.clientSocket.close()