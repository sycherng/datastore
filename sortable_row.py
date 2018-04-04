class SortableRow:
    def __init__(self, row, order_keys):
        self.row = row
        self.order_keys = order_keys

    def compare(self, other, order_keys):
        for key in order_keys:
            if self.row[key] > other.row[key]:
                return 1

        for key in order_keys:
            if self.row[key] != other.row[key]:
                return -1

        return 0

    def __lt__(self, other):
        return self.compare(other, self.order_keys) < 0

    def __le__(self, other):
        return self.compare(other, self.order_keys) <= 0

    def __gt__(self, other):
        return self.compare(other, self.order_keys) > 0

    def __ge__(self, other):
        return self.compare(other, self.order_keys) >= 0

    def __eq__(self, other):
        return self.compare(other, self.order_keys) == 0

    def __ne__(self, other):
        return self.compare(other, self.order_keys) != 0

