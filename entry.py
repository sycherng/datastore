class Entry:
    def __init__(self, fields_dict):
        self.stb = fields_dict["STB"] #pkey
        self.title = fields_dict["TITLE"] #pkey
        self.provider = fields_dict["PROVIDER"]
        self.date = fields_dict["DATE"] #pkey
        self.rev = fields_dict["REV"]
        self.view_time = fields_dict["VIEW_TIME"]

    def __str__(self):
        return "{}|{}|{}".format(
            self.stb[:5], 
            self.title[:5], 
            "".join(self.date.split('-'))[2:])

    def __repr__(self):
        return "{}|{}|{}|{}|{}|{}".format(
            self.stb[:6],
            self.title[:6],
            self.provider[:6],
            self.date,
            self.rev,
            self.view_time)

    @staticmethod
    def _compare(a, b):
        if a.stb > b.stb: return 1
        if a.title > b.title: return 1
        if a.date > b.date: return 1
        if a.stb == b.stb and a.title == b.title and a.date == b.date: return 0
        return -1

    def __lt__(self, other):
        return Entry._compare(self, other) < 0

    def __le__(self, other):
        return Entry._compare(self, other) <= 0

    def __gt__(self, other):
        return Entry._compare(self, other) > 0

    def __ge__(self, other):
        return Entry._compare(self, other) >= 0

    def __eq__(self, other):
        return Entry._compare(self, other) == 0

    def __ne__(self, other):
        return Entry._compare(self, other) != 0

    @classmethod
    def lineToEntry(cls, line, fields=main.DATASTORE_HEADING, delimiter="|"):
        """(str, str, str) -> Entry | instantiate an Entry object given a line in a file, fields, and delimiter"""
        if not line or line.isspace(): return None
        line = line[:-1] #remove /n
        line_dict = dict(zip(fields.split(delimiter), (value for value in line.split(delimiter))))
        return cls(line_dict)

    @staticmethod
    def sortEntries(list_of_entries):
        """(list) -> None | Tim sorts a list of Entry objects by primary keys .stb, .title, .date"""
        list_of_entries.sort()

    def toStorageString(self):
        """(Entry) -> str | Returns the string this Entry will be stored as in datastore"""
        return "{}|{}|{}|{}|{}|{}\n".format(
            self.stb,
            self.title,
            self.date,
            self.provider,
            self.rev,
            self.view_time)

    def getAttribute(self, attribute):
        if attribute = "STB":
            return self.stb
        elif attribute = "TITLE":
            return self.title
        elif attribute = "PROVIDER":
            return self.provider
        elif attribute = "DATE":
            return self.date
        elif attribute = "REV":
            return self.rev
        elif attribute = "VIEW_TIME":
            return self.view_time
        else:
            raise ValueError(f"Entry class has no .{attribute} attribute.")

    def getAttributesString(self, attributes_list):
        attributes_string = ''
        for attribute in attributes_list: #loops over a max of len(main.VALID_HEADINGS), in this case 6 items
            attributes_string.append(self.getAttribute(attribute)
        return attributes_string
