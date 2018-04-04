import values

class Entry:


    def __init__(self, fields_dict):
        """Initializes an Entry object from a dictionary with all 6 fields."""
        self.stb = fields_dict["STB"]
        self.title = fields_dict["TITLE"]
        self.provider = fields_dict["PROVIDER"]
        self.date = fields_dict["DATE"]
        self.rev = fields_dict["REV"]
        self.view_time = fields_dict["VIEW_TIME"]


    def __str__(self):
        """Informal string representation of Entry objects. Mostly for debugging."""
        return "{}|{}|{}".format(
            self.stb[:5], 
            self.title[:5], 
            "".join(self.date.split('-'))[2:]) ##YYMMDD


    def __repr__(self):
        """Formal string representation of Entry objects. Mostly for debugging."""
        return "{}|{}|{}|{}|{}|{}".format(
            self.stb[:6],
            self.title[:6],
            self.provider[:6],
            self.date,
            self.rev,
            self.view_time)


    @staticmethod
    def _compare(a, b):
        """(Entry, Entry) -> int
        Compares 2 Entry objects by their primary keys,
        returns 1 if a > b, 0 if a == b, -1 if a < b."""
        if a.stb > b.stb: return 1
        if a.title > b.title: return 1
        if a.date > b.date: return 1
        if a.stb == b.stb and a.title == b.title and a.date == b.date: return 0
        return -1


    def __lt__(self, other): #< operator override
        return Entry._compare(self, other) < 0


    def __le__(self, other): #<= operator override
        return Entry._compare(self, other) <= 0


    def __gt__(self, other): #> operator override
        return Entry._compare(self, other) > 0


    def __ge__(self, other): #>= operator override
        return Entry._compare(self, other) >= 0


    def __eq__(self, other): #== operator override
        return Entry._compare(self, other) == 0


    def __ne__(self, other): #!= operator override
        return Entry._compare(self, other) != 0


    @classmethod
    def lineToEntry(cls, line, fields=values.DATASTORE_HEADING, delimiter="|"):
        """(Entry, str, str, str) -> Entry
        Instantiates an Entry object given a line in a file, fields, and delimiter."""
        if not line or line.isspace():
            return
        line = line[:-1] #remove /n
        line_dict = dict(zip(fields.split(delimiter), (value for value in line.split(delimiter))))
        return cls(line_dict)


    @staticmethod
    def sortEntries(list_of_entries):
        """(list<Entry>) -> None
        Tim sorts a list of Entry objects based on the operator overrides for Entry class.
        In other words, this sorts a list of Entry objects by primary keys .stb, .title, .date"""
        list_of_entries.sort()


    def toStorageString(self):
        """(self) -> str
        Returns a storable string representation of this Entry to be inserted to our datastore."""
        return "{}|{}|{}|{}|{}|{}\n".format(
            self.stb,
            self.title,
            self.date,
            self.provider,
            self.rev,
            self.view_time)


    def getAttribute(self, attribute):
        """(self, str) -> str
        Attribute getter."""
        if attribute == "STB":
            return self.stb
        elif attribute == "TITLE":
            return self.title
        elif attribute == "PROVIDER":
            return self.provider
        elif attribute == "DATE":
            return self.date
        elif attribute == "REV":
            return self.rev
        elif attribute == "VIEW_TIME":
            return self.view_time
        else:
            raise ValueError(f"Entry class has no .{attribute} attribute.")


    def toDict(self):
        """(self) -> dict
        Returns a dictionary representation of an Entry object."""
        dictionary = {}
        dictionary['STB'] = self.stb
        dictionary['TITLE'] = self.title
        dictionary['PROVIDER'] = self.provider
        dictionary['DATE'] = self.date
        dictionary['REV'] = self.rev
        dictionary['VIEW_TIME'] = self.view_time
        return dictionary


    def getAttributesString(self, attributes_list):
        """(self, List<str>) -> str
        Returns a string with the concatenation of all attributes of this Entry
        specified in a list of attributes."""
        attributes_stringbuilder = ''
        for attribute in attributes_list: #Max 6 valid attributes
            attributes_stringbuilder += self.getAttribute(attribute)
        return attributes_stringbuilder
