
class Operation:
    def __init__(self, store = "N/A", itemList = None):
        self.store = store
        self.itemList = itemList

class Return(Operation):
    def __init__(self, store = "N/A", itemList = None):
        Operation.__init__(self, store, itemList)

class Purchase(Operation):
    def __init__(self, store = "N/A", itemList = None):
        Operation.__init__(self, store, itemList)