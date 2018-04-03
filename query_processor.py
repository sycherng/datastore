import main

class QueryProcessor:
    def __init__(self, query):
        self.query = query
        self.parsed_query_dict = {} #dict of valid flags to string specifying details
        #try to get all the flags
        self.parseQuery()

        #no point continuing if nothing selected
        if not ['-s'] in self.parsed_query_dict:
            raise SyntaxError("Nothing was selected with this query.")

        #is the filter request advanced? allows us to ignore advanced stuff for now
        self.filter_is_advanced = self.isFilterAdvanced() #boolean

        #try to parse the flags
        if self.filter_is_advanced == False:
            self.filter = self.parseSimpleFilter() #None or Tuple(String key, String specification)
        self.groups = self.parseGroups() #None or List(String key)
        self.selects = self.parseSelects() #List(Tuple(String key, String aggregate_option)
        self.orders = self.parseOrders() #None or List(Tuple(String key, String aggregate_option))

        #raise errors if fail logical checks like
            #-s items must be in -g or -s:agg
            #-o items must be in -g or -o:agg
        self.raiseErrorIfInvalidSelects()
        self.raiseErrorIfInvalidOrders()

    def raiseErrorIfInvalidSelects(self):
        for select in self.selects:
            key, aggregate_option = select
            if key in self.groups and aggregate_option == None:
                continue
            elif key not in self.groups and aggregate_option != None:
                continue
            raise SyntaxError("-s items must be in -g or -s:aggregated.")

    def raiseErrorIfInvalidOrders(self):
        for order in self.orders:
            key, aggregate_option = order
            if key in self.groups and aggregate_option == None:
                continue
            elif key not in self.groups and aggregate_option != None:
                continue
            raise SyntaxError("-o items must be in -g or -o:aggregated.")

    def parseOrders(self):
        if not '-o' in self.parsed_query_dict:
            return None
        orders = []
        order_string = self.parsed_query_dict['-o']
        comma_split_strings = order_string.split(',')
        for string in comma_split_strings:
            pair = string.split(':')
            key = pair[0]
            value = pair[1]
            QueryProcessor.raiseErrorIfInvalidKey(key, '-o')
            QueryProcessor.raiseErrorIfInvalidAggregate(value, '-o') 
            orders.append((key, value))
        return orders

    @staticmethod
    def raiseErrorIfInvalidAggregate(key, flag):
        if key not in main.VALID_AGGREGATE_OPTIONS:
            raise SyntaxError(f"{key} is an invalid aggregation option for {flag}.")


    def parseSelects(self):
        """(QueryProcessor) -> List(Tuple(String key, String aggregate_option)

        Example select_string: STB,PROVIDER,TITLE,REV:min,DATE:max
        """
        selects = []
        select_string = self.parsed_query_dict['-s']
        comma_split_strings = select_string.split(',')
        for string in comma_split_strings:
            pair = string.split(':')
            key = pair[0]
            value = pair[1]
            QueryProcessor.raiseErrorIfInvalidKey(key, '-s')
            
        selects.append((key, value))
        return selects

    def parseGroups(self):
        if not '-g' in self.parsed_query_dict:
            return None
        groups_string = self.tokenized_query_dict['-g']
        keys = groups_string.split(',')
        for key in keys:
            QueryProcessor.raiseErrorIfInvalidKey(key, '-g')
       return keys


    def parseFlags(self):
        if ['-f'] in self.parsed_query_dict and filter_is_advanced == False:
            self.parseSimpleFilter()

        if ['-g'] in self.parsed_query_dict:
            self.parseGroups()

        self.parseSelects()

        if ['-o'] in self.parsed_query_dict:
            self.parseOrders()

    def parseSimpleFilter(self):
        '''
        Accounts for edge case where a key such as TITLE contains multiple spaces, commas, and equal signs.
        '''
        if not '-f' in self.parsed_query_dict:
            return None
        filter_string = self.parsed_query_dict["-f"]
        eq_split_strings = filter_string.split("=")
        key = eq_split_strings[0]
        QueryProcessor.raiseErrorIfInvalidKey(key, '-f')
        value = '='.join(eq_split_strings[1:])
        if value == '':
            raise SyntaxError(f"-f key {key} lacks specifications.")
        return (key, value)


    def isFilterAdvanced(self):
         for token in ['AND', 'OR', '(', ')']:
            if token in self.parsed_query_dict['f']:
                return True
        return False

    def parseQuery(self):
        if self.query == '':
            return
        space_split_strings = self.query.split(" ")
        value_stringbuilder = ''
        prev_flag = None
        for string in space_split_strings:
            if string in main.VALID_FLAGS:
                self.updateTokenizedQueryDict(prev_flag, value_stringbuilder)
                value_stringbuilder = ''
                prev_flag = string
            else:
                value_stringbuilder += (string + ' ')
        self.updateParsedQueryDict(prev_flag, value_stringbuilder)

    def updateParsedQueryDict(self, key, value_stringbuilder):
        if value_stringbuilder == '':
            return
        QueryProcessor.raiseErrorIfDuplicate(key, 'query', self.parsed_query_dict)
        self.parsed_query_dict[key] = value_stringbuilder[:-1]
 
    @staticmethod
    def raiseErrorIfInvalidKey(key, flag):
        if key not in main.VALID_FLAGS:
            raise SyntaxError(f"{key} is an invalid key for {flag}.")

    @staticmethod
    def raiseErrorIfDuplicate(key, flag, dictionary):
        if key in dictionary:
            raise SyntaxError(f"{key} can only be specified once in {flag}.")

    def processQuery(self):
        #actually process the query
            #simple filter or complex filter to get data from datastore
            #group the data
            #select and aggregate the data
            #order the data



############################################old code###############
        self.flag_specs = self._getFlagsSpecs()
        if self.query = "": return #nothing to print, query is blank
        if "s" not in self.flags_specs: return #nothing to print, nothing is SELECTed        
        self.select_by = self._getSelectBy()
        self.aggregate_keys = self.getAggregateKeys()

        self.group_by = self._getGroupBy()
        self.order_by = self.getOrderBy()

    def _getOrderBy(self):
        order_by_tokens = self._getFlagSpecificTokens("o") #make self.order_by
        self._raiseErrorIfDuplicates(self.order_by, 'o') #no duplicates allowed in self.order_by
        self._validateOrderKeys()

    def _getGroupBy(self):
        group_by_tokens = self.getFlagSpecificTokens("g")
        self.raiseErrorIfDuplicates(group_by_tokens, "g")
        self.raiseErrorIfAggregatedOver(group_by_tokens, "g")
        return group_by_tokens
        
    def _getSelectBy(self):
        selected_tokens = self._getFlagSpecificTokens("s")
        selected = QueryProcessor._pairStringsToTuple(selected_tokens)
        return selected

    def _getAggregateKeys(self):
        return [select_by_tuple[0] for select_by_tuple in self.select_by if select_by_tuple[1] != None]

    def _raiseErrorIfAggregatedOver(keys_list, error, flag):
        #-g keys cannot be -s:aggregated over
        if [key for key in keys_list if key in self.aggregate_keys]:
        #alternatively if set(keys_list).intersection(set(self.aggregate_keys)):
            raise ValueError(f"-{flag} keys cannot be aggregated over.")

    def _validateOrderKeys(self):
        self.order_by #list of keys
        for order_key in self.order_by:
            if order_key not in self.group_by or order_key not in list(filter(lambda x: x[1] != None, self.select_by 
        if self._orderKeyNotInGroup() or self._orderKeyNotInAggregate()
            raise ValueError("-o keys must be in -g or -s:agg.")
#TODO^
    def _orderKeyNotInGroup(self):
    def _orderKeyNotInAggregate(self):

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
        #-s items must be in -g or -s:agg
        raise NotImplementedError("Advanced filtering not available.")

    def _satisfiesSimpleFilter(self, entry, filters):
        for filter_tuple in filters: #list of tuple
            filter_key, filter_value = filter_tuple
            if entry.getAttribute(filter_key) == filter_value:
                return True #ok as long as satisfies any of the simple filter tuples ex. ("REV", 4.00)
        return False


