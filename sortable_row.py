class SortableRow:
    """Convenience class to help sort rows 
    by *arbitrary number of ordering keys when ORDER BY clause has multiple parameters.

    Example: -o STB,DATE,REV:min,VIEW_TIME:max

    *maxes out at 30 ordering keys (6 valid keys * 5 aggregate options)
    """

    def __init__(self, row, order_keys):
        self.attributes_dict = row
        self.order_keys = order_keys


    @staticmethod
    def _compare(a, b, order_keys):
        """(SortableRow, SortableRow, list<str>) -> int
        Compares 2 SortableRow objects 
        by an arbitrary length list of attributes_dict keys.

        Example order_keys:
        ['STB', 'DATE', 'REV:min', 'VIEW_TIME:max']
        """
        for key in order_keys:
            if a.attributes_dict[key] > b.attributes_dict[key]:
                return 1

            elif a.attributes_dict[key] < b.attributes_dict[key]:
                return -1

        return 0


    def __lt__(self, other): #< operator override
        return SortableRow._compare(self, other, self.order_keys) < 0


    def __le__(self, other): #<= operator override
        return SortableRow._compare(self, other, self.order_keys) <= 0


    def __gt__(self, other): #> operator override
        return SortableRow._compare(self, other, self.order_keys) > 0


    def __ge__(self, other): #>= operator override
        return SortableRow._compare(self, other, self.order_keys) >= 0


    def __eq__(self, other): #== operator override
        return SortableRow._compare(self, other, self.order_keys) == 0


    def __ne__(self, other): #!= operator override
        return SortableRow._compare(self, other, self.order_keys) != 0
