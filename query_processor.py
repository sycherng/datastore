class QueryProcessor:
    def __init__(self, query):
        self.query = query

    def process(self):
        if self.query = "":
            print("")
            return

        self._initializeQueryFlags()
        if "s" not in self.flags_specs:
            print("")
            return

        simple_filter = self._checkIfSimpleFilter()
        if simple_filter:
            self.filtered_entries = self._getSimpleFilteredEntries()
        else:
            self.filtered_entries = self._getComplexFilteredEntries()
 
    def _initializeQueryFlags(self):
        flags_split_query = self.query.split("-") #split at flags
        '''
        f KEY=value,KEY=valueSPACE
        g KEY,KEYSPACE
        s KEY:agg,KEYSPACE
        o KEY, KEY
        '''
        length = len(flags_split_query)
        self.flags_specs = {}
        for index in range(length):
            flag_segment = flags_split_query[index]
            if not index == length - 1: #last flag
                flag_segment = flags_split_query[:-1] #remove trailing space
            key = flag_segment[0] #flag letter
            if key not in ['f, g, s, o']:
                raise ValueError(f"-{key} is an invalid flag.")
            value = flag_segment[2:] #remove flag letter and trailing space
            QueryProcessor.raiseErrorIfExists(key, self.flags_specs, ValueError(f"Duplicate flag -{key}."))
            self.flags_specs[key] = value    
                
    @staticmethod
    def raiseErrorIfExists(key, provided_dict, error):
        if key in provided_dict:
            raise error

    def _checkIfSimpleFilter(self):
        for token in ['(', ')', 'AND', 'OR']:
            if token in self.flags_specs['f']:
                return False
        return True

    def _getSimpleFilteredEntries(self):
        filter_tokens = self._getFlagSpecificTokens("f")
        filters = QueryProcessor._pairStringsToDicts(filter_tokens)
        filtered_entries = []
        with open(main.DATASTORE_NAME) as ds:
            line = ds.readline()
            while line:
                entry = Entry.lineToEntry(line)
                if self._satisfiesSimpleFilter(entry, filters):
                    filtered_entries.append(entry)
        return filtered_entries

    def _satisfiesSimpleFilter(self, entry, filters):
        for spec in filters:

    @staticmethod
    def _satisfiesSpec(entry, spec):
        spec_key = 
        spec_value = 
        if spec_key = "STB":
            return spec_value == entry.stb
        elif spec_key = "TITLE":
            return spec_value == entry.title
        elif spec_key = "PROVIDER":
            return spec_value == entry.provider
        elif spec_key = "DATE":
            return spec_value == entry.date
        elif spec_key = "REV":
            return spec_value == entry.rev
        else: # spec_key = "VIEW_TIME"
            return spec_value == entry.view_time

    def _getFlagSpecificTokens(self, flag):
        return self.flags_specs[flag].split(",")

    @staticmethod
    def _pairStringsToDicts(provided_list, delimiter="="): #delimiter=":" for -s flag
        '''(list of str, str) -> list of dict | Takes a list of strings representing key value pairs and returns a list of dict generated from those pairs.'''
        pairs = []
        for pair_string in provided_list:
            pairs.append(QueryProcessor._pairStringToDict(pair_string, delimiter)
        return pairs

    @staticmethod
    def _pairStringToDict(pair_string, delimiter):
        '''(str, str) -> dict | Takes a string representing a key value pair and returns a dict generated from that pair.'''
        split_pair = pair_string.split(delimiter)
        key = split_pair[0]
        if key not in main.VALID_KEYS:
            raise ValueError(f'Invalid key \"{key}\".')
        value = split_pair[1]
        return dict(key=value)

    def _getComplexFilteredEntries(self):
        raise NotImplementedError("Advanced filtering not available.")

