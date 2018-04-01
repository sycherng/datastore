class QueryProcessor:
    def __init__(self, query):
        self.query = query

    def process(self):
        if self.query = "": return #nothing to print, query is blank

        self._initializeQueryFlags()
        if "s" not in self.flags_specs: return #nothing to print, nothing is SELECTed

        self._filter()
        if self.filtered_entries == []: return #nothing to print, no valid entries after filtering

        self._group()

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
            if key not in main.VALID_FLAGS:
                raise ValueError(f"-{key} is an invalid flag.")
            value = flag_segment[2:] #remove flag letter and trailing space
            QueryProcessor.raiseErrorIfExists(key, self.flags_specs, ValueError(f"Duplicate flag -{key}."))
            self.flags_specs[key] = value    

    def _filter(self):
        simple_filter = self._checkIfSimpleFilter()
        if simple_filter:
            self.filtered_entries = self._getSimpleFilteredEntries()
        else:
            self.filtered_entries = self._getComplexFilteredEntries()        

    def _group(self):
        groups = self.getFlagSpecificTokens("g") # "REV","PROVIDER" #cat entry.group[0],entry.group[1] etc as key
        self.grouped_entries = {}
        for entry in self.filtered_entries:
            key = entry.getAttributesString(groups)
            if key in self.grouped_entries:
                self.grouped_entries[key].append(entry)
            else:
                self.grouped_entries[key] = entry
                 
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
        for spec_dict in filters:
            '''Footnote:
            There is only 1 key-value pair per spec_dict. 
            In order to get the key and value, we can either do:
                for k, v in spec_dict:
                    key = k
                    value = v
            or we can do:
                key = list(spec_dict.keys())[0]
                value = list(spec_dict.values())[1]
            Both look ugly, but the latter costs more time and space, 
            so I will opt for the former. Although it looks like O(n^2), 
            the inner loop really only ever runs once.
            Perhaps this indicates that a tuple is a better structure for spec_dict, 
            but at this point in implementation I suspect dict structure may come in handy further along the process.

            Memo: If it turns out dict doesn't provide extra benefits,
            I should convert to tuples and index[0], index[1] for k, v.
            '''
            for filter_key, filter_value in spec_dict:
                if Entry.getAttribute(filter_key) == filter_value:
                return True
        return False

    def _getFlagSpecificTokens(self, flag):
        if flag not in self.flags_specs: return []
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

