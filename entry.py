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
