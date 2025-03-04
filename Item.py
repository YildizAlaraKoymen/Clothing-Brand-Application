class Item:

    def __init__(self, itemID=0, itemName="N/A", color="N/A", price=0, stockAvailable=0):
        self.itemID = itemID
        self.itemName = itemName
        self.type = {color: [price, stockAvailable]}

