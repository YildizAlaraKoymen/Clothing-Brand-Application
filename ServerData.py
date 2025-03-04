from User import User
from Operation import *
from Customer import Customer
from Item import Item
import sys


class ServerData:
    def __init__(self):  # Object oriented approach has been taken
        self.users = self.loadUser()
        self.items = self.loadItems()
        self.customers = self.loadCustomers()

    def stripNewline(self, filename):  # Strip trailing newline (mostly used before reading a txt file)
        try:
            try:
                file = open(filename, 'r')
            except IOError:
                print(f"{filename} could not be opened")
                return

            updated = file.read().rstrip("\n")
            file.close()

            try:
                file = open(filename, 'w')
            except IOError:
                print(f"{filename} could not be opened")
                return

            file.write(updated)
            file.close()

        except Exception as e:
            print(f"Error updating item.txt: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def updateItems(self):  # Update items.txt
        try:
            try:
                itemFile = open("items.txt", "w")
            except IOError:
                print("items.txt could not be opened")
                return None

            for item in self.items:
                for key in item.type.keys():
                    line = item.itemID + ";" + item.itemName + ";"
                    line = line + key + ";" + item.type[key][0] + ";" + item.type[key][1]
                    itemFile.write(line + "\n")

            itemFile.close()
            self.stripNewline("items.txt")
            self.items = self.loadItems()

        except Exception as e:
            print(f"Error updating item.txt: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def addCustomer(self, store, customerName, typeof, items, customers):  # Add customer to self.customers
        try:
            operation = None
            if typeof == "purchase":
                operation = Purchase(store, items)
            elif typeof == "return":
                operation = Return(store, items)

            existCustomer = self.checkCustomer(customerName, customers)
            if existCustomer is not None:
                existCustomer.operations.append(operation)
            else:
                customer = Customer(customerName)
                customer.operations.append(operation)
                customers.append(customer)
        except Exception as e:
            print(f"Error adding customer: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def addOperation(self, clientMsg, availableItems):  # Update addOperation.txt
        try:
            if len(availableItems) == 0:
                return
            records = clientMsg.split(";")
            typeof = records[0]
            store = records[1]
            items = records[3].split(";")
            customerName = records[-1]
            line = typeof + ";" + store + ";" + customerName + ";"

            for item in availableItems:
                if len(availableItems) - 1 == availableItems.index(item):
                    line = line + item
                else:
                    line = line + item + ";"

            try:
                operationFile = open("operations.txt", "a")
            except IOError:
                print("operations.txt could not be opened")
                return

            operationFile.write(line + "\n")
            operationFile.close()

            self.addCustomer(store, customerName, typeof, items, self.customers)

        except Exception as e:
            print(f"Error updating operations.txt: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def loadUser(self):  # Fill users from file
        try:
            try:
                userFile = open("users.txt", 'r')
            except IOError:
                print("users.txt could not be opened")
                return []

            userLine = userFile.read().split("\n")
            userFile.close()
            users = []

            if len(userLine) <= 1:
                print("End of file of users.txt")
                return []

            for line in userLine:
                records = line.split(";")
                user = User(records[0], records[1], records[2])
                users.append(user)

            return users
        except Exception as e:
            print(f"Error loading users: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def get_most_bought_item(self):  # Report 1
        try:
            with open("operations.txt", "r+") as operationFile:
                self.stripNewline("operations.txt")
                operation_lines = operationFile.read().splitlines()
                operationFile.write("\n")
                item_counts = {}

                for line in operation_lines:
                    records = line.split(";")
                    if records[0] == "purchase":
                        items = records[3:]
                        for item in items:
                            quantity, item_id, _ = item.split("-")  # Splitting into quantity, itemID, and color
                            item_counts[item_id] = item_counts.get(item_id, 0) + int(quantity)

                # Finding the most bought item count
                max_bought_item = max(item_counts.values(), default=0)

                # collect all items with maximum operations count
                max_items = [item for item, count in item_counts.items() if count == max_bought_item]

                # Prepare the message
                if max_items:
                    message = "The item(s) with the highest number of purchases is/are: "
                    appendage = ", ".join(
                        f"{self.checkItem(item, self.items).itemName} ({item_counts[item]} times)" for item in
                        max_items)
                    return message + appendage
                else:
                    return "No operations data available."
        except Exception as e:
            print(f"Error processing most bought item: {e} at " + str(sys.exc_info()[2].tb_lineno))
            return f"Error processing most bought item: {e}"

    def get_highest_operations_store(self):  # Report2
        try:
            with open("operations.txt", "r+") as operationFile:
                self.stripNewline("operations.txt")
                operation_lines = operationFile.read().splitlines()
                operationFile.write("\n")
                store_operations = {}

                for line in operation_lines:
                    records = line.split(";")
                    store_id = records[1]
                    store_operations[store_id] = store_operations.get(store_id, 0) + 1

                # Find the maximum operations count
                max_operations = max(store_operations.values(), default=0)

                # Collect all stores with the maximum operations count
                max_occurrences = [store for store, count in store_operations.items() if count == max_operations]

                # Prepare the message
                if max_occurrences:
                    message = "The store(s) with the highest number of operations is/are: "
                    appendage = ", ".join(
                        f"{store} ({store_operations[store]} operations)" for store in max_occurrences)
                    return message + appendage
                else:
                    return "No operations data available."

        except Exception as e:
            print(f"Error processing highest operations store: {e} at" + str(sys.exc_info()[2].tb_lineno))
            return f"Error processing highest operations store: {e}"

    def get_total_generated_income(self):  # Report3
        try:
            with open("operations.txt", "r+") as operationFile:
                self.stripNewline("operations.txt")
                operation_lines = operationFile.read().splitlines()
                total_income = 0
                operationFile.write("\n")

                for line in operation_lines:
                    records = line.split(";")
                    if records[0] == "purchase":
                        items = records[3:]
                        for item in items:
                            quantity, item_id, item_color = item.split("-")
                            item = self.checkItem(item_id, self.items)
                            if item:
                                price = float(item.type[item_color][0])
                                total_income += price * int(quantity)
                    elif records[0] == "return":
                        items = records[3:]
                        for item in items:
                            quantity, item_id, item_color = item.split("-")
                            item = self.checkItem(item_id, self.items)
                            if item:
                                price = float(item.type[item_color][0])
                                total_income -= price * int(quantity)

                return f"The total generated income of the store is: ${total_income:.2f}."
        except Exception as e:
            print(f"Error calculating total income: {e} at" + str(sys.exc_info()[2].tb_lineno))
            return f"Error calculating total income: {e}"

    def get_most_returned_color(self):  # Report4
        try:
            with open("operations.txt", "r+") as operationFile:
                self.stripNewline("operations.txt")
                operation_lines = operationFile.read().splitlines()
                operationFile.write("\n")
                color_returns = {}

                for line in operation_lines:
                    records = line.split(";")
                    if records[0] == "return":
                        items = records[3:]
                        for item in items:
                            _, itemID, color = item.split("-")  # Extracting the colour
                            if itemID == "1":
                                color_returns[color] = color_returns.get(color, 0) + 1

                if len(color_returns) == 0:
                    return "No returns"

                # Finding the most returned color
                top_color = max(color_returns, key=color_returns.get, default=None)
                if top_color:
                    return f"The most returned color for the Basic T-shirt is: {top_color} ({color_returns[top_color]} returns)."
                else:
                    return "No return data available."
        except Exception as e:
            print(f"Error processing most returned color: {e} at" + str(sys.exc_info()[2].tb_lineno))
            return f"Error processing most returned color: {e}"

    def checkCustomer(self, name, customers):  # return customer by name
        for customer in customers:
            if customer.name == name:
                return customer
        return None

    def loadCustomers(self):  # Load all customers from operations.txt
        try:
            self.stripNewline("operations.txt")
            try:
                operationFile = open("operations.txt", 'r+')
            except IOError:
                print("operations.txt could not be opened")
                return []

            operationLine = operationFile.read().split("\n")
            operationFile.write("\n")
            operationFile.close()
            customers = []

            for line in operationLine:
                records = line.split(";")
                items = records[3:]
                self.addCustomer(records[1], records[2], records[0], items, customers)

            return customers

        except Exception as e:
            print(f"Error loading customer: {e} at " + str(sys.exc_info()[2].tb_lineno))

    def checkItem(self, ID, items):  # Return item by ID
        for item in items:
            if item.itemID == ID:
                return item

        return None

    def loadItems(self):  # Fill items
        try:
            try:
                itemFile = open("items.txt", 'r')
            except IOError:
                print("items.txt could not be opened")
                return []

            itemLine = itemFile.read().split("\n")
            itemFile.close()
            items = []

            if len(itemLine) <= 1:
                print("End of file of items.txt")
                return []
            for line in itemLine:
                records = line.split(";")
                sameItem = self.checkItem(records[0], items)
                if sameItem is not None:
                    sameItem.type[records[2]] = [records[3], records[4]]
                else:
                    item = Item(records[0], records[1], records[2], records[3], records[4])
                    items.append(item)

            return items
        except Exception as e:
            print(f"Error loading items: {e} at " + str(sys.exc_info()[2].tb_lineno))