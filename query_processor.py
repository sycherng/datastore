import main

#call QueryProcessor(query).process()
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

    def process(self):
        #actually process the query
        #simple filter or complex filter to get data from datastore
        self.filtered_entries = self.getFilteredEntries()
        #group the data #TODO last point
        #select and aggregate the data
        #order the data

    def getFilteredEntries(self):
        if self.filter_is_advanced:
            return self.getAdvancedFilteredEntries()
        else:
            return self.getSimpleFilteredEntries()

    def getSimpleFilteredEntries(self):
        """None or Tuple(String key, String specification)
        (REV, 4.00)
        """
        if self.filter != ():
            check = self.simpleFilteredCheck()

        with open(main.DATASTORE_NAME) as datastore:
            line = datastore.readline()
            while line:
                entry = Entry.lineToEntry(line)
                if self.survivesSimpleFilter():
                    filtered_entries.append(entry)
        return filtered_entries

    def survivesSimpleFilter(self);
        if self.filter == (): #no filters, automatically passes
            return True
        key, value = self.filter
        if entry.getAttribute(key) == value:
            return True
        return False

    def getAdvancedFilteredEntries(self):
        #TODO implement this using expression tree parsing -> getting valid entries from datastore.
        #Reminder: -s items must be in -g or -s:agg
        raise NotImplementedError("Advanced filtering not available.")


############################################old code###############
    def _getAggregateKeys(self):
        return [select_by_tuple[0] for select_by_tuple in self.select_by if select_by_tuple[1] != None]

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
