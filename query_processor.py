class QueryProcessor:
    def __init__(self, query):
        self.query = query
        self.flag_specs = self._getFlagsSpecs()
        if self.query = "": return #nothing to print, query is blank
        if "s" not in self.flags_specs: return #nothing to print, nothing is SELECTed        

        self.group_by = self._getFlagSpecificTokens("g") #make self.group_by
        self._raiseErrorIfDuplicates(self.group_by, "g") #no duplicates allowed in self.group_by
        self.select_by = self._getSelectedList()         #make self.select_by
        self.order_by = self._getFlagSpecificTokens("o") #make self.order_by
        self._raiseErrorIfDuplicates(self.order_by, 'o') #no duplicates allowed in self.order_by

        if self._willAggregateByGroupKey():
            raise ValueError("-g keys cannot be aggregated over.")

    def _willAggregateByGroupKey()
        #-g keys cannot be -s:aggregated over
        #(key, None) <= aggregate by key, if key in g-keys, raise error
        for select_tuple in self.select_by:
            if select_tuple[1] == None and select_tuple[0] in self.group_by:
                    return True
        return False

    def _getFlagsSpecs(self):
        flags_split_query = self.query.split("-") #split at flags
        '''
        f KEY=value,KEY=valueSPACE
        g KEY,KEYSPACE
        s KEY:agg,KEYSPACE
        o KEY, KEY
        '''
        length = len(flags_split_query)
        flags_specs = {}
        for index in range(length):
            flag_segment = flags_split_query[index]
            if not index == length - 1: #last flag
                flag_segment = flags_split_query[:-1] #remove trailing space
            key = flag_segment[0] #flag letter
            if key not in main.VALID_FLAGS:
                raise ValueError(f"-{key} is an invalid flag.")
            value = flag_segment[2:] #remove flag letter and trailing space
            if key in self.flags_specs:
                raise ValueError(f"Duplicate flag -{key}."))
            flags_specs[key] = value
        return flags_specs   

    def _raiseErrorIfDuplicates(self, provided_list, flag):
        copy_list = provided_list.copy()
        copy_list.sort()
        last_item = None
        for item in copy_list:
            if item == last_item:
                raise ValueError("No duplicates allowed in -{flag}.")
            last_item = item

    def process(self):
        self._filter()
        if self.filtered_entries == []: return #nothing to print, no valid entries after filtering

        self._group()

        self._select()

    def _getFlagSpecificTokens(self, flag):
        if flag not in self.flags_specs: return []
        return self.flags_specs[flag].split(",")

    def _getSelectedList(self):
        selected_tokens = self._getFlagSpecificTokens("s")
        selected = QueryProcessor._pairStringsToTuple(selected_tokens)
        return selected           

    def _filter(self):
        simple_filter = self._checkIfSimpleFilter()
        if simple_filter:
            self.filtered_entries = self._getSimpleFilteredEntries()
        else:
            self.filtered_entries = self._getComplexFilteredEntries()        

    def _group(self):
        self.grouped_entries = {}
        for entry in self.filtered_entries:
            key = entry.getAttributesString(self.group_by)
            if key in self.grouped_entries:
                self.grouped_entries[key].append(entry)
            else:
                self.grouped_entries[key] = entry

    def _select(self):
        self.select_keys #list of tuples, sequence must be preserved
        self.grouped_entries #list of dict  
        #TODO       
 
    @staticmethod
    def _pairStringsToTuples(provided_list, delimiter="="): #delimiter=":" for -s flag
        '''(list of str, str) -> list of tuple | Takes a list of strings representing key value pairs and returns a list of tuples generated from those pairs.'''
        pairs = []
        for pair_string in provided_list:
            pairs.append(QueryProcessor._pairStringToTuple(pair_string, delimiter)
        return pairs

    @staticmethod
    def _pairStringToTuple(pair_string, delimiter):
        '''(str, str) -> tuple | Takes a string representing a key value pair and returns a tuple generated from that pair. If there is only a key, return a tuple of (key, None).'''
        try:
            pair_string.split(delimiter)
        except:
            key = pair_string
            value = None
        else:
            key = split_pair[0]
            value = split_pair[1]
        if key not in main.VALID_KEYS:
            raise ValueError(f'Invalid key \"{key}\".')
        return (key, value)
                 
    def _checkIfSimpleFilter(self):
        for token in ['(', ')', 'AND', 'OR']:
            if token in self.flags_specs['f']:
                return False
        return True

    def _getSimpleFilteredEntries(self):
        filter_tokens = self._getFlagSpecificTokens("f")
        filters = QueryProcessor._pairStringsToTuples(filter_tokens)
        filtered_entries = []
        self._raiseErrorIfDuplicates(filtered_entries)
        with open(main.DATASTORE_NAME) as ds:
            line = ds.readline()
            while line:
                entry = Entry.lineToEntry(line)
                if self._satisfiesSimpleFilter(entry, filters):
                    filtered_entries.append(entry)
        return filtered_entries

    def _getComplexFilteredEntries(self):
        raise NotImplementedError("Advanced filtering not available.")

    def _satisfiesSimpleFilter(self, entry, filters):
        for filter_tuple in filters: #list of tuple
            filter_key, filter_value = filter_tuple
            if entry.getAttribute(filter_key) == filter_value:
                return True #ok as long as satisfies any of the simple filter tuples ex. ("REV", 4.00)
        return False


