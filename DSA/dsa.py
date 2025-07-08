# -------------LDS-------------#
# Array vs LL

# -------------NLDS-------------#


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LL:
    def __init__(self):
        self.head = None

    def insert(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def display(self):
        current = self.head
        while current:
            print(current.data, end="->")
            current = current.next
        print(None)


if __name__ == "__main__":
    dd = LL()
    dd.insert(10)
    dd.insert(30)
    dd.display()


else:
    print("Usage: python my_script.py")
